"""Offline tests for key presence and the intentionally small model resolver."""

import importlib
import sys

import pytest

from harborlight_responses.config import api_key_available, require_api_key, resolve_model


def test_no_api_key() -> None:
    assert api_key_available({}) is False
    with pytest.raises(ValueError, match="Live API mode requires"):
        require_api_key({})


def test_api_key_present() -> None:
    assert api_key_available({"OPENAI_API_KEY": "test-value"}) is True
    assert require_api_key({"OPENAI_API_KEY": "test-value"}) == "test-value"


def test_default_balanced_tier() -> None:
    selection = resolve_model({})
    assert selection.model == "gpt-5.6-terra"
    assert selection.tier == "balanced"


def test_economy_tier() -> None:
    assert resolve_model({"OPENAI_MODEL_TIER": "economy"}).model == "gpt-5.6-luna"


def test_explicit_model_override() -> None:
    selection = resolve_model(
        {"OPENAI_MODEL_TIER": "economy", "OPENAI_DEFAULT_MODEL": "gpt-5.6-sol"}
    )
    assert selection.model == "gpt-5.6-sol"
    assert selection.source == "OPENAI_DEFAULT_MODEL"


def test_invalid_tier() -> None:
    with pytest.raises(ValueError, match="economy, balanced|balanced, economy"):
        resolve_model({"OPENAI_MODEL_TIER": "fastest"})


def test_import_does_not_construct_openai_client(monkeypatch: pytest.MonkeyPatch) -> None:
    import openai

    def fail(*args: object, **kwargs: object) -> None:
        raise AssertionError("OpenAI client construction is forbidden during import")

    monkeypatch.setattr(openai, "OpenAI", fail)
    sys.modules.pop("harborlight_responses.client", None)
    importlib.import_module("harborlight_responses.client")
