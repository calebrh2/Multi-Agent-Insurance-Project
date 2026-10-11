"""The four-agent pipeline on one scripted case."""

import json

from underwriting.adapters.scripted import ScriptedAdapter
from underwriting.pipeline import run_pipeline
from underwriting.schemas import RawApplication
from underwriting.tracing import TraceLog

RAW = RawApplication(
    applicant_id="APP-1001",
    full_name="Maya Chen",
    age=34,
    product="Home",
    coverage_amount=300_000,
    stated_claims=0,
    notes="Primary residence, new roof",
)


def test_scripted_case_runs_all_four_agents() -> None:
    """A complete case returns a recommendation and a four-span trace."""
    model = ScriptedAdapter(
        [
            json.dumps(
                {
                    "normalized_notes": "Primary residence, new roof",
                    "missing_fields": [],
                }
            ),
            json.dumps({"enrichment_notes": "Excellent credit and no prior claims."}),
            json.dumps(
                {
                    "risk_score": 0.15,
                    "risk_factors": [],
                    "rationale": "Excellent credit and no prior claims.",
                }
            ),
            json.dumps(
                {
                    "decision": "approve",
                    "rationale": "A score of 0.15 with no material factors supports approval.",
                }
            ),
        ]
    )
    trace = TraceLog(applicant_id=RAW.applicant_id)
    result = run_pipeline(RAW, model, trace)
    assert [span.agent for span in trace.spans] == [
        "intake_agent",
        "enrichment_agent",
        "risk_scoring_agent",
        "recommendation_agent",
    ]
    assert trace.spans[3].input == trace.spans[2].output
    assert result.decision == "approve"
    assert result.risk.risk_score == 0.15
    assert result.applicant_id == "APP-1001"
