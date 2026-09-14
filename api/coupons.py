"""Coupon & Promo Code Redemption Engine for Penta-Assistant.

Provides coupon code generation, redemption tracking, expiry validation,
and license key activation authorized by the Admin Panel.
"""

import json
import os
import time
import uuid
from typing import Dict, Any, List, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
COUPONS_FILE = os.path.join(DATA_DIR, "coupons.json")
LICENSES_FILE = os.path.join(DATA_DIR, "licenses.json")

os.makedirs(DATA_DIR, exist_ok=True)

class CouponManager:
    @classmethod
    def _load_coupons(cls) -> Dict[str, Dict[str, Any]]:
        if not os.path.isfile(COUPONS_FILE):
            # Seed with default launch coupons
            initial = {
                "PENTAFREE": {
                    "code": "PENTAFREE",
                    "discount_type": "free_trial",
                    "value": 365, # 1 year full free pro access
                    "max_uses": 1000,
                    "current_uses": 0,
                    "expires_at": time.time() + (365 * 86400),
                    "enabled": True,
                    "created_at": time.time(),
                    "notes": "Launch 100% Free Pro Access"
                },
                "LAUNCH50": {
                    "code": "LAUNCH50",
                    "discount_type": "percent",
                    "value": 50, # 50% off
                    "max_uses": 500,
                    "current_uses": 0,
                    "expires_at": time.time() + (180 * 86400),
                    "enabled": True,
                    "created_at": time.time(),
                    "notes": "50% Early Bird Discount"
                }
            }
            cls._save_coupons(initial)
            return initial

        try:
            with open(COUPONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @classmethod
    def _save_coupons(cls, data: Dict[str, Dict[str, Any]]):
        with open(COUPONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def _load_licenses(cls) -> Dict[str, Dict[str, Any]]:
        if not os.path.isfile(LICENSES_FILE):
            return {}
        try:
            with open(LICENSES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @classmethod
    def _save_licenses(cls, data: Dict[str, Dict[str, Any]]):
        with open(LICENSES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def create_coupon(
        cls,
        code: str,
        discount_type: str = "percent",
        value: float = 100,
        max_uses: int = 100,
        days_valid: int = 90,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Admin creates a new coupon code."""
        code = code.strip().upper()
        if not code:
            raise ValueError("Coupon code cannot be empty.")
            
        coupons = cls._load_coupons()
        coupon_data = {
            "code": code,
            "discount_type": discount_type,
            "value": value,
            "max_uses": max_uses,
            "current_uses": 0,
            "expires_at": time.time() + (days_valid * 86400),
            "enabled": True,
            "created_at": time.time(),
            "notes": notes
        }
        coupons[code] = coupon_data
        cls._save_coupons(coupons)
        return coupon_data

    @classmethod
    def redeem_coupon(cls, code: str, user_email: Optional[str] = None) -> Dict[str, Any]:
        """Redeem a coupon and issue a license token."""
        code = code.strip().upper()
        coupons = cls._load_coupons()

        if code not in coupons:
            return {"success": False, "error": "Invalid coupon code."}

        c = coupons[code]
        if not c.get("enabled", True):
            return {"success": False, "error": "This coupon code has been deactivated."}

        if time.time() > c.get("expires_at", 0):
            return {"success": False, "error": "This coupon code has expired."}

        if c.get("current_uses", 0) >= c.get("max_uses", 0):
            return {"success": False, "error": "This coupon code has reached its maximum redemptions."}

        # Increment usage
        c["current_uses"] = c.get("current_uses", 0) + 1
        coupons[code] = c
        cls._save_coupons(coupons)

        # Generate activated license key
        license_key = f"PENTA-PRO-{uuid.uuid4().hex[:12].upper()}"
        days = int(c["value"]) if c["discount_type"] == "free_trial" else 365
        expires = time.time() + (days * 86400)

        licenses = cls._load_licenses()
        licenses[license_key] = {
            "license_key": license_key,
            "plan": "pro",
            "redeemed_via": code,
            "user_email": user_email or "anonymous@penta.ai",
            "activated_at": time.time(),
            "expires_at": expires,
            "active": True
        }
        cls._save_licenses(licenses)

        return {
            "success": True,
            "license_key": license_key,
            "plan": "pro",
            "discount_type": c["discount_type"],
            "discount_value": c["value"],
            "expires_at": expires,
            "message": f"Successfully activated Pro access via coupon {code}!"
        }

    @classmethod
    def list_coupons(cls) -> List[Dict[str, Any]]:
        """List all coupons for the admin panel."""
        coupons = cls._load_coupons()
        return list(coupons.values())

    @classmethod
    def toggle_coupon(cls, code: str, enabled: bool) -> bool:
        """Toggle coupon active status."""
        code = code.strip().upper()
        coupons = cls._load_coupons()
        if code in coupons:
            coupons[code]["enabled"] = enabled
            cls._save_coupons(coupons)
            return True
        return False

    @classmethod
    def verify_license(cls, license_key: str) -> Dict[str, Any]:
        """Verify an activated license key."""
        license_key = license_key.strip().upper()
        licenses = cls._load_licenses()
        if license_key in licenses:
            lic = licenses[license_key]
            if lic.get("active") and time.time() < lic.get("expires_at", 0):
                return {"valid": True, "plan": lic.get("plan", "pro"), "expires_at": lic.get("expires_at")}
        return {"valid": False, "error": "Invalid or expired license key."}
