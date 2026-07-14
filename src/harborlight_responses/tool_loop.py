"""A small, observable, bounded Responses function-tool loop."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from .tools import HARBORLIGHT_TOOLS, TOOL_REGISTRY, ToolHandler
from .transparency import TransparencyEvent


@dataclass(frozen=True)
class ToolExecution:
    """Observable record of one requested and locally executed function call."""

    call_id: str
    name: str
    arguments: dict[str, Any] | None
    output: str
    ok: bool


@dataclass(frozen=True)
class ToolLoopResult:
    """Final response plus transparent local tool activity."""

    response: Any
    executions: tuple[ToolExecution, ...]
    events: tuple[TransparencyEvent, ...]
    rounds: int


def _error_output(code: str, message: str) -> str:
    return json.dumps({"ok": False, "error": {"code": code, "message": message}})


def execute_function_calls(
    response: Any,
    *,
    registry: dict[str, ToolHandler] | None = None,
    mode: str = "live",
) -> tuple[list[dict[str, str]], list[ToolExecution], list[TransparencyEvent]]:
    """Validate and execute every function call in one response."""

    handlers = TOOL_REGISTRY if registry is None else registry
    outputs: list[dict[str, str]] = []
    executions: list[ToolExecution] = []
    events: list[TransparencyEvent] = []
    for item in getattr(response, "output", []) or []:
        if getattr(item, "type", None) != "function_call":
            continue
        name = str(getattr(item, "name", ""))
        call_id = str(getattr(item, "call_id", ""))
        raw_arguments = getattr(item, "arguments", None) or "{}"
        arguments: dict[str, Any] | None = None
        ok = False
        try:
            decoded = json.loads(raw_arguments)
            if not isinstance(decoded, dict):
                raise ValueError("Function arguments must decode to a JSON object.")
            arguments = decoded
            if name not in handlers:
                output = _error_output("unknown_tool", f"No local tool is registered as {name!r}.")
            else:
                result = handlers[name](arguments)
                output = json.dumps({"ok": True, "result": result}, default=str, sort_keys=True)
                ok = True
        except json.JSONDecodeError as exc:
            output = _error_output("invalid_json", f"Invalid tool arguments: {exc.msg}.")
        except ValidationError as exc:
            output = _error_output("invalid_arguments", str(exc))
        except Exception as exc:
            output = _error_output("tool_error", f"{type(exc).__name__}: {exc}")

        outputs.append(
            {"type": "function_call_output", "call_id": call_id, "output": output}
        )
        execution = ToolExecution(
            call_id=call_id,
            name=name,
            arguments=arguments,
            output=output,
            ok=ok,
        )
        executions.append(execution)
        event_mode = "fixture" if mode == "fixture" else "live"
        events.extend(
            [
                TransparencyEvent(
                    kind="tool_call",
                    label="Tool requested",
                    value=name,
                    mode=event_mode,
                ),
                TransparencyEvent(
                    kind="tool_arguments",
                    label="Validated tool arguments",
                    value=arguments,
                    mode=event_mode,
                ),
                TransparencyEvent(
                    kind="tool_result",
                    label="Deterministic tool output",
                    value=json.loads(output),
                    mode=event_mode,
                ),
            ]
        )
    return outputs, executions, events


def run_tool_loop(
    client: Any,
    *,
    model: str,
    input: Any,
    instructions: str,
    tools: list[dict[str, Any]] | None = None,
    registry: dict[str, ToolHandler] | None = None,
    max_rounds: int = 5,
    mode: str = "live",
) -> ToolLoopResult:
    """Run model request, local calls, and required function-call continuations."""

    if max_rounds < 1:
        raise ValueError("max_rounds must be at least 1.")
    active_tools = HARBORLIGHT_TOOLS if tools is None else tools
    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=input,
        tools=active_tools,
    )
    all_executions: list[ToolExecution] = []
    all_events: list[TransparencyEvent] = []

    for round_number in range(1, max_rounds + 1):
        outputs, executions, events = execute_function_calls(
            response, registry=registry, mode=mode
        )
        all_executions.extend(executions)
        all_events.extend(events)
        if not outputs:
            return ToolLoopResult(
                response=response,
                executions=tuple(all_executions),
                events=tuple(all_events),
                rounds=round_number,
            )
        response = client.responses.create(
            model=model,
            instructions=instructions,
            previous_response_id=getattr(response, "id"),
            input=outputs,
            tools=active_tools,
        )

    raise RuntimeError(
        f"Tool loop exceeded max_rounds={max_rounds} without a final model answer."
    )