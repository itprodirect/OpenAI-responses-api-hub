"""Typed contracts shared by deterministic services and model-facing examples."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    """Forbid undeclared fields in tutorial data and tool arguments."""

    model_config = ConfigDict(extra="forbid")


class PolicyRecord(StrictModel):
    """One validated, visibly fictional policy record."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    policy_id: str
    customer_label: str
    line_of_business: str = Field(min_length=1)
    renewal_date: date
    current_premium_cents: int = Field(strict=True, gt=0)
    proposed_premium_cents: int = Field(strict=True, gt=0)
    fictional_record: Literal[True]

    @field_validator("policy_id")
    @classmethod
    def fictional_policy_prefix(cls, value: str) -> str:
        if not value.startswith("FIC-"):
            raise ValueError("policy_id must start with 'FIC-'")
        return value

    @field_validator("customer_label")
    @classmethod
    def fictional_customer_prefix(cls, value: str) -> str:
        if not value.startswith("Fictional "):
            raise ValueError("customer_label must start with 'Fictional '")
        return value


class ListUpcomingRenewalsArgs(StrictModel):
    """Validated arguments for the renewal-window function tool."""

    days: int = Field(strict=True, ge=0, le=365)


class CalculatePremiumChangeArgs(StrictModel):
    """Validated arguments for the premium-change function tool."""

    current_cents: int = Field(strict=True, gt=0)
    renewal_cents: int = Field(strict=True, gt=0)


class RenewalReview(StrictModel):
    """Schema-controlled model output for a fictional renewal review."""

    policy_id: str
    customer_label: str
    renewal_date: date
    current_premium_cents: int = Field(strict=True, gt=0)
    proposed_premium_cents: int = Field(strict=True, gt=0)
    percentage_change: Decimal
    attention_level: Literal["routine", "review", "urgent"]
    concise_summary: str = Field(min_length=1, max_length=500)
    next_actions: list[str] = Field(min_length=1, max_length=5)

    @field_validator("policy_id")
    @classmethod
    def review_policy_prefix(cls, value: str) -> str:
        if not value.startswith("FIC-"):
            raise ValueError("policy_id must start with 'FIC-'")
        return value

    @field_validator("customer_label")
    @classmethod
    def review_customer_prefix(cls, value: str) -> str:
        if not value.startswith("Fictional "):
            raise ValueError("customer_label must start with 'Fictional '")
        return value
