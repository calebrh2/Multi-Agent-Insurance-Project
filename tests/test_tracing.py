"""Tracing on the intake-to-enrichment handoff."""

import json

import pytest

from underwriting.adapters.scripted import ScriptedAdapter
from underwriting.pipeline import run_intake_and_enrichment
from underwriting.schemas import IntakeResult, RawApplication
from underwriting.tracing import TraceLog, run_step

RAW = RawApplication(
    applicant_id="APP-1001",
    full_name="Maya Chen",
    age=34,
    product="Home",
    coverage_amount=300_000,
    stated_claims=0,
    notes="Primary residence, new roof",
)

INTAKE = IntakeResult(
    applicant_id="APP-1001",
    full_name="Maya Chen",
    age=34,
    product="home",
    coverage_amount=300_000,
    stated_claims=0,
    normalized_notes="Primary residence, new roof",
    missing_fields=[],
)


def test_two_agent_trace_records_input_output_duration_and_tokens() -> None:
    """Each connected agent leaves a span with the fields the rubric requires."""
    notes = {"enrichment_notes": "Excellent credit and no prior claims."}
    model = ScriptedAdapter([INTAKE.model_dump_json(), json.dumps(notes)])
    trace = TraceLog(applicant_id=RAW.applicant_id)
    result = run_intake_and_enrichment(RAW, model, trace)
    assert [span.agent for span in trace.spans] == ["intake_agent", "enrichment_agent"]
    intake_span, enrichment_span = trace.spans
    assert intake_span.input["applicant_id"] == "APP-1001"
    assert intake_span.output == INTAKE.model_dump()
    assert enrichment_span.input == INTAKE.model_dump()
    assert enrichment_span.output == result.model_dump()
    for span in trace.spans:
        assert span.duration_ms >= 0
        assert span.prompt_tokens == 11
        assert span.completion_tokens == 7
        assert span.tokens_used == 18
        assert span.timestamp
        assert span.error is None


def test_failed_step_is_traced_and_reraised() -> None:
    """A failed step records the error and does not swallow it."""
    trace = TraceLog(applicant_id="APP-1001")
    model = ScriptedAdapter([])

    def boom() -> IntakeResult:
        raise TimeoutError("slow")

    with pytest.raises(TimeoutError, match="slow"):
        run_step(
            trace,
            model,
            step="intake",
            agent="intake_agent",
            received={"applicant_id": "APP-1001"},
            call=boom,
        )
    assert trace.spans[0].error == "TimeoutError"
    assert trace.spans[0].output is None
    assert trace.spans[0].tokens_used == 0
