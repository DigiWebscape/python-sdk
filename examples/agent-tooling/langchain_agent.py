"""
Example: Integrating DigiWebscape AI Visibility with an LLM Agent
"""

import os
from digiwebscape import DigiWebscape

# Initialize client
client = DigiWebscape(
    api_key=os.getenv("DIGIWEBSCAPE_API_KEY", "dw_eval_preview"),
    organization_id=os.getenv("DIGIWEBSCAPE_ORG_ID")
)


def get_ai_visibility_tool(domain: str) -> str:
    """
    Agent tool function to audit a brand's AI search engine visibility across
    OpenAI ChatGPT, Anthropic Claude, Google Gemini, and Perplexity.
    """
    audit = client.visibility.audit_domain({
        "domain": domain,
        "focus_queries": ["best developer productivity software"]
    })

    score = audit.get("overall_score", 0)
    recommendations = audit.get("recommendations", [])

    return f"Domain {domain} AI Visibility Index: {score}/100. Recommendations: {len(recommendations)} active items."


if __name__ == "__main__":
    print(get_ai_visibility_tool("example.com"))
