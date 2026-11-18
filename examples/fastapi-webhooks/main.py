import os
import json
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from digiwebscape import DigiWebscape

app = FastAPI(title="DigiWebscape FastAPI Webhook Receiver")
WEBHOOK_SECRET = os.getenv("DIGIWEBSCAPE_WEBHOOK_SECRET", "")


@app.post("/webhooks/digiwebscape")
async def handle_webhook(request: Request):
    """
    Receives and cryptographically verifies inbound DigiWebscape webhooks.
    """
    if not WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: DIGIWEBSCAPE_WEBHOOK_SECRET is not set."
        )

    # 1. Read the raw request body as bytes and decode as UTF-8
    raw_body_bytes = await request.body()
    raw_body_str = raw_body_bytes.decode("utf-8")
    signature_header = request.headers.get("x-digiwebscape-signature", "")

    # 2. Verify signature with timing-safe HMAC comparison
    is_valid = DigiWebscape.verify_webhook_signature(
        payload=raw_body_str,
        signature_header=signature_header,
        secret=WEBHOOK_SECRET,
        tolerance_seconds=300
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature or expired timestamp"
        )

    # 3. Parse and dispatch verified event
    event = json.loads(raw_body_str)
    event_type = event.get("event")

    if event_type == "atp.order.completed":
        # Handle autonomous digital license fulfillment
        pass
    elif event_type == "atp.order.reserved":
        # Handle ephemeral inventory reservation
        pass
    elif event_type == "insights.conversion.recorded":
        # Handle cookieless conversion telemetry
        pass
    elif event_type == "visibility.sweep.completed":
        # Handle completed AI Visibility sweep
        pass

    return JSONResponse(content={"received": True, "event": event_type})
