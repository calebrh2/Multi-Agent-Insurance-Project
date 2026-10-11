"""Handoff from intake to enrichment, with a trace of each step.

Risk scoring and recommendation are not wired yet.
"""

from underwriting.adapters.base import ModelAdapter
from underwriting.agents.enrichment import enrichment_agent
from underwriting.agents.intake import intake_agent
from underwriting.schemas import EnrichmentResult, RawApplication
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
