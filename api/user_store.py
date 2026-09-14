"""User Store & Role-Based Access Control (RBAC) Engine for Penta-Assistant.

Manages user identities, roles (admin, subscriber, free_user), subscription status,
license keys, and coupon redemption associations.
"""

import json
import os
import time
import uuid
from typing import Dict, Any, List, Optional

# In Vercel / serverless environments, /var/task is read-only.
# /tmp is the standard writable directory across serverless providers.
if os.getenv("VERCEL") or os.name != "nt":
    DATA_DIR = "/tmp/penta_data"
else:
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

try:
    os.makedirs(DATA_DIR, exist_ok=True)
except Exception:
    DATA_DIR = "/tmp/penta_data"
    os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, "users.json")


class UserStore:
    """In-memory and file-backed user and role store."""
    _mem_users: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def _get_seed_users(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "admin@pentactopus.com": {
                "email": "admin@pentactopus.com",
                "name": "System Administrator",
                "role": "admin",
                "plan": "enterprise",
                "license_key": "PENTA-ADMIN-MASTER-001",
                "expires_at": time.time() + (3650 * 86400),
                "created_at": time.time(),
                "redeemed_coupons": ["MASTER"],
                "paired_devices": ["win-pc-office", "pixel-9-pro"]
            },
            "alex@pro.com": {
                "email": "alex@pro.com",
                "name": "Alex Rivera",
                "role": "subscriber",
                "plan": "pro",
                "license_key": "PENTA-PRO-2026-X7K",
                "expires_at": time.time() + (365 * 86400),
                "created_at": time.time() - 86400 * 10,
                "redeemed_coupons": ["PENTAFREE"],
                "paired_devices": ["workstation-win11", "galaxy-s24-ultra"]
            },
            "guest@free.com": {
                "email": "guest@free.com",
                "name": "Guest Explorer",
                "role": "free_user",
                "plan": "free",
                "license_key": None,
                "expires_at": None,
                "created_at": time.time() - 86400 * 2,
                "redeemed_coupons": [],
                "paired_devices": ["laptop-surface"]
            }
        }

    @classmethod
    def _load_users(cls) -> Dict[str, Dict[str, Any]]:
        if cls._mem_users:
            return cls._mem_users

        if os.path.isfile(USERS_FILE):
            try:
                with open(USERS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cls._mem_users = data
                    return cls._mem_users
            except Exception:
                pass

        cls._mem_users = cls._get_seed_users()
        cls._save_users(cls._mem_users)
        return cls._mem_users

    @classmethod
    def _save_users(cls, users: Dict[str, Dict[str, Any]]) -> None:
        cls._mem_users = users
        try:
            with open(USERS_FILE, "w", encoding="utf-8") as f:
                json.dump(users, f, indent=2)
        except Exception:
            # Serverless fallback to memory
            pass

    @classmethod
    def list_users(cls) -> List[Dict[str, Any]]:
        """Return all users formatted for admin management."""
        users = cls._load_users()
        return list(users.values())

    @classmethod
    def get_user(cls, email: str) -> Optional[Dict[str, Any]]:
        """Retrieve user by email or return None."""
        if not email:
            return None
        users = cls._load_users()
        return users.get(email.lower().strip())

    @classmethod
    def create_or_get_user(
        cls,
        email: str,
        name: Optional[str] = None,
        role: str = "free_user",
        plan: str = "free"
    ) -> Dict[str, Any]:
        """Fetch existing user or create a new one."""
        email = email.lower().strip()
        users = cls._load_users()
        if email in users:
            return users[email]

        user = {
            "email": email,
            "name": name or email.split("@")[0].capitalize(),
            "role": role,
            "plan": plan,
            "license_key": None,
            "expires_at": None,
            "created_at": time.time(),
            "redeemed_coupons": [],
            "paired_devices": []
        }
        users[email] = user
        cls._save_users(users)
        return user

    @classmethod
    def update_role(
        cls,
        email: str,
        role: str,
        plan: Optional[str] = None
    ) -> Dict[str, Any]:
        """Admin operation: promote/demote user role and assign plan tier."""
        email = email.lower().strip()
        users = cls._load_users()
        if email not in users:
            user = cls.create_or_get_user(email, role=role, plan=plan or "free")
            users = cls._load_users()
        else:
            user = users[email]

        valid_roles = ["admin", "subscriber", "free_user"]
        if role not in valid_roles:
            raise ValueError(f"Invalid role '{role}'. Must be one of {valid_roles}")

        user["role"] = role
        if plan:
            user["plan"] = plan
            if plan in ["pro", "team", "enterprise"] and not user.get("license_key"):
                user["license_key"] = f"PENTA-ADMIN-GRANT-{uuid.uuid4().hex[:8].upper()}"
                user["expires_at"] = time.time() + (365 * 86400)
        elif role == "admin":
            user["plan"] = "enterprise"
            user["license_key"] = user.get("license_key") or f"PENTA-ADMIN-{uuid.uuid4().hex[:8].upper()}"
        elif role == "free_user":
            user["plan"] = "free"

        users[email] = user
        cls._save_users(users)
        return user

    @classmethod
    def grant_subscription(
        cls,
        email: str,
        plan: str = "pro",
        days: int = 365,
        license_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Grant a subscription with license key to a user."""
        email = email.lower().strip()
        users = cls._load_users()
        user = users.get(email) or cls.create_or_get_user(email)

        user["role"] = "subscriber"
        user["plan"] = plan
        user["license_key"] = license_key or f"PENTA-{plan.upper()}-{uuid.uuid4().hex[:8].upper()}"
        user["expires_at"] = time.time() + (days * 86400)
        users[email] = user
        cls._save_users(users)
        return user

    @classmethod
    def associate_coupon_redemption(
        cls,
        email: str,
        coupon_code: str,
        license_key: str,
        days: int
    ) -> Dict[str, Any]:
        """Link redeemed coupon to user account."""
        email = email.lower().strip()
        users = cls._load_users()
        user = users.get(email) or cls.create_or_get_user(email)

        user["role"] = "subscriber"
        user["plan"] = "pro"
        user["license_key"] = license_key
        user["expires_at"] = time.time() + (days * 86400)
        if "redeemed_coupons" not in user:
            user["redeemed_coupons"] = []
        if coupon_code not in user["redeemed_coupons"]:
            user["redeemed_coupons"].append(coupon_code)

        users[email] = user
        cls._save_users(users)
        return user
