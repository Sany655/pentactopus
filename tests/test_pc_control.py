"""Unit tests for PC Hardware & Remote Desktop Controller."""

import pytest
from pc_control.desktop_controller import DesktopController
from agent.pc_agent import PCAgent
from models.mock import MockModelProvider

def test_screen_resolution():
    c = DesktopController()
    w, h = c.get_screen_resolution()
    assert w > 0
    assert h > 0
    assert isinstance(w, int)
    assert isinstance(h, int)

def test_screen_capture_jpeg():
    c = DesktopController()
    jpeg_bytes = c.capture_screen_jpeg(quality=50, max_width=640)
    assert len(jpeg_bytes) > 1000
    assert jpeg_bytes.startswith(b"\xff\xd8")  # JPEG magic bytes

def test_coordinate_scaling():
    c = DesktopController()
    w, h = c.get_screen_resolution()
    x, y = c.scale_coordinates(0.5, 0.5)
    assert x == w // 2
    assert y == h // 2

    # Edge clipping
    x_min, y_min = c.scale_coordinates(-1.0, -1.0)
    assert x_min == 0
    assert y_min == 0

    x_max, y_max = c.scale_coordinates(2.0, 2.0)
    assert x_max == w - 1
    assert y_max == h - 1

def test_hotkey_validation():
    c = DesktopController()
    assert c.send_hotkey("win_d") is True
    assert c.send_hotkey("enter") is True
    assert c.send_hotkey("vol_up") is True
    assert c.send_hotkey("unknown_invalid_key_xyz") is False

def test_pc_agent_execution():
    agent = PCAgent(model_provider=MockModelProvider(), dry_run=True, max_steps=2)
    res = agent.run_goal("Minimize all windows on PC")
    assert res["success"] is True
    assert len(res["steps"]) > 0
