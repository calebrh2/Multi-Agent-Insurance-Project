"""Planning price from the state-and-memory design, applied to captured token counts.

Local Ollama bills nothing. These rates exist so a trace can still be priced.
"""

PROMPT_USD_PER_MILLION = 0.10
COMPLETION_USD_PER_MILLION = 0.40
REAL_TIME_MS = 10_000
BATCH_MS = 180_000
REAL_TIME_USD = 0.05


def planning_cost_usd(prompt_tokens: int, completion_tokens: int) -> float:
    """Price one case at the planning rate. The local API invoice is still zero."""
    return (
        prompt_tokens * PROMPT_USD_PER_MILLION
        + completion_tokens * COMPLETION_USD_PER_MILLION
    ) / 1_000_000
