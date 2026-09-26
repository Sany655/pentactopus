import pytest
from tools.action_schema import validate_action, ActionValidationError

def test_valid_tap():
    action = validate_action({"action": "tap", "x": 500, "y": 800})
    assert action.action_type == "tap"
    assert action.params["x"] == 500
    assert action.params["y"] == 800

def test_invalid_tap_coords():
    with pytest.raises(ActionValidationError):
        validate_action({"action": "tap", "x": -10, "y": 500})

def test_valid_key_event():
    action = validate_action({"action": "key_event", "key": "BACK"})
    assert action.action_type == "key_event"
    assert action.params["keycode"] == 4

def test_invalid_key_event():
    with pytest.raises(ActionValidationError):
        validate_action({"action": "key_event", "key": "EXPLODE_PHONE"})

def test_cross_platform_action_normalization():
    # click -> tap
    click_act = validate_action({"action": "click", "x": 300, "y": 400})
    assert click_act.action_type == "tap"
    assert click_act.params["x"] == 300

    # scroll -> swipe
    scroll_act = validate_action({"action": "scroll", "direction": "down"})
    assert scroll_act.action_type == "swipe"
    assert "x1" in scroll_act.params
    assert "y1" in scroll_act.params

def test_desktop_only_unsupported_handling():
    # double_click on Android -> unsupported
    dc = validate_action({"action": "double_click", "x": 100, "y": 200})
    assert dc.action_type == "unsupported"
    assert "not supported on Android" in dc.params["message"]

    # Windows hotkey on Android -> unsupported
    whk = validate_action({"action": "key_event", "key": "WIN_R"})
    assert whk.action_type == "unsupported"
    assert "not available on Android" in whk.params["message"]

def test_valid_run_command():
    rc = validate_action({"action": "run_command", "command": "getprop ro.build.version.release"})
    assert rc.action_type == "run_command"
    assert rc.params["command"] == "getprop ro.build.version.release"
