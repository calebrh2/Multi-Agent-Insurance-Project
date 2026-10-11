"""Intake's result is the object enrichment receives."""

import json

from underwriting.adapters.scripted import ScriptedAdapter
from underwriting.pipeline import run_intake_and_enrichment
from underwriting.schemas import IntakeResult, RawApplication

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


def test_enrichment_receives_the_intake_message() -> None:
    """The second agent's input is the first agent's output, not a shared record."""
    notes = {"enrichment_notes": "Excellent credit and no prior claims."}
    model = ScriptedAdapter([INTAKE.model_dump_json(), json.dumps(notes)])
    result = run_intake_and_enrichment(RAW, model)
    assert result.intake == INTAKE
    sent = json.loads(model.calls[1]["user"])
    assert sent["intake"] == INTAKE.model_dump()
    assert len(model.calls) == 2
