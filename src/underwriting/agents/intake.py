"""Intake agent: normalize one raw application into an intake message."""

from pydantic import BaseModel

from underwriting.adapters.base import ModelAdapter
from underwriting.agents.common import complete_json
from underwriting.prompts.loader import load_prompt
from underwriting.schemas import IntakeResult, RawApplication


class _IntakeNotes(BaseModel):
    """Notes and missing fields. Structured columns are copied from the application."""

    normalized_notes: str
    missing_fields: list[str]


def intake_agent(raw_application: RawApplication, model: ModelAdapter) -> IntakeResult:
    """Normalize one application. The model call writes the notes and missing fields."""
    notes = complete_json(
        model,
        system=load_prompt("intake-v0.md"),
        user=raw_application.model_dump_json(),
        result_type=_IntakeNotes,
    )
    return IntakeResult(
        applicant_id=raw_application.applicant_id,
        full_name=raw_application.full_name.strip(),
        age=raw_application.age,
        product=raw_application.product.strip().lower(),
        coverage_amount=raw_application.coverage_amount,
        stated_claims=raw_application.stated_claims,
        normalized_notes=notes.normalized_notes,
        missing_fields=notes.missing_fields,
    )
