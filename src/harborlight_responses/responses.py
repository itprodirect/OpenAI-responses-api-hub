"""Focused live Responses helpers used by lessons and the application."""

from __future__ import annotations

from datetime import date
from typing import Any

from .client import response_usage
from .services import PolicyRecord


def policy_prompt(record: PolicyRecord) -> str:
    """Serialize one deterministic policy record without hidden or private data."""

    return chr(10).join(
        [
            f"Policy ID: {record.policy_id}",
            f"Customer: {record.customer_label}",
            f"Line: {record.line_of_business}",
            f"Renewal date: {record.renewal_date.isoformat()}",
            f"Current premium cents: {record.current_premium_cents}",
            f"Proposed premium cents: {record.proposed_premium_cents}",
        ]
    )


def create_first_response(client: Any, *, model: str, record: PolicyRecord) -> Any:
    """Create the first Harborlight prose response with current SDK parameters."""

    return client.responses.create(
        model=model,
        instructions=(
            "Explain this visibly fictional insurance renewal to a beginner in three concise "
            "sentences. Separate supplied facts from your interpretation."
        ),
        input=policy_prompt(record),
    )


def create_web_evidence_response(client: Any, *, model: str) -> Any:
    """Run a dated hosted web search limited to official preparedness sources."""

    execution_date = date.today().isoformat()
    return client.responses.create(
        model=model,
        instructions=(
            "Research current public hurricane-preparedness guidance for a fictional small "
            "business insurance client. Separate retrieved facts from a concise generated "
            "communication checklist. Cite sources; do not provide insurance advice."
        ),
        input=f"Execution date: {execution_date}. Use only public official guidance.",
        tools=[
            {
                "type": "web_search",
                "filters": {
                    "allowed_domains": ["ready.gov", "fema.gov", "noaa.gov"],
                },
            }
        ],
        tool_choice="required",
        include=["web_search_call.action.sources"],
    )


def extract_web_sources(response: Any) -> list[dict[str, str]]:
    """Collect URL/title evidence returned on hosted web-search call items."""

    sources: list[dict[str, str]] = []
    for item in getattr(response, "output", []) or []:
        if getattr(item, "type", None) != "web_search_call":
            continue
        action = getattr(item, "action", None)
        for source in getattr(action, "sources", []) or []:
            url = getattr(source, "url", None)
            if url:
                sources.append(
                    {
                        "title": getattr(source, "title", None) or url,
                        "url": url,
                    }
                )
    return sources


def response_metadata(response: Any) -> dict[str, Any]:
    """Return beginner-facing metadata without persisting reusable identifiers."""

    return {
        "object": getattr(response, "object", None),
        "status": getattr(response, "status", None),
        "model": getattr(response, "model", None),
        "usage": response_usage(response),
    }