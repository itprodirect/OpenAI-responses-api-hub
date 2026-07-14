"""Small event representation for separating request, tool, evidence, and model output."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

EventKind = Literal[
    "notice",
    "request",
    "model",
    "tool_call",
    "tool_arguments",
    "tool_result",
    "evidence",
    "answer",
    "usage",
    "latency",
    "error",
]


@dataclass(frozen=True)
class TransparencyEvent:
    """One user-visible event from a fixture or live workflow."""

    kind: EventKind
    label: str
    value: Any
    mode: Literal["fixture", "live"]
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
