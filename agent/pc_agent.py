"""Autonomous Computer-Use & System AI Agent for Windows PC.

Perceives the Windows Desktop screen, reasons via Unified Multi-Model Gateway,
maintains multi-turn execution memory, and executes mouse clicks, keystrokes,
application launches, shell commands, and system actions.
"""

import time
import json
import re
import logging
from typing import Dict, Any, Optional, List
from pc_control.desktop_controller import DesktopController
from models.router import get_model_provider
from models.base import BaseModelProvider
from vision.screen_analyzer import ScreenAnalyzer

logger = logging.getLogger("pc_agent")

PC_SYSTEM_PROMPT = """You are an autonomous Windows PC Desktop Computer-Use & System Agent.
Your job is to accomplish the user's goal on the Windows PC by issuing structured actions or providing answers.
You are provided with:
1. The user's goal
2. Current screen resolution
3. Optionally a screenshot of the current Windows Desktop
4. Action history with execution feedback

You MUST respond ONLY with a valid JSON object describing the single next action to take.
Allowed actions:
- {"action": "click", "x": 683, "y": 384}
- {"action": "double_click", "x": 100, "y": 200}
- {"action": "right_click", "x": 500, "y": 400}
- {"action": "type", "text": "notepad"}
- {"action": "hotkey", "key": "ENTER" | "ESC" | "WIN_D" | "WIN_R" | "WIN_E" | "WIN_S" | "CTRL_C" | "CTRL_V" | "CTRL_S" | "CTRL_A" | "CTRL_Z" | "ALT_TAB" | "ALT_F4" | "TAB" | "SPACE" | "BACKSPACE" | "VOL_UP" | "VOL_DOWN" | "MUTE" | "PLAY_PAUSE"}
- {"action": "scroll", "clicks": 3, "direction": "down" | "up"}
- {"action": "launch_app", "app": "chrome" | "notepad" | "calc" | "code" | "explorer" | "terminal" | "<app_name_or_exe>"}
- {"action": "open_url", "url": "https://google.com"}
- {"action": "run_command", "command": "powershell or cmd command here"}
- {"action": "wait", "seconds": 2}
- {"action": "finish", "status": "success" | "error", "message": "Detailed natural language explanation or summary of accomplishment for the user"}

Important Rules:
1. Check the previous action history to learn from past outcomes and avoid repeating errors.
2. If the goal is a coding task, planning task, or explanation, issue {"action": "finish", "status": "success", "message": "<markdown text here>"}.
3. When the goal is completed or verified, issue {"action": "finish", "status": "success", "message": "<completion report>"}.
4. Do NOT output conversational text outside JSON. Output ONLY the raw JSON object.
"""

PAIR_PROGRAMMER_PROMPT = """You are an elite AI Pair Programmer and Software Architect inside Pentactopus.
Provide comprehensive, production-grade solutions, complete code implementations, or detailed architectural plans as requested.
Format your response using clean GitHub-flavored markdown.
You MUST wrap your final output in a JSON object:
{"action": "finish", "status": "success", "message": "<complete markdown text here>"}
"""

class PCAgent:
    def __init__(
        self,
        model_provider: Optional[BaseModelProvider] = None,
        controller: Optional[DesktopController] = None,
        max_steps: int = 15,
        dry_run: bool = False
    ):
        self.model = model_provider or get_model_provider("gemini")
        self.controller = controller or DesktopController()
        self.vision = ScreenAnalyzer()
        self.max_steps = max_steps
        self.dry_run = dry_run
        self.history: List[Dict[str, Any]] = []

    def _smart_extract_app_name(self, text: str) -> str:
        """Extract clean application name from conversational commands like 'open the antigravity ide'."""
        cleaned = text.strip()
        for prefix in ("open ", "launch ", "start ", "run "):
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                break

        # Remove filler words
        cleaned = re.sub(r'^(the|a|an)\s+', '', cleaned, flags=re.IGNORECASE)
        # Extract core name before parenthetical descriptions e.g. "antigravity (google's original) ide" -> "antigravity"
        match = re.search(r'\((.*?)\)', cleaned)
        if match:
            cleaned = cleaned.replace(match.group(0), ' ').strip()
        cleaned = re.sub(r'\s+(ide|app|application|editor|browser)\b', '', cleaned, flags=re.IGNORECASE).strip()
        return cleaned or text.strip()

    def run_goal(self, goal: str) -> Dict[str, Any]:
        logger.info(f"[PC AGENT] Starting goal: '{goal}' (dry_run={self.dry_run}, max_steps={self.max_steps})")
        steps_trace: List[Dict[str, Any]] = []

        # -------------------------------------------------------------
        # 1. Direct Intent: Terminal Shell Action (/run command)
        # -------------------------------------------------------------
        if "[TERMINAL SHELL ACTION] Run command:" in goal:
            raw_cmd = goal.split("[TERMINAL SHELL ACTION] Run command:", 1)[1].strip()
            logger.info(f"[PC AGENT] Direct shell action detected: '{raw_cmd}'")

            # Check if user asked to open/launch an app via /run
            lower_cmd = raw_cmd.lower()
            if any(lower_cmd.startswith(p) for p in ("open ", "launch ", "start ")):
                app_query = self._smart_extract_app_name(raw_cmd)
                launch_res = self.controller.launch_app(app_query)
                action_data = {
                    "action": "launch_app",
                    "app": app_query,
                    "output": launch_res.get("message") or launch_res.get("error", ""),
                    "success": launch_res.get("success", False)
                }
                steps_trace.append({"step": 1, "action": action_data})
                self.history.append({"step": 1, "action": action_data})
                msg = launch_res.get("message") or launch_res.get("error", "Launch attempt completed.")
                return {
                    "success": launch_res.get("success", False),
                    "goal": goal,
                    "steps": steps_trace,
                    "message": f"**Application Launch**\n\n{msg}"
                }

            # Direct shell command execution
            cmd_res = self.controller.run_command(raw_cmd)
            action_data = {
                "action": "run_command",
                "command": raw_cmd,
                "output": cmd_res.get("output", ""),
                "success": cmd_res.get("success", False)
            }
            steps_trace.append({"step": 1, "action": action_data})
            self.history.append({"step": 1, "action": action_data})
            cmd_out = cmd_res.get("output", "") or ("Command completed with code 0 (no output)." if cmd_res.get("success") else "Command failed.")
            return {
                "success": cmd_res.get("success", False),
                "goal": goal,
                "steps": steps_trace,
                "message": f"```terminal\n$ {raw_cmd}\n{cmd_out}\n```"
            }

        # -------------------------------------------------------------
        # 2. Direct Intent: Pair Programmer / Architecture / Code Generation
        # -------------------------------------------------------------
        is_pair_coding = any(k in goal for k in [
            "[PLANNING & ARCHITECTURE TASK]",
            "[PAIR PROGRAMMER CODE TASK]",
            "[PAIR PROGRAMMER / CHAT ASSISTANT]"
        ])

        if is_pair_coding:
            logger.info("[PC AGENT] Pair programmer reasoning mode activated.")
            try:
                action_data = self.model.predict_action(
                    goal=f"{PAIR_PROGRAMMER_PROMPT}\n\nTask: {goal}",
                    screen_state_text="Desktop code workspace active.",
                    screenshot_bytes=None,
                    history=self.history
                )
            except Exception as e:
                action_data = {"action": "finish", "status": "error", "message": f"Model inference error: {e}"}

            steps_trace.append({"step": 1, "action": action_data})
            self.history.append({"step": 1, "action": action_data})
            final_msg = action_data.get("message") or action_data.get("code") or json.dumps(action_data)
            return {
                "success": action_data.get("status") != "error",
                "goal": goal,
                "steps": steps_trace,
                "message": final_msg
            }

        # -------------------------------------------------------------
        # 3. Autonomous Windows Computer-Use Execution Loop
        # -------------------------------------------------------------
        w, h = self.controller.get_screen_resolution()

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

            act_type = action_data.get("action", "wait")
            logger.info(f"[PC AGENT] Step {step}/{self.max_steps}: {action_data}")

            if act_type == "finish":
                steps_trace.append({"step": step, "action": action_data})
                self.history.append({"step": step, "action": action_data})
                return {
                    "success": action_data.get("status") == "success",
                    "goal": goal,
                    "steps": steps_trace,
                    "message": action_data.get("message", "Task finished.")
                }

            # Execute action with feedback capture
            if not self.dry_run:
                self._execute_pc_action(action_data)
            else:
                action_data["output"] = f"[Simulated execution: {act_type}]"
                action_data["success"] = True

            steps_trace.append({"step": step, "action": action_data})
            self.history.append({"step": step, "action": action_data})

            time.sleep(1)

        summary_lines = [f"- Step {s['step']}: {s['action'].get('action')} ({s['action'].get('output', 'executed')})" for s in steps_trace]
        return {
            "success": True,
            "goal": goal,
            "steps": steps_trace,
            "message": f"Reached max steps ({self.max_steps}). Actions taken:\n" + "\n".join(summary_lines)
        }

    def _execute_pc_action(self, action_data: Dict[str, Any]):
        act = action_data.get("action")
        if act == "click":
            x = action_data.get("x", 500)
            y = action_data.get("y", 500)
            self.controller.click(x, y)
            action_data["output"] = f"Clicked at ({x}, {y})"
            action_data["success"] = True
        elif act == "double_click":
            x = action_data.get("x", 500)
            y = action_data.get("y", 500)
            self.controller.double_click(x, y)
            action_data["output"] = f"Double clicked at ({x}, {y})"
            action_data["success"] = True
        elif act == "right_click":
            x = action_data.get("x", 500)
            y = action_data.get("y", 500)
            self.controller.click(x, y, button="right")
            action_data["output"] = f"Right clicked at ({x}, {y})"
            action_data["success"] = True
        elif act == "type":
            text = action_data.get("text", "")
            if text:
                self.controller.type_text(text)
                action_data["output"] = f"Typed: '{text}'"
                action_data["success"] = True
        elif act == "hotkey":
            key = action_data.get("key", "ENTER")
            ok = self.controller.send_hotkey(key)
            action_data["output"] = f"Hotkey {key} ({'sent' if ok else 'unknown'})"
            action_data["success"] = ok
        elif act == "scroll":
            clicks = action_data.get("clicks", 3)
            direction = action_data.get("direction", "down").lower()
            amt = -clicks if direction == "down" else clicks
            self.controller.scroll(amt)
            action_data["output"] = f"Scrolled {direction} by {clicks} notches"
            action_data["success"] = True
        elif act == "launch_app":
            app = action_data.get("app", "notepad")
            res = self.controller.launch_app(app)
            action_data["output"] = res.get("message") or res.get("error", "")
            action_data["success"] = res.get("success", False)
        elif act == "open_url":
            url = action_data.get("url", "")
            if url:
                self.controller.open_url(url)
                action_data["output"] = f"Opened URL: {url}"
                action_data["success"] = True
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
            action_data["output"] = f"Waited {secs}s"
            action_data["success"] = True
