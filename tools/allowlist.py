"""Security allowlist and sanitization layer for Android Agent commands.

Ensures no arbitrary shell execution occurs and enforces safety policies.
"""

import re
from typing import Set, Optional
from tools.action_schema import ValidatedAction

SAFE_PACKAGES: Set[str] = {
    "com.android.settings",
    "com.google.android.calculator",
    "com.android.calculator2",
    "com.google.android.deskclock",
    "com.android.deskclock",
    "com.google.android.calendar",
    "com.android.calendar",
    "com.google.android.contacts",
    "com.android.contacts",
    "com.google.android.dialer",
    "com.android.dialer"
}

DANGEROUS_PATTERNS = [
    r";", r"&", r"\|", r"`", r"\$", r">", r"<", r"\n", r"\r",
    r"rm\s+", r"reboot", r"wipe", r"factory", r"uninstall", r"pm\s+clear"
]

class SecurityViolationError(Exception):
    pass

def sanitize_text_input(text: str) -> str:
    """Sanitize text to be safely passed to 'adb shell input text'."""
    # Replace dangerous shell metacharacters and spaces
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, text):
            raise SecurityViolationError(f"Potential shell injection detected in text input: {text}")
    # Android 'input text' replaces spaces with %s
    escaped = text.replace(" ", "%s").replace("'", "\'").replace('"', '\"')
    return escaped

def check_security_allowlist(action: ValidatedAction, enforce_strict_packages: bool = False) -> None:
    """Strictly checks if action violates security constraints."""
    if action.action_type == "launch_app":
        pkg = action.params["package"]
        # Basic validation of package format
        if not re.match(r"^[a-zA-Z0-9_.]+$", pkg) or ".." in pkg or pkg.startswith("."):
            raise SecurityViolationError(f"Malicious package name syntax: '{pkg}'")
        if enforce_strict_packages and pkg not in SAFE_PACKAGES:
            raise SecurityViolationError(f"Package '{pkg}' is not in the safe package allowlist: {SAFE_PACKAGES}")

    elif action.action_type == "type":
        # Check text
        sanitize_text_input(action.params["text"])
