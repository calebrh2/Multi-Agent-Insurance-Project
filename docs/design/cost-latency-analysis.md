# Cost and latency analysis

Figures below come from `agent/runs/20261011T032007Z/summary.json`, the three live `qwen3:8b` cases. They are not the observability article's hypothetical $0.02 / $0.05 / $0.03 / $0.02 illustration.

The planning rate was set in `docs/design/state-and-memory.md` before the pipeline was built:

- $0.10 per 1,000,000 prompt tokens
- $0.40 per 1,000,000 completion tokens

Local Ollama's marginal API cost for this run is $0. The planning rate is what a hosted 8B-class model would charge for the same token counts. `planning_cost_usd` in `src/underwriting/cost.py` is the formula, and `tests/test_cost.py` checks it against this run.

Real-time budget: under 10 seconds and under $0.05 per case. Overnight batch budget: under 180 seconds per case, and the same $0.05 cost cap.

## Measured cases

| Case | Decision | Duration | Prompt tokens | Completion tokens | Planning cost |
| --- | --- | --- | --- | --- | --- |
| APP-1001 | approve | 12,336.52 ms | 1,940 | 110 | $0.00023800 |
| APP-1002 | deny | 7,842.49 ms | 1,974 | 147 | $0.00025620 |
| APP-1003 | refer | 7,642.10 ms | 1,975 | 145 | $0.00025550 |

APP-1001 cost is `1940 * 0.10 / 1_000_000 + 110 * 0.40 / 1_000_000`. The other two rows use the same formula on their own token counts. Every case is about two and a half hundredths of a cent, far under $0.05. At 10,000 cases a month the planning bill would be about $2.50, and the local API bill would stay $0.

Per agent, the warm cases spend the most time in risk scoring: 3,176.94 ms on APP-1002 and 2,690.31 ms on APP-1003. APP-1001's slowest step is intake at 5,165.89 ms. The later intake calls took 1,029.62 ms and 994.36 ms, so that first intake call is the model loading into memory, not a property of Maya Chen's application.

## Conclusion

This pipeline is acceptable for overnight batch and not acceptable for a real-time decision.

Cost clears both budgets. Latency does not clear the real-time budget on every measured case. APP-1001 took 12.3 seconds, over the 10 second line. APP-1002 and APP-1003 finished in 7.8 and 7.6 seconds, inside the line, but only after the model was already loaded, and with little room left if a step had to be retried. A retry of the slowest warm step would push those cases over 10 seconds as well. All three cases are well under the 180 second overnight limit, including the cold start.

The steps stay sequential because risk scoring reads enrichment's message. Parallelism would not remove the cold-start miss, and it would break the handoff this pipeline is built on.
