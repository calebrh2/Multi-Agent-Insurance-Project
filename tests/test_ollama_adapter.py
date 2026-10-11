"""Tests for the Ollama adapter using a stand-in HTTP opener."""

import json
import urllib.error
import urllib.request
from typing import Self

import pytest

from underwriting.adapters.ollama import DEFAULT_HOST, DEFAULT_MODEL, OllamaAdapter


class _Body:
    """Minimal response object that urlopen's context manager would return."""

    def __init__(self, payload: dict[str, object]) -> None:
        self._raw = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        """Return the canned HTTP body."""
        return self._raw

    def __enter__(self) -> Self:
        """Enter the context manager."""
        return self

    def __exit__(self, *_args: object) -> bool:
        """Leave the context manager without swallowing exceptions."""
        return False


def test_ollama_adapter_reads_content_and_token_counts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A successful chat response becomes a ModelResponse."""
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    seen: dict[str, object] = {}

    def opener(request: urllib.request.Request, timeout: float) -> _Body:
        seen["timeout"] = timeout
        raw = request.data
        assert isinstance(raw, bytes)
        seen["body"] = json.loads(raw.decode("utf-8"))
        return _Body(
            {
                "message": {"content": '{"product": "home"}'},
                "prompt_eval_count": 20,
                "eval_count": 5,
            }
        )

    adapter = OllamaAdapter(opener=opener, timeout_seconds=12)
    response = adapter.complete(
        system="sys", user="applicant", json_schema={"type": "object"}
    )
    assert response.content == '{"product": "home"}'
    assert response.tokens_used == 25
    assert adapter.last_response == response
    assert adapter.host == DEFAULT_HOST.rstrip("/")
    assert adapter.model == DEFAULT_MODEL
    assert seen["timeout"] == 12
    body = seen["body"]
    assert isinstance(body, dict)
    assert body["think"] is False
    assert body["model"] == DEFAULT_MODEL


def test_ollama_adapter_reads_host_and_model_from_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """OLLAMA_HOST and OLLAMA_MODEL fill in when arguments are omitted."""
    monkeypatch.setenv("OLLAMA_HOST", "http://env.test")
    monkeypatch.setenv("OLLAMA_MODEL", "from-env:8b")

    def opener(request: urllib.request.Request, timeout: float) -> _Body:
        return _Body({"message": {"content": "{}"}})

    adapter = OllamaAdapter(opener=opener)
    adapter.complete(system="s", user="u", json_schema={})
    assert adapter.host == "http://env.test"
    assert adapter.model == "from-env:8b"


def test_ollama_adapter_uses_host_and_model_arguments() -> None:
    """Explicit host and model override the defaults."""

    def opener(request: urllib.request.Request, timeout: float) -> _Body:
        return _Body({"message": {"content": "{}"}})

    adapter = OllamaAdapter(
        host="http://example.test/", model="other:1b", opener=opener
    )
    adapter.complete(system="s", user="u", json_schema={})
    assert adapter.host == "http://example.test"
    assert adapter.model == "other:1b"


def test_ollama_timeout_is_reraised() -> None:
    """A socket timeout becomes TimeoutError."""

    def opener(request: urllib.request.Request, timeout: float) -> _Body:
        raise TimeoutError("slow")

    adapter = OllamaAdapter(opener=opener)
    with pytest.raises(TimeoutError, match="ollama chat timed out"):
        adapter.complete(system="s", user="u", json_schema={})


def test_ollama_urlerror_timeout_is_reraised() -> None:
    """A URLError whose reason is a timeout becomes TimeoutError."""

    def opener(request: urllib.request.Request, timeout: float) -> _Body:
        raise urllib.error.URLError(TimeoutError("slow"))

    adapter = OllamaAdapter(opener=opener)
    with pytest.raises(TimeoutError, match="ollama chat timed out"):
        adapter.complete(system="s", user="u", json_schema={})


def test_ollama_other_urlerror_propagates() -> None:
    """A non-timeout URLError is not swallowed."""

    def opener(request: urllib.request.Request, timeout: float) -> _Body:
        raise urllib.error.URLError("refused")

    adapter = OllamaAdapter(opener=opener)
    with pytest.raises(urllib.error.URLError, match="refused"):
        adapter.complete(system="s", user="u", json_schema={})
