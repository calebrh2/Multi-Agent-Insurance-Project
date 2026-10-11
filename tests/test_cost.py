"""The cost figures in the write-up match the captured run."""

import json
from pathlib import Path

from underwriting.cost import BATCH_MS, REAL_TIME_MS, REAL_TIME_USD, planning_cost_usd

RUN = Path(__file__).parents[1] / "agent" / "runs" / "20261011T032007Z" / "summary.json"


def test_planning_cost_matches_the_captured_run() -> None:
    """Each saved case prices under the budget and the slowest misses real time."""
    summary = json.loads(RUN.read_text(encoding="utf-8"))
    costs = []
    durations = []
    for case in summary["cases"]:
        cost = planning_cost_usd(case["prompt_tokens"], case["completion_tokens"])
        costs.append(cost)
        durations.append(case["total_duration_ms"])
        assert cost < REAL_TIME_USD
        assert case["total_duration_ms"] < BATCH_MS
    assert costs[0] == planning_cost_usd(1940, 110)
    assert round(costs[0], 8) == 0.00023800
    assert round(costs[1], 8) == 0.00025620
    assert round(costs[2], 8) == 0.00025550
    assert durations[0] > REAL_TIME_MS
    assert durations[1] < REAL_TIME_MS
    assert durations[2] < REAL_TIME_MS
