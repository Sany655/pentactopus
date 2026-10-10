from __future__ import annotations

import json
import os
from typing import Any, Mapping
from urllib import request, error


class LocalModelClient:
    """Small BYOK client abstraction for local or cloud model calls.

    The Windows client keeps provider keys only on-device. For v1 we support a
    local-only mock default and an optional OpenAI-compatible provider when the
    user supplies credentials in the environment.
    """

    def __init__(
        self,
        provider: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.provider = (provider or os.getenv("WINDOWS_AGENT_MODEL_PROVIDER") or "mock").lower()
        self.api_key = api_key or os.getenv("MODEL_PROVIDER_API_KEY")
        self.model = model or os.getenv("MODEL_NAME") or "gpt-4o-mini"
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL") or os.getenv("MODEL_BASE_URL")

    def draft_message(self, prompt: str, *, system_prompt: str | None = None) -> str:
        if self.provider == "mock":
            return f"Draft: {prompt.strip()}"
        if self.provider in {"ollama", "local"}:
            return self._call_ollama(prompt, system_prompt=system_prompt)
        if not self.api_key:
            raise RuntimeError("A model provider API key is required when not using local-only mode.")
        return self._call_openai_compatible(prompt, system_prompt=system_prompt)

    def _call_ollama(self, prompt: str, *, system_prompt: str | None = None) -> str:
        if not self.base_url:
            return f"Local-only draft: {prompt.strip()}"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "system": system_prompt or "Respond as a concise drafting assistant.",
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.base_url.rstrip("/") + "/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=30) as response:
                body = json.loads(response.read().decode("utf-8"))
                return str(body.get("response") or body.get("content") or prompt)
        except error.URLError:
            return f"Local draft: {prompt.strip()}"

    def _call_openai_compatible(self, prompt: str, *, system_prompt: str | None = None) -> str:
        endpoint = (self.base_url or "https://api.openai.com/v1/chat/completions").rstrip("/")
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt or "Write a concise draft."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            endpoint,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with request.urlopen(req, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
            choices = body.get("choices") or []
            if not choices:
                raise RuntimeError("The model provider returned no choices.")
            message = choices[0].get("message") or {}
            return str(message.get("content") or prompt)
