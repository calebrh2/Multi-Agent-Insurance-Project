"""Step traces for one underwriting case.

Each span records the agent, the message it received, the message it produced,
how long it took, and how many tokens the model call used.
"""

import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from underwriting.adapters.base import ModelAdapter


class TraceSpan(BaseModel):
    """One agent step in a case trace."""

    step: str
    agent: str
    input: dict[str, Any]
    output: dict[str, Any] | None = None
    duration_ms: float = Field(ge=0)
    tokens_used: int = Field(ge=0)
    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    timestamp: str
    error: str | None = None
    attempt: int = Field(default=1, ge=1)


class TraceLog(BaseModel):
    """Ordered spans for a single applicant."""

    applicant_id: str
    spans: list[TraceSpan] = Field(default_factory=list)


def token_counts(model: ModelAdapter) -> tuple[int, int]:
    """Return prompt and completion tokens from the adapter's most recent call."""
    if model.last_response is None:
        return (0, 0)
    return (model.last_response.prompt_tokens, model.last_response.completion_tokens)


def run_step[T: BaseModel](
    trace: TraceLog | None,
    model: ModelAdapter,
    *,
    step: str,
    agent: str,
    received: dict[str, Any],
    call: Callable[[], T],
    attempt: int = 1,
) -> T:
    """Run one agent step and append a span when a trace was provided."""
    started = time.perf_counter()
    timestamp = datetime.now(UTC).isoformat()
    try:
        result = call()
    except Exception as exc:
        prompt_tokens, completion_tokens = token_counts(model)
        _append(
            trace,
            step=step,
            agent=agent,
            received=received,
            output=None,
            started=started,
            timestamp=timestamp,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            error=type(exc).__name__,
            attempt=attempt,
        )
        raise
    prompt_tokens, completion_tokens = token_counts(model)
    _append(
        trace,
        step=step,
        agent=agent,
        received=received,
        output=result.model_dump(),
        started=started,
        timestamp=timestamp,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        error=None,
        attempt=attempt,
    )
    return result


def _append(
    trace: TraceLog | None,
    *,
    step: str,
    agent: str,
    received: dict[str, Any],
    output: dict[str, Any] | None,
    started: float,
    timestamp: str,
    prompt_tokens: int,
    completion_tokens: int,
    error: str | None,
    attempt: int,
) -> None:
    """Append a span, or do nothing when the caller did not ask for a trace."""
    if trace is None:
        return
    elapsed_ms = max((time.perf_counter() - started) * 1000, 0)
    trace.spans.append(
        TraceSpan(
            step=step,
            agent=agent,
            input=received,
            output=output,
            duration_ms=elapsed_ms,
            tokens_used=prompt_tokens + completion_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            timestamp=timestamp,
            error=error,
            attempt=attempt,
        )
    )
