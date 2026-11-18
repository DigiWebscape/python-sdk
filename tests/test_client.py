"""
DigiWebscape Python SDK — Unit Tests
"""

import unittest
import time
import hmac
import hashlib
import json
from digiwebscape import DigiWebscape, DigiWebscapeError, verify_webhook_signature


class TestDigiWebscapeClient(unittest.TestCase):

    def test_client_initialization(self):
        client = DigiWebscape(
            api_key="dw_live_1234567890abcdef",
            organization_id="org_test_123",
            base_url="https://api.digiwebscape.com"
        )
        self.assertEqual(client.api_key, "dw_live_1234567890abcdef")
        self.assertEqual(client.organization_id, "org_test_123")
        self.assertEqual(client.base_url, "https://api.digiwebscape.com")

        # Verify namespaces exist
        self.assertTrue(hasattr(client, "visibility"))
        self.assertTrue(hasattr(client, "insights"))
        self.assertTrue(hasattr(client, "studio"))
        self.assertTrue(hasattr(client, "webhooks"))
        self.assertTrue(hasattr(client, "keys"))
        self.assertTrue(hasattr(client, "projects"))
        self.assertTrue(hasattr(client, "mcp"))

    def test_client_dynamic_configuration(self):
        client = DigiWebscape()
        self.assertIsNone(client.api_key)
        self.assertIsNone(client.organization_id)

        client.set_api_key("dw_live_new_key")
        client.set_organization_id("org_new_456")
        self.assertEqual(client.api_key, "dw_live_new_key")
        self.assertEqual(client.organization_id, "org_new_456")

    def test_mcp_config_cursor(self):
        client = DigiWebscape(
            api_key="dw_live_key_xyz",
            organization_id="org_cyberdyne"
        )
        mcp = client.mcp.get_config(client_type="cursor")
        self.assertEqual(mcp["client_type"], "cursor")
        self.assertIn(".cursor/mcp.json", mcp["instructions"])

        server_cfg = mcp["config"]["mcpServers"]["digiwebscape"]
        self.assertEqual(server_cfg["command"], "npx")
        self.assertEqual(server_cfg["args"], ["-y", "@digiwebscape/mcp"])
        self.assertEqual(server_cfg["env"]["DWS_API_KEY"], "dw_live_key_xyz")
        self.assertEqual(server_cfg["env"]["DWS_ORG_ID"], "org_cyberdyne")

    def test_mcp_config_claude(self):
        client = DigiWebscape(api_key="dw_live_key_xyz")
        mcp = client.mcp.get_config(client_type="claude")
        self.assertEqual(mcp["client_type"], "claude")
        self.assertIn("claude_desktop_config.json", mcp["instructions"])


class TestWebhookSecurity(unittest.TestCase):

    def setUp(self):
        self.secret = "whsec_abcdef1234567890abcdef1234567890"
        self.payload = json.dumps({"event": "atp.order.completed", "total_cents": 4900})

    def _generate_signature(self, payload: str, secret: str, timestamp: int) -> str:
        clean_secret = secret[6:] if secret.startswith("whsec_") else secret
        signed_bytes = f"{timestamp}.{payload}".encode("utf-8")
        sig = hmac.new(clean_secret.encode("utf-8"), signed_bytes, hashlib.sha256).hexdigest()
        return f"t={timestamp},v1={sig}"

    def test_valid_webhook_signature(self):
        now = int(time.time())
        sig_header = self._generate_signature(self.payload, self.secret, now)

        is_valid = verify_webhook_signature(self.payload, sig_header, self.secret)
        self.assertTrue(is_valid)

        # Also test via class static method
        self.assertTrue(DigiWebscape.verify_webhook_signature(self.payload, sig_header, self.secret))

    def test_tampered_payload_rejected(self):
        now = int(time.time())
        sig_header = self._generate_signature(self.payload, self.secret, now)
        tampered_payload = json.dumps({"event": "atp.order.completed", "total_cents": 100})

        is_valid = verify_webhook_signature(tampered_payload, sig_header, self.secret)
        self.assertFalse(is_valid)

    def test_expired_timestamp_rejected(self):
        # 400 seconds ago (tolerance is 300s)
        old_time = int(time.time()) - 400
        sig_header = self._generate_signature(self.payload, self.secret, old_time)

        is_valid = verify_webhook_signature(self.payload, sig_header, self.secret, tolerance_seconds=300)
        self.assertFalse(is_valid)

    def test_invalid_secret_rejected(self):
        now = int(time.time())
        sig_header = self._generate_signature(self.payload, self.secret, now)

        is_valid = verify_webhook_signature(self.payload, sig_header, "whsec_wrongsecret")
        self.assertFalse(is_valid)


class TestDigiWebscapeError(unittest.TestCase):

    def test_error_properties(self):
        err = DigiWebscapeError(
            code="RATE_LIMITED",
            message="Too many requests",
            status_code=429,
            request_id="req_12345"
        )
        self.assertEqual(err.code, "RATE_LIMITED")
        self.assertEqual(err.status_code, 429)
        self.assertEqual(err.request_id, "req_12345")
        self.assertIn("RATE_LIMITED", str(err))


if __name__ == "__main__":
    unittest.main()
