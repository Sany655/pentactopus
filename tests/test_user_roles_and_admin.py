"""Tests for UserStore, Role-Based Access Control, and Admin Management Console."""

import pytest
import time
from api.user_store import UserStore
from api.admin_dashboard import AdminDashboard
from api.coupons import CouponManager

def test_seed_users_initialization():
    users = UserStore.list_users()
    assert len(users) >= 3

    admin = UserStore.get_user("admin@pentatopus.com")
    assert admin is not None
    assert admin["role"] == "admin"
    assert admin["plan"] == "enterprise"

    alex = UserStore.get_user("alex@pentatopus.com")
    assert alex is not None
    assert alex["role"] == "subscriber"
    assert alex["plan"] == "pro"

    guest = UserStore.get_user("guest@pentatopus.com")
    assert guest is not None
    assert guest["role"] == "free_user"
    assert guest["plan"] == "free"

def test_create_and_get_user():
    email = f"newuser_{int(time.time())}@test.com"
    user = UserStore.create_or_get_user(email, name="Tester", role="free_user")
    assert user["email"] == email
    assert user["role"] == "free_user"
    assert user["name"] == "Tester"

    fetched = UserStore.get_user(email)
    assert fetched is not None
    assert fetched["email"] == email

def test_update_user_role_and_plan():
    email = f"roleuser_{int(time.time())}@test.com"
    UserStore.create_or_get_user(email, name="RoleTester", role="free_user")

    # Promote to subscriber
    sub = UserStore.update_role(email, role="subscriber", plan="pro")
    assert sub["role"] == "subscriber"
    assert sub["plan"] == "pro"
    assert sub.get("license_key") is not None

    # Promote to admin
    adm = UserStore.update_role(email, role="admin")
    assert adm["role"] == "admin"
    assert adm["plan"] == "enterprise"

    # Demote back to free_user
    demoted = UserStore.update_role(email, role="free_user")
    assert demoted["role"] == "free_user"
    assert demoted["plan"] == "free"

def test_associate_coupon_redemption():
    email = f"couponuser_{int(time.time())}@test.com"
    lic = "PENTA-TEST-LIC-123"
    user = UserStore.associate_coupon_redemption(email, "PENTAFREE", lic, 365)
    assert user["role"] == "subscriber"
    assert user["plan"] == "pro"
    assert user["license_key"] == lic
    assert "PENTAFREE" in user["redeemed_coupons"]

def test_admin_html_renders_user_management():
    html = AdminDashboard.render_admin_html()
    assert "User Accounts & Roles (RBAC)" in html
    assert "admin@pentatopus.com" in html
    assert "alex@pentatopus.com" in html
    assert "PRO SUBSCRIBER" in html
    assert "Promo & Coupon Engine" in html
    assert "Active Device Mesh Nodes" in html
