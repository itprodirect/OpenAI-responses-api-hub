"""Convenience helpers for calling the OpenAI Responses API."""

from __future__ import annotations

import os
from collections.abc import Generator, Iterable
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables eagerly so local .env files Just Work™.
load_dotenv()

_API_KEY = os.getenv("OPENAI_API_KEY")

if not _API_KEY:
    raise ValueError("Missing OPENAI_API_KEY environment variable.")

_CLIENT = OpenAI(api_key=_API_KEY)

ResponseInput = Union[str, List[Dict[str, Any]]]


def _extract_text(response: Any) -> str:
    """Safely pull the first text block from a Responses API payload."""

    try:
        return response.output[0].content[0].text or ""
    except (AttributeError, IndexError, TypeError):
        return ""


def _stream_text(stream: Any) -> Generator[str, None, None]:
    """Yield incremental text deltas from a streaming Responses call."""

    with stream as response_stream:
        for event in response_stream:
            if event.type == "response.output_text.delta":
                yield event.delta
            elif event.type == "response.error":
                raise RuntimeError(event.error)
        # Make sure any trailing text is emitted after the stream ends.
        final_response = response_stream.get_final_response()
        tail = _extract_text(final_response)
        if tail:
            yield tail


def get_response(
    input_text: ResponseInput,
    *,
    model: str = "gpt-4o-mini",
    modalities: Optional[Iterable[str]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    stream: bool = False,
    client: Optional[OpenAI] = None,
    **extra_params: Any,
) -> Union[str, Generator[str, None, None]]:
    """Call the Responses API with sensible defaults.

    Parameters
    ----------
    input_text:
        Either a raw string prompt or the structured list accepted by the
        Responses API. The helper will pass this through unchanged.
    model:
        Model name to target. Defaults to ``gpt-4o-mini`` for cost/latency balance.
    modalities / tools:
        Optional lists that expose multimodal generation or tool-calling without
        rewriting the helper.
    stream:
        When ``True`` the function returns a generator that yields text deltas so
        callers can render output incrementally.
    client:
        Override the shared ``OpenAI`` client—useful for dependency injection in
        tests.
    extra_params:
        Any other keyword arguments supported by ``client.responses.create`` will
        be forwarded untouched (e.g., ``metadata`` or ``max_output_tokens``).
    """

    active_client = client or _CLIENT

    payload: Dict[str, Any] = {
        "model": model,
        "input": input_text,
    }

    if modalities is not None:
        payload["modalities"] = list(modalities)
    if tools is not None:
        payload["tools"] = tools
    payload.update(extra_params)

    if stream:
        return _stream_text(active_client.responses.stream(**payload))

    response = active_client.responses.create(**payload)
    return _extract_text(response)
