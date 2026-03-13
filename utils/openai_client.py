"""Shared OpenAI client helpers for notebooks and reusable modules."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables eagerly so local .env files Just Work™.
load_dotenv()


def get_api_key(explicit_api_key: Optional[str] = None) -> str:
    """Resolve an API key from explicit input or the environment."""

    api_key = explicit_api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing OPENAI_API_KEY environment variable. "
            "Add it to your shell or .env file."
        )
    return api_key


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    """Return a cached OpenAI client configured from environment variables."""

    return OpenAI(api_key=get_api_key())


def build_openai_client(api_key: str) -> OpenAI:
    """Create a non-cached client (useful for tests or multi-key workflows)."""

    return OpenAI(api_key=get_api_key(api_key))


def get_response(
    input_text: Any,
    *,
    model: str = "gpt-4.1-mini",
    stream: bool = False,
    client: Optional[OpenAI] = None,
    **extra_params: Any,
) -> Any:
    """Backwards-compatible response helper used by existing notebooks."""

    from .responses_api import create_streaming_text_response, create_text_response

    if stream:
        return create_streaming_text_response(
            input_text,
            model=model,
            client=client,
            **extra_params,
        )

    return create_text_response(
        input_text,
        model=model,
        client=client,
        **extra_params,
    )
