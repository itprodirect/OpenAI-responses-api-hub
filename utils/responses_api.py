"""Reusable building blocks for modern OpenAI Responses API workflows."""

from __future__ import annotations

import json
from collections.abc import Generator, Iterable
from typing import Any, Dict, List, Optional, Union

from openai import OpenAI

from .openai_client import get_openai_client

ResponseInput = Union[str, List[Dict[str, Any]]]


def extract_output_text(response: Any) -> str:
    """Safely collect concatenated output text from a Responses API payload."""

    chunks: List[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                chunks.append(text)

    if chunks:
        return "\n".join(chunks).strip()

    # Newer SDK convenience field (when available).
    return getattr(response, "output_text", "") or ""


def stream_text_deltas(stream: Any) -> Generator[str, None, None]:
    """Yield text deltas from a streaming Responses call."""

    with stream as response_stream:
        for event in response_stream:
            if event.type == "response.output_text.delta":
                yield event.delta
            elif event.type == "response.error":
                raise RuntimeError(event.error)


def create_text_response(
    input_text: ResponseInput,
    *,
    model: str,
    modalities: Optional[Iterable[str]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    client: Optional[OpenAI] = None,
    **extra_params: Any,
) -> str:
    """Create a text response and return normalized plain text."""

    active_client = client or get_openai_client()

    payload: Dict[str, Any] = {
        "model": model,
        "input": input_text,
    }

    if modalities is not None:
        payload["modalities"] = list(modalities)
    if tools is not None:
        payload["tools"] = tools
    payload.update(extra_params)

    response = active_client.responses.create(**payload)
    return extract_output_text(response)


def create_streaming_text_response(
    input_text: ResponseInput,
    *,
    model: str,
    client: Optional[OpenAI] = None,
    **extra_params: Any,
) -> Generator[str, None, None]:
    """Create a streaming response and yield deltas as they arrive."""

    active_client = client or get_openai_client()
    stream = active_client.responses.stream(model=model, input=input_text, **extra_params)
    return stream_text_deltas(stream)


def create_json_response(
    input_text: ResponseInput,
    *,
    model: str,
    schema_name: str,
    schema: Dict[str, Any],
    client: Optional[OpenAI] = None,
    **extra_params: Any,
) -> Dict[str, Any]:
    """Request structured output via strict JSON Schema and parse it."""

    text = create_text_response(
        input_text,
        model=model,
        client=client,
        text={
            "format": {
                "type": "json_schema",
                "name": schema_name,
                "schema": schema,
                "strict": True,
            }
        },
        **extra_params,
    )
    return json.loads(text)
