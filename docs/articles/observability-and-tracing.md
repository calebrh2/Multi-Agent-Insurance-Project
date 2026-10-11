Observability and Tracing; Cost and Latency Budgeting
Last article covered how agents manage state and memory. This article covers how you, as the engineer, actually see what a multi-agent system is doing while it runs, and how you plan for its cost and speed before it surprises you in production.

Why Observability Matters More for Agentic Systems
You've been debugging deterministic code since Week 1: a bug has a specific line, a specific cause, and running the same input twice gives the same result. Multi-agent systems break this assumption in two ways: multiple agents interacting means a failure could originate in any one of them, or in how they handed off information to each other, and the sampling variability from Week 5 means the same input might not reproduce the same failure on a second run.

Observability is the practice of instrumenting your system so you can see what actually happened, after the fact, without having to reproduce the failure live. Tracing specifically means capturing a structured, step-by-step record of a request's full journey, every agent it touched, every tool it called, every decision it made, in order.

What a Trace Actually Looks Like
Use Case 1: Tracing your Week 7 equipment request agent. Recall the ReAct trace from Week 7, Thought, Action, Observation. That's already a form of tracing, a plain-text record of the agent's reasoning path. A production observability setup formalizes this: instead of just printing it to a terminal, each step gets logged with a timestamp, which agent or component produced it, how long it took, and what it cost (if it involved a model call). If a specific equipment request got denied incorrectly, you could pull up its full trace and see exactly which tool call returned what, and which reasoning step led to the wrong conclusion, rather than trying to guess or re-run the request and hope it fails the same way again.

Use Case 2: Tracing a multi-agent underwriting case. In this week's lab scenario (intake → enrichment → risk scoring → recommendation), a trace for one applicant's case should show: which agent ran, when, what it read from shared state, what it wrote, how long it took, and what it cost. If the final recommendation seems wrong, tracing lets you pinpoint whether the intake agent captured bad data, the enrichment step failed to add something it should have, or the risk scoring agent misapplied its logic, rather than treating the whole pipeline as one opaque black box that produced a wrong answer.

What to Actually Log
A useful trace, at minimum, captures for each step:

Which agent or component executed this step

What input it received (and, where relevant, where that input came from, another agent, a tool call, user input)

What output or decision it produced

Timestamp and duration (this feeds directly into latency budgeting, covered below)

Token usage and cost, if the step involved a model call (this feeds into cost budgeting)

Any errors or retries that occurred

python

# Conceptual example of a trace entry
{
    "step": "risk_assessment",
    "agent": "risk_scoring_agent",
    "input": {"applicant_id": "APP-2291", "intake_data": {...}},
    "output": {"risk_score": 0.72, "risk_factors": ["prior_claim", "high_value_asset"]},
    "duration_ms": 1840,
    "tokens_used": 612,
    "timestamp": "2024-06-01T14:22:03Z"
}
Cost Budgeting
Recall from Week 5 that every model call costs money, proportional to tokens processed, and multi-agent systems multiply this concern: if a single request now involves four separate agents, each potentially making one or more model calls, the total cost per request can grow quickly if it isn't deliberately tracked and bounded.

Use Case 3: Budgeting the underwriting pipeline. Suppose your intake agent costs roughly $0.02 per case, enrichment $0.05 (it may need to search external context), risk scoring $0.03, and recommendation $0.02, for a total of about $0.12 per case in model costs alone. If this pipeline processes 10,000 applications a month, that's $1,200 in model costs, a real, plannable number, but one that only becomes visible if you're actually tracking cost per agent, per case, rather than only seeing an aggregate bill at the end of the month with no way to attribute it to a specific step.

A practical habit: set an expected cost budget per request before building the system, based on estimated token usage per step, and monitor actual costs against that budget once it's running, so a regression (a prompt that grew too long, a step that started retrying unnecessarily) gets caught quickly rather than silently inflating your bill.

Latency Budgeting
The same discipline applies to speed. A multi-agent system where each agent calls a model sequentially accumulates latency: if each of the four underwriting agents takes 2 seconds, the whole pipeline takes at least 8 seconds, before accounting for any tool calls, retries, or the agent needing multiple reasoning steps internally (as in a ReAct loop).

Use Case 4: Identifying a latency bottleneck through tracing. Suppose the underwriting pipeline is taking 25 seconds per case, well beyond what's acceptable for the use case. Without tracing, you're guessing which of the four agents is slow. With tracing capturing duration_ms for each step, you can see directly that the enrichment agent alone is taking 18 of those 25 seconds, likely because it's making an external call to check additional data sources. That's a concrete, actionable finding, optimize or parallelize that one step, rather than guessing at the whole pipeline.

A useful design question: do these steps genuinely need to run sequentially, or could some run in parallel? If risk scoring doesn't actually depend on enrichment's specific output for every case, running them concurrently rather than one after another could cut meaningful time off the total.

Setting Budgets Before You Build
The same way you defined requirements before writing code back in Week 2, defining a cost and latency budget before building a multi-agent system gives you a concrete target to design against, rather than discovering after the fact that the system is too slow or too expensive for its actual use case. A system used for a real-time customer-facing chat has a very different acceptable latency than one processing overnight batch underwriting cases, and that difference should shape your architecture decisions from the start, not get discovered as a problem later.

Why This Matters for an FDE
Client engagements will hold you accountable to both correctness and performance. When a multi-agent system a client is paying for turns out to be slow or expensive in production, "let me check the traces" is a far stronger position than "let me try to reproduce it," and having cost and latency budgets defined up front, as in Use Case 3, lets you catch regressions before a client notices them in their bill or their users' complaints.

Comprehension Check
Using Use Case 2, explain why tracing helps pinpoint the source of a wrong final recommendation in a multi-agent pipeline, compared to treating the pipeline as one black box.

Walk through Use Case 3's cost calculation and explain why tracking cost per agent, not just total cost, matters.

In Use Case 4, what specific piece of trace data let you identify the bottleneck, and what are two ways you might address it once found?

Next up: "Integration patterns: APIs, webhooks, queues, event-driven flows — taught in the context of agents calling enterprise systems and handling failure." Ready when you are.