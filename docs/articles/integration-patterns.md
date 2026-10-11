Integration Patterns: APIs, Webhooks, Queues, and Event-Driven Flows
You now understand how agents manage state and how to observe what they're doing. This article covers the actual mechanisms agents use to connect to enterprise systems, the systems client engagements are built around, and, critically, how to handle it when those connections fail, because in a multi-agent system, failures don't just affect one request, they can cascade.

APIs: Direct, Synchronous Calls
An API call is the most direct integration pattern: your agent (or the tool it calls, as covered in Week 7) sends a request to another system and waits for a response before continuing.

Use Case 1: The risk scoring agent calling a credit check API. In this week's underwriting pipeline, the risk scoring agent needs current credit information for an applicant. It calls a credit bureau's API directly, sends the applicant's details, and waits for the response before it can proceed to calculate a risk score. This is synchronous: the agent's work is blocked until that API responds.

The tradeoff: APIs are simple to reason about, request goes out, response comes back, but the calling agent is stuck waiting the entire time, and if the API is slow or down, that delay (or failure) propagates directly into your pipeline's latency and reliability, exactly the kind of bottleneck you'd catch through tracing, as covered in the last article.

Webhooks: Systems Notifying You
A webhook flips the direction: instead of your system asking another system for information, the other system calls you, automatically, when something relevant happens on its end.

Use Case 2: A document upload triggering the enrichment agent. In the underwriting scenario, an applicant might upload additional documents (proof of income, an inspection report) after their initial application. Rather than having your enrichment agent repeatedly poll "has anything new arrived?" every few minutes, wasting calls checking for nothing, the document management system sends a webhook, an automatic notification, to your system the moment a new document is uploaded. That webhook triggers the enrichment agent to run, exactly when it actually has new work to do, rather than on a fixed guess-and-check schedule.

Why this matters: webhooks are more efficient than polling, and they let a multi-agent system react to real-world events (a document arriving, a payment clearing, an external status changing) as they happen, rather than only when an agent happens to check.

Queues: Decoupling and Buffering
A queue sits between systems, holding messages or tasks until whatever's supposed to process them is ready. Instead of one system calling another directly, it drops a message onto a queue, and a separate process picks it up when it can.

Use Case 3: Buffering incoming applications during a volume spike. Imagine 500 new underwriting applications arrive at once, more than the risk scoring agent can process immediately if it's calling external APIs sequentially. Rather than the intake agent trying to call the risk scoring agent directly for all 500 at once (likely overwhelming it, or the external credit API, causing failures), each completed intake gets placed onto a queue. The risk scoring agent pulls cases off that queue at whatever rate it can actually sustain, processing all 500 eventually, reliably, without either side needing to know or care about the other's current load.

Why this matters: queues decouple the pace of one part of a system from another. The intake agent doesn't need to slow down just because risk scoring is backed up, and risk scoring doesn't crash under a burst of simultaneous requests, it just works through the queue at a sustainable pace.

Event-Driven Flows: Composing All Three
An event-driven architecture combines these patterns: instead of a fixed, hardcoded sequence (as in a workflow from Week 7), each component reacts to events, and produces its own events for the next component to react to.

Use Case 4: The full underwriting pipeline as an event-driven flow. Intake completes and emits an "application received" event. This lands on a queue. The enrichment agent, watching that queue, picks it up, does its work, and emits an "enrichment complete" event. Risk scoring watches for that event, picks it up when it appears, does its work, and emits a "risk assessed" event. Recommendation watches for that, and produces the final output. No component calls another directly, each just reacts to the events relevant to it. This is a direct evolution of the message-passing memory pattern from the last article, formalized around events and queues rather than direct handoffs.

Handling Failure in These Patterns
This is where these integration patterns matter most in practice, because enterprise systems fail: APIs time out, webhooks get missed, queues can back up.

Use Case 5: The credit check API times out. Back in Use Case 1, if the credit bureau's API doesn't respond within a reasonable time, the risk scoring agent needs a defined behavior, not just an unhandled crash. Following the error-handling discipline from Week 3, a well-built agent should catch this specific failure, retry a limited number of times (with backoff, waiting a bit longer between each retry rather than hammering a struggling API), and if it still fails, escalate the case for manual review rather than either blocking indefinitely or guessing at a risk score without real data.

Use Case 6: A webhook that never arrives. In Use Case 2, what if the document management system's webhook delivery itself fails silently, an infrastructure issue on their end, and your enrichment agent never gets notified a new document arrived? A resilient system doesn't rely purely on webhooks arriving reliably. A common mitigation is a periodic reconciliation check, occasionally polling for anything that should have triggered a webhook but didn't, as a safety net, catching gaps that pure event-driven reliance would otherwise miss silently.

Use Case 7: A queue backing up faster than it's being processed. If applications keep arriving faster than the risk scoring agent can pull them off the queue (Use Case 3), the queue simply grows, and cases start waiting significantly longer than expected without an obvious "error" occurring anywhere, this is a form of failure that doesn't crash anything but quietly breaks the client's expectations. Monitoring queue depth (following the observability discipline from the last article) and having a defined threshold for "this needs attention" is how you catch this before a client asks why their applications are taking two days to process instead of two hours.

Why This Matters for an FDE
Client environments are built almost entirely on these integration patterns already, and your agentic systems need to connect into that existing infrastructure, not replace it. Recognizing which pattern fits a given need (a direct API call for something you need an immediate answer to, a queue for buffering variable load, an event-driven flow for a genuinely multi-step, multi-system process) and building deliberate failure handling around each, is what separates a demo that works once from a system that survives real-world conditions.

Comprehension Check
Using Use Cases 1 and 2, explain why a webhook is more efficient than an API call for detecting a new document upload.

In Use Case 3, what problem does the queue solve that a direct call from intake to risk scoring wouldn't?

Using Use Cases 5-7, describe the different failure mode each integration pattern is vulnerable to, and how each is mitigated.