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

PC_SYSTEM_PROMPT = """You are an autonomous Windows PC Desktop Computer-Use Agent.
Your job is to accomplish the user's goal on the Windows PC by issuing structured actions.
You are provided with:
1. The user's goal
2. Current screen resolution
3. Optionally a screenshot of the current Windows Desktop.

You MUST respond ONLY with a valid JSON object describing the single next action to take.
Allowed actions:
- {"action": "click", "x": 683, "y": 384}
- {"action": "double_click", "x": 100, "y": 200}
- {"action": "right_click", "x": 500, "y": 400}
- {"action": "type", "text": "notepad"}
- {"action": "hotkey", "key": "ENTER" | "ESC" | "WIN_D" | "TAB" | "SPACE" | "VOL_UP" | "VOL_DOWN" | "MUTE" | "PLAY_PAUSE"}
- {"action": "launch_app", "app": "chrome" | "notepad" | "calc" | "explorer" | "terminal"}
- {"action": "open_url", "url": "https://example.com"}
- {"action": "wait", "seconds": 2}
- {"action": "finish", "status": "success", "message": "Goal accomplished on PC"}

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

        # Dynamically determine platform prompt: PC Desktop vs Android Mobile
        is_pc = any(k in goal.lower() or k in screen_state_text.lower() for k in ["[pc", "windows", "desktop", "pc agent"])
        sys_prompt = PC_SYSTEM_PROMPT if is_pc else SYSTEM_PROMPT

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        prompt = f"Goal: {goal}\n\nCurrent UI State:\n{screen_state_text}\n\nWhat is the single next JSON action?"

        parts = [{"text": prompt}]
        if screenshot_bytes:
            b64_img = base64.b64encode(screenshot_bytes).decode("utf-8")
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg" if is_pc else "image/png",
                    "data": b64_img
                }
            })

        payload = {
            "system_instruction": {"parts": [{"text": sys_prompt}]},
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Pentactopus/2.5.7"
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                body = e.read().decode("utf-8")
                err_data = json.loads(body)
                err_msg = (
                    err_data.get("error", {}).get("message")
                    or err_data.get("message")
                    or body
                )
                raise ValueError(f"Gemini API Error ({e.code}): {err_msg}")
            except Exception as parse_err:
                if isinstance(parse_err, ValueError):
                    raise parse_err
                raise ValueError(f"Gemini HTTP Error {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise ValueError(f"Failed to connect to Google Gemini: {e.reason}")

        try:
            text_resp = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text_resp)
        except Exception as e:
            raise ValueError(f"Invalid response from Gemini API: {data.get('promptFeedback', data)}")

