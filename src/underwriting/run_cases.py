"""Run mock applications through a model and save traces."""

from collections.abc import Sequence
from pathlib import Path

from underwriting.adapters.base import ModelAdapter
from underwriting.adapters.ollama import OllamaAdapter
from underwriting.fixtures import MOCK_APPLICATIONS
from underwriting.pipeline import run_pipeline
from underwriting.runs import new_run_directory, write_case, write_summary
from underwriting.schemas import RawApplication
from underwriting.tracing import TraceLog


def evaluate(
    model: ModelAdapter,
    applications: Sequence[RawApplication],
    directory: Path,
) -> list[TraceLog]:
    """Run each application and write its trace under the directory."""
    traces: list[TraceLog] = []
    for raw in applications:
        trace = TraceLog(applicant_id=raw.applicant_id)
        outcome = run_pipeline(raw, model, trace)
        if outcome.recommendation is None:
            raise RuntimeError(outcome.escalation_reason or "case escalated")
        write_case(directory, trace, outcome.recommendation)
        traces.append(trace)
        print(f"{raw.applicant_id} {outcome.recommendation.decision}", flush=True)
    write_summary(directory, traces)
    return traces


def main() -> None:
    """Evaluate the three mock applications with qwen3:8b and print the run directory."""
    directory = new_run_directory()
    evaluate(OllamaAdapter(), MOCK_APPLICATIONS, directory)
    print(directory, flush=True)


if __name__ == "__main__":  # pragma: no cover
    main()
