"""Lazy OpenAI client construction and clear live-request error messages."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from openai import OpenAI

from .config import ModelSelection, require_api_key, resolve_model


class LiveRequestError(RuntimeError):
    """Raised when a user-requested live API operation cannot complete."""


def build_client(*, api_key: str | None = None, environ: Mapping[str, str] | None = None) -> OpenAI:
    """Create a client only when explicitly called; no client exists at import time."""

    return OpenAI(api_key=api_key or require_api_key(environ))


def raise_live_request_error(exc: Exception, selection: ModelSelection) -> None:
    """Translate SDK failures into actionable tutorial guidance."""

    if selection.source == "OPENAI_DEFAULT_MODEL":
        message = (
            f"The explicitly configured model {selection.model!r} failed. Verify that the model "
            "identifier is current and available to this API project; no fallback was attempted."
        )
    else:
        message = (
            f"The live request using {selection.model!r} failed. Check API access, limits, and the "
            "official model documentation; demo fixture mode remains available offline."
        )
    raise LiveRequestError(message) from exc


def live_context(environ: Mapping[str, str] | None = None) -> tuple[OpenAI, ModelSelection]:
    """Return the lazy client and visible model selection for a live workflow."""

    selection = resolve_model(environ)
    return build_client(environ=environ), selection


def response_usage(response: Any) -> dict[str, int | None]:
    """Normalize the small usage subset shown by notebooks and the app."""

    usage = getattr(response, "usage", None)
    return {
        "input_tokens": getattr(usage, "input_tokens", None),
        "output_tokens": getattr(usage, "output_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }
