"""Demo, live-mock, Gradio-contract, and import-safety tests for the Renewal Desk."""

import importlib
import sys
from types import SimpleNamespace

import gradio as gr
import pytest

from app import harborlight_renewal_desk as desk
from harborlight_responses.fixtures import FIXTURE_LABEL, STRUCTURED_REVIEW_FIXTURE


def _postprocess_panels(result: dict[str, object]) -> None:
    """Exercise the same Gradio component contracts used by the Blocks app."""

    components = {
        "mode_notice": gr.Textbox(),
        "request_input": gr.Textbox(),
        "model_selected": gr.Textbox(),
        "tool_requested": gr.JSON(),
        "validated_arguments": gr.JSON(),
        "deterministic_output": gr.JSON(),
        "structured_result": gr.JSON(),
        "retrieved_evidence": gr.JSON(),
        "final_answer": gr.Markdown(),
        "usage_and_latency": gr.JSON(),
        "error": gr.Markdown(),
    }
    assert set(components) == set(desk._PANEL_FIELDS)
    for field, component in components.items():
        component.postprocess(result[field])


def _mock_usage() -> SimpleNamespace:
    return SimpleNamespace(input_tokens=10, output_tokens=5, total_tokens=15)


def test_fixture_label_describes_authored_provenance() -> None:
    assert FIXTURE_LABEL == (
        "Authored demonstration fixture - no live OpenAI API call was made."
    )


def test_demo_structured_mode_requires_no_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = desk.run_structured_workflow("Demo Fixture", "FIC-HLA-1002")
    assert result["error"] == ""
    assert result["mode_notice"] == FIXTURE_LABEL
    assert result["tool_requested"] == {
        "type": "structured_output",
        "function_tools": [],
        "description": "Typed structured output; no function tool was requested.",
    }
    assert result["structured_result"]["policy_id"] == "FIC-HLA-1002"
    _postprocess_panels(result)


def test_demo_tool_mode_executes_deterministic_services(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0
    real = desk.list_upcoming_renewals

    def recording_service(days: int):
        nonlocal calls
        calls += 1
        return real(days)

    monkeypatch.setattr(desk, "list_upcoming_renewals", recording_service)
    result = desk.run_tool_workflow("Demo Fixture", "FIC-HLA-1003", 30)
    assert calls == 1
    assert result["error"] == ""
    assert result["tool_requested"] == [
        "list_upcoming_renewals",
        "calculate_premium_change",
    ]
    assert result["deterministic_output"]["upcoming_renewals"]["fictional"] is True
    assert FIXTURE_LABEL in result["mode_notice"]
    _postprocess_panels(result)


def test_live_mode_without_key_fails_clearly(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    results = [
        desk.run_structured_workflow("Live API", "FIC-HLA-1002"),
        desk.run_tool_workflow("Live API", "FIC-HLA-1002", 30),
    ]
    for result in results:
        assert "requires OPENAI_API_KEY" in result["error"]
        assert "fixture" not in result["mode_notice"].lower()
        _postprocess_panels(result)


def test_mocked_live_structured_workflow_postprocesses(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = SimpleNamespace(usage=_mock_usage())
    monkeypatch.setattr(desk, "require_api_key", lambda: "available")
    monkeypatch.setattr(desk, "OpenAI", lambda: object())
    monkeypatch.setattr(
        desk,
        "parse_renewal_review",
        lambda client, *, model, note: (response, STRUCTURED_REVIEW_FIXTURE),
    )

    result = desk.run_structured_workflow("Live API", "FIC-HLA-1002")

    assert result["error"] == ""
    assert result["structured_result"]["policy_id"] == "FIC-HLA-1002"
    _postprocess_panels(result)


def test_mocked_live_tool_workflow_preserves_tool_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    executions = (
        SimpleNamespace(
            name="list_upcoming_renewals",
            arguments={"days": 30},
            output='{"ok": true, "result": {"fictional": true, "renewals": []}}',
        ),
        SimpleNamespace(
            name="calculate_premium_change",
            arguments={"current_cents": 126000, "renewal_cents": 132300},
            output='{"ok": true, "result": {"change_percent": 5.0}}',
        ),
    )
    loop = SimpleNamespace(
        executions=executions,
        response=SimpleNamespace(output_text="Live mocked answer.", usage=_mock_usage()),
    )
    monkeypatch.setattr(desk, "require_api_key", lambda: "available")
    monkeypatch.setattr(desk, "OpenAI", lambda: object())
    monkeypatch.setattr(desk, "run_tool_loop", lambda *args, **kwargs: loop)

    result = desk.run_tool_workflow("Live API", "FIC-HLA-1002", 30)

    assert result["error"] == ""
    assert result["tool_requested"] == [
        "list_upcoming_renewals",
        "calculate_premium_change",
    ]
    _postprocess_panels(result)


def test_app_import_does_not_launch_server(monkeypatch: pytest.MonkeyPatch) -> None:
    launched = False

    def fail_launch(*args: object, **kwargs: object) -> None:
        nonlocal launched
        launched = True

    monkeypatch.setattr("gradio.Blocks.launch", fail_launch)
    sys.modules.pop("app.harborlight_renewal_desk", None)
    importlib.import_module("app.harborlight_renewal_desk")
    assert launched is False


def test_build_app_returns_blocks() -> None:
    app = desk.build_app()
    assert app.__class__.__name__ == "Blocks"
