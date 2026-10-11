"""Tests that versioned prompts load and contain few-shot examples."""

import pytest

from underwriting.prompts.loader import load_prompt


def test_intake_prompt_has_few_shot_examples() -> None:
    """The intake prompt is labeled and includes examples."""
    text = load_prompt("intake-v0.md")
    assert "<system>" in text
    assert "<examples>" in text
    assert text.count("<example>") >= 2


def test_missing_prompt_raises() -> None:
    """Asking for a prompt that is not on disk fails."""
    with pytest.raises(FileNotFoundError):
        load_prompt("missing-v0.md")
