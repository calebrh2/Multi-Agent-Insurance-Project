"""Model adapter that returns predetermined completions for unit tests."""

from collections.abc import Sequence
from typing import Any

from underwriting.adapters.base import ModelResponse


class ScriptedAdapter:
    """Return scripted completions in order and record each call."""

    def __init__(
        self,
        contents: Sequence[str],
        *,
        prompt_tokens: int = 11,
        completion_tokens: int = 7,
    ) -> None:
        """Store the completions this adapter will hand out, in order."""
        self._contents = list(contents)
        self._prompt_tokens = prompt_tokens
        self._completion_tokens = completion_tokens
        self.last_response: ModelResponse | None = None
        self.calls: list[dict[str, Any]] = []

    def complete(
        self,
        *,
        system: str,
        user: str,
        json_schema: dict[str, Any],
    ) -> ModelResponse:
        """Return the next scripted completion and remember the request."""
        self.calls.append({"system": system, "user": user, "json_schema": json_schema})
        if not self._contents:
            raise RuntimeError("scripted adapter has no remaining responses")
        response = ModelResponse(
            content=self._contents.pop(0),
            prompt_tokens=self._prompt_tokens,
            completion_tokens=self._completion_tokens,
        )
        self.last_response = response
        return response
