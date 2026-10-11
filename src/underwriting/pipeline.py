"""Underwriting pipeline. Agents are wired one at a time.

Recommendation is not wired yet.
"""

from underwriting.adapters.base import ModelAdapter
from underwriting.agents.enrichment import enrichment_agent
from underwriting.agents.intake import intake_agent
from underwriting.agents.risk_scoring import risk_scoring_agent
from underwriting.schemas import EnrichmentResult, RawApplication, RiskScoreResult
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
