"""Risk scoring agent: turn one enrichment message into a score."""

from pydantic import BaseModel, Field

from underwriting.adapters.base import ModelAdapter
from underwriting.agents.common import complete_json
from underwriting.prompts.loader import load_prompt
from underwriting.schemas import EnrichmentResult, RiskScoreResult


class _RiskJudgment(BaseModel):
    """Score and factors the model writes. The enrichment message is attached in code."""

    risk_score: float = Field(ge=0, le=1)
    risk_factors: list[str]
    rationale: str


def risk_scoring_agent(
    enrichment: EnrichmentResult,
    model: ModelAdapter,
) -> RiskScoreResult:
    """Score the enrichment message. That message is the only case data read."""
    judgment = complete_json(
        model,
        system=load_prompt("risk_scoring-v0.md"),
        user=enrichment.model_dump_json(),
        result_type=_RiskJudgment,
    )
    return RiskScoreResult(
        applicant_id=enrichment.applicant_id,
        risk_score=judgment.risk_score,
        risk_factors=judgment.risk_factors,
        rationale=judgment.rationale,
        enrichment=enrichment,
    )
