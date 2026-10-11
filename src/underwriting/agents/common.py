"""Shared model call used by each standalone agent."""

from typing import Any

from pydantic import BaseModel

from underwriting.adapters.base import ModelAdapter
from underwriting.parsing import extract_json_object


def complete_json[T: BaseModel](
    model: ModelAdapter,
    *,
    system: str,
    user: str,
    result_type: type[T],
) -> T:
    """Call the model once and parse the completion as a Pydantic model."""
    schema: dict[str, Any] = result_type.model_json_schema()
    response = model.complete(system=system, user=user, json_schema=schema)
    return result_type.model_validate_json(extract_json_object(response.content))
