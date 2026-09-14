"""Deterministic Mock Model Provider for testing, dry-runs, and offline CI."""

import re
from typing import Dict, Any, Optional, List
from models.base import BaseModelProvider

class MockModelProvider(BaseModelProvider):
    def __init__(self, model_name: str = "mock-v1", api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
        self.call_count = 0

    def predict_action(
        self,
        goal: str,
        screen_state_text: str,
        screenshot_bytes: Optional[bytes] = None,
        history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        self.call_count += 1
        goal_lower = goal.lower()

        # Step 1: Handle "Open Settings"
        if "settings" in goal_lower:
            if self.call_count == 1:
                return {
                    "action": "launch_app",
                    "package": "com.android.settings"
                }
            else:
                return {
                    "action": "finish",
                    "status": "success",
                    "message": "Android Settings successfully opened and verified."
                }

        # Step 2: Handle "Open Calculator"
        if "calculator" in goal_lower:
            if self.call_count == 1:
                return {
                    "action": "launch_app",
                    "package": "com.google.android.calculator"
                }
            else:
                return {
                    "action": "finish",
                    "status": "success",
                    "message": "Calculator successfully opened."
                }

        # Default fallback
        return {
            "action": "finish",
            "status": "success",
            "message": f"Completed mock goal: {goal}"
        }
