"""Adapter surface every underwriting model call goes through."""

from typing import Any, Protocol

from pydantic import BaseModel, Field


class ModelResponse(BaseModel):
    """Text returned by a model call, with the token counts for that call."""

    content: str
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)

    @property
    def tokens_used(self) -> int:
        """Return prompt tokens plus completion tokens."""
        return self.prompt_tokens + self.completion_tokens


class ModelAdapter(Protocol):
    """One model call in, one response out. Agents depend on this, not on Ollama."""

    last_response: ModelResponse | None

    def complete(
        self,
        *,
        system: str,
        user: str,
        json_schema: dict[str, Any],
    ) -> ModelResponse:
        """Send one chat turn and return the model's text and token counts."""
