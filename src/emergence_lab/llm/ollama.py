"""Ollama HTTP client. Stdlib only; no inference cache."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class LlmResponse:
    text: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    model: str | None = None
    raw: dict[str, Any] | None = None


class LlmClient(Protocol):
    def complete(self, prompt: str) -> LlmResponse: ...


class FakeLlmClient:
    """Deterministic stand-in for tests. Never talks to the network."""

    def __init__(self, texts: str | list[str], model: str = "fake") -> None:
        self.texts = [texts] if isinstance(texts, str) else list(texts)
        self.model = model
        self.prompts: list[str] = []
        self.i = 0

    def complete(self, prompt: str) -> LlmResponse:
        self.prompts.append(prompt)
        text = self.texts[min(self.i, len(self.texts) - 1)]
        self.i += 1
        return LlmResponse(
            text=text,
            prompt_tokens=1,
            completion_tokens=1,
            model=self.model,
        )


class OllamaClient:
    def __init__(
        self,
        *,
        model: str,
        endpoint: str = "http://127.0.0.1:11434",
        temperature: float = 0.0,
        num_predict: int = 64,
        timeout_s: float = 120.0,
        think: bool = False,
    ) -> None:
        if not model:
            raise ValueError("llm model is empty; set --llm-model or config llm.model")
        self.model = model
        self.endpoint = endpoint.rstrip("/")
        self.temperature = temperature
        self.num_predict = num_predict
        self.timeout_s = timeout_s
        self.think = think

    def complete(self, prompt: str) -> LlmResponse:
        payload = self._payload(prompt, include_think=True)
        try:
            body = self._post(payload)
        except urllib.error.HTTPError as exc:
            if exc.code in {400, 422}:
                body = self._post(self._payload(prompt, include_think=False))
            else:
                raise RuntimeError(
                    f"Ollama request failed ({self.endpoint}, model={self.model}): {exc}"
                ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Ollama request failed ({self.endpoint}, model={self.model}): {exc}"
            ) from exc
        message = body.get("message") or {}
        text = str(message.get("content") or body.get("response") or "")
        thinking = message.get("thinking")
        if not text.strip() and thinking:
            text = str(thinking)
        return LlmResponse(
            text=text,
            prompt_tokens=_as_int(body.get("prompt_eval_count")),
            completion_tokens=_as_int(body.get("eval_count")),
            model=str(body.get("model") or self.model),
            raw=body if isinstance(body, dict) else None,
        )

    def _payload(self, prompt: str, *, include_think: bool) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.num_predict,
            },
        }
        if include_think:
            payload["think"] = self.think
        return payload

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.endpoint}/api/chat"
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout_s) as handle:
            return json.loads(handle.read().decode("utf-8"))


def _as_int(value: object) -> int | None:
    if value is None or value == "":
        return None
    return int(value)
