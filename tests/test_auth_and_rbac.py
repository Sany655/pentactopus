"""Comprehensive Tests for Pentatopus Authentication, Password Hashing,
Brute-Force Lockout Shields, RBAC Access, and Zero-Brand-Infringement Auditing.
"""

import pytest
import time
import os
from api.user_store import (
    UserStore,
    hash_password,
    verify_password,
    AuthError,
    LockoutError,
    MAX_FAILED_ATTEMPTS
)
from api.admin_dashboard import AdminDashboard

def test_pbkdf2_password_hashing():
    pwd = "SuperSecretPassword123!"
    h = hash_password(pwd)
    assert h.startswith("pbkdf2:sha256:100000$")
    assert verify_password(pwd, h) is True
    assert verify_password("WrongPassword!", h) is False

def test_user_registration_and_safe_serialization():
    email = f"user_{int(time.time() * 1000)}@pentatopus.com"
    user, token = UserStore.register_user(
        name="Jordan Lee",
        email=email,
        password="MySecurePassword123!"
    )
    assert user["email"] == email
    assert user["name"] == "Jordan Lee"
    assert user["role"] == "free_user"
    assert "password_hash" not in user  # Crucial: safe serialization
    assert token.startswith("penta_sess_")

    # Duplicate registration must fail
    with pytest.raises(AuthError):
        UserStore.register_user(
            name="Jordan Duplicate",
            email=email,
            password="AnotherPassword123!"
        )

def test_authentication_flow_and_session_lifecycle():
    email = f"authuser_{int(time.time() * 1000)}@pentatopus.com"
    pwd = "ValidPassword2026!"
    UserStore.register_user(name="Auth Tester", email=email, password=pwd)

    # Valid login
    user, token = UserStore.authenticate_user(email=email, password=pwd, client_ip="192.168.1.50")
    assert user["email"] == email
    assert token.startswith("penta_sess_")

    # Validate session
    active_user = UserStore.validate_session(token)
    assert active_user is not None
    assert active_user["email"] == email

    # Logout / Revocation
    assert UserStore.revoke_session(token) is True
    assert UserStore.validate_session(token) is None

def test_brute_force_lockout_shield():
    email = f"victim_{int(time.time() * 1000)}@pentatopus.com"
    UserStore.register_user(name="Victim", email=email, password="RealPassword2026!")
    ip = "10.0.0.99"

    # Attempt 4 failed logins (should raise AuthError)
    for _ in range(MAX_FAILED_ATTEMPTS - 1):
        with pytest.raises(AuthError):
            UserStore.authenticate_user(email=email, password="WrongPassword!", client_ip=ip)

    # 5th failed login must trigger LockoutError (HTTP 429)
    with pytest.raises(LockoutError) as exc_info:
        UserStore.authenticate_user(email=email, password="WrongPassword!", client_ip=ip)
    assert exc_info.value.retry_after > 0

    # Even with correct password, account must remain locked during cooldown
    with pytest.raises(LockoutError):
        UserStore.authenticate_user(email=email, password="RealPassword2026!", client_ip=ip)

def test_admin_rbac_authorization():
    # Master secret key authorizes
    assert AdminDashboard.verify_auth("Bearer penta_admin_secret_2026") is True
    assert AdminDashboard.verify_auth("penta_admin_secret_2026") is True
    assert AdminDashboard.verify_auth("Bearer wrong_secret") is False

    # Admin user session token authorizes
    admin_user, admin_token = UserStore.authenticate_user("admin@pentatopus.com", "PentaAdmin2026!")
    assert AdminDashboard.verify_auth(admin_token) is True
    assert AdminDashboard.verify_auth(f"Bearer {admin_token}") is True

    # Regular subscriber session token is REJECTED from admin
    pro_user, pro_token = UserStore.authenticate_user("alex@pentatopus.com", "PentaPro2026!")
    assert AdminDashboard.verify_auth(pro_token) is False
    assert AdminDashboard.verify_auth(f"Bearer {pro_token}") is False

def test_zero_third_party_brand_infringement():
    """Verify that NO core source files contain 'anydesk' or 'antigravity'."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_files = [
        os.path.join(base_dir, "api", "index.py"),
        os.path.join(base_dir, "api", "web_template.py"),
        os.path.join(base_dir, "api", "admin_dashboard.py"),
        os.path.join(base_dir, "api", "user_store.py"),
        os.path.join(base_dir, "ui.py")
    ]

    for fpath in target_files:
        if os.path.isfile(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read().lower()
                assert "anydesk" not in content, f"Forbidden brand 'anydesk' found in {fpath}"
                assert "antigravity" not in content, f"Forbidden brand 'antigravity' found in {fpath}"
