"""Adapter that times out the risk-scoring call for one applicant."""

from typing import Any

from underwriting.adapters.base import ModelAdapter, ModelResponse


class RiskTimeoutAdapter:
    """Raise TimeoutError on the risk-scoring call for a chosen applicant.

    Other agents, and other applicants, are forwarded to the inner adapter.
    """

    def __init__(
        self,
        inner: ModelAdapter,
        *,
        applicant_id: str,
        failures: int,
    ) -> None:
        """Fail the next `failures` risk-scoring calls whose user payload names this applicant."""
        self._inner = inner
        self.applicant_id = applicant_id
        self._failures_left = failures
        self.last_response: ModelResponse | None = None

    def complete(
        self,
        *,
        system: str,
        user: str,
        json_schema: dict[str, Any],
    ) -> ModelResponse:
        """Time out a risk-scoring call, otherwise delegate."""
        properties = json_schema.get("properties", {})
        is_risk_call = isinstance(properties, dict) and "risk_score" in properties
        if is_risk_call and self.applicant_id in user and self._failures_left > 0:
            self._failures_left -= 1
            self.last_response = None
            raise TimeoutError("risk scoring timed out")
        response = self._inner.complete(
            system=system, user=user, json_schema=json_schema
        )
        self.last_response = response
        return response
