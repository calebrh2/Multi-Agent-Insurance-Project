"""Standalone unit test for the recommendation agent."""

import json

from underwriting.adapters.scripted import ScriptedAdapter
from underwriting.agents.recommendation import recommendation_agent
from underwriting.schemas import (
    EnrichmentResult,
    ExternalRecord,
    IntakeResult,
    RiskScoreResult,
)

RISK = RiskScoreResult(
    applicant_id="APP-1003",
    risk_score=0.52,
    risk_factors=["prior_claim", "high_coverage"],
    rationale="One prior claim and a high coverage amount leave the case in the middle.",
    enrichment=EnrichmentResult(
        applicant_id="APP-1003",
        intake=IntakeResult(
            applicant_id="APP-1003",
            full_name="Priya Shah",
            age=41,
            product="home",
            coverage_amount=900_000,
            stated_claims=1,
            normalized_notes="Coastal property, one water claim",
            missing_fields=[],
        ),
        external=ExternalRecord(
            applicant_id="APP-1003",
            credit_band="good",
            prior_claims=1,
            property_risk="moderate",
        ),
        enrichment_notes="External records show good credit, one prior claim, and moderate property risk.",
    ),
)


def test_recommendation_agent_refers_a_hardcoded_borderline_score() -> None:
    """A known mid-range risk message produces a refer recommendation."""
    payload = {
        "decision": "refer",
        "rationale": "A score of 0.52 with a prior claim and high coverage should go to a human underwriter.",
    }
    model = ScriptedAdapter([json.dumps(payload)])
    result = recommendation_agent(RISK, model)
    assert result.risk == RISK
    assert result.applicant_id == "APP-1003"
    assert result.decision == "refer"
    assert "0.52" in result.rationale
    assert "APP-1003" in model.calls[0]["user"]
    assert "<examples>" in model.calls[0]["system"]
