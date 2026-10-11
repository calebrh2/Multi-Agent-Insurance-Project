"""Messages each underwriting agent reads and produces.

Agents do not share a case store. The object returned by one agent is the
argument passed to the next agent.
"""

from typing import Literal

from pydantic import BaseModel, Field


class RawApplication(BaseModel):
    """Application fields as the applicant submitted them."""

    applicant_id: str
    full_name: str
    age: int = Field(ge=0)
    product: str
    coverage_amount: int = Field(ge=0)
    stated_claims: int = Field(ge=0)
    notes: str = ""


class IntakeResult(BaseModel):
    """Normalized application produced by the intake agent."""

    applicant_id: str
    full_name: str
    age: int = Field(ge=0)
    product: str
    coverage_amount: int = Field(ge=0)
    stated_claims: int = Field(ge=0)
    normalized_notes: str
    missing_fields: list[str]


class ExternalRecord(BaseModel):
    """Reference row the enrichment agent looks up for one applicant."""

    applicant_id: str
    credit_band: Literal["excellent", "good", "fair", "poor"]
    prior_claims: int = Field(ge=0)
    property_risk: Literal["low", "moderate", "high"]


class EnrichmentResult(BaseModel):
    """Intake message plus the external row and what that row changes."""

    applicant_id: str
    intake: IntakeResult
    external: ExternalRecord
    enrichment_notes: str


class RiskScoreResult(BaseModel):
    """Risk score for the enrichment message that was scored."""

    applicant_id: str
    risk_score: float = Field(ge=0, le=1)
    risk_factors: list[str]
    rationale: str
    enrichment: EnrichmentResult


class RecommendationResult(BaseModel):
    """Final approve, deny, or refer decision for one scored case."""

    applicant_id: str
    decision: Literal["approve", "deny", "refer"]
    rationale: str
    risk: RiskScoreResult
