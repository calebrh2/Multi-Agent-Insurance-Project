"""Risk scoring is handed the enrichment message."""

import json

from underwriting.adapters.scripted import ScriptedAdapter
from underwriting.pipeline import run_through_risk
from underwriting.schemas import IntakeResult, RawApplication
from underwriting.tracing import TraceLog

RAW = RawApplication(
    applicant_id="APP-1002",
    full_name="Leon Ruiz",
    age=62,
    product="Auto",
    coverage_amount=150_000,
    stated_claims=3,
    notes="Three at-fault accidents in five years",
)

INTAKE = IntakeResult(
    applicant_id="APP-1002",
    full_name="Leon Ruiz",
    age=62,
    product="auto",
    coverage_amount=150_000,
    stated_claims=3,
    normalized_notes="Three at-fault accidents in five years",
    missing_fields=[],
)


def test_risk_scoring_receives_the_enrichment_message() -> None:
    """The trace shows enrichment's output as risk scoring's input."""
    model = ScriptedAdapter(
        [
            INTAKE.model_dump_json(),
            json.dumps({"enrichment_notes": "Poor credit and four prior claims."}),
            json.dumps(
                {
                    "risk_score": 0.86,
                    "risk_factors": ["poor_credit"],
                    "rationale": "Poor credit and several prior claims.",
                }
            ),
        ]
    )
    trace = TraceLog(applicant_id=RAW.applicant_id)
    result = run_through_risk(RAW, model, trace)
    assert [span.agent for span in trace.spans] == [
        "intake_agent",
        "enrichment_agent",
        "risk_scoring_agent",
    ]
    assert trace.spans[2].input == trace.spans[1].output
    assert result.risk_score == 0.86
    assert result.enrichment.applicant_id == "APP-1002"
