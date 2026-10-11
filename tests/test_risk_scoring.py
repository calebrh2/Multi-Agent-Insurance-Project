"""Standalone unit test for the risk scoring agent."""

import json

from underwriting.adapters.scripted import ScriptedAdapter
from underwriting.agents.risk_scoring import risk_scoring_agent
from underwriting.schemas import EnrichmentResult, ExternalRecord, IntakeResult

ENRICHMENT = EnrichmentResult(
    applicant_id="APP-1002",
    intake=IntakeResult(
        applicant_id="APP-1002",
        full_name="Leon Ruiz",
        age=62,
        product="auto",
        coverage_amount=150_000,
        stated_claims=3,
        normalized_notes="Three at-fault accidents in five years",
        missing_fields=[],
    ),
    external=ExternalRecord(
        applicant_id="APP-1002",
        credit_band="poor",
        prior_claims=4,
        property_risk="high",
    ),
    enrichment_notes="External records show poor credit, four prior claims, and high property risk.",
)


def test_risk_scoring_agent_scores_a_hardcoded_enrichment_message() -> None:
    """A known high-risk enrichment message produces a high score and factors."""
    payload = {
        "risk_score": 0.86,
        "risk_factors": ["poor_credit", "multiple_prior_claims", "high_property_risk"],
        "rationale": "Poor credit and four prior claims put this case near the top of the scale.",
    }
    model = ScriptedAdapter([json.dumps(payload)])
    result = risk_scoring_agent(ENRICHMENT, model)
    assert result.enrichment == ENRICHMENT
    assert result.applicant_id == "APP-1002"
    assert result.risk_score == 0.86
    assert "poor_credit" in result.risk_factors
    assert "prior claims" in result.rationale
    assert "APP-1002" in model.calls[0]["user"]
    assert "<examples>" in model.calls[0]["system"]
