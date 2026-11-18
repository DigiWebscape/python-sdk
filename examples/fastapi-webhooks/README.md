# FastAPI Webhook Ingestion Recipe

Complete example demonstrating timing-safe HMAC signature verification for DigiWebscape webhooks using FastAPI.

## Usage

1. Install FastAPI and Uvicorn:
   ```bash
   pip install fastapi uvicorn digiwebscape
   ```

2. Set your environment variable:
   ```bash
   export DIGIWEBSCAPE_WEBHOOK_SECRET="whsec_your_secret_here"
   ```

3. Run the server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
