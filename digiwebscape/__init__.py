"""
DigiWebscape Official Python SDK
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A typed, lightweight Python client for the DigiWebscape Platform.
Supports AI Visibility benchmarks, Private Insights telemetry,
Webhook dispatch & signature verification, and Model Context Protocol (MCP).

Usage:
    >>> from digiwebscape import DigiWebscape
    >>> client = DigiWebscape(api_key="dw_live_...", organization_id="org_...")
    >>> metrics = client.visibility.get_metrics("prj_...")
"""

from .client import DigiWebscape
from .errors import DigiWebscapeError
from .security import verify_webhook_signature

__version__ = "0.16.17"
__all__ = ["DigiWebscape", "DigiWebscapeError", "verify_webhook_signature", "__version__"]
