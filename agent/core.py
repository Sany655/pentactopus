"""Autonomous Android Agent execution loop.

Perceives mobile UI hierarchy and screenshot, reasons via Unified Multi-Model Gateway,
maintains multi-turn execution memory, and executes touch gestures, key events,
application launches, shell commands, and system actions.
"""

import time
import json
import re
import logging
from typing import Optional, Dict, Any, List
from adb.client import ADBClient, ADBError
from android.uiautomator import UIHierarchyParser, UIElement
from tools.action_schema import validate_action, ValidatedAction, ActionValidationError
from tools.allowlist import check_security_allowlist, SecurityViolationError
from models.base import BaseModelProvider
from vision.screen_analyzer import ScreenAnalyzer

logger = logging.getLogger("android_agent")

PAIR_PROGRAMMER_PROMPT = """You are an elite AI Pair Programmer and Software Architect inside Pentactopus.
Provide comprehensive, production-grade solutions, complete code implementations, or detailed architectural plans as requested.
Format your response using clean GitHub-flavored markdown.
You MUST wrap your final output in a JSON object:
{"action": "finish", "status": "success", "message": "<complete markdown text here>"}
"""

# Map common friendly app names to standard Android packages
ANDROID_APP_MAP = {
    "settings": "com.android.settings",
    "calc": "com.google.android.calculator",
    "calculator": "com.google.android.calculator",
    "clock": "com.google.android.deskclock",
    "deskclock": "com.google.android.deskclock",
    "camera": "com.android.camera2",
    "calendar": "com.google.android.calendar",
    "chrome": "com.android.chrome",
    "browser": "com.android.chrome",
    "contacts": "com.google.android.contacts",
    "dialer": "com.google.android.dialer",
    "phone": "com.google.android.dialer",
    "messages": "com.google.android.apps.messaging",
    "maps": "com.google.android.apps.maps",
    "youtube": "com.google.android.youtube",
    "photos": "com.google.android.apps.photos",
    "gallery": "com.android.gallery3d",
    "files": "com.google.android.documentsui"
}

WINDOWS_ONLY_APPS = {
    "antigravity", "antigravity ide", "notepad", "code", "vscode", "visual studio",
    "explorer", "powershell", "cmd", "terminal", "taskmgr", "taskmanager", "git bash",
    "calc.exe", "notepad.exe"
}

WINDOWS_ONLY_CMDS = {
    "dir", "cls", "ipconfig", "powershell", "start-process", "get-process",
    "tasklist", "systeminfo", "format", "sc", "netstat -ano"
}

class AndroidAgent:
    def __init__(
        self,
        model_provider: BaseModelProvider,
        adb_client: Optional[ADBClient] = None,
        max_steps: int = 15,
        dry_run: bool = False
    ):
        self.model = model_provider
        self.adb = adb_client or ADBClient()
        self.vision = ScreenAnalyzer()
        self.max_steps = max_steps
        self.dry_run = dry_run
        self.history: List[Dict[str, Any]] = []

    def _smart_extract_app_name(self, text: str) -> str:
        """Extract clean application name from conversational commands like 'open the camera'."""
        cleaned = text.strip()
        for prefix in ("open ", "launch ", "start ", "run "):
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                break

        cleaned = re.sub(r'^(the|a|an)\s+', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\(.*?\)', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = re.sub(r'\s+(ide|app|application|editor|browser)\b', '', cleaned, flags=re.IGNORECASE).strip()
        return cleaned or text.strip()

    def run_goal(self, goal: str) -> Dict[str, Any]:
        """Execute the perception -> reasoning -> validation -> action -> verification loop."""
        logger.info(f"[ANDROID AGENT] Starting goal: '{goal}' (dry_run={self.dry_run}, max_steps={self.max_steps})")
        steps_trace: List[Dict[str, Any]] = []

        # -------------------------------------------------------------
        # 1. Direct Intent: Terminal Shell Action (/run command)
        # -------------------------------------------------------------
        if "[TERMINAL SHELL ACTION] Run command:" in goal:
            raw_cmd = goal.split("[TERMINAL SHELL ACTION] Run command:", 1)[1].strip()
            logger.info(f"[ANDROID AGENT] Direct shell action detected: '{raw_cmd}'")

            # Check if user asked to open/launch an app via /run
            lower_cmd = raw_cmd.lower()
            if any(lower_cmd.startswith(p) for p in ("open ", "launch ", "start ")):
                app_target = self._smart_extract_app_name(raw_cmd)
                low_target = app_target.lower()

                # Check if user requested a Windows-only desktop app
                if low_target in WINDOWS_ONLY_APPS or low_target.endswith(".exe"):
                    msg = (
                        f"**Feature Not Available on Android (Coming Soon / Desktop Only)**\n\n"
                        f"'{app_target.title()}' is a Windows desktop application and cannot run natively on Android. "
                        f"Please switch your Target Device to **Windows** to execute desktop applications."
                    )
                    action_data = {"action": "launch_app", "app": app_target, "status": "unsupported", "message": msg}
                    steps_trace.append({"step": 1, "action": action_data})
                    return {
                        "success": False,
                        "goal": goal,
                        "steps": steps_trace,
                        "message": msg,
                        "platform": "android"
                    }

                # Resolve standard Android package
                pkg = ANDROID_APP_MAP.get(low_target, low_target)
                if self.dry_run:
                    action_data = {"action": "launch_app", "package": pkg, "output": f"[Simulated launch of {pkg}]", "success": True}
                    steps_trace.append({"step": 1, "action": action_data})
                    return {
                        "success": True,
                        "goal": goal,
                        "steps": steps_trace,
                        "message": f"**Application Launch**\n\nLaunched '{app_target}' ({pkg}) on Android device.",
                        "platform": "android"
                    }

                try:
                    self.adb.run_command(["shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"])
                    action_data = {"action": "launch_app", "package": pkg, "output": f"Launched package {pkg}", "success": True}
                    steps_trace.append({"step": 1, "action": action_data})
                    return {
                        "success": True,
                        "goal": goal,
                        "steps": steps_trace,
                        "message": f"**Application Launch**\n\nLaunched '{app_target}' ({pkg}) on Android device.",
                        "platform": "android"
                    }
                except Exception as e:
                    action_data = {"action": "launch_app", "package": pkg, "output": str(e), "success": False}
                    steps_trace.append({"step": 1, "action": action_data})
                    return {
                        "success": False,
                        "goal": goal,
                        "steps": steps_trace,
                        "message": f"Could not launch '{app_target}' on Android: {e}",
                        "platform": "android"
                    }

            # Direct shell command execution on Android
            first_word = raw_cmd.split()[0].lower() if raw_cmd.split() else ""
            if first_word in WINDOWS_ONLY_CMDS or any(w in raw_cmd.lower() for w in ("powershell", "start-process")):
                msg = (
                    f"**Command Not Supported on Android (Coming Soon / Desktop Only)**\n\n"
                    f"Windows PowerShell and CMD commands cannot run on the Android Linux environment. "
                    f"Switch your Target Device to **Windows** or run Android shell commands (e.g. `pm list packages`, `getprop`, `ls /sdcard`)."
                )
                action_data = {"action": "run_command", "command": raw_cmd, "status": "unsupported", "message": msg}
                steps_trace.append({"step": 1, "action": action_data})
                return {
                    "success": False,
                    "goal": goal,
                    "steps": steps_trace,
                    "message": msg,
                    "platform": "android"
                }

            if self.dry_run:
                action_data = {"action": "run_command", "command": raw_cmd, "output": f"[Simulated execution: {raw_cmd}]", "success": True}
                steps_trace.append({"step": 1, "action": action_data})
                return {
                    "success": True,
                    "goal": goal,
                    "steps": steps_trace,
                    "message": f"```terminal\n$ adb shell {raw_cmd}\n[Simulated execution of: {raw_cmd}]\n```",
                    "platform": "android"
                }

            try:
                code, out, err = self.adb.run_command(["shell", raw_cmd])
                output_str = out or err or f"Command finished with code {code}."
                action_data = {"action": "run_command", "command": raw_cmd, "output": output_str, "success": code == 0}
                steps_trace.append({"step": 1, "action": action_data})
                return {
                    "success": code == 0,
                    "goal": goal,
                    "steps": steps_trace,
                    "message": f"```terminal\n$ adb shell {raw_cmd}\n{output_str}\n```",
                    "platform": "android"
                }
            except Exception as e:
                action_data = {"action": "run_command", "command": raw_cmd, "output": str(e), "success": False}
                steps_trace.append({"step": 1, "action": action_data})
                return {
                    "success": False,
                    "goal": goal,
                    "steps": steps_trace,
                    "message": f"ADB Shell execution failed: {e}",
                    "platform": "android"
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
            logger.info("[ANDROID AGENT] Pair programmer reasoning mode activated.")
            try:
                action_data = self.model.predict_action(
                    goal=f"{PAIR_PROGRAMMER_PROMPT}\n\nTask: {goal}",
                    screen_state_text="Android development workspace active.",
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
                "message": final_msg,
                "platform": "android"
            }

        # -------------------------------------------------------------
        # 3. Autonomous Android Perception -> Action Loop
        # -------------------------------------------------------------
        step = 0
        while step < self.max_steps:
            step += 1

            # 1. Perception
            elements: List[UIElement] = []
            screenshot_bytes: Optional[bytes] = None
            screen_state_text = ""

            if not self.dry_run:
                try:
                    xml_dump = self.adb.dump_ui_hierarchy()
                    elements = UIHierarchyParser.parse(xml_dump)
                    screen_state_text = UIHierarchyParser.to_readable_state(elements)
                except ADBError as e:
                    screen_state_text = "UI hierarchy unavailable."

                try:
                    screenshot_bytes = self.adb.capture_screenshot()
                    if screenshot_bytes:
                        analysis = self.vision.analyze(screenshot_bytes)
                        screen_state_text = f"{screen_state_text}\n{analysis.grid_description}"
                except ADBError as e:
                    pass
            else:
                screen_state_text = f"Simulated UI state for goal: {goal}"

            # 2. Reasoning with Multi-Turn Memory
            try:
                raw_action = self.model.predict_action(
                    goal=goal,
                    screen_state_text=screen_state_text,
                    screenshot_bytes=screenshot_bytes,
                    history=self.history
                )
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Model inference failed: {e}",
                    "message": f"Model inference error: {e}",
                    "steps": steps_trace,
                    "platform": "android"
                }

            # 3. Validation & Desktop Fallback Handling
            try:
                validated: ValidatedAction = validate_action(raw_action)
                check_security_allowlist(validated)
            except (ActionValidationError, SecurityViolationError) as e:
                return {
                    "success": False,
                    "error": f"Security validation failed: {e}",
                    "message": f"Action blocked: {e}",
                    "steps": steps_trace,
                    "platform": "android"
                }

            # Check for completion
            if validated.action_type == "finish":
                steps_trace.append({"step": step, "action": validated.raw})
                self.history.append({"step": step, "action": validated.raw})
                return {
                    "success": validated.params.get("status") == "success",
                    "message": validated.params.get("message", "Task finished."),
                    "goal": goal,
                    "steps": steps_trace,
                    "platform": "android"
                }

            # 4. Action Execution
            exec_feedback = {}
            if validated.action_type == "unsupported":
                exec_feedback = {"status": "skipped", "details": validated.params.get("message")}
            elif not self.dry_run:
                try:
                    exec_feedback = self.adb.execute_action(validated)
                except ADBError as e:
                    return {
                        "success": False,
                        "error": f"ADB execution error: {e}",
                        "message": f"Execution error: {e}",
                        "steps": steps_trace,
                        "platform": "android"
                    }
            else:
                exec_feedback = {"status": "executed", "details": f"[Simulated execution: {validated.action_type}]"}

            recorded_action = dict(validated.raw)
            recorded_action["result"] = exec_feedback.get("details", "")
            recorded_action["status"] = exec_feedback.get("status", "executed")
            steps_trace.append({"step": step, "action": recorded_action})
            self.history.append({"step": step, "action": recorded_action})

            time.sleep(1.0)

        summary_lines = [f"- Step {s['step']}: {s['action'].get('action')} ({s['action'].get('result', 'done')})" for s in steps_trace]
        return {
            "success": False,
            "error": f"Exceeded max steps ({self.max_steps}) without completing goal.",
            "message": f"Reached max steps ({self.max_steps}). Actions taken:\n" + "\n".join(summary_lines),
            "goal": goal,
            "steps": steps_trace,
            "platform": "android"
        }
