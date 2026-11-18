# digiwebscape

[![PyPI version](https://img.shields.io/pypi/v/digiwebscape.svg)](https://pypi.org/project/digiwebscape/)
[![Python Versions](https://img.shields.io/pypi/pyversions/digiwebscape.svg)](https://pypi.org/project/digiwebscape/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-0-success.svg)](https://pypi.org/project/digiwebscape/)

Official Python SDK for the [DigiWebscape Platform](https://digiwebscape.com) (AI Visibility Matrix™, Private Insights Telemetry™, Content Architecture Studio™, Agentic Commerce Fabric™, and Model Context Protocol).

Built with **zero external runtime dependencies** using Python's standard library. Works out of the box with Python 3.9 through 3.14, async agent frameworks (LangChain, LlamaIndex, CrewAI, AutoGen), and standard web frameworks (FastAPI, Flask, Django).

---

## Installation

```bash
pip install digiwebscape
```

---

## Quickstart

```python
from digiwebscape import DigiWebscape

# Initialize client with your Workspace API Key
client = DigiWebscape(
    api_key="dw_live_...",
    organization_id="org_..."
)

# 1. Fetch AI Visibility Benchmarks
metrics = client.visibility.get_metrics("prj_your_project_id")
print("Visibility Score:", metrics.get("visibility_score"))

# 2. Query Private Insights Realtime Pulse (Cookieless Analytics)
realtime = client.insights.get_realtime("prj_your_project_id", window="24h")
print("Active Visitors:", realtime.get("active_visitors"))

# 3. Register a Webhook Endpoint (Slack / Discord / Standard JSON)
webhook = client.webhooks.create({
    "name": "Production Slack Alerts",
    "url": "https://hooks.slack.com/services/T00/B00/X00",
    "events": ["insights.conversion.recorded", "visibility.sweep.completed"],
    "format": "slack"
})

# 4. Generate Cursor or Claude Desktop MCP Configuration
mcp_config = client.mcp.get_config(client_type="cursor")
print(mcp_config["config"])
```

---

## Webhook Signature Verification

The SDK exports timing-safe HMAC-SHA256 signature verification conforming to the Standard Webhooks specification:

```python
from digiwebscape import DigiWebscape

# Verify inbound webhook in FastAPI, Flask, or Django
is_valid = DigiWebscape.verify_webhook_signature(
    payload=raw_request_body_str,
    signature_header=request.headers.get("X-DigiWebscape-Signature"),
    secret="whsec_...",
    tolerance_seconds=300
)

if not is_valid:
    return "Invalid signature", 401
```

---

## Integration Recipes & Examples

Explore complete sample implementations in [`examples/`](./examples/):

* [`examples/fastapi-webhooks/`](./examples/fastapi-webhooks/): FastAPI route handler for cryptographically verified webhook delivery.
* [`examples/flask-webhooks/`](./examples/flask-webhooks/): Lightweight Flask webhook receiver capturing raw payload strings.
* [`examples/agent-tooling/`](./examples/agent-tooling/): Autonomous AI agent tool function for LangChain/CrewAI sweeps.

---

## Evaluation Mode

Developers testing SDK schemas locally without a paid subscription can use evaluation preview credentials:

```python
client = DigiWebscape(api_key="dw_eval_preview")
```

---

## License & Fair Use

* **License**: MIT License ([LICENSE](./LICENSE)).
* **Programmatic Fair Use**: Governed by Section 10 of the DigiWebscape Terms of Service at [`https://digiwebscape.com/terms/#t7`](https://digiwebscape.com/terms/#t7).
* **Copyright**: Copyright © 2026 DigiWebscape. All rights reserved.
