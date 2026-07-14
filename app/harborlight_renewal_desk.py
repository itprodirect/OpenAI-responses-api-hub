"""Focused Gradio desk for two fictional Harborlight renewal workflows."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Any, Literal

import gradio as gr
from openai import OpenAI

from harborlight_responses.client import response_usage
from harborlight_responses.config import require_api_key, resolve_model
from harborlight_responses.fixtures import FIXTURE_LABEL, STRUCTURED_REVIEW_FIXTURE
from harborlight_responses.responses import policy_prompt
from harborlight_responses.schemas import RenewalReview
from harborlight_responses.services import (
    calculate_premium_change,
    get_policy,
    list_upcoming_renewals,
    load_fictional_policies,
    verify_review_arithmetic,
)
from harborlight_responses.structured import parse_renewal_review
from harborlight_responses.tool_loop import run_tool_loop

Mode = Literal["Demo Fixture", "Live API"]
FICTIONAL_NOTICE = (
    "Fictional tutorial data only — no real people, customers, policies, or insurance advice."
)


@dataclass
class DeskResult:
    """Panel-ready result that keeps model, tool, fixture, and evidence boundaries visible."""

    data_notice: str = FICTIONAL_NOTICE
    mode_notice: str = ""
    request_input: str = ""
    model_selected: str = ""
    tool_requested: str = ""
    validated_arguments: Any = None
    deterministic_output: Any = None
    structured_result: Any = None
    retrieved_evidence: Any = None
    final_answer: str = ""
    usage_and_latency: Any = None
    error: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _selection() -> str:
    return resolve_model().model


def _demo_review(policy_id: str) -> RenewalReview:
    policy = get_policy(policy_id)
    if policy_id == STRUCTURED_REVIEW_FIXTURE.policy_id:
        return STRUCTURED_REVIEW_FIXTURE
    change = calculate_premium_change(
        policy.current_premium_cents,
        policy.proposed_premium_cents,
    )
    attention = "review" if change["direction"] != "unchanged" else "routine"
    return RenewalReview(
        policy_id=policy.policy_id,
        customer_label=policy.customer_label,
        renewal_date=policy.renewal_date,
        current_premium_cents=policy.current_premium_cents,
        proposed_premium_cents=policy.proposed_premium_cents,
        percentage_change=Decimal(str(change["change_percent"])),
        attention_level=attention,
        concise_summary=(
            "A recorded demonstration summary assembled from deterministic fictional data."
        ),
        next_actions=[
            "Review the fictional renewal record.",
            "Explain the deterministically verified proposed premium change.",
        ],
    )


def run_structured_workflow(mode: Mode, policy_id: str) -> dict[str, Any]:
    """Run a fixture or live typed-renewal workflow without hidden fallback."""

    started = time.perf_counter()
    policy = get_policy(policy_id)
    model = _selection()
    note = (
        "Review this fictional renewal and return the typed Harborlight schema."
        + chr(10)
        + policy_prompt(policy)
    )
    result = DeskResult(
        mode_notice=FIXTURE_LABEL if mode == "Demo Fixture" else "Live OpenAI API request.",
        request_input=note,
        model_selected=model,
        tool_requested="No function tool — typed structured output",
        deterministic_output=policy.model_dump(mode="json"),
        retrieved_evidence=[],
    )
    try:
        if mode == "Demo Fixture":
            review = _demo_review(policy_id)
            usage = {"input_tokens": None, "output_tokens": None, "total_tokens": None}
            answer = "Recorded typed result; deterministic premium arithmetic was verified."
        else:
            require_api_key()
            client = OpenAI()
            response, review = parse_renewal_review(client, model=model, note=note)
            usage = response_usage(response)
            answer = "Live typed result; deterministic premium arithmetic was verified."
        verified = verify_review_arithmetic(review)
        result.structured_result = review.model_dump(mode="json")
        result.deterministic_output = {
            "policy": policy.model_dump(mode="json"),
            "verified_premium_change": verified,
        }
        result.final_answer = answer
        result.usage_and_latency = {
            **usage,
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),
        }
    except Exception as exc:
        result.error = str(exc)
        result.final_answer = "No result was produced. Review the error and retry."
        result.usage_and_latency = {
            "latency_ms": round((time.perf_counter() - started) * 1000, 1)
        }
    return result.as_dict()


def run_tool_workflow(mode: Mode, policy_id: str, days: int) -> dict[str, Any]:
    """Run upcoming-renewal analysis and expose every local tool boundary."""

    started = time.perf_counter()
    model = _selection()
    selected = get_policy(policy_id)
    prompt = (
        f"Review fictional renewals in the next {days} days and explain the proposed "
        f"change for {selected.customer_label}."
    )
    result = DeskResult(
        mode_notice=FIXTURE_LABEL if mode == "Demo Fixture" else "Live OpenAI API request.",
        request_input=prompt,
        model_selected=model,
        retrieved_evidence=[],
    )
    try:
        if mode == "Demo Fixture":
            renewals = list_upcoming_renewals(days)
            change = calculate_premium_change(
                selected.current_premium_cents,
                selected.proposed_premium_cents,
            )
            result.tool_requested = (
                "list_upcoming_renewals; calculate_premium_change "
                "(deterministic demo execution)"
            )
            result.validated_arguments = {
                "list_upcoming_renewals": {"days": days},
                "calculate_premium_change": {
                    "current_cents": selected.current_premium_cents,
                    "renewal_cents": selected.proposed_premium_cents,
                },
            }
            result.deterministic_output = {
                "upcoming_renewals": renewals,
                "selected_premium_change": change,
            }
            result.final_answer = (
                f"Recorded fixture summary: {len(renewals['renewals'])} fictional policies "
                f"renew in the window; {selected.customer_label} has a "
                f"{change['change_percent']:.2f}% proposed {change['direction']}."
            )
            usage = {"input_tokens": None, "output_tokens": None, "total_tokens": None}
        else:
            require_api_key()
            loop = run_tool_loop(
                OpenAI(),
                model=model,
                input=prompt,
                instructions=(
                    "Use Harborlight tools for all renewal facts and premium arithmetic. "
                    "Discuss only fictional records and provide no insurance advice."
                ),
            )
            result.tool_requested = [item.name for item in loop.executions]
            result.validated_arguments = [item.arguments for item in loop.executions]
            result.deterministic_output = [
                json.loads(item.output) for item in loop.executions
            ]
            result.final_answer = loop.response.output_text
            usage = response_usage(loop.response)
        result.usage_and_latency = {
            **usage,
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),
        }
    except Exception as exc:
        result.error = str(exc)
        result.final_answer = "No result was produced. Review the error and retry."
        result.usage_and_latency = {
            "latency_ms": round((time.perf_counter() - started) * 1000, 1)
        }
    return result.as_dict()


_PANEL_FIELDS = [
    "mode_notice",
    "request_input",
    "model_selected",
    "tool_requested",
    "validated_arguments",
    "deterministic_output",
    "structured_result",
    "retrieved_evidence",
    "final_answer",
    "usage_and_latency",
    "error",
]


def _panel_values(result: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(result[field] for field in _PANEL_FIELDS)


def build_app() -> gr.Blocks:
    """Construct the Blocks UI; importing this module never launches a server."""

    policies = load_fictional_policies()
    choices = [(f"{item.customer_label} — {item.policy_id}", item.policy_id) for item in policies]
    default_policy = policies[1].policy_id

    with gr.Blocks(title="Harborlight Renewal Desk") as demo:
        gr.Markdown("# Harborlight Renewal Desk")
        gr.Markdown(
            f"**{FICTIONAL_NOTICE}**",
        )
        with gr.Row():
            mode = gr.Radio(
                ["Demo Fixture", "Live API"],
                value="Demo Fixture",
                label="Mode",
            )
            policy = gr.Dropdown(choices=choices, value=default_policy, label="Fictional policy")
            days = gr.Slider(0, 365, value=30, step=1, label="Renewal window (days)")
        gr.Markdown(
            f"Configured model: **{_selection()}**. Live mode never falls back to fixtures."
        )

        with gr.Tabs():
            with gr.Tab("Structured renewal review"):
                structured_run = gr.Button("Run structured review", variant="primary")
            with gr.Tab("Tool-assisted renewal analysis"):
                tool_run = gr.Button("Run tool-assisted analysis", variant="primary")

        mode_notice = gr.Textbox(label="Mode notice", interactive=False)
        request_input = gr.Textbox(label="User / request input", interactive=False)
        model_selected = gr.Textbox(label="Model selected", interactive=False)
        tool_requested = gr.JSON(label="Tool requested")
        validated_arguments = gr.JSON(label="Validated tool arguments")
        deterministic_output = gr.JSON(label="Deterministic tool output")
        structured_result = gr.JSON(label="Structured result")
        retrieved_evidence = gr.JSON(label="Retrieved evidence (when applicable)")
        final_answer = gr.Markdown(label="Final generated answer")
        usage_and_latency = gr.JSON(label="Usage and latency")
        error = gr.Markdown(label="Errors and recovery guidance")
        outputs = [
            mode_notice,
            request_input,
            model_selected,
            tool_requested,
            validated_arguments,
            deterministic_output,
            structured_result,
            retrieved_evidence,
            final_answer,
            usage_and_latency,
            error,
        ]

        structured_run.click(
            lambda selected_mode, selected_policy: _panel_values(
                run_structured_workflow(selected_mode, selected_policy)
            ),
            inputs=[mode, policy],
            outputs=outputs,
        )
        tool_run.click(
            lambda selected_mode, selected_policy, window: _panel_values(
                run_tool_workflow(selected_mode, selected_policy, int(window))
            ),
            inputs=[mode, policy, days],
            outputs=outputs,
        )
    return demo


if __name__ == "__main__":
    build_app().launch()