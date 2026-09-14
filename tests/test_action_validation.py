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
