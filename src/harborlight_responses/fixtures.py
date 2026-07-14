"""Small, dated, clearly labeled recorded fixtures for credential-free learning."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .schemas import RenewalReview

FIXTURE_LABEL = "Recorded demonstration fixture — no live OpenAI API call was made."
WEB_FIXTURE_DATE = "2026-07-14"

FIRST_RESPONSE_FIXTURE = (
    "Fictional Beacon Books renews on July 10, 2026. Its proposed premium is $1,323.00, "
    "up $63.00 (5.00%) from $1,260.00. This deterministic policy data is fictional; the "
    "wording shown here is a recorded model-output fixture."
)

STRUCTURED_REVIEW_FIXTURE = RenewalReview(
    policy_id="FIC-HLA-1002",
    customer_label="Fictional Beacon Books",
    renewal_date="2026-07-10",
    current_premium_cents=126_000,
    proposed_premium_cents=132_300,
    percentage_change="5.00",
    attention_level="review",
    concise_summary="A modest increase needs a clear explanation before the fictional renewal.",
    next_actions=[
        "Confirm the fictional customer received the renewal proposal.",
        "Explain the verified 5.00% proposed premium increase.",
    ],
)

WEB_SEARCH_FIXTURE: dict[str, Any] = {
    "fixture_date": WEB_FIXTURE_DATE,
    "request_summary": "Public hurricane-preparedness guidance for a fictional small business.",
    "retrieved_facts": [
        (
            "Build a business preparedness plan that includes communications, "
            "IT recovery, and continuity."
        ),
        "Train staff and exercise the plan before operations are disrupted.",
        "Follow official local instructions and know evacuation routes.",
    ],
    "sources": [
        {
            "title": "Ready Business",
            "url": "https://www.ready.gov/business",
            "publisher": "Ready.gov",
        },
        {
            "title": "Ready Business Hurricane Toolkit",
            "url": "https://www.ready.gov/sites/default/files/2020-04/ready_business_hurricane-toolkit.pdf",
            "publisher": "Ready.gov / FEMA",
        },
    ],
    "generated_interpretation": [
        "Name the staff contact responsible for alerts and closure messages.",
        "Confirm backups, emergency contacts, and continuity steps are accessible off-site.",
        "Schedule a short staff drill and record any gaps for follow-up.",
    ],
}


def web_search_fixture() -> dict[str, Any]:
    """Return a defensive copy so demo callers cannot mutate shared fixture state."""

    return deepcopy(WEB_SEARCH_FIXTURE)
