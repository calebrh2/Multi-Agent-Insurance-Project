Deliverable
Submit a single PDF containing screenshots, in order, of:

Your state/memory design decision and rationale
Each agent's standalone unit test, and terminal output showing them passing
Your full pipeline code, including the state-sharing/message-passing mechanism
Your tracing implementation
Full traces for 3 different mock applications run through the complete pipeline
Your cost/latency calculation and written analysis (real-time vs. batch suitability)
Your simulated failure, the handling code, and terminal output showing the system responding correctly (retry, then escalate, not crash)
A passing pipeline run


Rubric (100 points)
Criteria	Points
State/memory approach is clearly designed and justified before implementation	8
All four agents implemented and individually unit tested	15
Pipeline correctly connects all four agents using the chosen state pattern	15
Tracing captures agent, input/output, duration, and token usage for each step	15
Traces are captured and legible for all 3 test applications	8
Cost/latency analysis is accurate and draws a specific, justified conclusion	12
Simulated failure is handled correctly (retry then escalate, no crash, no silent wrong answer)	17
Submitted and passing through the pipeline	10
Total	100
