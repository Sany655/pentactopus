"""Autonomous Android Agent execution loop."""

import time
import json
from typing import Optional, Dict, Any, List
from adb.client import ADBClient, ADBError
from android.uiautomator import UIHierarchyParser, UIElement
from tools.action_schema import validate_action, ValidatedAction, ActionValidationError
from tools.allowlist import check_security_allowlist, SecurityViolationError
from models.base import BaseModelProvider
from vision.screen_analyzer import ScreenAnalyzer

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

    def run_goal(self, goal: str) -> Dict[str, Any]:
        """Execute the perception -> reasoning -> validation -> action -> verification loop."""
        print(f"\n[AGENT] Starting goal: '{goal}'")
        print(f"[AGENT] Model Provider: {self.model.model_name} (Dry run: {self.dry_run})")

        step = 0
        while step < self.max_steps:
            step += 1
            print(f"\n--- STEP {step}/{self.max_steps} ---")

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
                    print(f"[WARN] Failed to dump UI hierarchy: {e}")
                    screen_state_text = "UI hierarchy unavailable."

                try:
                    screenshot_bytes = self.adb.capture_screenshot()
                    if screenshot_bytes:
                        analysis = self.vision.analyze(screenshot_bytes)
                        screen_state_text = f"{screen_state_text}\n{analysis.grid_description}"
                except ADBError as e:
                    print(f"[WARN] Failed to capture screenshot: {e}")
            else:
                screen_state_text = f"Simulated UI state for goal: {goal}"

            # 2. Reasoning
            print("[AGENT] Requesting next action from model...")
            try:
                raw_action = self.model.predict_action(
                    goal=goal,
                    screen_state_text=screen_state_text,
                    screenshot_bytes=screenshot_bytes,
                    history=self.history
                )
                print(f"[MODEL RESPONSE] {json.dumps(raw_action)}")
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Model inference failed: {e}",
                    "steps": step,
                    "history": self.history
                }

            # 3. Validation & Security Allowlist
            try:
                validated: ValidatedAction = validate_action(raw_action)
                check_security_allowlist(validated)
            except (ActionValidationError, SecurityViolationError) as e:
                print(f"[SECURITY BLOCKED] Invalid action: {e}")
                return {
                    "success": False,
                    "error": f"Security validation failed: {e}",
                    "steps": step,
                    "history": self.history
                }

            # Check for completion
            if validated.action_type == "finish":
                print(f"[AGENT COMPLETE] {validated.params.get('message')}")
                return {
                    "success": validated.params.get("status") == "success",
                    "message": validated.params.get("message"),
                    "steps": step,
                    "history": self.history
                }

            # 4. Action Execution
            print(f"[EXECUTE] Performing {validated.action_type}: {validated.params}")
            if not self.dry_run:
                try:
                    result = self.adb.execute_action(validated)
                    print(f"[ADB RESULT] {result}")
                except ADBError as e:
                    print(f"[ADB ERROR] Execution failed: {e}")
                    return {
                        "success": False,
                        "error": f"ADB execution error: {e}",
                        "steps": step,
                        "history": self.history
                    }
            else:
                print(f"[DRY-RUN] Simulated execution of {validated.action_type}")

            self.history.append({
                "step": step,
                "action": validated.raw
            })

            # Small observation pause
            time.sleep(1.0)

        return {
            "success": False,
            "error": f"Exceeded max steps ({self.max_steps}) without completing goal.",
            "steps": step,
            "history": self.history
        }
