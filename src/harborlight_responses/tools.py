"""Strict Responses function definitions and validated local implementations."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .schemas import CalculatePremiumChangeArgs, ListUpcomingRenewalsArgs
from .services import calculate_premium_change, list_upcoming_renewals

LIST_UPCOMING_RENEWALS_TOOL: dict[str, Any] = {
    "type": "function",
    "name": "list_upcoming_renewals",
    "description": (
        "List fictional Harborlight policies renewing from the fixed 2026-07-01 "
        "snapshot through the requested inclusive window."
    ),
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "days": {
                "type": "integer",
                "minimum": 0,
                "maximum": 365,
                "description": "Inclusive renewal window in whole days.",
            }
        },
        "required": ["days"],
        "additionalProperties": False,
    },
}

CALCULATE_PREMIUM_CHANGE_TOOL: dict[str, Any] = {
    "type": "function",
    "name": "calculate_premium_change",
    "description": (
        "Calculate amount, percentage, and direction for two positive whole-cent premiums."
    ),
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "current_cents": {
                "type": "integer",
                "exclusiveMinimum": 0,
                "description": "Current premium in positive whole cents.",
            },
            "renewal_cents": {
                "type": "integer",
                "exclusiveMinimum": 0,
                "description": "Proposed renewal premium in positive whole cents.",
            },
        },
        "required": ["current_cents", "renewal_cents"],
        "additionalProperties": False,
    },
}

HARBORLIGHT_TOOLS = [
    LIST_UPCOMING_RENEWALS_TOOL,
    CALCULATE_PREMIUM_CHANGE_TOOL,
]


def execute_list_upcoming_renewals(arguments: dict[str, Any]) -> dict[str, Any]:
    validated = ListUpcomingRenewalsArgs.model_validate(arguments)
    return list_upcoming_renewals(validated.days)


def execute_calculate_premium_change(arguments: dict[str, Any]) -> dict[str, Any]:
    validated = CalculatePremiumChangeArgs.model_validate(arguments)
    return calculate_premium_change(validated.current_cents, validated.renewal_cents)


ToolHandler = Callable[[dict[str, Any]], Any]
TOOL_REGISTRY: dict[str, ToolHandler] = {
    "list_upcoming_renewals": execute_list_upcoming_renewals,
    "calculate_premium_change": execute_calculate_premium_change,
}