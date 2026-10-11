"""Tests for the timestamped run directory writer."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from underwriting.adapters.scripted import ScriptedAdapter
from underwriting.fixtures import MOCK_APPLICATIONS
from underwriting.run_cases import evaluate, main
from underwriting.runs import new_run_directory, write_case, write_summary
from underwriting.schemas import (
    EnrichmentResult,
    ExternalRecord,
    IntakeResult,
    RawApplication,
    RecommendationResult,
    RiskScoreResult,
)
from underwriting.tracing import TraceLog, TraceSpan


def _recommendation() -> RecommendationResult:
    intake = IntakeResult(
        applicant_id="APP-1001",
        full_name="Maya Chen",
        age=34,
        product="home",
        coverage_amount=300_000,
        stated_claims=0,
        normalized_notes="Primary residence",
        missing_fields=[],
    )
    enrichment = EnrichmentResult(
        applicant_id="APP-1001",
        intake=intake,
        external=ExternalRecord(
            applicant_id="APP-1001",
            credit_band="excellent",
            prior_claims=0,
            property_risk="low",
        ),
        enrichment_notes="Clean record.",
    )
    risk = RiskScoreResult(
        applicant_id="APP-1001",
        risk_score=0.15,
        risk_factors=[],
        rationale="Low risk.",
        enrichment=enrichment,
    )
    return RecommendationResult(
        applicant_id="APP-1001",
        decision="approve",
        rationale="Approve.",
        risk=risk,
    )


def test_run_directory_uses_the_utc_timestamp(tmp_path: Path) -> None:
    """The folder name is the UTC timestamp passed in."""
    moment = datetime(2026, 10, 11, 3, 4, 5, tzinfo=UTC)
    directory = new_run_directory(tmp_path / "runs", now=moment)
    assert directory.name == "20261011T030405Z"
    with pytest.raises(FileExistsError):
        new_run_directory(tmp_path / "runs", now=moment)


def test_write_case_and_summary_round_trip(tmp_path: Path) -> None:
    """A case trace and the summary are legible JSON on disk."""
    directory = tmp_path / "run"
    directory.mkdir()
    trace = TraceLog(
        applicant_id="APP-1001",
        spans=[
            TraceSpan(
                step="intake",
                agent="intake_agent",
                input={"applicant_id": "APP-1001"},
                output={"product": "home"},
                duration_ms=12.5,
                tokens_used=30,
                prompt_tokens=20,
                completion_tokens=10,
                timestamp="2026-10-11T03:04:05+00:00",
            )
        ],
    )
    case_dir = write_case(directory, trace, _recommendation())
    summary = write_summary(directory, [trace])
    saved = json.loads((case_dir / "trace.json").read_text(encoding="utf-8"))
    assert saved["spans"][0]["agent"] == "intake_agent"
    assert saved["spans"][0]["tokens_used"] == 30
    assert "approve" in (case_dir / "recommendation.json").read_text(encoding="utf-8")
    totals = json.loads(summary.read_text(encoding="utf-8"))
    assert totals["cases"][0]["total_tokens"] == 30
    assert totals["cases"][0]["total_duration_ms"] == 12.5


def test_evaluate_writes_one_scripted_case(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """evaluate runs the pipeline and leaves a trace file behind."""
    raw = RawApplication(
        applicant_id="APP-1001",
        full_name="Maya Chen",
        age=34,
        product="Home",
        coverage_amount=300_000,
        stated_claims=0,
        notes="Primary residence, new roof",
    )
    model = ScriptedAdapter(
        [
            json.dumps(
                {
                    "normalized_notes": "Primary residence, new roof",
                    "missing_fields": [],
                }
            ),
            json.dumps({"enrichment_notes": "Excellent credit."}),
            json.dumps({"risk_score": 0.15, "risk_factors": [], "rationale": "Low."}),
            json.dumps({"decision": "approve", "rationale": "Approve."}),
        ]
    )
    traces = evaluate(model, [raw], tmp_path)
    assert traces[0].spans[3].agent == "recommendation_agent"
    assert (tmp_path / "APP-1001" / "trace.json").is_file()
    assert (tmp_path / "summary.json").is_file()
    assert "APP-1001 approve" in capsys.readouterr().out


def test_main_uses_the_three_mock_applications(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """main evaluates the fixture applications and prints the directory."""
    responses: list[str] = []
    for _raw in MOCK_APPLICATIONS:
        responses.extend(
            [
                json.dumps({"normalized_notes": "notes", "missing_fields": []}),
                json.dumps({"enrichment_notes": "Looked up."}),
                json.dumps(
                    {
                        "risk_score": 0.4,
                        "risk_factors": ["prior_claim"],
                        "rationale": "Mid.",
                    }
                ),
                json.dumps({"decision": "refer", "rationale": "Refer."}),
            ]
        )
    monkeypatch.setattr(
        "underwriting.run_cases.OllamaAdapter",
        lambda: ScriptedAdapter(responses),
    )
    monkeypatch.setattr("underwriting.run_cases.new_run_directory", lambda: tmp_path)
    main()
    assert "APP-1001" in capsys.readouterr().out
    assert (tmp_path / "summary.json").is_file()
    saved = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert len(saved["cases"]) == 3
