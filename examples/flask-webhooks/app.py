import os
import json
from flask import Flask, request, jsonify
from digiwebscape import DigiWebscape

app = Flask(__name__)
WEBHOOK_SECRET = os.getenv("DIGIWEBSCAPE_WEBHOOK_SECRET", "")


@app.route("/webhooks/digiwebscape", methods=["POST"])
def webhook_handler():
    if not WEBHOOK_SECRET:
        return jsonify({"error": "Missing DIGIWEBSCAPE_WEBHOOK_SECRET"}), 500

    raw_body = request.get_data(as_text=True)
    signature_header = request.headers.get("X-DigiWebscape-Signature", "")

    is_valid = DigiWebscape.verify_webhook_signature(
        payload=raw_body,
        signature_header=signature_header,
        secret=WEBHOOK_SECRET
    )

    if not is_valid:
        return jsonify({"error": "Invalid signature"}), 401

    event = json.loads(raw_body)
    return jsonify({"received": True, "event": event.get("event")}), 200


if __name__ == "__main__":
    app.run(port=5000)
