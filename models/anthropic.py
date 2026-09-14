"""Anthropic Claude Model Provider for Multimodal Android Control.

Supports:
- claude-3-5-sonnet-20241022
- claude-3-5-haiku-20241022
- claude-3-opus-20240229
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

Do NOT output markdown or explanations. Output ONLY raw valid JSON.
"""

class AnthropicProvider(BaseModelProvider):
    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None):
        key = api_key or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_API_KEY")
        super().__init__(model_name, key)
        self.endpoint = "https://api.anthropic.com/v1/messages"

    def predict_action(
        self,
        goal: str,
        screen_state_text: str,
        screenshot_bytes: Optional[bytes] = None,
        history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is missing. Please set it in .env")

        prompt_text = f"Goal: {goal}\n\nCurrent UI State:\n{screen_state_text}\n\nWhat is the single next JSON action?"

        content_parts: List[Dict[str, Any]] = []
        if screenshot_bytes:
            b64_img = base64.b64encode(screenshot_bytes).decode("utf-8")
            content_parts.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": b64_img
                }
            })
        content_parts.append({"type": "text", "text": prompt_text})

        payload = {
            "model": self.model_name,
            "max_tokens": 1024,
            "system": SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": content_parts}
            ],
            "temperature": 0.1
        }

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=35) as resp:
            raw_resp = json.loads(resp.read().decode("utf-8"))

        text = ""
        for block in raw_resp.get("content", []):
            if block.get("type") == "text":
                text += block.get("text", "")

        return self._extract_json(text.strip())

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
            raise ValueError(f"Could not parse JSON action from Claude response: {text}")
