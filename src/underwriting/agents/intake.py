"""Intake agent: normalize one raw application into an intake message."""

from underwriting.adapters.base import ModelAdapter
from underwriting.agents.common import complete_json
from underwriting.prompts.loader import load_prompt
from underwriting.schemas import IntakeResult, RawApplication


def intake_agent(raw_application: RawApplication, model: ModelAdapter) -> IntakeResult:
    """Normalize one application. The model call is this agent's reasoning step."""
    return complete_json(
        model,
        system=load_prompt("intake-v0.md"),
        user=raw_application.model_dump_json(),
        result_type=IntakeResult,
    )
