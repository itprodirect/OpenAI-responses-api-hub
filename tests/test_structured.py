"""Mocked SDK tests for native typed structured outputs."""

from types import SimpleNamespace

import pytest

from harborlight_responses.fixtures import STRUCTURED_REVIEW_FIXTURE
from harborlight_responses.structured import (
    StructuredOutputError,
    parse_renewal_review,
    parsed_renewal_review,
)


def test_mocked_responses_parse_and_parsed_object_handling() -> None:
    response = SimpleNamespace(output_parsed=STRUCTURED_REVIEW_FIXTURE, output=[])
    calls = []

    class Responses:
        def parse(self, **kwargs: object) -> object:
            calls.append(kwargs)
            return response

    client = SimpleNamespace(responses=Responses())
    raw, parsed = parse_renewal_review(
        client,
        model="test-model",
        note="Fictional Beacon Books renewal note.",
    )

    assert raw is response
    assert parsed.policy_id == "FIC-HLA-1002"
    assert calls[0]["text_format"].__name__ == "RenewalReview"


def test_missing_parsed_result() -> None:
    with pytest.raises(StructuredOutputError, match="did not contain"):
        parsed_renewal_review(SimpleNamespace(output_parsed=None, output=[]))


def test_refusal_is_reported_before_missing_result() -> None:
    refusal = SimpleNamespace(type="refusal", refusal="Cannot process this input.")
    response = SimpleNamespace(
        output_parsed=None,
        output=[SimpleNamespace(content=[refusal])],
    )
    with pytest.raises(StructuredOutputError, match="refused.*Cannot process"):
        parsed_renewal_review(response)


def test_invalid_mapping_is_validated() -> None:
    response = SimpleNamespace(output_parsed={"policy_id": "REAL-1"}, output=[])
    with pytest.raises(Exception):
        parsed_renewal_review(response)