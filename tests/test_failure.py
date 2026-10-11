"""Risk-scoring timeouts retry, then escalate without a fabricated decision."""

import json
from pathlib import Path

import pytest

from underwriting.adapters.scripted import ScriptedAdapter
from underwriting.adapters.timeout import RiskTimeoutAdapter
from underwriting.pipeline import run_pipeline
from underwriting.run_cases import evaluate
from underwriting.schemas import RawApplication
from underwriting.tracing import TraceLog

TIMEOUT_CASE = RawApplication(
    applicant_id="APP-TIMEOUT",
    full_name="Casey Timeout",
    age=45,
    product="Home",
    coverage_amount=200_000,
    stated_claims=0,
    notes="Used only to time out risk scoring",
)

INTAKE_AND_ENRICHMENT = [
    json.dumps(
        {"normalized_notes": "Used only to time out risk scoring", "missing_fields": []}
    ),
    json.dumps({"enrichment_notes": "Fair credit and moderate property risk."}),
]


def test_risk_timeout_retries_then_escalates_without_a_decision() -> None:
    """Three timeouts leave an escalated case and do not crash or invent a score."""
    delays: list[float] = []
    model = RiskTimeoutAdapter(
        ScriptedAdapter(INTAKE_AND_ENRICHMENT),
        applicant_id="APP-TIMEOUT",
        failures=3,
    )
    trace = TraceLog(applicant_id="APP-TIMEOUT")
    result = run_pipeline(
        TIMEOUT_CASE,
        model,
        trace,
        sleeper=delays.append,
    )
    assert result.status == "escalated"
    assert result.recommendation is None
    assert result.escalation_reason is not None
    assert "no risk score" in result.escalation_reason
    assert delays == [0.5, 1.0]
    risk_spans = [span for span in trace.spans if span.agent == "risk_scoring_agent"]
    assert [span.attempt for span in risk_spans] == [1, 2, 3]
    assert [span.error for span in risk_spans] == [
        "TimeoutError",
        "TimeoutError",
        "TimeoutError",
    ]
    assert all(span.output is None for span in risk_spans)
    assert "recommendation_agent" not in [span.agent for span in trace.spans]


def test_risk_timeout_recovers_on_the_second_attempt() -> None:
    """A later attempt can still complete, after one backoff."""
    delays: list[float] = []
    model = RiskTimeoutAdapter(
        ScriptedAdapter(
            [
                *INTAKE_AND_ENRICHMENT,
                json.dumps(
                    {
                        "risk_score": 0.4,
                        "risk_factors": ["moderate_property_risk"],
                        "rationale": "Moderate property risk.",
                    }
                ),
                json.dumps(
                    {"decision": "refer", "rationale": "A human should review this."}
                ),
            ]
        ),
        applicant_id="APP-TIMEOUT",
        failures=1,
    )
    trace = TraceLog(applicant_id="APP-TIMEOUT")
    result = run_pipeline(TIMEOUT_CASE, model, trace, sleeper=delays.append)
    assert delays == [0.5]
    assert result.status == "completed"
    assert result.recommendation is not None
    assert result.recommendation.decision == "refer"
    assert result.recommendation.risk.risk_score == 0.4
    risk_spans = [span for span in trace.spans if span.agent == "risk_scoring_agent"]
    assert [span.error for span in risk_spans] == ["TimeoutError", None]
    assert risk_spans[1].attempt == 2


def test_evaluate_refuses_to_save_an_escalated_case(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A timed-out case is not written out as a normal recommendation."""
    monkeypatch.setattr("underwriting.pipeline.time.sleep", lambda _seconds: None)
    model = RiskTimeoutAdapter(
        ScriptedAdapter(INTAKE_AND_ENRICHMENT),
        applicant_id="APP-TIMEOUT",
        failures=3,
    )
    with pytest.raises(RuntimeError, match="no risk score"):
        evaluate(model, [TIMEOUT_CASE], tmp_path)


def test_zero_attempts_escalates_without_calling_risk() -> None:
    """A caller that allows no attempts gets an escalation and no decision."""
    model = ScriptedAdapter(INTAKE_AND_ENRICHMENT)
    result = run_pipeline(TIMEOUT_CASE, model, max_attempts=0)
    assert result.status == "escalated"
    assert result.recommendation is None
    assert result.escalation_reason == "risk scoring was not attempted"
