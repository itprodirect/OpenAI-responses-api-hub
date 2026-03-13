"""Configuration helpers shared across notebooks and scripts."""

from __future__ import annotations

import os

from .models import choose_default_model


def get_default_model(preference: str = "fast") -> str:
    """Resolve the default model from env, with resilient local fallback."""

    env_override = os.getenv("OPENAI_DEFAULT_MODEL")
    if env_override:
        return env_override

    try:
        return choose_default_model(preference)
    except Exception:
        # Keep import-time behavior predictable for offline notebook editing.
        return "gpt-4.1-mini"


DEFAULT_MODEL = get_default_model()
