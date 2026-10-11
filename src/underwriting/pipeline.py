"""Handoff from intake to enrichment.

Risk scoring and recommendation are not wired yet. Tracing is added once
this two-agent handoff is confirmed.
"""

from underwriting.adapters.base import ModelAdapter
from underwriting.agents.enrichment import enrichment_agent
from underwriting.agents.intake import intake_agent
from underwriting.schemas import EnrichmentResult, RawApplication


def run_intake_and_enrichment(
    raw_application: RawApplication,
    model: ModelAdapter,
) -> EnrichmentResult:
    """Run intake, then pass that intake message straight to enrichment."""
    intake = intake_agent(raw_application, model)
    return enrichment_agent(intake, model)
