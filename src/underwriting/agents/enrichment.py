"""Enrichment agent: attach a reference row to an intake message."""

import json

from pydantic import BaseModel

from underwriting.adapters.base import ModelAdapter
from underwriting.agents.common import complete_json
from underwriting.prompts.loader import load_prompt
from underwriting.reference import lookup_external_record
from underwriting.schemas import EnrichmentResult, IntakeResult


class _EnrichmentNotes(BaseModel):
    """The only field the model is asked to write for enrichment."""

    enrichment_notes: str


def enrichment_agent(intake: IntakeResult, model: ModelAdapter) -> EnrichmentResult:
    """Look up reference data for this intake message and describe what it adds.

    The intake argument is the only case data this agent receives. The lookup
    is a tool call inside the agent, not a store shared with the other agents.
    """
    external = lookup_external_record(intake.applicant_id)
    user = json.dumps(
        {
            "intake": intake.model_dump(),
            "external_record": external.model_dump(),
        }
    )
    notes = complete_json(
        model,
        system=load_prompt("enrichment-v0.md"),
        user=user,
        result_type=_EnrichmentNotes,
    )
    return EnrichmentResult(
        applicant_id=intake.applicant_id,
        intake=intake,
        external=external,
        enrichment_notes=notes.enrichment_notes,
    )
