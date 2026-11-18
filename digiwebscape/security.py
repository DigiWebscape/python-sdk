"""
DigiWebscape SDK — Webhook Security & Signature Verification
"""

import hmac
import hashlib
import time
from typing import Optional


def verify_webhook_signature(
    payload: str,
    signature_header: str,
    secret: str,
    tolerance_seconds: int = 300
) -> bool:
    """
    Verifies an inbound webhook HMAC-SHA256 signature conforming to the Standard Webhooks spec.
    Timing-safe and protects against replay attacks.
    """
    if not signature_header or not secret:
        return False

    parts = [p.strip() for p in signature_header.split(",")]
    timestamp: Optional[int] = None
    received_signature: Optional[str] = None

    for part in parts:
        if part.startswith("t="):
            try:
                timestamp = int(part[2:])
            except ValueError:
                return False
        elif part.startswith("v1="):
            received_signature = part[3:]

    if timestamp is None or not received_signature:
        return False

    now = int(time.time())
    if abs(now - timestamp) > tolerance_seconds:
        return False

    # Strip whsec_ prefix if present
    clean_secret = secret[6:] if secret.startswith("whsec_") else secret
    signed_payload = f"{timestamp}.{payload}".encode("utf-8")
    secret_bytes = clean_secret.encode("utf-8")

    expected_signature = hmac.new(secret_bytes, signed_payload, hashlib.sha256).hexdigest()

    return hmac.compare_digest(expected_signature, received_signature)
