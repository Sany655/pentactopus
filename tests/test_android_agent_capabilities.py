"""Unit tests for upgraded AndroidAgent capabilities and cross-platform feature parity."""

import pytest
from agent.core import AndroidAgent
from models.mock import MockModelProvider

def test_android_direct_shell_execution():
    agent = AndroidAgent(model_provider=MockModelProvider(), dry_run=True)
    res = agent.run_goal("[TERMINAL SHELL ACTION] Run command: getprop ro.build.version.release")
    assert res["success"] is True
    assert "adb shell" in res["message"]
    assert len(res["steps"]) == 1
    assert res["steps"][0]["action"]["action"] == "run_command"

def test_android_direct_app_launch():
    agent = AndroidAgent(model_provider=MockModelProvider(), dry_run=True)
    res = agent.run_goal("[TERMINAL SHELL ACTION] Run command: open camera")
    assert res["success"] is True
    assert "Application Launch" in res["message"]
    assert "com.android.camera2" in res["message"]
    assert len(res["steps"]) == 1

def test_windows_app_on_android_coming_soon():
    agent = AndroidAgent(model_provider=MockModelProvider(), dry_run=True)
    res = agent.run_goal("[TERMINAL SHELL ACTION] Run command: open the antigravity (google's original) ide")
    assert res["success"] is False
    assert "Feature Not Available on Android" in res["message"]
    assert "Coming Soon" in res["message"]
    assert "Windows desktop application" in res["message"]

def test_windows_shell_cmd_on_android_coming_soon():
    agent = AndroidAgent(model_provider=MockModelProvider(), dry_run=True)
    res = agent.run_goal("[TERMINAL SHELL ACTION] Run command: powershell Get-Process")
    assert res["success"] is False
    assert "Command Not Supported on Android" in res["message"]
    assert "Coming Soon" in res["message"]

def test_android_pair_programmer_mode():
    class DummyCodeModel:
        model_name = "test-mobile-code"
        def predict_action(self, goal, screen_state_text, screenshot_bytes=None, history=None):
            return {
                "action": "finish",
                "status": "success",
                "message": "### Android Plan\n1. Use Jetpack Compose\n2. Integrate Retrofit"
            }

    agent = AndroidAgent(model_provider=DummyCodeModel(), dry_run=True)
    res = agent.run_goal("[PLANNING & ARCHITECTURE TASK] Design mobile architecture")
    assert res["success"] is True
    assert "Android Plan" in res["message"]
    assert len(res["steps"]) == 1

def test_android_multi_turn_history():
    class MultiTurnMockModel:
        model_name = "test-multiturn"
        def __init__(self):
            self.turn = 0
        def predict_action(self, goal, screen_state_text, screenshot_bytes=None, history=None):
            self.turn += 1
            if self.turn == 1:
                return {"action": "tap", "x": 100, "y": 200}
            else:
                assert history is not None
                assert len(history) >= 1
                return {"action": "finish", "status": "success", "message": "Multi-turn complete"}

    agent = AndroidAgent(model_provider=MultiTurnMockModel(), dry_run=True, max_steps=5)
    res = agent.run_goal("Perform multi-step mobile workflow")
    assert res["success"] is True
    assert len(res["steps"]) == 2
