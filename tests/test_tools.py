"""Strict schemas, argument validation, execution, and continuation tests."""

import json
from types import SimpleNamespace

import pytest

from harborlight_responses.tool_loop import execute_function_calls, run_tool_loop
from harborlight_responses.tools import HARBORLIGHT_TOOLS


def function_call(name: str, call_id: str, arguments: str) -> SimpleNamespace:
    return SimpleNamespace(
        type="function_call",
        name=name,
        call_id=call_id,
        arguments=arguments,
    )


def test_function_schemas_are_strict_and_closed() -> None:
    for tool in HARBORLIGHT_TOOLS:
        assert tool["strict"] is True
        parameters = tool["parameters"]
        assert parameters["additionalProperties"] is False
        assert set(parameters["required"]) == set(parameters["properties"])


def test_tool_argument_validation_serializes_error() -> None:
    response = SimpleNamespace(
        output=[function_call("list_upcoming_renewals", "call-a", '{"days": 2.5}')]
    )
    outputs, executions, _ = execute_function_calls(response)
    payload = json.loads(outputs[0]["output"])
    assert payload["error"]["code"] == "invalid_arguments"
    assert executions[0].ok is False


def test_unknown_tool_is_returned_to_model_as_error() -> None:
    response = SimpleNamespace(output=[function_call("missing", "call-b", "{}")])
    outputs, _, _ = execute_function_calls(response)
    assert json.loads(outputs[0]["output"])["error"]["code"] == "unknown_tool"


def test_tool_exception_is_serialized() -> None:
    response = SimpleNamespace(output=[function_call("explode", "call-c", "{}")])

    def explode(arguments: dict[str, object]) -> None:
        raise RuntimeError("controlled failure")

    outputs, _, _ = execute_function_calls(response, registry={"explode": explode})
    payload = json.loads(outputs[0]["output"])
    assert payload["error"]["code"] == "tool_error"
    assert "controlled failure" in payload["error"]["message"]


def test_multiple_calls_execute_in_one_response() -> None:
    response = SimpleNamespace(
        output=[
            function_call("echo", "call-1", '{"value": 1}'),
            function_call("echo", "call-2", '{"value": 2}'),
        ]
    )
    outputs, executions, _ = execute_function_calls(
        response, registry={"echo": lambda arguments: arguments}
    )
    assert [item["call_id"] for item in outputs] == ["call-1", "call-2"]
    assert [item.arguments for item in executions] == [{"value": 1}, {"value": 2}]


def test_function_call_output_continues_to_final_response() -> None:
    first = SimpleNamespace(
        id="temporary-first",
        output=[function_call("echo", "call-1", '{"value": 7}')],
    )
    final = SimpleNamespace(id="temporary-final", output=[], output_text="Done.")
    calls = []

    class Responses:
        def create(self, **kwargs: object) -> object:
            calls.append(kwargs)
            return first if len(calls) == 1 else final

    result = run_tool_loop(
        SimpleNamespace(responses=Responses()),
        model="test-model",
        input="Use the tool.",
        instructions="Return a short answer.",
        registry={"echo": lambda arguments: arguments},
    )

    continuation = calls[1]
    assert continuation["previous_response_id"] == "temporary-first"
    assert continuation["input"][0]["type"] == "function_call_output"
    assert continuation["input"][0]["call_id"] == "call-1"
    assert result.response is final


def test_maximum_round_protection() -> None:
    repeated = SimpleNamespace(
        id="temporary-loop",
        output=[function_call("echo", "call-loop", '{"value": 1}')],
    )

    class Responses:
        def create(self, **kwargs: object) -> object:
            return repeated

    with pytest.raises(RuntimeError, match="max_rounds=2"):
        run_tool_loop(
            SimpleNamespace(responses=Responses()),
            model="test-model",
            input="Loop.",
            instructions="Keep calling.",
            registry={"echo": lambda arguments: arguments},
            max_rounds=2,
        )