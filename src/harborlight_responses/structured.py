"""Typed Responses parsing with explicit missing-result and refusal handling."""

from __future__ import annotations

from typing import Any

from .schemas import RenewalReview
from .services import verify_review_arithmetic


class StructuredOutputError(RuntimeError):
    """Raised when a typed response is refused, absent, or fails deterministic checks."""


def extract_refusal(response: Any) -> str | None:
    """Return the first refusal message from a Responses payload, if present."""

    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            if getattr(content, "type", None) == "refusal":
                return getattr(content, "refusal", None) or "The model refused this request."
    return None


def parsed_renewal_review(response: Any) -> RenewalReview:
    """Extract and verify a parsed renewal review from an SDK response."""

    refusal = extract_refusal(response)
    if refusal:
        raise StructuredOutputError(f"Structured request was refused: {refusal}")
    parsed = getattr(response, "output_parsed", None)
    if parsed is None:
        raise StructuredOutputError("The response did not contain a parsed renewal review.")
    if not isinstance(parsed, RenewalReview):
        parsed = RenewalReview.model_validate(parsed)
    verify_review_arithmetic(parsed)
    return parsed


def parse_renewal_review(
    client: Any,
    *,
    model: str,
    note: str,
) -> tuple[Any, RenewalReview]:
    """Use the SDK's Pydantic helper and return both raw and validated results."""

    response = client.responses.parse(
        model=model,
        instructions=(
            "Extract a concise review for the fictional Harborlight record. "
            "Do not invent premiums. Use the note's values and label uncertainty clearly."
        ),
        input=note,
        text_format=RenewalReview,
    )
    return response, parsed_renewal_review(response)