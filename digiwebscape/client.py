"""
DigiWebscape SDK — Official Python Client
"""

import json
import urllib.request
import urllib.error
import urllib.parse
from typing import Optional, Dict, Any, List
from .errors import DigiWebscapeError
from .security import verify_webhook_signature


class DigiWebscape:
    """
    DigiWebscape Platform Python SDK Client.
    Provides fluent interfaces for AI Visibility, Private Insights Telemetry,
    Content Architecture Studio™, Webhooks, Workspace Credentials, and Model Context Protocol (MCP).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        organization_id: Optional[str] = None,
        base_url: str = "https://api.digiwebscape.com"
    ) -> None:
        self.api_key = api_key
        self.organization_id = organization_id
        self.base_url = base_url.rstrip("/")

        self.visibility = VisibilityNamespace(self)
        self.insights = InsightsNamespace(self)
        self.studio = StudioNamespace(self)
        self.webhooks = WebhooksNamespace(self)
        self.keys = KeysNamespace(self)
        self.projects = ProjectsNamespace(self)
        self.mcp = MCPNamespace(self)

    def set_api_key(self, api_key: Optional[str]) -> None:
        self.api_key = api_key

    def set_organization_id(self, organization_id: Optional[str]) -> None:
        self.organization_id = organization_id

    def _request(
        self,
        path: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        org_override: Optional[str] = None
    ) -> Any:
        url = f"{self.base_url}{path if path.startswith('/') else '/' + path}"
        headers: Dict[str, str] = {
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "DigiWebscape-Python-SDK/0.16.13"
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        effective_org = org_override or self.organization_id
        if effective_org:
            headers["x-organization-id"] = effective_org

        body_bytes: Optional[bytes] = None
        if data is not None:
            headers["Content-Type"] = "application/json"
            body_bytes = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                status_code = resp.getcode()
                if status_code == 204:
                    return None
                resp_bytes = resp.read()
                if not resp_bytes:
                    return None
                return json.loads(resp_bytes.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            status_code = exc.code
            request_id = exc.headers.get("x-request-id")
            error_code = "REQUEST_FAILED"
            error_message = f"HTTP {status_code}: {exc.reason}"
            details = None

            try:
                err_body = exc.read().decode("utf-8")
                err_json = json.loads(err_body)
                if isinstance(err_json, dict) and "error" in err_json:
                    err_obj = err_json["error"]
                    error_code = err_obj.get("code", error_code)
                    error_message = err_obj.get("message", error_message)
                    details = err_obj.get("details")
            except Exception:
                pass

            raise DigiWebscapeError(
                code=error_code,
                message=error_message,
                status_code=status_code,
                request_id=request_id,
                details=details
            ) from exc
        except urllib.error.URLError as exc:
            raise DigiWebscapeError(
                code="NETWORK_ERROR",
                message=str(exc.reason),
                status_code=0
            ) from exc

    @staticmethod
    def verify_webhook_signature(
        payload: str,
        signature_header: str,
        secret: str,
        tolerance_seconds: int = 300
    ) -> bool:
        return verify_webhook_signature(payload, signature_header, secret, tolerance_seconds)


class VisibilityNamespace:
    def __init__(self, client: DigiWebscape) -> None:
        self._client = client

    def get_metrics(self, project_id: str) -> Dict[str, Any]:
        res = self._client._request(f"/v1/ai/metrics?project_id={project_id}")
        return res.get("metrics", {})

    def get_metrics_history(self, project_id: str, range_window: str = "30d") -> Dict[str, Any]:
        return self._client._request(f"/v1/ai/metrics/history?project_id={project_id}&range={range_window}")

    def list_prompts(self, project_id: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        query = f"project_id={project_id}"
        if category:
            query += f"&category={category}"
        res = self._client._request(f"/v1/ai/prompts?{query}")
        return res.get("prompts", [])

    def create_prompt(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._client._request("/v1/ai/prompts", method="POST", data=data)
        return res.get("prompt", {})

    def delete_prompt(self, prompt_id: str) -> None:
        self._client._request(f"/v1/ai/prompts/{prompt_id}", method="DELETE")

    def run_check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._client._request("/v1/ai/checks/run", method="POST", data=data)
        return res.get("comparison", {})

    def list_runs(self, project_id: str) -> List[Dict[str, Any]]:
        res = self._client._request(f"/v1/ai/runs?project_id={project_id}")
        return res.get("runs", [])

    def get_run(self, run_id: str) -> Dict[str, Any]:
        res = self._client._request(f"/v1/ai/runs/{run_id}")
        return res.get("comparison", {})

    def list_recommendations(self, project_id: str) -> List[Dict[str, Any]]:
        res = self._client._request(f"/v1/ai/recommendations?project_id={project_id}")
        return res.get("recommendations", [])

    def update_recommendation(self, recommendation_id: str, data: Dict[str, Any]) -> None:
        self._client._request(f"/v1/ai/recommendations/{recommendation_id}", method="PATCH", data=data)

    def audit_domain(self, domain: str) -> Dict[str, Any]:
        res = self._client._request("/v1/ai/audit/domain", method="POST", data={"domain": domain})
        return res.get("audit", {})

    def list_competitors(self, project_id: str) -> List[Dict[str, Any]]:
        res = self._client._request(f"/v1/ai/competitors?project_id={project_id}")
        return res.get("competitors", [])

    def add_competitor(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._client._request("/v1/ai/competitors", method="POST", data=data)
        return res.get("competitor", {})

    def delete_competitor(self, competitor_id: str) -> None:
        self._client._request(f"/v1/ai/competitors/{competitor_id}", method="DELETE")

    def get_competitor_gap_intelligence(self, project_id: str) -> Dict[str, Any]:
        res = self._client._request(f"/v1/ai/competitors/gap-analysis?project_id={project_id}")
        return res.get("intelligence", {})


class InsightsNamespace:
    def __init__(self, client: DigiWebscape) -> None:
        self._client = client

    def get_realtime(self, project_id: str, window: str = "24h") -> Dict[str, Any]:
        res = self._client._request(f"/v1/insights/realtime?project_id={project_id}&window={window}")
        return res.get("data", {})

    def get_metrics(self, project_id: str, range_window: str = "7d") -> Dict[str, Any]:
        res = self._client._request(f"/v1/insights/metrics?project_id={project_id}&range={range_window}")
        return res.get("data", {})

    def get_privacy_settings(self, project_id: str) -> Dict[str, Any]:
        res = self._client._request(f"/v1/insights/privacy?project_id={project_id}")
        return res.get("data", {})

    def update_privacy_settings(self, project_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        payload = {"project_id": project_id, **data}
        res = self._client._request("/v1/insights/privacy", method="PATCH", data=payload)
        return res.get("data", {})

    def track(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._client._request("/v1/events/collect", method="POST", data=payload)


class StudioNamespace:
    """
    Content Architecture Studio™ Headless API & Sovereign Edge Telemetry Namespace.
    """
    def __init__(self, client: DigiWebscape) -> None:
        self._client = client

    def get_page(self, slug_or_id: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves full headless page payload (compiled HTML, Markdown, Schema JSON-LD, AST blocks).
        """
        query_parts = [f"slug={urllib.parse.quote(slug_or_id)}"]
        effective_org = tenant_id or self._client.organization_id
        if effective_org:
            query_parts.append(f"tenantId={urllib.parse.quote(effective_org)}")
        query_str = "&".join(query_parts)
        res = self._client._request(f"/v1/studio/headless/page?{query_str}")
        return res.get("data", res)

    def import_content(
        self,
        content: str,
        format: str = "markdown",
        slug: Optional[str] = None,
        tenant_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Imports content (Markdown with frontmatter, WordPress WXR XML, or AST JSON) into a PageDocument.
        """
        effective_org = tenant_id or self._client.organization_id
        payload = {
            "content": content,
            "format": format,
            "slug": slug,
            "tenantId": effective_org,
            "projectId": project_id
        }
        res = self._client._request("/v1/studio/headless/import", method="POST", data=payload)
        return res.get("data", res)

    def export_page(
        self,
        slug_or_id: str,
        format: str = "markdown",
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Exports a page in the specified format (markdown, html, schema, ast, llms).
        """
        page = self.get_page(slug_or_id, tenant_id=tenant_id)
        fmt = format.lower()
        if fmt == "markdown":
            return {"format": "markdown", "content": page.get("markdown", "")}
        elif fmt == "html":
            return {"format": "html", "content": page.get("html", "")}
        elif fmt == "schema":
            return {"format": "schema", "content": page.get("schemaGraph", {})}
        elif fmt == "ast":
            return {"format": "ast", "content": page.get("blocks", [])}
        elif fmt == "llms":
            return {
                "format": "llms",
                "content": f"# {page.get('title')}\n> {page.get('metaDescription')}\n- [Canonical]({page.get('canonicalUrl')})"
            }
        return {"format": format, "data": page}

    def get_analytics(
        self,
        slug: str,
        range: str = "7d",
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetches cookieless Private Insights Telemetry™ metrics for a published Studio page.
        """
        query_parts = [f"slug={urllib.parse.quote(slug)}", f"range={urllib.parse.quote(range)}"]
        effective_org = tenant_id or self._client.organization_id
        if effective_org:
            query_parts.append(f"tenantId={urllib.parse.quote(effective_org)}")
        query_str = "&".join(query_parts)
        res = self._client._request(f"/v1/studio/analytics?{query_str}")
        return res.get("data", res)


class WebhooksNamespace:
    def __init__(self, client: DigiWebscape) -> None:
        self._client = client

    def list(self) -> List[Dict[str, Any]]:
        org_id = self._client.organization_id
        if not org_id:
            raise DigiWebscapeError("MISSING_ORG", "Organization ID required for webhook operations")
        res = self._client._request(f"/v1/organizations/{org_id}/webhooks")
        return res.get("endpoints", [])

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        org_id = self._client.organization_id
        if not org_id:
            raise DigiWebscapeError("MISSING_ORG", "Organization ID required for webhook operations")
        res = self._client._request(f"/v1/organizations/{org_id}/webhooks", method="POST", data=data)
        return res.get("endpoint", {})

    def update(self, webhook_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        org_id = self._client.organization_id
        if not org_id:
            raise DigiWebscapeError("MISSING_ORG", "Organization ID required for webhook operations")
        res = self._client._request(f"/v1/organizations/{org_id}/webhooks/{webhook_id}", method="PATCH", data=data)
        return res.get("endpoint", {})

    def delete(self, webhook_id: str) -> None:
        org_id = self._client.organization_id
        if not org_id:
            raise DigiWebscapeError("MISSING_ORG", "Organization ID required for webhook operations")
        self._client._request(f"/v1/organizations/{org_id}/webhooks/{webhook_id}", method="DELETE")

    def test(self, webhook_id: str) -> Dict[str, Any]:
        org_id = self._client.organization_id
        if not org_id:
            raise DigiWebscapeError("MISSING_ORG", "Organization ID required for webhook operations")
        res = self._client._request(f"/v1/organizations/{org_id}/webhooks/{webhook_id}/test", method="POST")
        return res.get("result", {})

    def list_deliveries(self, webhook_id: str) -> List[Dict[str, Any]]:
        org_id = self._client.organization_id
        if not org_id:
            raise DigiWebscapeError("MISSING_ORG", "Organization ID required for webhook operations")
        res = self._client._request(f"/v1/organizations/{org_id}/webhooks/{webhook_id}/deliveries")
        return res.get("deliveries", [])


class KeysNamespace:
    def __init__(self, client: DigiWebscape) -> None:
        self._client = client

    def list(self) -> List[Dict[str, Any]]:
        org_id = self._client.organization_id
        if not org_id:
            raise DigiWebscapeError("MISSING_ORG", "Organization ID required for key operations")
        res = self._client._request(f"/v1/organizations/{org_id}/keys")
        return res.get("keys", [])

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        org_id = self._client.organization_id
        if not org_id:
            raise DigiWebscapeError("MISSING_ORG", "Organization ID required for key operations")
        return self._client._request(f"/v1/organizations/{org_id}/keys", method="POST", data=data)

    def revoke(self, key_id: str) -> None:
        org_id = self._client.organization_id
        if not org_id:
            raise DigiWebscapeError("MISSING_ORG", "Organization ID required for key operations")
        self._client._request(f"/v1/organizations/{org_id}/keys/{key_id}", method="DELETE")


class ProjectsNamespace:
    def __init__(self, client: DigiWebscape) -> None:
        self._client = client

    def list(self) -> List[Dict[str, Any]]:
        res = self._client._request("/v1/projects")
        return res.get("projects", [])

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._client._request("/v1/projects", method="POST", data=data)
        return res.get("project", {})

    def get(self, project_id: str) -> Dict[str, Any]:
        res = self._client._request(f"/v1/projects/{project_id}")
        return res.get("project", {})

    def update(self, project_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._client._request(f"/v1/projects/{project_id}", method="PATCH", data=data)
        return res.get("project", {})

    def delete(self, project_id: str) -> None:
        self._client._request(f"/v1/projects/{project_id}", method="DELETE")


class MCPNamespace:
    def __init__(self, client: DigiWebscape) -> None:
        self._client = client

    def get_config(
        self,
        client_type: str = "cursor",
        binary_command: str = "npx",
        binary_args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        key = self._client.api_key or "YOUR_WORKSPACE_API_KEY"
        org = self._client.organization_id or "YOUR_ORGANIZATION_ID"
        args = binary_args or ["-y", "@digiwebscape/mcp"]

        if client_type in ("cursor", "claude", "cline"):
            instructions = {
                "cursor": "Add this snippet to your Cursor configuration at .cursor/mcp.json",
                "claude": "Paste this snippet into claude_desktop_config.json",
                "cline": "Configure this in VS Code under Cline MCP settings."
            }[client_type]

            return {
                "client_type": client_type,
                "config": {
                    "mcpServers": {
                        "digiwebscape": {
                            "command": binary_command,
                            "args": args,
                            "env": {
                                "DWS_API_KEY": key,
                                "DWS_ORG_ID": org,
                                "DWS_API_URL": self._client.base_url
                            }
                        }
                    }
                },
                "instructions": instructions
            }

        return {
            "client_type": "generic",
            "config": {
                "server_url": f"{self._client.base_url}/v1/mcp/sse",
                "transport": "sse",
                "headers": {
                    "Authorization": f"Bearer {key}",
                    "x-organization-id": org
                }
            },
            "instructions": "Use this endpoint and authorization headers for remote agent swarms."
        }
