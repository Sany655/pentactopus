"""Action schema definitions and validation for Android agent actions."""

from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ValidatedAction:
    action_type: str
    params: Dict[str, Any]
    raw: Dict[str, Any]

class ActionValidationError(Exception):
    pass

SUPPORTED_ACTIONS = {
    "tap": ["x", "y"],
    "type": ["text"],
    "swipe": ["x1", "y1", "x2", "y2"],
    "key_event": ["key"],
    "launch_app": ["package"],
    "wait": ["seconds"],
    "finish": ["status", "message"]
}

VALID_KEYS = {
    "BACK": 4,
    "HOME": 3,
    "RECENTS": 187,
    "ENTER": 66,
    "POWER": 26,
    "VOLUME_UP": 24,
    "VOLUME_DOWN": 25,
    "TAB": 61,
    "ESCAPE": 111,
    "DPAD_UP": 19,
    "DPAD_DOWN": 20,
    "DPAD_LEFT": 21,
    "DPAD_RIGHT": 22
}

def validate_action(data: Dict[str, Any], screen_width: int = 4000, screen_height: int = 4000) -> ValidatedAction:
    if not isinstance(data, dict):
        raise ActionValidationError(f"Action must be a JSON dictionary, got {type(data)}")

    action_type = data.get("action")
    if not action_type or not isinstance(action_type, str):
        raise ActionValidationError("Action missing valid 'action' type string")

    action_type = action_type.lower().strip()
    if action_type not in SUPPORTED_ACTIONS:
        raise ActionValidationError(f"Unsupported action: '{action_type}'. Allowed: {list(SUPPORTED_ACTIONS.keys())}")

    required_fields = SUPPORTED_ACTIONS[action_type]
    params = {}

    if action_type == "tap":
        for coord in ("x", "y"):
            val = data.get(coord)
            if val is None or not isinstance(val, (int, float)):
                raise ActionValidationError(f"tap requires numeric '{coord}', got {val}")
            params[coord] = int(val)
        if not (0 <= params["x"] <= screen_width and 0 <= params["y"] <= screen_height):
            raise ActionValidationError(f"Tap coordinates ({params['x']}, {params['y']}) out of range (0-{screen_width}, 0-{screen_height})")

    elif action_type == "type":
        text = data.get("text")
        if text is None or not isinstance(text, str):
            raise ActionValidationError("type action requires string 'text'")
        params["text"] = text

    elif action_type == "swipe":
        for coord in ("x1", "y1", "x2", "y2"):
            val = data.get(coord)
            if val is None or not isinstance(val, (int, float)):
                raise ActionValidationError(f"swipe requires numeric '{coord}'")
            params[coord] = int(val)
        duration = data.get("duration_ms", 300)
        if not isinstance(duration, (int, float)) or duration <= 0 or duration > 10000:
            duration = 300
        params["duration_ms"] = int(duration)

    elif action_type == "key_event":
        key = str(data.get("key", "")).upper().strip()
        if key not in VALID_KEYS:
            raise ActionValidationError(f"Unknown key '{key}'. Allowed: {list(VALID_KEYS.keys())}")
        params["key"] = key
        params["keycode"] = VALID_KEYS[key]

    elif action_type == "launch_app":
        pkg = data.get("package")
        if not pkg or not isinstance(pkg, str):
            raise ActionValidationError("launch_app requires string 'package'")
        params["package"] = pkg.strip()

    elif action_type == "wait":
        sec = data.get("seconds", 1.0)
        if not isinstance(sec, (int, float)) or sec < 0 or sec > 60:
            sec = 1.0
        params["seconds"] = float(sec)

    elif action_type == "finish":
        params["status"] = str(data.get("status", "success"))
        params["message"] = str(data.get("message", "Task completed"))

    return ValidatedAction(action_type=action_type, params=params, raw=data)
