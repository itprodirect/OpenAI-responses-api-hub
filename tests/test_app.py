"""Demo-mode and import-safety tests for the focused Renewal Desk."""

import importlib
import sys

import pytest

from app import harborlight_renewal_desk as desk
from harborlight_responses.fixtures import FIXTURE_LABEL


def test_fixture_label_describes_authored_provenance() -> None:
    assert FIXTURE_LABEL == (
        "Authored demonstration fixture - no live OpenAI API call was made."
    )


def test_demo_structured_mode_requires_no_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = desk.run_structured_workflow("Demo Fixture", "FIC-HLA-1002")
    assert result["error"] == ""
    assert result["mode_notice"] == FIXTURE_LABEL
    assert result["structured_result"]["policy_id"] == "FIC-HLA-1002"


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
    assert result["deterministic_output"]["upcoming_renewals"]["fictional"] is True
    assert FIXTURE_LABEL in result["mode_notice"]


def test_live_mode_without_key_fails_clearly(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = desk.run_structured_workflow("Live API", "FIC-HLA-1002")
    assert "requires OPENAI_API_KEY" in result["error"]
    assert "fixture" not in result["mode_notice"].lower()


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