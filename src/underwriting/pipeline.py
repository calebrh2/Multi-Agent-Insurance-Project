"""Underwriting pipeline. Each agent's message is the next agent's input."""

import time
from collections.abc import Callable

from underwriting.adapters.base import ModelAdapter
from underwriting.agents.enrichment import enrichment_agent
from underwriting.agents.intake import intake_agent
from underwriting.agents.recommendation import recommendation_agent
from underwriting.agents.risk_scoring import risk_scoring_agent
from underwriting.schemas import (
    EnrichmentResult,
    PipelineResult,
    RawApplication,
    RecommendationResult,
    RiskScoreResult,
)
from underwriting.tracing import TraceLog, run_step


def run_intake_and_enrichment(
    raw_application: RawApplication,
    model: ModelAdapter,
    trace: TraceLog | None = None,
) -> EnrichmentResult:
    """Run intake, pass that message to enrichment, and record both steps."""
    intake = run_step(
        trace,
        model,
        step="intake",
        agent="intake_agent",
        received=raw_application.model_dump(),
        call=lambda: intake_agent(raw_application, model),
    )
    return run_step(
        trace,
        model,
        step="enrichment",
        agent="enrichment_agent",
        received=intake.model_dump(),
        call=lambda: enrichment_agent(intake, model),
    )


def run_through_risk(
    raw_application: RawApplication,
    model: ModelAdapter,
    trace: TraceLog | None = None,
) -> RiskScoreResult:
    """Continue the traced handoff through risk scoring."""
    enrichment = run_intake_and_enrichment(raw_application, model, trace)
    return run_step(
        trace,
        model,
        step="risk_scoring",
        agent="risk_scoring_agent",
        received=enrichment.model_dump(),
        call=lambda: risk_scoring_agent(enrichment, model),
    )


_BACKOFF_SECONDS = (0.5, 1.0)


def run_pipeline(
    raw_application: RawApplication,
    model: ModelAdapter,
    trace: TraceLog | None = None,
    *,
    sleeper: Callable[[float], None] = time.sleep,
    max_attempts: int = 3,
) -> PipelineResult:
    """Run all four agents. Risk scoring retries with backoff, then escalates.

    An escalated case has no recommendation. It is not an approve, deny, or refer.
    """
    enrichment = run_intake_and_enrichment(raw_application, model, trace)
    for attempt in range(1, max_attempts + 1):
        try:
            scored = run_step(
                trace,
                model,
                step="risk_scoring",
                agent="risk_scoring_agent",
                received=enrichment.model_dump(),
                call=lambda: risk_scoring_agent(enrichment, model),
                attempt=attempt,
            )
        except TimeoutError:
            if attempt == max_attempts:
                return PipelineResult(
                    applicant_id=raw_application.applicant_id,
                    status="escalated",
                    escalation_reason=(
                        f"risk scoring timed out after {max_attempts} attempts; "
                        "no risk score and no approve or deny was produced"
                    ),
                )
            sleeper(_BACKOFF_SECONDS[attempt - 1])
            continue

        def recommend(scored_case: RiskScoreResult = scored) -> RecommendationResult:
            return recommendation_agent(scored_case, model)

        recommendation = run_step(
            trace,
            model,
            step="recommendation",
            agent="recommendation_agent",
            received=scored.model_dump(),
            call=recommend,
        )
        return PipelineResult(
            applicant_id=raw_application.applicant_id,
            status="completed",
            recommendation=recommendation,
        )
    return PipelineResult(
        applicant_id=raw_application.applicant_id,
        status="escalated",
        escalation_reason="risk scoring was not attempted",
    )
