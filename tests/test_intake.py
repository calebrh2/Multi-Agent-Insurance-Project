"""Standalone unit test for the intake agent."""

from underwriting.adapters.scripted import ScriptedAdapter
from underwriting.agents.intake import intake_agent
from underwriting.prompts.loader import load_prompt
from underwriting.schemas import IntakeResult, RawApplication

RAW = RawApplication(
    applicant_id="APP-1001",
    full_name="Maya Chen",
    age=34,
    product="Home",
    coverage_amount=300_000,
    stated_claims=0,
    notes="Primary residence, new roof",
)

EXPECTED = IntakeResult(
    applicant_id="APP-1001",
    full_name="Maya Chen",
    age=34,
    product="home",
    coverage_amount=300_000,
    stated_claims=0,
    normalized_notes="Primary residence, new roof",
    missing_fields=[],
)


def test_intake_agent_normalizes_a_hardcoded_application() -> None:
    """A known application comes back as a normalized intake message."""
    model = ScriptedAdapter([EXPECTED.model_dump_json()])
    result = intake_agent(RAW, model)
    assert result == EXPECTED
    assert result.missing_fields == []
    assert result.product == "home"
    assert model.last_response is not None
    assert model.last_response.tokens_used == 18
    sent = model.calls[0]
    assert "APP-1001" in sent["user"]
    assert "<system>" in sent["system"]
    assert "<examples>" in sent["system"]
    assert sent["system"] == load_prompt("intake-v0.md")
