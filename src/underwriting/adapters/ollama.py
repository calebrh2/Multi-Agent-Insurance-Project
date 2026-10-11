"""Ollama chat adapter. The default model is qwen3:8b on the host machine."""

import json
import os
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

from underwriting.adapters.base import ModelResponse

DEFAULT_HOST = "http://host.docker.internal:11434"
DEFAULT_MODEL = "qwen3:8b"
Opener = Callable[..., Any]


class OllamaAdapter:
    """Call a local Ollama model through its HTTP chat API."""

    def __init__(
        self,
        *,
        host: str | None = None,
        model: str | None = None,
        timeout_seconds: float = 180,
        opener: Opener | None = None,
    ) -> None:
        """Point the adapter at Ollama. Host and model fall back to the environment."""
        configured_host = host if host is not None else os.environ.get("OLLAMA_HOST")
        configured_model = (
            model if model is not None else os.environ.get("OLLAMA_MODEL")
        )
        self.host = (configured_host or DEFAULT_HOST).rstrip("/")
        self.model = configured_model or DEFAULT_MODEL
        self.timeout_seconds = timeout_seconds
        self._opener = opener or urllib.request.urlopen
        self.last_response: ModelResponse | None = None

    def complete(
        self,
        *,
        system: str,
        user: str,
        json_schema: dict[str, Any],
    ) -> ModelResponse:
        """POST one chat request and map an HTTP timeout to TimeoutError."""
        payload = {
            "model": self.model,
            "stream": False,
            "think": False,
            "format": json_schema,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        request = urllib.request.Request(
            f"{self.host}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self._opener(request, timeout=self.timeout_seconds) as response:
                raw = response.read()
        except TimeoutError as exc:
            raise TimeoutError("ollama chat timed out") from exc
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, TimeoutError):
                raise TimeoutError("ollama chat timed out") from exc
            raise
        body = json.loads(raw.decode("utf-8"))
        result = ModelResponse(
            content=body["message"]["content"],
            prompt_tokens=int(body.get("prompt_eval_count") or 0),
            completion_tokens=int(body.get("eval_count") or 0),
        )
        self.last_response = result
        return result
