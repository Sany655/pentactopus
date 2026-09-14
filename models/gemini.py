"""Google Gemini Model Provider for Multimodal Android Control."""

import json
import os
import base64
import urllib.request
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

Do NOT output markdown or explanations. Output ONLY JSON.
"""

class GeminiProvider(BaseModelProvider):
    def __init__(self, model_name: str = "gemini-2.5-flash", api_key: Optional[str] = None):
        key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("API_KEY")
        super().__init__(model_name, key)

    def predict_action(
        self,
        goal: str,
        screen_state_text: str,
        screenshot_bytes: Optional[bytes] = None,
        history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        prompt = f"Goal: {goal}\n\nCurrent UI State:\n{screen_state_text}\n\nWhat is the single next JSON action?"

        parts = [{"text": prompt}]
        if screenshot_bytes:
            b64_img = base64.b64encode(screenshot_bytes).decode("utf-8")
            parts.append({
                "inline_data": {
                    "mime_type": "image/png",
                    "data": b64_img
                }
            })

        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        text_resp = data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text_resp)
