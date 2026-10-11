# State and memory design

Written before any orchestration code. The pipeline is a fixed sequence: intake, enrichment, risk scoring, recommendation. The pattern is explicit message passing.

## Choice

Each agent is a function. Its only case data is the argument it is given, and its return value is the only thing the next agent is given. There is no shared case record, dictionary, file, or database that agents read from or write to.

Message passing is the right fit here because the steps are a fixed workflow and each step needs the previous step's result. The state article's tradeoff applies directly: a shared store is simpler to set up and riskier, because any agent can read or write a field it should not touch. Message passing costs more explicit plumbing and keeps those boundaries clear. Queues, webhooks, and an event bus solve load spikes and outside notifications this lab does not have, so they are not part of the design.

Short-term memory is the Pydantic message for the case being handled. It is created for that call and dropped when the case returns. Nothing is stored on a module global, so a second application cannot see the first one's details. There is no long-term store. A case finishes in one run.

## What each agent reads and produces

`intake_agent(raw_application) -> IntakeResult`

- Reads the raw application only: applicant id, full name, age, product, coverage amount, stated claims, and free-text notes.
- Produces a normalized intake record and the list of fields that were missing or unusable.

`enrichment_agent(intake_result) -> EnrichmentResult`

- Reads the `IntakeResult` and nothing else from prior agents.
- Inside the agent, a pure lookup by applicant id loads a local reference row (credit band, prior claims, property risk). That lookup is a tool the agent calls. It is not a store the other agents can see.
- Produces the intake it was given, the external row, and a short note about what the extra data changes.

`risk_scoring_agent(enrichment_result) -> RiskScoreResult`

- Reads the `EnrichmentResult` only.
- Produces a risk score from 0 to 1, the risk factors, a rationale, and the enrichment message it scored, so the score stays tied to the case that produced it.

`recommendation_agent(risk_result) -> RecommendationResult`

- Reads the `RiskScoreResult` only.
- Produces `approve`, `deny`, or `refer`, with a rationale. `refer` means a human underwriter should decide a borderline case. It is a normal recommendation, not an error path.

Each result object carries the message that produced it. The next agent does not reach backward into a store.

## Budgets, set before the build

These are the targets Part 4 will compare with measured traces. They are not the article's hypothetical $0.02 / $0.05 / $0.03 / $0.02 illustration.

Local Ollama has a marginal API cost of $0. Token counts are still recorded on every span. Dollar figures use this planning rate for a hosted 8B-class model, chosen so the same traces can be priced again later:

- $0.10 per 1,000,000 prompt tokens
- $0.40 per 1,000,000 completion tokens

Real-time budget: under 10 seconds per case, and under $0.05 per case at the planning rate. That is the bar for an interactive underwriting decision.

Overnight batch budget: under 180 seconds per case. Cost at the planning rate should stay under $0.05 as well. A case that misses the real-time latency bar and lands inside the batch bar is acceptable for overnight processing and is not acceptable for a real-time decision.

The four model calls run one after another. Risk scoring reads enrichment's output, so those two steps are not parallel.

## Failure policy, implemented only after the happy path

Part 5, not this step. If the risk-scoring model call raises a timeout, the pipeline retries a limited number of times with backoff. If the retries are exhausted, the case comes back `escalated` for a human, with the reason recorded, and with no risk score and no approve or deny. An escalated case must not look like a normal `refer`.
