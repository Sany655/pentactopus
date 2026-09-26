"""Autonomous Computer-Use AI Agent for Windows PC.

Perceives the Windows Desktop screen, reasons via Unified Multi-Model Gateway,
and executes mouse clicks, keystrokes, application launches, and system actions.
"""

import time
import json
import logging
from typing import Dict, Any, Optional, List
from pc_control.desktop_controller import DesktopController
from models.router import get_model_provider
from models.base import BaseModelProvider
from vision.screen_analyzer import ScreenAnalyzer

logger = logging.getLogger("pc_agent")

PC_SYSTEM_PROMPT = """You are an autonomous Windows PC Desktop Computer-Use Agent.
Your job is to accomplish the user's goal on the Windows PC by issuing structured actions.
You are provided with:
1. The user's goal
2. Current screen resolution
3. Optionally a screenshot of the current Windows Desktop

You MUST respond ONLY with a valid JSON object describing the single next action to take.
Allowed actions:
- {"action": "click", "x": 683, "y": 384}
- {"action": "double_click", "x": 100, "y": 200}
- {"action": "right_click", "x": 500, "y": 400}
- {"action": "type", "text": "notepad"}
- {"action": "hotkey", "key": "ENTER" | "ESC" | "WIN_D" | "TAB" | "SPACE" | "VOL_UP" | "VOL_DOWN" | "MUTE" | "PLAY_PAUSE"}
- {"action": "launch_app", "app": "chrome" | "notepad" | "calc" | "explorer" | "terminal"}
- {"action": "open_url", "url": "https://youtube.com"}
- {"action": "run_command", "command": "npm run build"}
- {"action": "wait", "seconds": 2}
- {"action": "finish", "status": "success", "message": "Goal accomplished on PC"}

Do NOT output conversational markdown. Output ONLY the JSON object.
"""

class PCAgent:
    def __init__(
        self,
        model_provider: Optional[BaseModelProvider] = None,
        controller: Optional[DesktopController] = None,
        max_steps: int = 5,
        dry_run: bool = False
    ):
        self.model = model_provider or get_model_provider("gemini")
        self.controller = controller or DesktopController()
        self.vision = ScreenAnalyzer()
        self.max_steps = max_steps
        self.dry_run = dry_run
        self.history: List[Dict[str, Any]] = []

    def run_goal(self, goal: str) -> Dict[str, Any]:
        logger.info(f"[PC AGENT] Starting goal: '{goal}' (dry_run={self.dry_run})")
        w, h = self.controller.get_screen_resolution()
        steps_trace = []

        for step in range(1, self.max_steps + 1):
            # Capture current desktop state
            try:
                screen_jpeg = self.controller.capture_screen_jpeg(quality=70, max_width=1024)
            except Exception as e:
                screen_jpeg = None
                logger.warning(f"Could not capture screen: {e}")

            analysis = self.vision.analyze(screen_jpeg)
            state_desc = f"Screen resolution: {w}x{h}. {analysis.grid_description} Step: {step}/{self.max_steps}."

            try:
                action_data = self.model.predict_action(
                    goal=f"[PC DESKTOP TASK] {goal}",
                    screen_state_text=state_desc,
                    screenshot_bytes=screen_jpeg,
                    history=self.history
                )
            except Exception as e:
                action_data = {"action": "finish", "status": "error", "message": f"Model inference error: {e}"}

            steps_trace.append({"step": step, "action": action_data})
            self.history.append({"step": step, "action": action_data})

            act_type = action_data.get("action", "wait")
            logger.info(f"[PC AGENT] Step {step}: {action_data}")

            if act_type == "finish":
                return {
                    "success": action_data.get("status") == "success",
                    "goal": goal,
                    "steps": steps_trace,
                    "message": action_data.get("message", "Task finished.")
                }

            if not self.dry_run:
                self._execute_pc_action(action_data)

            time.sleep(1)

        return {
            "success": True,
            "goal": goal,
            "steps": steps_trace,
            "message": f"Reached max steps ({self.max_steps})."
        }

    def _execute_pc_action(self, action_data: Dict[str, Any]):
        act = action_data.get("action")
        if act == "click":
            x = action_data.get("x", 500)
            y = action_data.get("y", 500)
            self.controller.click(x, y)
        elif act == "double_click":
            x = action_data.get("x", 500)
            y = action_data.get("y", 500)
            self.controller.double_click(x, y)
        elif act == "right_click":
            x = action_data.get("x", 500)
            y = action_data.get("y", 500)
            self.controller.click(x, y, button="right")
        elif act == "type":
            text = action_data.get("text", "")
            if text:
                self.controller.type_text(text)
        elif act == "hotkey":
            key = action_data.get("key", "ENTER")
            self.controller.send_hotkey(key)
        elif act == "launch_app":
            app = action_data.get("app", "notepad")
            self.controller.launch_app(app)
        elif act == "open_url":
            url = action_data.get("url", "")
            if url:
                self.controller.open_url(url)
        elif act == "run_command":
            cmd = action_data.get("command", "")
            if cmd:
                res = self.controller.run_command(cmd)
                action_data["output"] = res.get("output", "")
                action_data["success"] = res.get("success", False)
                logger.info(f"[PC AGENT] Command result: {res}")
        elif act == "wait":
            secs = min(5, action_data.get("seconds", 1))
            time.sleep(secs)
