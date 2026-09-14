"""Unit tests for Penta-Assistant Stripe Billing, Coupons, and Admin Dashboard."""

import pytest
from api.coupons import CouponManager
from api.billing import BillingManager, PLANS
from api.admin_dashboard import AdminDashboard

def test_create_and_redeem_coupon():
    c = CouponManager.create_coupon(
        code="TESTPROMO100",
        discount_type="free_trial",
        value=30,
        max_uses=5,
        days_valid=30,
        notes="Test coupon"
    )
    assert c["code"] == "TESTPROMO100"
    assert c["enabled"] is True

    # Redeem coupon
    res = CouponManager.redeem_coupon("TESTPROMO100", "tester@example.com")
    assert res["success"] is True
    assert "license_key" in res
    assert res["license_key"].startswith("PENTA-PRO-")

    # Verify generated license
    lic = CouponManager.verify_license(res["license_key"])
    assert lic["valid"] is True
    assert lic["plan"] == "pro"

def test_invalid_and_expired_coupon():
    res = CouponManager.redeem_coupon("NONEXISTENT_CODE_XYZ")
    assert res["success"] is False
    assert "Invalid coupon code" in res["error"]

def test_coupon_usage_limit():
    c = CouponManager.create_coupon(
        code="ONETIME_ONLY",
        discount_type="percent",
        value=50,
        max_uses=1,
        days_valid=10
    )
    res1 = CouponManager.redeem_coupon("ONETIME_ONLY")
    assert res1["success"] is True

    # Second redemption must fail due to max_uses reached
    res2 = CouponManager.redeem_coupon("ONETIME_ONLY")
    assert res2["success"] is False
    assert "maximum redemptions" in res2["error"]

def test_toggle_coupon():
    CouponManager.create_coupon(code="TOGGLE_ME", value=20)
    assert CouponManager.toggle_coupon("TOGGLE_ME", False) is True
    res = CouponManager.redeem_coupon("TOGGLE_ME")
    assert res["success"] is False
    assert "deactivated" in res["error"]

def test_resource_cost_calculator():
    cost = BillingManager.calculate_resource_cost(
        devices=3,
        ai_tasks_per_day=20,
        stream_hours_per_week=15
    )
    assert cost["devices"] == 3
    assert cost["ai_operating_cost"] > 0
    assert cost["turn_operating_cost"] > 0
    assert cost["cloud_infra_cost"] > 0
    assert cost["total_operating_cost"] > 0
    assert cost["suggested_price"] >= 12.0
    assert cost["monthly_savings"] > 0

def test_stripe_checkout_generation():
    session = BillingManager.create_checkout_session(
        plan_id="pro",
        customer_email="sub@test.com"
    )
    assert "checkout_url" in session
    assert "final_price" in session
    assert session["final_price"] == 12.0

def test_admin_metrics():
    metrics = AdminDashboard.get_overview_metrics()
    assert "total_subscribers" in metrics
    assert "mrr_usd" in metrics
    assert "total_coupons" in metrics
    assert "active_devices_count" in metrics
