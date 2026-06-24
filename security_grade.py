"""Security Headers & SSL/TLS grading — SSL Labs-style posture analysis."""

import re
import ssl
import socket
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests


HEADER_CHECKS = [
    {
        "name": "Strict-Transport-Security",
        "key": "strict-transport-security",
        "max_points": 15,
        "description": "Forces browsers to use HTTPS",
    },
    {
        "name": "Content-Security-Policy",
        "key": "content-security-policy",
        "max_points": 15,
        "description": "Mitigates XSS and data injection attacks",
    },
    {
        "name": "X-Frame-Options",
        "key": "x-frame-options",
        "max_points": 10,
        "description": "Prevents clickjacking via iframe embedding",
        "alt_keys": ["content-security-policy"],
        "alt_check": "frame-ancestors",
    },
    {
        "name": "X-Content-Type-Options",
        "key": "x-content-type-options",
        "max_points": 10,
        "description": "Blocks MIME-type sniffing",
    },
    {
        "name": "Referrer-Policy",
        "key": "referrer-policy",
        "max_points": 10,
        "description": "Controls referrer information leakage",
    },
    {
        "name": "Permissions-Policy",
        "key": "permissions-policy",
        "max_points": 10,
        "description": "Restricts browser feature access",
        "alt_keys": ["feature-policy"],
    },
]

SSL_MAX_POINTS = 30


def _parse_cert_date(date_str):
    return datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)


def _score_hsts(value):
    if not value:
        return 0, "Missing"
    lower = value.lower()
    score = 8
    notes = []
    max_age_match = re.search(r"max-age=(\d+)", lower)
    if max_age_match:
        max_age = int(max_age_match.group(1))
        if max_age >= 31536000:
            score = 12
            notes.append("max-age ≥ 1 year")
        elif max_age >= 86400:
            score = 10
            notes.append("max-age ≥ 1 day")
        else:
            score = 6
            notes.append("max-age too short")
    if "includesubdomains" in lower.replace(" ", ""):
        score = min(score + 2, 15)
        notes.append("includeSubDomains")
    if "preload" in lower:
        score = 15
        notes.append("preload enabled")
    status = "pass" if score >= 12 else "warn" if score >= 6 else "fail"
    return score, "; ".join(notes) or value[:80]


def _score_csp(value, headers):
    report_only = headers.get("content-security-policy-report-only", "")
    if not value and report_only:
        return 10, "Report-Only policy (not enforced)"
    if not value:
        return 0, "Missing"
    lower = value.lower()
    if "default-src" in lower or "script-src" in lower:
        return 15, "Policy defined"
    return 8, "Present but weak"


def _score_xfo(value, headers):
    csp = headers.get("content-security-policy", "")
    if csp and "frame-ancestors" in csp.lower():
        return 10, "CSP frame-ancestors"
    if not value:
        return 0, "Missing"
    upper = value.upper()
    if upper in ("DENY", "SAMEORIGIN") or upper.startswith("ALLOW-FROM"):
        return 10, value
    return 5, value


def _score_xcto(value):
    if not value:
        return 0, "Missing"
    if value.lower().strip() == "nosniff":
        return 10, "nosniff"
    return 5, value


def _score_referrer(value):
    if not value:
        return 0, "Missing"
    strong = {"no-referrer", "strict-origin", "strict-origin-when-cross-origin", "same-origin", "no-referrer-when-downgrade"}
    if value.lower().strip() in strong:
        return 10, value
    return 6, value


def _score_permissions(value):
    if not value:
        return 0, "Missing"
    return 10, "Policy defined"


def _score_header(check, headers):
    key = check["key"]
    value = headers.get(key, "")
    if not value and check.get("alt_keys"):
        for alt in check["alt_keys"]:
            alt_val = headers.get(alt, "")
            if alt_val and check.get("alt_check") in alt_val.lower():
                value = alt_val
                break

    name = check["name"]
    max_pts = check["max_points"]

    if name == "Strict-Transport-Security":
        pts, detail = _score_hsts(value)
    elif name == "Content-Security-Policy":
        pts, detail = _score_csp(value, headers)
    elif name == "X-Frame-Options":
        pts, detail = _score_xfo(value, headers)
    elif name == "X-Content-Type-Options":
        pts, detail = _score_xcto(value)
    elif name == "Referrer-Policy":
        pts, detail = _score_referrer(value)
    elif name == "Permissions-Policy":
        pts, detail = _score_permissions(value)
    else:
        pts = max_pts if value else 0
        detail = value[:80] if value else "Missing"

    status = "pass" if pts >= max_pts * 0.8 else "warn" if pts > 0 else "fail"
    return {
        "name": name,
        "present": bool(value),
        "value": value or None,
        "status": status,
        "points": pts,
        "max_points": max_pts,
        "detail": detail,
        "description": check["description"],
    }


def _analyze_ssl(hostname, port=443):
    result = {
        "enabled": False,
        "protocol": None,
        "certificate": None,
        "issues": [],
        "points": 0,
        "max_points": SSL_MAX_POINTS,
    }

    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=8) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                result["enabled"] = True
                result["protocol"] = ssock.version()
                cert = ssock.getpeercert()
                if not cert:
                    result["issues"].append("No certificate returned")
                    return result

                not_before = _parse_cert_date(cert["notBefore"])
                not_after = _parse_cert_date(cert["notAfter"])
                now = datetime.now(timezone.utc)
                days_remaining = (not_after - now).days

                issuer_parts = dict(x[0] for x in cert.get("issuer", []))
                subject_parts = dict(x[0] for x in cert.get("subject", []))

                result["certificate"] = {
                    "issuer": issuer_parts.get("organizationName", issuer_parts.get("commonName", "Unknown")),
                    "subject": subject_parts.get("commonName", hostname),
                    "valid_from": not_before.isoformat(),
                    "valid_until": not_after.isoformat(),
                    "days_remaining": days_remaining,
                    "valid": not_before <= now <= not_after,
                }

                points = 10  # HTTPS + valid connection
                if result["certificate"]["valid"]:
                    points += 10
                else:
                    result["issues"].append("Certificate expired or not yet valid")

                if days_remaining < 30:
                    result["issues"].append(f"Certificate expires in {days_remaining} days")
                else:
                    points += 5

                proto = result["protocol"] or ""
                if "TLSv1.3" in proto:
                    points += 5
                elif "TLSv1.2" in proto:
                    points += 3
                    result["issues"].append("Consider upgrading to TLS 1.3")
                else:
                    result["issues"].append(f"Weak protocol: {proto}")

                result["points"] = min(points, SSL_MAX_POINTS)
    except ssl.SSLCertVerificationError as e:
        result["issues"].append(f"Certificate verification failed: {e}")
        result["points"] = 5
    except (socket.timeout, socket.gaierror, ConnectionRefusedError, OSError) as e:
        result["issues"].append(f"SSL connection failed: {e}")
    except Exception as e:
        result["issues"].append(str(e))

    return result


def _score_to_grade(score):
    if score >= 97:
        return "A+"
    if score >= 93:
        return "A"
    if score >= 90:
        return "A-"
    if score >= 87:
        return "B+"
    if score >= 83:
        return "B"
    if score >= 80:
        return "B-"
    if score >= 77:
        return "C+"
    if score >= 73:
        return "C"
    if score >= 70:
        return "C-"
    if score >= 60:
        return "D"
    return "F"


def _grade_summary(grade, header_results, ssl_result):
    missing = [h["name"] for h in header_results if not h["present"]]
    if grade in ("A+", "A"):
        return "Excellent baseline security posture"
    if grade.startswith("B"):
        base = "Good security posture"
        if missing:
            return f"{base} — consider adding {missing[0]}"
        return base
    if grade.startswith("C"):
        return f"Fair posture — missing: {', '.join(missing[:3])}" if missing else "Fair security posture"
    if not ssl_result.get("enabled"):
        return "Critical: site not served over HTTPS"
    return "Poor security posture — immediate remediation recommended"


def analyze_security_posture(target_url):
    parsed = urlparse(target_url if "://" in target_url else f"https://{target_url}")
    hostname = parsed.hostname or target_url
    scheme = parsed.scheme or "https"
    fetch_url = f"{scheme}://{hostname}"
    if parsed.port and parsed.port not in (80, 443):
        fetch_url = f"{scheme}://{hostname}:{parsed.port}"

    headers = {}
    fetch_error = None
    try:
        resp = requests.get(fetch_url, timeout=10, allow_redirects=True, verify=True)
        headers = {k.lower(): v for k, v in resp.headers.items()}
        final_url = resp.url
        if urlparse(final_url).scheme == "https":
            scheme = "https"
    except requests.exceptions.SSLError:
        fetch_error = "SSL certificate error when fetching headers"
        try:
            resp = requests.get(fetch_url, timeout=10, allow_redirects=True, verify=False)
            headers = {k.lower(): v for k, v in resp.headers.items()}
        except Exception as e:
            fetch_error = str(e)
    except Exception as e:
        fetch_error = str(e)

    header_results = [_score_header(check, headers) for check in HEADER_CHECKS]
    header_points = sum(h["points"] for h in header_results)

    ssl_port = parsed.port or (443 if scheme == "https" else 443)
    ssl_result = _analyze_ssl(hostname, ssl_port)

    if scheme != "https" and not ssl_result["enabled"]:
        ssl_result["points"] = 0
        ssl_result["issues"].append("Site accessed over HTTP — no TLS encryption")

    total_score = header_points + ssl_result["points"]
    max_score = sum(c["max_points"] for c in HEADER_CHECKS) + SSL_MAX_POINTS
    normalized = round((total_score / max_score) * 100) if max_score else 0
    grade = _score_to_grade(normalized)

    hsts = next((h for h in header_results if h["name"] == "Strict-Transport-Security"), None)
    csp = next((h for h in header_results if h["name"] == "Content-Security-Policy"), None)
    if (
        grade == "A"
        and hsts
        and hsts["points"] == 15
        and csp
        and csp["points"] >= 15
        and ssl_result.get("protocol") == "TLSv1.3"
        and ssl_result.get("points", 0) >= 28
    ):
        grade = "A+"

    return {
        "grade": grade,
        "score": normalized,
        "headers": header_results,
        "ssl": ssl_result,
        "summary": _grade_summary(grade, header_results, ssl_result),
        "target": fetch_url,
        "fetch_error": fetch_error,
    }
