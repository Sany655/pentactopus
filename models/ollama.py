"""Local Ollama Provider for on-premise, zero-cloud Android agent control."""

import json
import urllib.request
from typing import Dict, Any, Optional, List
from models.base import BaseModelProvider

class OllamaProvider(BaseModelProvider):
    def __init__(self, model_name: str = "llama3.2", host: str = "http://localhost:11434"):
        super().__init__(model_name, None)
        self.host = host

    def predict_action(
        self,
        goal: str,
        screen_state_text: str,
        screenshot_bytes: Optional[bytes] = None,
        history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        prompt = f"""You are an Android AI Agent.
Goal: {goal}
Current Screen Elements:
{screen_state_text}

Respond ONLY with a JSON action:
{{"action": "tap", "x": 100, "y": 200}} or {{"action": "launch_app", "package": "com.android.settings"}} or {{"action": "finish", "status": "success", "message": "done"}}
"""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }

        req = urllib.request.Request(
            f"{self.host}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        return json.loads(data.get("response", "{}"))
