"""
SIEM integration module for VulnX.

Forwards vulnerability scan results to Elasticsearch/OpenSearch (ELK) or
Wazuh Indexer via REST API. Supports async delivery, retries, and local
fallback logging when the SIEM endpoint is unreachable.
"""

import json
import logging
import os
import threading
import time
from datetime import datetime, timezone
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

# Map scanner vulnerability types to SIEM severity levels.
SEVERITY_MAP = {
    "SQL Injection": "CRITICAL",
    "SQLi": "CRITICAL",
    "XSS": "HIGH",
    "Cross-Site Scripting": "HIGH",
    "CSRF": "MEDIUM",
    "Open Redirect": "MEDIUM",
    "Security Misconfiguration": "LOW",
    "Information Disclosure": "LOW",
}

DEFAULT_SEVERITY = "MEDIUM"
MAX_RETRIES = 3
RETRY_BASE_DELAY_SECONDS = 1.0


class SIEMForwarder:
    """Send VulnX vulnerability events to a SIEM system over HTTP."""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_token: Optional[str] = None,
        siem_type: Optional[str] = None,
    ):
        self.endpoint = (endpoint or os.environ.get("SIEM_ENDPOINT", "")).strip()
        self.api_token = (
            api_token
            or os.environ.get("SIEM_TOKEN")
            or os.environ.get("API_TOKEN")
            or ""
        ).strip()
        self.siem_type = (siem_type or os.environ.get("SIEM_TYPE", "auto")).lower()
        self.fallback_log_path = os.environ.get("SIEM_FALLBACK_LOG", "./siem_fallback.log")
        self.enabled = bool(self.endpoint)
        self.max_retries = MAX_RETRIES

        if self.enabled:
            logger.info(
                "[SIEM] Integration enabled — endpoint=%s type=%s",
                self.endpoint,
                self._resolve_siem_type(),
            )
        else:
            logger.info("[SIEM] Integration disabled — SIEM_ENDPOINT not configured")

    def _resolve_siem_type(self) -> str:
        if self.siem_type not in ("auto", ""):
            return self.siem_type
        endpoint_lower = self.endpoint.lower()
        if "wazuh" in endpoint_lower or ":55000" in endpoint_lower:
            return "wazuh"
        return "elasticsearch"

    @staticmethod
    def _utc_timestamp() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def generate_scan_id() -> str:
        return f"SCAN_{int(time.time() * 1000)}"

    @staticmethod
    def map_severity(vulnerability_type: str) -> str:
        return SEVERITY_MAP.get(vulnerability_type, DEFAULT_SEVERITY)

    def format_event(
        self,
        target_url: str,
        vulnerability: dict[str, Any],
        scan_id: str,
    ) -> dict[str, Any]:
        """Build a DPDPA-compliant audit log payload for a single finding."""
        vuln_type = vulnerability.get("type", "Unknown")
        affected_url = vulnerability.get("url", target_url)

        return {
            "timestamp": self._utc_timestamp(),
            "source": "VulnX_Scanner",
            "event_type": "VULNERABILITY_DETECTED",
            "scan_id": scan_id,
            "target_url": target_url,
            "vulnerability_type": vuln_type,
            "severity": self.map_severity(vuln_type),
            "message": f"VulnX detected {vuln_type} on {affected_url}",
            "compliance_tag": "DPDPA_AUDIT_LOG",
            "affected_url": affected_url,
        }

    def _build_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if not self.api_token:
            return headers

        if self.api_token.startswith(("Bearer ", "ApiKey ", "Basic ")):
            headers["Authorization"] = self.api_token
        elif self._resolve_siem_type() == "wazuh":
            headers["Authorization"] = f"Bearer {self.api_token}"
        else:
            headers["Authorization"] = f"ApiKey {self.api_token}"

        return headers

    def _wrap_for_wazuh(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Wrap the standard payload for Wazuh Indexer / manager ingestion.
        Wazuh expects alert-like documents with a nested data section.
        """
        return {
            "timestamp": payload["timestamp"],
            "rule": {
                "level": self._severity_to_wazuh_level(payload["severity"]),
                "description": payload["message"],
                "groups": ["vulnx", "web_security", "dpdpa"],
            },
            "agent": {"name": "VulnX_Scanner", "id": "000"},
            "data": payload,
        }

    @staticmethod
    def _severity_to_wazuh_level(severity: str) -> int:
        return {
            "CRITICAL": 12,
            "HIGH": 10,
            "MEDIUM": 7,
            "LOW": 3,
        }.get(severity, 5)

    def _prepare_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self._resolve_siem_type() == "wazuh":
            return self._wrap_for_wazuh(payload)
        return payload

    def _send_event(self, payload: dict[str, Any]) -> bool:
        """POST a single event to the configured SIEM endpoint with retry logic."""
        prepared = self._prepare_payload(payload)
        headers = self._build_headers()

        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.post(
                    self.endpoint,
                    json=prepared,
                    headers=headers,
                    timeout=10,
                )
                response.raise_for_status()
                logger.info(
                    "[SIEM] Event delivered — scan_id=%s type=%s severity=%s",
                    payload.get("scan_id"),
                    payload.get("vulnerability_type"),
                    payload.get("severity"),
                )
                return True
            except requests.RequestException as exc:
                logger.warning(
                    "[SIEM] Delivery attempt %d/%d failed: %s",
                    attempt,
                    self.max_retries,
                    exc,
                )
                if attempt < self.max_retries:
                    time.sleep(RETRY_BASE_DELAY_SECONDS * attempt)

        return False

    def _write_fallback_log(self, payload: dict[str, Any]) -> None:
        """Persist events locally when the SIEM endpoint is unavailable."""
        try:
            with open(self.fallback_log_path, "a", encoding="utf-8") as log_file:
                log_file.write(json.dumps(payload) + "\n")
            logger.error(
                "[SIEM] SIEM unreachable after %d attempts — event saved to %s",
                self.max_retries,
                self.fallback_log_path,
            )
        except OSError as exc:
            logger.error("[SIEM] Failed to write fallback log: %s", exc)

    def _forward_worker(self, payload: dict[str, Any]) -> None:
        if not self._send_event(payload):
            self._write_fallback_log(payload)

    def forward_vulnerability(
        self,
        target_url: str,
        vulnerability: dict[str, Any],
        scan_id: str,
    ) -> None:
        """Queue a single vulnerability event for async SIEM delivery."""
        if not self.enabled:
            return

        payload = self.format_event(target_url, vulnerability, scan_id)
        thread = threading.Thread(
            target=self._forward_worker,
            args=(payload,),
            daemon=True,
            name=f"siem-forward-{scan_id}",
        )
        thread.start()

    def forward_scan_results(
        self,
        target_url: str,
        vulnerabilities: list[dict[str, Any]],
        scan_id: Optional[str] = None,
    ) -> str:
        """
        Forward all vulnerabilities from a completed scan without blocking the caller.

        Returns the scan_id used for correlated SIEM events.
        """
        scan_id = scan_id or self.generate_scan_id()

        if not self.enabled:
            logger.debug("[SIEM] Skipping forward — integration disabled")
            return scan_id

        if not vulnerabilities:
            logger.info("[SIEM] No vulnerabilities to forward for scan_id=%s", scan_id)
            return scan_id

        logger.info(
            "[SIEM] Queuing %d event(s) for scan_id=%s target=%s",
            len(vulnerabilities),
            scan_id,
            target_url,
        )

        for vulnerability in vulnerabilities:
            self.forward_vulnerability(target_url, vulnerability, scan_id)

        return scan_id
