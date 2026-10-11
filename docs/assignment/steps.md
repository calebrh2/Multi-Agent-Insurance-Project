What You'll Do
Part 1: Design Your State and Memory Approach

Document your choice: shared state store or message passing, and why. Define what data each agent needs to read and what it produces.

Part 2: Build Each Agent as a Standalone Function

Implement intake_agent, enrichment_agent, risk_scoring_agent, and recommendation_agent as individually testable functions, each using an LLM call for its reasoning step. Write a unit test for each agent using a hardcoded, known input, confirming it produces reasonable output before connecting anything.

Part 3: Connect the Pipeline with Tracing

Wire the four agents together using your chosen state-sharing pattern. Add tracing that logs, for each agent: what it received, what it produced, duration, and token usage. Run at least 3 different mock applications through the full pipeline and capture their complete traces.

Part 4: Cost and Latency Budgeting

Using your captured traces, calculate the actual cost and total latency per case. State whether this would be acceptable for a real-time use case versus an overnight batch use case, and explain your reasoning.

Part 5: Simulate and Handle a Failure

Deliberately introduce a failure in one agent (e.g., make the risk scoring agent's underlying call raise a timeout exception on a specific test case). Implement handling for it, following the retry-then-escalate pattern from this week's integration article, and confirm your system behaves correctly: it should not crash, and it should either recover or clearly flag the case for human review rather than silently producing an incomplete or wrong recommendation.

Part 6: Pipeline

Push all agent code, tests, and tracing through your CI pipeline.