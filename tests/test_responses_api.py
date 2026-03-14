import unittest
from types import SimpleNamespace

from utils.responses_api import extract_output_text, stream_text_deltas


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
