"""Tests for pulling JSON out of model completions."""

from underwriting.parsing import extract_json_object


def test_extracts_plain_object() -> None:
    """A bare JSON object is returned unchanged."""
    assert extract_json_object('{"ok": true}') == '{"ok": true}'


def test_strips_think_tags_and_fences() -> None:
    """Think tags and markdown fences are ignored."""
    content = '<think>draft</think>\n```json\n{"ok": 1}\n```'
    assert extract_json_object(content) == '{"ok": 1}'


def test_returns_text_when_no_object_is_present() -> None:
    """Text with no braces is returned stripped."""
    assert extract_json_object("  not json  ") == "not json"
