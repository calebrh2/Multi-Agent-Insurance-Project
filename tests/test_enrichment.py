"""Standalone unit test for the enrichment agent."""

import json

import pytest

from underwriting.adapters.scripted import ScriptedAdapter
from underwriting.agents.enrichment import enrichment_agent
from underwriting.reference import lookup_external_record
from underwriting.schemas import IntakeResult

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


def test_enrichment_agent_attaches_the_lookup_to_a_hardcoded_intake() -> None:
    """Enrichment reads the intake message and the reference row for that id."""
    notes = "Excellent credit and no prior claims support the clean application."
    model = ScriptedAdapter([json.dumps({"enrichment_notes": notes})])
    result = enrichment_agent(INTAKE, model)
    assert result.intake == INTAKE
    assert result.external == lookup_external_record("APP-1001")
    assert result.external.credit_band == "excellent"
    assert result.external.prior_claims == 0
    assert result.enrichment_notes == notes
    payload = json.loads(model.calls[0]["user"])
    assert payload["intake"]["applicant_id"] == "APP-1001"
    assert payload["external_record"]["property_risk"] == "low"
    assert "<examples>" in model.calls[0]["system"]


def test_lookup_rejects_an_unknown_applicant() -> None:
    """A missing reference row is an error, not a guessed record."""
    with pytest.raises(KeyError, match="APP-MISSING"):
        lookup_external_record("APP-MISSING")
