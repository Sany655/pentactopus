import pytest
from tools.action_schema import validate_action
from tools.allowlist import check_security_allowlist, SecurityViolationError, sanitize_text_input

def test_reject_shell_injection():
    action = validate_action({"action": "type", "text": "hello; rm -rf /"})
    with pytest.raises(SecurityViolationError):
        check_security_allowlist(action)

def test_reject_malicious_package():
    action = validate_action({"action": "launch_app", "package": "com.android.settings; reboot"})
    with pytest.raises(SecurityViolationError):
        check_security_allowlist(action)

def test_safe_sanitization():
    sanitized = sanitize_text_input("hello world")
    assert sanitized == "hello%sworld"
