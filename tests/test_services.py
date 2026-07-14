"""Data-contract, renewal-window, and premium arithmetic tests."""

from datetime import date

import pytest

from harborlight_responses.schemas import PolicyRecord
from harborlight_responses.services import (
    DataValidationError,
    calculate_premium_change,
    find_upcoming_renewals,
    load_fictional_policies,
    parse_policy_rows,
)


def valid_row(**overrides: str) -> dict[str, str]:
    row = {
        "policy_id": "FIC-HLA-T001",
        "customer_label": "Fictional Test Shop",
        "line_of_business": "Businessowners",
        "renewal_date": "2026-07-01",
        "current_premium_cents": "10000",
        "proposed_premium_cents": "10500",
        "fictional_record": "true",
    }
    row.update(overrides)
    return row


def record(policy_id: str, renewal_date: date) -> PolicyRecord:
    return PolicyRecord(
        policy_id=policy_id,
        customer_label=f"Fictional Customer {policy_id}",
        line_of_business="Businessowners",
        renewal_date=renewal_date,
        current_premium_cents=100_000,
        proposed_premium_cents=105_000,
        fictional_record=True,
    )


def test_valid_dataset_loading() -> None:
    records = load_fictional_policies()
    assert len(records) == 6
    assert all(item.fictional_record for item in records)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"fictional_record": "false"}, "must be true"),
        ({"policy_id": "REAL-1"}, "must start with 'FIC-'"),
        ({"customer_label": "Test Shop"}, "must start with 'Fictional '"),
        ({"renewal_date": "July 1"}, "YYYY-MM-DD"),
        ({"current_premium_cents": "10.50"}, "whole cents"),
        ({"proposed_premium_cents": "0"}, "greater than zero"),
    ],
)
def test_invalid_rows_are_rejected(overrides: dict[str, str], message: str) -> None:
    with pytest.raises(DataValidationError, match=message):
        parse_policy_rows([valid_row(**overrides)])


def test_missing_required_field() -> None:
    row = valid_row()
    del row["line_of_business"]
    with pytest.raises(DataValidationError, match="missing required field"):
        parse_policy_rows([row])


def test_duplicate_policy_ids() -> None:
    with pytest.raises(DataValidationError, match="duplicate policy_id"):
        parse_policy_rows([valid_row(), valid_row()])


def test_renewal_window_day_zero_and_upper_boundary() -> None:
    records = (
        record("FIC-1", date(2026, 7, 1)),
        record("FIC-2", date(2027, 7, 1)),
    )
    assert [r["policy_id"] for r in find_upcoming_renewals(records, 0)["renewals"]] == [
        "FIC-1"
    ]
    assert [
        r["policy_id"] for r in find_upcoming_renewals(records, 365)["renewals"]
    ] == ["FIC-1", "FIC-2"]


@pytest.mark.parametrize("days", [-1, 366, 2.5, True])
def test_out_of_range_or_non_integer_window(days: object) -> None:
    with pytest.raises(ValueError, match="days must"):
        find_upcoming_renewals((), days)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("current", "renewal", "expected"),
    [
        (120_000, 126_000, (6_000, 5.0, "increase")),
        (80_000, 76_000, (-4_000, -5.0, "decrease")),
        (99_999, 99_999, (0, 0.0, "unchanged")),
        (3, 4, (1, 33.33, "increase")),
    ],
)
def test_premium_change_and_rounding(
    current: int, renewal: int, expected: tuple[int, float, str]
) -> None:
    result = calculate_premium_change(current, renewal)
    assert (result["change_cents"], result["change_percent"], result["direction"]) == expected


@pytest.mark.parametrize(
    ("current", "renewal"),
    [(0, 100), (-1, 100), (100, 0), (100.5, 101), (True, 100)],
)
def test_invalid_integer_or_non_positive_cents(current: object, renewal: object) -> None:
    with pytest.raises(ValueError):
        calculate_premium_change(current, renewal)  # type: ignore[arg-type]
