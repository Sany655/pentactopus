"""OpenAI-Compatible Model Provider for Unified Multi-Model Execution.

Supports:
- OpenAI (gpt-4o, gpt-4o-mini, o3-mini)
- DeepSeek (deepseek-chat, deepseek-reasoner)
- Groq (llama-3.3-70b-versatile, mixtral-8x7b-32768)
- OpenRouter (openrouter/auto, google/gemini-2.5-flash, anthropic/claude-3.5-sonnet, etc.)
- Local vLLM / LM Studio / LocalAI
"""

import json
import os
import base64
import urllib.request
import re
from typing import Dict, Any, Optional, List
from models.base import BaseModelProvider

SYSTEM_PROMPT = """You are an autonomous Android Computer-Use Agent.
Your job is to accomplish the user's goal on an Android phone by issuing structured actions.
You are provided with:
1. The user's goal
2. A list of interactive UI elements with their center coordinates and text
3. Optionally a screenshot of the current screen.

You MUST respond ONLY with a valid JSON object describing the single next action to take.
Allowed actions:
- {"action": "tap", "x": 500, "y": 800}
- {"action": "type", "text": "search query"}
- {"action": "swipe", "x1": 500, "y1": 1500, "x2": 500, "y2": 500}
- {"action": "key_event", "key": "BACK" | "HOME" | "RECENTS"}
- {"action": "launch_app", "package": "com.android.settings"}
- {"action": "wait", "seconds": 2}
- {"action": "finish", "status": "success", "message": "Goal accomplished"}

Do NOT output markdown or conversational explanations. Output ONLY the raw JSON object.
"""

ENDPOINT_MAP = {
    "openai": "https://api.openai.com/v1/chat/completions",
    "deepseek": "https://api.deepseek.com/chat/completions",
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
}

ENV_KEY_MAP = {
    "openai": "OPENAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "groq": "GROQ_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}

DEFAULT_MODEL_MAP = {
    "openai": "gpt-4o-mini",
    "deepseek": "deepseek-chat",
    "groq": "llama-3.3-70b-versatile",
    "openrouter": "google/gemini-2.5-flash",
}

class OpenAICompatibleProvider(BaseModelProvider):
    def __init__(
        self,
        flavor: str = "openai",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.flavor = flavor.lower()
        self.endpoint = base_url or ENDPOINT_MAP.get(self.flavor, "https://api.openai.com/v1/chat/completions")
        
        env_var = ENV_KEY_MAP.get(self.flavor, f"{self.flavor.upper()}_API_KEY")
        key = api_key or os.environ.get(env_var) or os.environ.get(f"{self.flavor.upper()}_KEY")
        chosen_model = model_name or DEFAULT_MODEL_MAP.get(self.flavor, "gpt-4o-mini")
        
        super().__init__(chosen_model, key)

    def predict_action(
        self,
        goal: str,
        screen_state_text: str,
        screenshot_bytes: Optional[bytes] = None,
        history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError(f"API key for '{self.flavor}' is missing. Set {ENV_KEY_MAP.get(self.flavor, 'API key')} in .env")

        prompt_text = f"Goal: {goal}\n\nCurrent UI State:\n{screen_state_text}\n\nWhat is the single next JSON action?"

        content_parts: List[Dict[str, Any]] = [{"type": "text", "text": prompt_text}]
        if screenshot_bytes:
            b64_img = base64.b64encode(screenshot_bytes).decode("utf-8")
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64_img}"}
            })

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content_parts}
        ]

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.1
        }

        # Some providers support response_format json_object
        if self.flavor in ("openai", "groq", "deepseek", "openrouter"):
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        if self.flavor == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/ai-android-agent"
            headers["X-Title"] = "AI Android Agent Command Hub"

        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=35) as resp:
            raw_resp = json.loads(resp.read().decode("utf-8"))

        text = raw_resp["choices"][0]["message"]["content"].strip()
        return self._extract_json(text)

    def _extract_json(self, text: str) -> Dict[str, Any]:
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text, flags=re.MULTILINE)
            text = re.sub(r"\n?```$", "", text, flags=re.MULTILINE)
        try:
            return json.loads(text.strip())
        except Exception:
            m = re.search(r"\{.*\}", text, re.DOTALL)
            if m:
                return json.loads(m.group(0))
            raise ValueError(f"Could not parse JSON action from {self.flavor} response: {text}")
