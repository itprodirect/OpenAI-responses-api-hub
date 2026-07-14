"""Typed structured-output contract tests."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from harborlight_responses.fixtures import STRUCTURED_REVIEW_FIXTURE
from harborlight_responses.schemas import RenewalReview
from harborlight_responses.services import verify_review_arithmetic


def test_expected_renewal_review_schema() -> None:
    schema = RenewalReview.model_json_schema()
    assert set(schema["required"]) == {
        "policy_id",
        "customer_label",
        "renewal_date",
        "current_premium_cents",
        "proposed_premium_cents",
        "percentage_change",
        "attention_level",
        "concise_summary",
        "next_actions",
    }
    assert schema["additionalProperties"] is False


def test_fixture_arithmetic_is_verified() -> None:
    result = verify_review_arithmetic(STRUCTURED_REVIEW_FIXTURE)
    assert result["change_percent"] == 5.0


def test_wrong_model_generated_percentage_is_rejected() -> None:
    wrong = STRUCTURED_REVIEW_FIXTURE.model_copy(update={"percentage_change": Decimal("7.00")})
    with pytest.raises(ValueError, match="percentage"):
        verify_review_arithmetic(wrong)


def test_extra_fields_are_rejected() -> None:
    data = STRUCTURED_REVIEW_FIXTURE.model_dump()
    data["hidden_reasoning"] = "not allowed"
    with pytest.raises(ValidationError):
        RenewalReview.model_validate(data)
