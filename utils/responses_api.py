"""Reusable building blocks for modern OpenAI Responses API workflows."""

from __future__ import annotations

import json
from collections.abc import Generator, Iterable
from typing import Any, Callable, Dict, List, Mapping, Optional, Union

from openai import OpenAI

from .openai_client import get_openai_client

ResponseInput = Union[str, List[Dict[str, Any]]]
ToolFunctionMap = Mapping[str, Callable[..., Any]]


def extract_output_text(response: Any) -> str:
    """Safely collect concatenated output text from a Responses API payload."""

    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text:
        return output_text

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

    emitted_text = False

    with stream as response_stream:
        for event in response_stream:
            if event.type == "response.output_text.delta":
                emitted_text = True
                yield event.delta
            elif event.type == "response.error":
                raise RuntimeError(event.error)

        final_response = response_stream.get_final_response()
        tail = extract_output_text(final_response)
        if tail and not emitted_text:
            yield tail


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


def invoke_function_tool_calls(
    response: Any,
    tool_functions: ToolFunctionMap,
) -> List[Dict[str, Any]]:
    """Execute function calls from a response and format continuation inputs."""

    outputs: List[Dict[str, Any]] = []

    for item in getattr(response, "output", []) or []:
        if getattr(item, "type", None) != "function_call":
            continue

        tool_name = getattr(item, "name", None)
        if tool_name not in tool_functions:
            raise KeyError(f"No Python tool registered for function call: {tool_name!r}")

        arguments = json.loads(getattr(item, "arguments", None) or "{}")

        try:
            result = tool_functions[tool_name](**arguments)
            output_text = (
                result if isinstance(result, str) else json.dumps(result, default=str)
            )
        except Exception as exc:
            output_text = json.dumps({"error": str(exc)})

        outputs.append(
            {
                "type": "function_call_output",
                "call_id": getattr(item, "call_id"),
                "output": output_text,
            }
        )

    return outputs


def create_function_tool_response(
    input_text: ResponseInput,
    *,
    model: str,
    tools: List[Dict[str, Any]],
    tool_functions: ToolFunctionMap,
    client: Optional[OpenAI] = None,
    max_rounds: int = 5,
    **extra_params: Any,
) -> Any:
    """Run a simple Responses API function-tool loop and return the final response."""

    active_client = client or get_openai_client()
    response = active_client.responses.create(
        model=model,
        input=input_text,
        tools=tools,
        **extra_params,
    )

    for _ in range(max_rounds):
        tool_outputs = invoke_function_tool_calls(response, tool_functions)
        if not tool_outputs:
            return response

        response = active_client.responses.create(
            model=model,
            previous_response_id=getattr(response, "id"),
            input=tool_outputs,
            tools=tools,
            **extra_params,
        )

    raise RuntimeError(
        f"Tool loop exceeded max_rounds={max_rounds} without reaching a final response."
    )
