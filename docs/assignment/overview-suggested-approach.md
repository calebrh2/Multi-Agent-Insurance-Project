Lab: Build a Multi-Agent Underwriting Pipeline
Overview
This week you'll build a multi-agent system from scratch: an insurance underwriting pipeline where separate agents handle intake, enrichment, risk scoring, and a final recommendation. You'll apply everything from this week, state/memory management, observability and tracing, and integration patterns with deliberate failure handling. No starter files, datasets, or containers are provided.

If you want a deeper reference on multi-agent design patterns beyond what the lesson covered, Anthropic's engineering guide "Building Effective Agents" https://www.anthropic.com/engineering/building-effective-agents covers exactly this material, when to use a fixed workflow versus a dynamic agent, and patterns like prompt chaining, routing, and parallelization, worth reading before you commit to an architecture. As always, ask Claude directly if you want help understanding a pattern or working through how it applies to your specific design.

The Scenario
An applicant submits an insurance application. Your pipeline needs to: capture their basic information (intake), gather any additional relevant data (enrichment), calculate a risk score (risk scoring), and produce a final recommendation (approve, deny, or refer to a human underwriter).

If you're unsure how a tool or concept works beyond what the lesson covered, ask Claude (in a regular conversation, separate from your script) to explain it, or to help you research an unfamiliar library, technique, or error message before you implement it.

Suggested Approach (Read This Before Starting)
Multi-agent systems fail most often because people try to build all the agents and their coordination at once. Build up in stages instead:

Build and test each agent as a standalone function first, completely separate from any orchestration. Write intake_agent(raw_application), test it in isolation with a hardcoded input, and confirm it produces reasonable output before it ever needs to talk to another agent.
Decide your state-sharing pattern before writing orchestration code. Following this week's article, choose either a shared state store (a simple dictionary or a local file/database representing "the case record," which each agent reads from and writes to) or explicit message passing (each agent's output becomes the next agent's input directly, no shared store). Write this decision down before coding it, it should be a deliberate choice, not something that emerges by accident.
Connect two agents first, not all four. Get intake successfully handing off to enrichment, confirm the handoff works correctly and enrichment receives what it needs, before adding risk scoring and recommendation on top.
Add tracing from the start, not as an afterthought. Once you have two agents connected, add a simple logging structure (following this week's trace format) that records what each agent did, when, and how long it took. Confirm you can see a clear trace before adding more agents, it's much easier to build this habit early than to retrofit it once four agents are already interacting.
Add the remaining two agents one at a time, using the same pattern: connect, confirm the trace shows the handoff correctly, then move to the next.
Add failure handling last, once the full four-agent pipeline works correctly on a normal case. Then deliberately introduce a failure (simulate a timeout or bad response from one agent) and confirm your handling behaves as intended.
