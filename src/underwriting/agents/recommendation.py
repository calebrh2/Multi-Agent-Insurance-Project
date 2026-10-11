"""Recommendation agent: turn one risk message into approve, deny, or refer."""

from typing import Literal

from pydantic import BaseModel

from underwriting.adapters.base import ModelAdapter
from underwriting.agents.common import complete_json
from underwriting.prompts.loader import load_prompt
from underwriting.schemas import RecommendationResult, RiskScoreResult


class _RecommendationJudgment(BaseModel):
    """Decision the model writes. The risk message is attached in code."""

    decision: Literal["approve", "deny", "refer"]
    rationale: str


def recommendation_agent(
    risk: RiskScoreResult,
    model: ModelAdapter,
) -> RecommendationResult:
    """Recommend a decision from the risk message. That message is the only case data read."""
    judgment = complete_json(
        model,
        system=load_prompt("recommendation-v0.md"),
        user=risk.model_dump_json(),
        result_type=_RecommendationJudgment,
    )
    return RecommendationResult(
        applicant_id=risk.applicant_id,
        decision=judgment.decision,
        rationale=judgment.rationale,
        risk=risk,
    )
