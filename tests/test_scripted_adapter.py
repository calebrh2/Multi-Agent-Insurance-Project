"""Tests for the scripted model adapter."""

import pytest

from underwriting.adapters.scripted import ScriptedAdapter


def test_scripted_adapter_returns_calls_in_order() -> None:
    """Each complete call consumes the next scripted completion."""
    adapter = ScriptedAdapter(
        ['{"a": 1}', '{"a": 2}'], prompt_tokens=3, completion_tokens=4
    )
    first = adapter.complete(system="sys", user="one", json_schema={"type": "object"})
    second = adapter.complete(system="sys", user="two", json_schema={"type": "object"})
    assert first.content == '{"a": 1}'
    assert first.tokens_used == 7
    assert second.content == '{"a": 2}'
    assert adapter.last_response == second
    assert [call["user"] for call in adapter.calls] == ["one", "two"]


def test_scripted_adapter_raises_when_empty() -> None:
    """A call with no remaining completions fails loudly."""
    adapter = ScriptedAdapter([])
    with pytest.raises(RuntimeError, match="no remaining"):
        adapter.complete(system="sys", user="one", json_schema={})
