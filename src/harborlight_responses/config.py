"""Environment-only configuration with no import-time API or network activity."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

MODEL_TIERS = {
    "economy": "gpt-5.6-luna",
    "balanced": "gpt-5.6-terra",
}
DEFAULT_MODEL_TIER = "balanced"


@dataclass(frozen=True)
class ModelSelection:
    """Resolved model and the configuration source that selected it."""

    model: str
    tier: str | None
    source: str


def api_key_available(environ: Mapping[str, str] | None = None) -> bool:
    """Return whether a nonblank API key is available without exposing it."""

    values = os.environ if environ is None else environ
    return bool(values.get("OPENAI_API_KEY", "").strip())


def require_api_key(environ: Mapping[str, str] | None = None) -> str:
    """Return the API key or raise recovery guidance for an explicit live action."""

    values = os.environ if environ is None else environ
    api_key = values.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "Live API mode requires OPENAI_API_KEY. Set it in the environment and retry; "
            "demo fixture mode does not require a key."
        )
    return api_key


def resolve_model(environ: Mapping[str, str] | None = None) -> ModelSelection:
    """Resolve an explicit model override or one of two intentionally small tiers."""

    values = os.environ if environ is None else environ
    explicit = values.get("OPENAI_DEFAULT_MODEL", "").strip()
    if explicit:
        return ModelSelection(model=explicit, tier=None, source="OPENAI_DEFAULT_MODEL")

    tier = values.get("OPENAI_MODEL_TIER", DEFAULT_MODEL_TIER).strip().lower()
    if tier not in MODEL_TIERS:
        choices = ", ".join(sorted(MODEL_TIERS))
        raise ValueError(f"OPENAI_MODEL_TIER must be one of: {choices}.")
    return ModelSelection(model=MODEL_TIERS[tier], tier=tier, source="OPENAI_MODEL_TIER")
