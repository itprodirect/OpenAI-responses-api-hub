import unittest
from types import SimpleNamespace
from unittest.mock import patch

from utils.responses_api import (
    create_function_tool_response,
    create_json_response,
    extract_output_text,
    invoke_function_tool_calls,
    stream_text_deltas,
)


class FakeStream:
    def __init__(self, events, final_response) -> None:
        self._events = events
        self._final_response = final_response

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def __iter__(self):
        return iter(self._events)

    def get_final_response(self):
        return self._final_response


class ResponsesApiTests(unittest.TestCase):
    def test_invoke_function_tool_calls_serializes_results(self) -> None:
        response = SimpleNamespace(
            output=[
                SimpleNamespace(
                    type="function_call",
                    name="lookup_account",
                    call_id="call_1",
                    arguments='{"account_id": 7}',
                )
            ]
        )

        outputs = invoke_function_tool_calls(
            response,
            {"lookup_account": lambda account_id: {"account_id": account_id, "status": "active"}},
        )

        self.assertEqual(
            outputs,
            [
                {
                    "type": "function_call_output",
                    "call_id": "call_1",
                    "output": '{"account_id": 7, "status": "active"}',
                }
            ],
        )

    def test_create_function_tool_response_continues_until_final_answer(self) -> None:
        initial_response = SimpleNamespace(
            id="resp_1",
            output=[
                SimpleNamespace(
                    type="function_call",
                    name="basic_calculator",
                    call_id="call_1",
                    arguments='{"operation": "add", "a": 2, "b": 3}',
                )
            ],
        )
        final_response = SimpleNamespace(id="resp_2", output_text="The answer is 5.")
        calls = []

        class FakeResponsesAPI:
            def create(self, **kwargs):
                calls.append(kwargs)
                return initial_response if len(calls) == 1 else final_response

        fake_client = SimpleNamespace(responses=FakeResponsesAPI())
        tools = [
            {
                "type": "function",
                "name": "basic_calculator",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string"},
                        "a": {"type": "number"},
                        "b": {"type": "number"},
                    },
                    "required": ["operation", "a", "b"],
                    "additionalProperties": False,
                },
            }
        ]

        def basic_calculator(operation: str, a: float, b: float) -> float:
            if operation == "add":
                return a + b
            raise ValueError("unsupported")

        result = create_function_tool_response(
            "What is 2 + 3?",
            model="gpt-4.1-mini",
            tools=tools,
            tool_functions={"basic_calculator": basic_calculator},
            client=fake_client,
        )

        self.assertIs(result, final_response)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0]["input"], "What is 2 + 3?")
        self.assertEqual(calls[1]["previous_response_id"], "resp_1")
        self.assertEqual(
            calls[1]["input"],
            [
                {
                    "type": "function_call_output",
                    "call_id": "call_1",
                    "output": "5",
                }
            ],
        )

    def test_invoke_function_tool_calls_captures_tool_errors(self) -> None:
        response = SimpleNamespace(
            output=[
                SimpleNamespace(
                    type="function_call",
                    name="divide",
                    call_id="call_2",
                    arguments='{"a": 4, "b": 0}',
                )
            ]
        )

        def divide(a: float, b: float) -> float:
            return a / b

        outputs = invoke_function_tool_calls(response, {"divide": divide})

        self.assertEqual(outputs[0]["type"], "function_call_output")
        self.assertEqual(outputs[0]["call_id"], "call_2")
        self.assertIn("error", outputs[0]["output"])

    def test_create_json_response_uses_strict_schema_and_parses_result(self) -> None:
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "priority": {"type": "string"},
            },
            "required": ["name", "priority"],
            "additionalProperties": False,
        }

        with patch("utils.responses_api.create_text_response") as create_text_response_mock:
            create_text_response_mock.return_value = (
                '{"name": "Draft proposal", "priority": "high"}'
            )

            result = create_json_response(
                "Extract the task.",
                model="gpt-4.1-mini",
                schema_name="task_summary",
                schema=schema,
            )

        self.assertEqual(
            result,
            {"name": "Draft proposal", "priority": "high"},
        )
        create_text_response_mock.assert_called_once_with(
            "Extract the task.",
            model="gpt-4.1-mini",
            client=None,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "task_summary",
                    "schema": schema,
                    "strict": True,
                }
            },
        )

    def test_extract_output_text_prefers_output_text(self) -> None:
        response = SimpleNamespace(
            output_text="hello",
            output=[SimpleNamespace(content=[SimpleNamespace(text="ignored")])],
        )

        self.assertEqual(extract_output_text(response), "hello")

    def test_stream_text_does_not_duplicate_final_text_after_deltas(self) -> None:
        stream = FakeStream(
            events=[SimpleNamespace(type="response.output_text.delta", delta="hello")],
            final_response=SimpleNamespace(output_text="hello"),
        )

        self.assertEqual(list(stream_text_deltas(stream)), ["hello"])

    def test_stream_text_falls_back_to_final_response_when_needed(self) -> None:
        stream = FakeStream(events=[], final_response=SimpleNamespace(output_text="tail"))

        self.assertEqual(list(stream_text_deltas(stream)), ["tail"])


if __name__ == "__main__":
    unittest.main()
