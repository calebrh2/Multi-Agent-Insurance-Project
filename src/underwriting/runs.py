"""Write one timestamped directory of case traces."""

import json
from datetime import UTC, datetime
from pathlib import Path

from underwriting.schemas import RecommendationResult
from underwriting.tracing import TraceLog


def new_run_directory(
    root: Path = Path("agent/runs"),
    now: datetime | None = None,
) -> Path:
    """Create agent/runs/<UTC timestamp> for one evaluation."""
    moment = now or datetime.now(UTC)
    directory = root / moment.strftime("%Y%m%dT%H%M%SZ")
    directory.mkdir(parents=True, exist_ok=False)
    return directory


def write_case(
    directory: Path,
    trace: TraceLog,
    recommendation: RecommendationResult,
) -> Path:
    """Write trace.json and recommendation.json for one applicant."""
    case_dir = directory / trace.applicant_id
    case_dir.mkdir()
    (case_dir / "trace.json").write_text(
        trace.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    (case_dir / "recommendation.json").write_text(
        recommendation.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    return case_dir


def write_summary(directory: Path, traces: list[TraceLog]) -> Path:
    """Write per-case token and duration totals next to the traces."""
    cases = []
    for trace in traces:
        cases.append(
            {
                "applicant_id": trace.applicant_id,
                "total_duration_ms": sum(span.duration_ms for span in trace.spans),
                "total_tokens": sum(span.tokens_used for span in trace.spans),
                "prompt_tokens": sum(span.prompt_tokens for span in trace.spans),
                "completion_tokens": sum(
                    span.completion_tokens for span in trace.spans
                ),
                "agents": [
                    {
                        "agent": span.agent,
                        "duration_ms": span.duration_ms,
                        "tokens_used": span.tokens_used,
                        "prompt_tokens": span.prompt_tokens,
                        "completion_tokens": span.completion_tokens,
                        "error": span.error,
                    }
                    for span in trace.spans
                ],
            }
        )
    path = directory / "summary.json"
    path.write_text(json.dumps({"cases": cases}, indent=2) + "\n", encoding="utf-8")
    return path
