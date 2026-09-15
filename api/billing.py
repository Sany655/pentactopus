"""Stripe Billing & Dynamic Resource Cost Engine for Penta-Assistant.

Handles subscription pricing tiers, dynamic resource cost calculations,
Stripe Checkout session generation, and webhook processing.
"""

import os
import json
import time
import uuid
from typing import Dict, Any, Optional
 
try:
    import stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock_key")
except ImportError:
    stripe = None

PLANS = {
    "free": {
        "id": "plan_free",
        "name": "Free Starter",
        "price_usd": 0.0,
        "interval": "forever",
        "features": [
            "1 Paired Device",
            "Local LAN P2P Remote Desktop",
            "Bring-Your-Own-Key (BYOK) AI",
            "30 min/day Cloud Remote Access"
        ]
    },
    "pro": {
        "id": "plan_pro",
        "name": "Pentactopus Pro",
        "price_usd": 12.0,
        "interval": "month",
        "stripe_price_id": os.getenv("STRIPE_PRICE_ID_PRO", "price_penta_pro_monthly"),
        "features": [
            "Unlimited P2P WebRTC Remote Desktop",
            "2,000 Monthly Autonomous Vision AI Steps",
            "Up to 5 Paired Windows & Android Devices",
            "Bi-directional Cloud Clipboard Sync",
            "Background Device Wake & Audio Streaming"
        ]
    },
    "team": {
        "id": "plan_team",
        "name": "Penta Team / Enterprise",
        "price_usd": 29.0,
        "interval": "month",
        "stripe_price_id": os.getenv("STRIPE_PRICE_ID_TEAM", "price_penta_team_monthly"),
        "features": [
            "Everything in Pro",
            "Unlimited Multi-Agent Organization Missions",
            "Dedicated High-Speed TURN Relay Bandwidth",
            "Admin Management Console & Custom Coupons",
            "Unlimited Paired Nodes & Priority AI Routing"
        ]
    }
}

class BillingManager:
    @classmethod
    def calculate_resource_cost(
        cls,
        devices: int = 2,
        ai_tasks_per_day: int = 15,
        stream_hours_per_week: int = 10
    ) -> Dict[str, Any]:
        """Calculate infrastructure resource consumption and transparent pricing."""
        devices = max(1, int(devices))
        ai_tasks_per_day = max(0, int(ai_tasks_per_day))
        stream_hours_per_week = max(0, int(stream_hours_per_week))

        # 1. AI Vision & Computer-Use Tokens
        # ~25k tokens per perception/action step * 30 days
        monthly_tokens = ai_tasks_per_day * 30 * 25000
        ai_cost = round((monthly_tokens / 1_000_000) * 0.25, 2)

        # 2. WebRTC Signaling & TURN Bandwidth
        # ~150 MB/hour * 4.3 weeks * 20% TURN relay
        turn_gb = round((stream_hours_per_week * 4.3 * 0.15) * 0.20, 2)
        turn_cost = round(turn_gb * 0.08, 2)

        # 3. Cloud Signaling & Edge State
        cloud_cost = round(devices * 0.20, 2)

        total_operating_cost = round(ai_cost + turn_cost + cloud_cost, 2)
        suggested_price = max(12.0, round(total_operating_cost * 2.2, 2))

        # Benchmark reference savings vs traditional remote desk and model APIs ($34.90/mo)
        competitor_price = 34.90
        monthly_savings = max(0.0, round(competitor_price - 12.0, 2))

        return {
            "devices": devices,
            "ai_tasks_per_day": ai_tasks_per_day,
            "stream_hours_per_week": stream_hours_per_week,
            "estimated_monthly_tokens": monthly_tokens,
            "ai_operating_cost": ai_cost,
            "turn_bandwidth_gb": turn_gb,
            "turn_operating_cost": turn_cost,
            "cloud_infra_cost": cloud_cost,
            "total_operating_cost": total_operating_cost,
            "suggested_price": suggested_price,
            "pro_price": 12.0,
            "monthly_savings": monthly_savings
        }

    @classmethod
    def create_checkout_session(
        cls,
        plan_id: str = "pro",
        customer_email: str = "customer@example.com",
        coupon_code: Optional[str] = None,
        success_url: str = "http://localhost:5050/?payment=success",
        cancel_url: str = "http://localhost:5050/?payment=cancelled"
    ) -> Dict[str, Any]:
        """Create a Stripe Checkout Session or test sandbox session."""
        plan = PLANS.get(plan_id, PLANS["pro"])

        # Check for coupon discount
        discount_percent = 0
        from api.coupons import CouponManager
        if coupon_code:
            coupons = CouponManager._load_coupons()
            c = coupons.get(coupon_code.strip().upper())
            if c and c.get("enabled"):
                if c["discount_type"] == "percent":
                    discount_percent = c["value"]
                elif c["discount_type"] == "free_trial":
                    # Instant redemption without Stripe
                    res = CouponManager.redeem_coupon(coupon_code, customer_email)
                    return {
                        "mode": "coupon_free",
                        "checkout_url": f"{success_url}&license_key={res.get('license_key')}",
                        "license_key": res.get("license_key"),
                        "message": "100% Free Trial Coupon Applied!"
                    }

        # Calculate final price
        final_price = plan["price_usd"] * (1.0 - (discount_percent / 100.0))

        # Real Stripe API if key is set
        stripe_key = os.getenv("STRIPE_SECRET_KEY", "")
        if stripe and stripe_key.startswith("sk_live_") or stripe_key.startswith("sk_test_"):
            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    line_items=[{
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": plan["name"],
                                "description": "Pentactopus Remote Desktop Mesh + Autonomous Computer-Use Vision AI"
                            },
                            "unit_amount": int(final_price * 100),
                            "recurring": {"interval": "month"}
                        },
                        "quantity": 1,
                    }],
                    mode="subscription",
                    customer_email=customer_email,
                    success_url=success_url + "&session_id={CHECKOUT_SESSION_ID}",
                    cancel_url=cancel_url,
                )
                return {
                    "mode": "stripe",
                    "session_id": session.id,
                    "checkout_url": session.url,
                    "final_price": final_price,
                    "discount_applied": discount_percent
                }
            except Exception as e:
                pass

        # Sandbox / Mock checkout session for immediate local & test environments
        mock_session_id = f"cs_test_{uuid.uuid4().hex[:16]}"
        mock_license = f"PENTA-PRO-{uuid.uuid4().hex[:12].upper()}"
        return {
            "mode": "sandbox",
            "session_id": mock_session_id,
            "checkout_url": f"{success_url}&session_id={mock_session_id}&license_key={mock_license}",
            "license_key": mock_license,
            "final_price": final_price,
            "discount_applied": discount_percent,
            "note": "Sandbox payment session generated."
        }

    @classmethod
    def handle_webhook_event(cls, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """Process incoming Stripe webhook events."""
        event = None
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        if stripe and webhook_secret:
            try:
                event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            try:
                event = json.loads(payload.decode("utf-8"))
            except Exception:
                return {"success": False, "error": "Invalid payload JSON"}

        event_type = event.get("type", "")
        data_obj = event.get("data", {}).get("object", {})

        if event_type == "checkout.session.completed":
            email = data_obj.get("customer_email") or data_obj.get("customer_details", {}).get("email")
            # Provision license key
            lic_key = f"PENTA-SUB-{uuid.uuid4().hex[:12].upper()}"
            from api.coupons import CouponManager
            licenses = CouponManager._load_licenses()
            licenses[lic_key] = {
                "license_key": lic_key,
                "plan": "pro",
                "redeemed_via": "stripe_checkout",
                "user_email": email or "customer@stripe.com",
                "activated_at": time.time(),
                "expires_at": time.time() + (30 * 86400),
                "active": True
            }
            CouponManager._save_licenses(licenses)
            return {"success": True, "action": "license_provisioned", "license_key": lic_key, "user_email": email}

        return {"success": True, "event": event_type}
