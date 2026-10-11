# Multi-agent underwriting pipeline

An applicant submits an insurance application. Four agents handle it in order: intake, enrichment, risk scoring, and a recommendation to approve, deny, or refer. Each agent calls `qwen3:8b` through Ollama for its reasoning step. The model sits behind an adapter, so tests use a scripted model and the live run uses Ollama.

## How the agents share information

They pass messages. There is no shared case record. `intake_agent` returns an `IntakeResult`, and that object is the only case data `enrichment_agent` receives. Enrichment returns an `EnrichmentResult` to risk scoring, and risk scoring returns a `RiskScoreResult` to recommendation. The choice, the fields each agent reads and writes, and the cost and latency budgets are in [docs/design/state-and-memory.md](docs/design/state-and-memory.md). That note was written before the orchestration code.

Short-term memory is the message for the case in hand. A second application does not see the first one's details, because nothing is stored on a global.

Enrichment does look up a local reference row (credit band, prior claims, property risk) by applicant id. That lookup is a tool inside the enrichment agent. The other agents never read it.

## Layout

- `src/underwriting/agents/` — `intake_agent`, `enrichment_agent`, `risk_scoring_agent`, `recommendation_agent`
- `src/underwriting/prompts/` — versioned prompts (`intake-v0.md` and the rest), with XML labels and few-shot examples
- `src/underwriting/adapters/` — `ModelAdapter`, the Ollama adapter, a scripted adapter for tests, and a timeout adapter used to simulate a failed risk call
- `src/underwriting/pipeline.py` — wires the four agents and retries risk scoring
- `src/underwriting/tracing.py` — one span per agent: input, output, duration, token counts
- `src/underwriting/fixtures.py` — three mock applications
- `agent/runs/20261011T032007Z/` — traces from the live run
- `docs/design/cost-latency-analysis.md` — cost and latency from those traces
- `docs/design/instruction-audit.md` — what in the lesson material is context rather than a requirement

## Run the tests

```bash
python -m pip install -e ".[dev]"
ruff check src tests
mypy --strict src/underwriting
pytest -q
```

The unit tests do not call Ollama. Each agent test passes a hardcoded application (or the previous agent's message) through a scripted model response and checks the structured result.

## Run the three live cases

Ollama is expected at `http://host.docker.internal:11434` with `qwen3:8b` already pulled. Override the host or model with `OLLAMA_HOST` and `OLLAMA_MODEL`.

```bash
PYTHONPATH=src python -m underwriting.run_cases
```

That writes `agent/runs/<UTC timestamp>/`. The checked-in run is `agent/runs/20261011T032007Z/`.

## What one case looks like

APP-1001 is Maya Chen, age 34, a home policy for $300,000, no stated claims, notes "Primary residence, new roof". In the live run the pipeline recommended **approve**.

The trace at `agent/runs/20261011T032007Z/APP-1001/trace.json` shows the handoff:

1. Intake received the raw application and produced a normalized record: product `home`, the same notes, no missing fields. 376 tokens, about 5.2 seconds. That first call also loaded the model.
2. Enrichment received that intake message, looked up excellent credit, zero prior claims, and low property risk, and wrote that the external row agrees with the application.
3. Risk scoring received the enrichment message and returned a score of 0.15 with no material factors.
4. Recommendation received that risk message and approved.

APP-1002 (poor credit, four prior claims, three stated accidents) was denied. APP-1003 (good credit, one prior claim, a $900,000 coastal home) was referred. Refer here is a normal recommendation for a borderline case. It is not an error.

## Cost and latency

Measured from that run, using the planning rate of $0.10 per million prompt tokens and $0.40 per million completion tokens. Local Ollama's API bill is $0.

- APP-1001: 12.3 seconds, $0.000238
- APP-1002: 7.8 seconds, $0.000256
- APP-1003: 7.6 seconds, $0.000256

The real-time budget is under 10 seconds and under $0.05. The overnight budget is under 180 seconds. Cost is fine for either use. Latency is not fine for a real-time decision: the cold case missed 10 seconds, and the warm cases only fit because the model was already loaded. All three fit overnight batch easily. The full write-up is [docs/design/cost-latency-analysis.md](docs/design/cost-latency-analysis.md).

## When risk scoring times out

For applicant `APP-TIMEOUT`, the adapter raises `TimeoutError` on the risk-scoring call. The pipeline waits 0.5 seconds, retries, waits 1 second, retries again, and then returns status `escalated`. The process does not crash. The result has no recommendation, no risk score, and no approve or deny. A trace records all three failed attempts. That path is covered by `tests/test_failure.py`.
