# VulnX SIEM Integration Guide

This document explains how to connect VulnX to a SIEM (Security Information and Event Management) platform so every detected vulnerability is forwarded as a structured audit log for monitoring and DPDPA compliance.

## Overview

When a scan completes, VulnX automatically sends one SIEM event per vulnerability via `siem_integration.py`. Delivery is **asynchronous** — scans return immediately while events are forwarded in background threads.

Supported targets:

| Platform | Integration method |
|----------|-------------------|
| **Elasticsearch / ELK Stack** | Direct REST POST to an index document endpoint |
| **Wazuh** | REST POST to Wazuh Indexer (OpenSearch-compatible) or Wazuh manager API |

---

## Quick Start

### 1. Configure environment variables

Copy the example file and edit it:

```bash
cp .env.example .env
```

Minimum configuration:

```env
SIEM_ENDPOINT=http://localhost:9200/vulnx-logs/_doc
SIEM_TOKEN=your-api-key-or-bearer-token
```

If `SIEM_ENDPOINT` is not set, SIEM forwarding is disabled and scans work normally.

### 2. Install dependencies

```bash
pip install -r requirements.ext
```

The SIEM module uses the `requests` library (already included).

### 3. Start VulnX

```bash
python app.py
```

On startup you should see:

```
[SIEM] Integration enabled — endpoint=http://localhost:9200/vulnx-logs/_doc type=elasticsearch
[SERVER] SIEM integration active — endpoint=http://localhost:9200/vulnx-logs/_doc
```

### 4. Run a scan

Trigger a scan from the VulnX UI or via API:

```bash
curl -X POST http://localhost:5000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

Each finding generates a separate SIEM event with the same `scan_id` for correlation.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SIEM_ENDPOINT` | Yes (to enable) | Full REST URL for log ingestion, e.g. `http://localhost:9200/vulnx-logs/_doc` |
| `SIEM_TOKEN` | No | Authentication token (also accepts `API_TOKEN`) |
| `SIEM_TYPE` | No | `elasticsearch`, `wazuh`, or `auto` (default) |
| `SIEM_FALLBACK_LOG` | No | Local file path for events when SIEM is down (default: `./siem_fallback.log`) |

---

## Event Payload Format

Each vulnerability is sent as JSON:

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "source": "VulnX_Scanner",
  "event_type": "VULNERABILITY_DETECTED",
  "scan_id": "SCAN_1736935800123",
  "target_url": "https://example.com",
  "vulnerability_type": "SQL Injection",
  "severity": "CRITICAL",
  "message": "VulnX detected SQL Injection on https://example.com?id=' OR '1'='1",
  "compliance_tag": "DPDPA_AUDIT_LOG",
  "affected_url": "https://example.com?id=' OR '1'='1"
}
```

### Severity mapping

| Vulnerability type | Severity |
|--------------------|----------|
| SQL Injection / SQLi | CRITICAL |
| XSS | HIGH |
| CSRF | MEDIUM |
| Open Redirect | MEDIUM |
| Security Misconfiguration | LOW |
| Information Disclosure | LOW |
| Unknown | MEDIUM |

### DPDPA compliance

Every event includes `"compliance_tag": "DPDPA_AUDIT_LOG"` to support Digital Personal Data Protection Act audit trails. All security-relevant scan findings are logged externally (or to the fallback file if the SIEM is offline).

---

## Setting Up a Local ELK Stack (Elasticsearch)

### Option A: Docker Compose (recommended for testing)

Create `docker-compose.siem.yml`:

```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.12.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - esdata:/usr/share/elasticsearch/data

  kibana:
    image: docker.elastic.co/kibana/kibana:8.12.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  esdata:
```

Start the stack:

```bash
docker compose -f docker-compose.siem.yml up -d
```

Configure VulnX:

```env
SIEM_ENDPOINT=http://localhost:9200/vulnx-logs/_doc
SIEM_TYPE=elasticsearch
```

Create an index pattern in Kibana:

1. Open [http://localhost:5601](http://localhost:5601)
2. Go to **Stack Management → Index Patterns**
3. Create pattern: `vulnx-logs*`
4. Set time field: `timestamp`

View alerts:

- **Discover** → filter `event_type: "VULNERABILITY_DETECTED"`
- **Dashboard** → build widgets on `severity`, `vulnerability_type`, `target_url`

---

## Setting Up Wazuh

Wazuh 4.x uses an OpenSearch-compatible **Indexer**. Point VulnX at the indexer document endpoint:

```env
SIEM_ENDPOINT=https://your-wazuh-indexer:9200/wazuh-alerts/_doc
SIEM_TOKEN=your-indexer-api-key
SIEM_TYPE=wazuh
```

When `SIEM_TYPE=wazuh`, events are wrapped in Wazuh-compatible alert structure:

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "rule": {
    "level": 12,
    "description": "VulnX detected SQL Injection on ...",
    "groups": ["vulnx", "web_security", "dpdpa"]
  },
  "agent": { "name": "VulnX_Scanner", "id": "000" },
  "data": { "...standard VulnX payload..." }
}
```

### View alerts in Wazuh Dashboard

1. Open the Wazuh Dashboard (typically port `443` or `5601`)
2. Navigate to **Threat Hunting** or **Security Events**
3. Filter by:
   - `rule.groups: vulnx`
   - `data.compliance_tag: DPDPA_AUDIT_LOG`
   - `data.severity: CRITICAL`

---

## Reliability and Fallback

The `SIEMForwarder` class implements:

- **3 retry attempts** with exponential backoff (1s, 2s)
- **Non-blocking delivery** via background threads
- **Graceful degradation** — scan API never fails if SIEM is down
- **Fallback logging** — failed events append to `SIEM_FALLBACK_LOG`

Example fallback log entry (JSON Lines format):

```bash
tail -f siem_fallback.log
```

Re-play fallback events manually:

```bash
while IFS= read -r line; do
  curl -s -X POST "$SIEM_ENDPOINT" \
    -H "Content-Type: application/json" \
    -d "$line"
done < siem_fallback.log
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `[SIEM] Integration disabled` | `SIEM_ENDPOINT` not set | Add variable to `.env` and restart |
| HTTP 401 / 403 | Invalid token | Set `SIEM_TOKEN` or `API_TOKEN` |
| Connection refused | SIEM not running | Start Elasticsearch/Wazuh stack |
| Events in fallback log | SIEM was temporarily down | Check SIEM health, replay fallback file |
| No events in Kibana | Index pattern missing | Create `vulnx-logs*` index pattern |

Enable verbose Flask logging:

```bash
export FLASK_DEBUG=true
python app.py
```

---

## Architecture

```
┌─────────────┐     POST /api/scan      ┌──────────────┐
│  React UI   │ ───────────────────────►│   app.py     │
└─────────────┘                         │  (Flask)     │
                                        └──────┬───────┘
                                               │
                                        scanner.py
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │ SIEMForwarder│─── async thread ───► SIEM REST API
                                        │ (siem_       │                      (Elasticsearch /
                                        │  integration)│                      Wazuh Indexer)
                                        └──────┬───────┘
                                               │ on failure
                                               ▼
                                        siem_fallback.log
```

---

## Files

| File | Purpose |
|------|---------|
| `siem_integration.py` | `SIEMForwarder` class — formatting, retries, async delivery |
| `app.py` | Initializes forwarder and triggers forwarding after scans |
| `.env.example` | Template for required environment variables |
| `README_SIEM.md` | This documentation |
