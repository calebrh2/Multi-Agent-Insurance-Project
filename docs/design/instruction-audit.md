# Instruction audit

This note was written before any underwriting code. It records a check of the assignment, the three articles, the workspace rules, and the git history for misleading guidance, contradictions, and hidden instructions. The numbered parts and the rubric are the spec. The articles explain the ideas and are not extra requirements.

## What was checked

- The six source documents under `docs/articles/` and `docs/assignment/`, plus their XML copies under `docs/llm/`.
- The three workspace rules under `.cursor/rules/`.
- Git history (`environment setup`, `gitignore`, `changing safe directory to fix git ownership check issue`) and the file list in the repo.
- Hidden payloads: null bytes, zero-width and bidi characters, HTML comments, long base64-like tokens, and odd filenames.
- Acrostics from headings and from the first letter of each prose line.

## Hidden content

No hidden payload turned up. The only non-ASCII characters are a normal em dash and a right arrow in the observability article (and the same characters in its XML copy), plus an arrow used as an example in the coding-style rule. First letters of the prose lines do not spell a word. There is no starter dataset, no secret file, and no instruction buried in git history.

## Findings that would mislead an implementation

The observability article's underwriting trace says a trace should show what an agent read from shared state and what it wrote. Part 3 of the assignment says to log what each agent received, what it produced, the duration, and the token usage. This project uses message passing, so each trace span records the message that agent received and the message it produced. A shared case store is not added just to match the article's wording.

The same article's prices ($0.02 intake, $0.05 enrichment, $0.03 risk scoring, $0.02 recommendation, $0.12 per case, $1,200 per month) are a hypothetical illustration. Part 4 has to be calculated from the captured traces.

That article also asks whether risk scoring could run beside enrichment. In this lab the risk-scoring agent reads the enrichment result, so the four agents stay in sequence.

The integration article's credit API, webhook, queue, and event-driven use cases are illustrations of enterprise patterns. The assignment's failure step points at one of them: retry a limited number of times with backoff, then escalate, and do not invent a risk score. Missed-webhook reconciliation and queue-depth alerts are not rubric items, so they are not built.

Comprehension checks, the sentences that say to ask Claude, the Week 7 equipment-request agent, and the Anthropic engineering guide are context. They are not deliverables. The pipeline is a fixed workflow, not a ReAct loop and not a dynamic router.

`refer` is a legitimate recommendation for a borderline application. A timeout must not come back as an ordinary `refer` with a filled-in score. That would be a silent wrong answer. The failure path returns an explicit escalated status, with no score and no approve or deny.

Part 6 is titled "Pipeline" and says to push the code, tests, and tracing through a CI pipeline. The rubric's last criterion is "Submitted and passing through the pipeline." Everywhere else, "pipeline" means the four agents. The last criterion is the CI run, not another agent stage.

The assignment never mentions git commit order. The ordered proof is the deliverable list of screenshots. Commits in this repo follow the suggested build order so each step is in history before the next one starts.

The prompting rule says to put prompts in `src/equipment_request/prompts/`. That path matches the Week 7 examples in the articles and does not appear in the assignment. Prompts for this lab live under `src/underwriting/prompts/` with the same versioning (`name-v0`), XML labels, and few-shot examples the rule asks for.

Local Ollama has no API invoice. Every trace still records token usage, because the rubric grades that field.

## Order the spec actually requires

The suggested approach and Parts 1–6 agree when read together:

1. Write the state decision before orchestration code.
2. Test each agent alone.
3. Connect intake to enrichment before the other two agents.
4. Add tracing once those two agents work.
5. Add risk scoring, then recommendation.
6. Add failure handling only after a clean four-agent run.

Nothing in the audit changes that sequence or the message-passing choice.
