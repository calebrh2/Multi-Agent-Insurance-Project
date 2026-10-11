State and Memory Management
Every agentic system you've built so far in this program handles a single request in isolation, receive input, reason, act, respond, done. This week moves into multi-agent orchestration, where multiple agents collaborate on a task, and the first thing that becomes critical is state and memory: what does each agent know, when, and how is that information shared or kept separate.

The Problem: Agents Need to Remember Things
An LLM, as covered back in Week 5, has no memory between separate calls by default, each call is stateless, it only knows what's in the context you send it. For a single-turn interaction, this is fine. But the moment you have a multi-step agent (as you built in Week 7), or multiple agents working together, you need a deliberate strategy for what information persists, where it lives, and who has access to it.

Short-Term (Working) Memory
Short-term memory, sometimes called working memory, is the information relevant to the current task or conversation, held only as long as needed to complete it.

Use Case 1: Your Week 7 equipment request agent. Within a single ReAct loop handling one equipment request, the agent needs to remember what it already looked up (the employee's role, the policy limits it already checked) as it reasons toward a decision. This is short-term memory, it exists only for the duration of that one request, and once the agent produces a final answer, that context can be discarded. If a new request comes in for a different employee, none of the previous request's details should leak into the new one.

python

# Short-term memory: scoped to one request, discarded after
def handle_request(request):
    context = []  # fresh, empty context for this request only
    while not done:
        context.append(next_observation)
    return final_decision
Long-Term (Persistent) Memory
Long-term memory is information that needs to persist across separate interactions, sometimes across days, weeks, or indefinitely, and be available to future requests, potentially from different users or sessions.

Use Case 2: A customer support agent that remembers prior interactions. If a customer contacts support about the same issue twice in a week, a well-designed system should be able to recall "this customer already reported this problem on Tuesday" rather than treating each interaction as if it's the first. This requires storing information (the customer's ID, the prior ticket, its resolution status) somewhere durable, a database, following the same structured data concepts from Week 6, not just in the temporary context of a single conversation.

Use Case 3: A multi-agent underwriting system tracking a case across days. An insurance underwriting workflow (the kind of scenario you'll build in this week's lab) might span multiple agents working on the same case over an extended period, one agent gathers applicant information today, another agent assesses risk tomorrow once additional documents arrive, and a third makes a final recommendation days later. Each of these agents needs access to what previous agents found, not by re-deriving it, but by reading it from a shared, persistent store. Without long-term memory, each agent would have to start from scratch, or worse, silently miss information a previous agent already gathered.

Shared State Across Multiple Agents
When multiple agents work on the same task, as you'll do in this week's multi-agent lab, a critical design decision is what state is shared between them, and how.

Two basic patterns:

Shared memory/state store. All agents read from and write to a common store (a database, a shared object), so any agent can see what others have already found or decided.

Message passing. Agents don't share a common store directly; instead, one agent's output becomes explicit input to the next agent in the pipeline, deliberately handed off rather than pulled from a shared pool.

Use Case 4: Comparing the two patterns for underwriting. In a shared-state approach, an "intake agent," a "risk assessment agent," and a "recommendation agent" might all read from and write to one shared case record: intake writes the applicant's basic info, risk assessment reads that and adds its risk score to the same record, recommendation reads the whole record and adds a final decision. In a message-passing approach, the intake agent's output is explicitly packaged and handed directly to the risk assessment agent as its input, and that agent's output is explicitly handed to the recommendation agent, no agent reads from a store it wasn't directly given access to. Shared state is often simpler to set up initially but riskier, since any agent can accidentally read or write something it shouldn't. Message passing enforces cleaner boundaries between agents' responsibilities, at the cost of more explicit plumbing between each handoff.

Why Memory Design Matters for Correctness, Not Just Convenience
Poor memory design causes real, specific failures:

Stale data. If an agent reads from a store that hasn't been updated yet by a step that should have run first, it makes a decision based on incomplete information.

Context bleed. If short-term memory isn't properly scoped, details from one user's request can leak into another's, a serious problem, especially for anything involving personal or sensitive data.

Unbounded growth. Long-term memory that accumulates indefinitely without any pruning or summarization eventually becomes too large to use effectively, echoing the context window constraints from Week 5.

Use Case 5: A context bleed bug. Imagine a poorly scoped agent implementation where the "context" list from Use Case 1 is accidentally created once, globally, rather than fresh per request. A second employee's equipment request would start with the first employee's data still sitting in context, potentially causing the agent to reference the wrong employee's tenure or equipment history when reasoning about the new request, a bug that would be easy to miss in testing with only one test case, but would show up immediately with concurrent or sequential real users.

Why This Matters for an FDE
Multi-agent systems for client engagements almost always require a deliberate decision about state and memory architecture, whether agents share a database, pass messages explicitly, or some combination. Getting this wrong doesn't just cause inefficiency, it causes real correctness bugs, like the context bleed in Use Case 5, that can be subtle and hard to catch without careful testing across multiple simulated users or cases.

Comprehension Check
Using Use Case 1 and Use Case 2, explain the difference between short-term and long-term memory in terms of how long each needs to persist.

In Use Case 4, what's the main tradeoff between a shared-state approach and a message-passing approach for a multi-agent system?

Using Use Case 5, describe how you would test for a context bleed bug before it reaches production.

