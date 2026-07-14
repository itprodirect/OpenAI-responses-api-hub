"""Focused response helper tests with no API access."""

from types import SimpleNamespace

from harborlight_responses.responses import (
    create_first_response,
    create_web_evidence_response,
    extract_web_sources,
    response_metadata,
)
from harborlight_responses.services import get_policy


class RecordingResponses:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        return SimpleNamespace(
            output_text="fixture",
            output=[],
            model=kwargs["model"],
            status="completed",
            object="response",
            usage=SimpleNamespace(input_tokens=3, output_tokens=4, total_tokens=7),
        )


def test_first_response_uses_instructions_input_and_selected_model() -> None:
    responses = RecordingResponses()
    create_first_response(
        SimpleNamespace(responses=responses),
        model="test-model",
        record=get_policy("FIC-HLA-1002"),
    )
    payload = responses.calls[0]
    assert payload["model"] == "test-model"
    assert "fictional" in str(payload["instructions"]).lower()
    assert "FIC-HLA-1002" in str(payload["input"])


def test_web_search_uses_current_hosted_tool_and_requests_sources() -> None:
    responses = RecordingResponses()
    create_web_evidence_response(
        SimpleNamespace(responses=responses),
        model="test-model",
    )
    payload = responses.calls[0]
    assert payload["tools"][0]["type"] == "web_search"
    assert payload["include"] == ["web_search_call.action.sources"]
    assert payload["tool_choice"] == "required"


def test_extract_web_sources_and_metadata() -> None:
    source = SimpleNamespace(title="Ready Business", url="https://www.ready.gov/business")
    response = SimpleNamespace(
        output=[
            SimpleNamespace(
                type="web_search_call",
                action=SimpleNamespace(sources=[source]),
            )
        ],
        object="response",
        status="completed",
        model="test-model",
        usage=SimpleNamespace(input_tokens=1, output_tokens=2, total_tokens=3),
    )
    assert extract_web_sources(response) == [
        {"title": "Ready Business", "url": "https://www.ready.gov/business"}
    ]
    assert response_metadata(response)["usage"]["total_tokens"] == 3