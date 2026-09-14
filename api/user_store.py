"""User Store, PBKDF2 Password Hashing, Session Management & Brute-Force Shield for Pentactopus.

Provides enterprise-grade RBAC, salted PBKDF2-SHA256 password hashing (100k rounds),
cryptographic session tokens, and IP/account brute-force lockout defenses.
"""

import json
import os
import time
import uuid
import hashlib
import hmac
import secrets
from typing import Dict, Any, List, Optional, Tuple
from api.db_adapter import DatabaseAdapter

# Serverless writable path
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
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.json")

# Brute-force policy: 5 failed attempts -> 15 min (900s) lockout
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 900
ATTEMPT_WINDOW_SECONDS = 300


def hash_password(password: str) -> str:
    """Generate salted PBKDF2-HMAC-SHA256 hash with 100,000 iterations."""
    salt = secrets.token_bytes(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return f"pbkdf2:sha256:100000${salt.hex()}${key.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored PBKDF2 hash using constant-time comparison."""
    try:
        parts = stored_hash.split("$")
        if len(parts) != 3:
            return False
        algo_info, salt_hex, key_hex = parts
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(key_hex)
        actual_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return hmac.compare_digest(actual_key, expected_key)
    except Exception:
        return False


class AuthError(Exception):
    """Authentication or authorization validation error."""
    pass


class LockoutError(AuthError):
    """Account or IP temporarily locked due to brute-force detection."""
    def __init__(self, message: str, retry_after: int):
        super().__init__(message)
        self.retry_after = retry_after


class UserStore:
    """Enterprise-grade persistent user and session registry."""
    _mem_users: Dict[str, Dict[str, Any]] = {}
    _mem_sessions: Dict[str, Dict[str, Any]] = {}
    _failed_attempts: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def _get_seed_users(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "admin@pentactopus.com": {
                "id": "usr_admin_master",
                "email": "admin@pentactopus.com",
                "name": "System Administrator",
                "password_hash": hash_password("PentaAdmin2026!"),
                "role": "admin",
                "plan": "enterprise",
                "license_key": "PENTA-ADMIN-MASTER-001",
                "expires_at": time.time() + (3650 * 86400),
                "created_at": time.time(),
                "paired_devices": ["workstation-core", "pixel-9-pro"]
            },
            "alex@pentactopus.com": {
                "id": "usr_alex_pro",
                "email": "alex@pentactopus.com",
                "name": "Alex Rivera",
                "password_hash": hash_password("PentaPro2026!"),
                "role": "subscriber",
                "plan": "pro",
                "license_key": "PENTA-PRO-2026-X7K",
                "expires_at": time.time() + (365 * 86400),
                "created_at": time.time() - 86400 * 10,
                "paired_devices": ["dell-xps-15", "galaxy-s24-ultra"]
            },
            "guest@pentactopus.com": {
                "id": "usr_guest_free",
                "email": "guest@pentactopus.com",
                "name": "Guest Explorer",
                "password_hash": hash_password("PentaFree2026!"),
                "role": "free_user",
                "plan": "free",
                "license_key": None,
                "expires_at": None,
                "created_at": time.time() - 86400 * 2,
                "paired_devices": ["laptop-surface"]
            }
        }

    @classmethod
    def _load_users(cls) -> Dict[str, Dict[str, Any]]:
        if cls._mem_users:
            return cls._mem_users

        # 1. Check PostgreSQL / Supabase if DATABASE_URL is configured
        db_users = DatabaseAdapter.load_users()
        if db_users:
            cls._mem_users = db_users
            return cls._mem_users

        # 2. Check local file storage
        if os.path.isfile(USERS_FILE):
            try:
                with open(USERS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "admin@pentactopus.com" in data and "password_hash" in data["admin@pentactopus.com"]:
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
            pass

        # Persist to database if configured
        if DatabaseAdapter.is_postgres_configured():
            for u in users.values():
                DatabaseAdapter.save_user(u)

    @classmethod
    def _load_sessions(cls) -> Dict[str, Dict[str, Any]]:
        if cls._mem_sessions:
            return cls._mem_sessions

        db_sessions = DatabaseAdapter.load_sessions()
        if db_sessions:
            cls._mem_sessions = db_sessions
            return cls._mem_sessions

        if os.path.isfile(SESSIONS_FILE):
            try:
                with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
                    cls._mem_sessions = json.load(f)
                    return cls._mem_sessions
            except Exception:
                pass
        return cls._mem_sessions

    @classmethod
    def _save_sessions(cls, sessions: Dict[str, Dict[str, Any]]) -> None:
        cls._mem_sessions = sessions
        try:
            with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(sessions, f, indent=2)
        except Exception:
            pass

        if DatabaseAdapter.is_postgres_configured():
            for s in sessions.values():
                DatabaseAdapter.save_session(s)

    @classmethod
    def check_brute_force(cls, key: str) -> None:
        """Verify that account or client key is not currently locked out."""
        now = time.time()
        record = cls._failed_attempts.get(key)
        if not record:
            return

        lockout_until = record.get("lockout_until", 0)
        if now < lockout_until:
            retry_after = int(lockout_until - now)
            raise LockoutError(
                f"Too many failed login attempts. For security, your access is locked. Retry in {retry_after}s.",
                retry_after=retry_after
            )

        # Reset window if expired
        if now - record.get("last_attempt", 0) > ATTEMPT_WINDOW_SECONDS:
            cls._failed_attempts.pop(key, None)

    @classmethod
    def record_failed_attempt(cls, key: str) -> None:
        """Increment failed attempts and apply lockout if threshold exceeded."""
        now = time.time()
        record = cls._failed_attempts.get(key, {"count": 0, "last_attempt": now, "lockout_until": 0})
        record["count"] += 1
        record["last_attempt"] = now

        if record["count"] >= MAX_FAILED_ATTEMPTS:
            record["lockout_until"] = now + LOCKOUT_DURATION_SECONDS

        cls._failed_attempts[key] = record

    @classmethod
    def reset_failed_attempts(cls, key: str) -> None:
        """Clear failed attempts on successful authentication."""
        cls._failed_attempts.pop(key, None)

    @classmethod
    def register_user(
        cls,
        name: str,
        email: str,
        password: str
    ) -> Tuple[Dict[str, Any], str]:
        """Register a new user account with PBKDF2 hashing."""
        email = email.lower().strip()
        if not email or "@" not in email or "." not in email:
            raise AuthError("Please provide a valid email address.")

        if len(password) < 8:
            raise AuthError("Password must be at least 8 characters long.")

        users = cls._load_users()
        if email in users:
            raise AuthError("An account with this email already exists.")

        user_id = f"usr_{uuid.uuid4().hex[:10]}"
        new_user = {
            "id": user_id,
            "email": email,
            "name": name.strip() or email.split("@")[0].capitalize(),
            "password_hash": hash_password(password),
            "role": "free_user",
            "plan": "free",
            "license_key": None,
            "expires_at": None,
            "created_at": time.time(),
            "paired_devices": []
        }
        users[email] = new_user
        cls._save_users(users)

        token = cls.create_session(email)
        return cls.safe_user(new_user), token

    @classmethod
    def authenticate_user(
        cls,
        email: str,
        password: str,
        client_ip: str = "127.0.0.1"
    ) -> Tuple[Dict[str, Any], str]:
        """Authenticate user credentials with brute-force defense."""
        email = email.lower().strip()
        throttle_key = f"{email}:{client_ip}"

        # 1. Enforce brute-force lockout
        cls.check_brute_force(throttle_key)
        cls.check_brute_force(email)

        # 2. Check user existence
        users = cls._load_users()
        user = users.get(email)
        if not user or not verify_password(password, user.get("password_hash", "")):
            cls.record_failed_attempt(throttle_key)
            cls.record_failed_attempt(email)
            remaining = MAX_FAILED_ATTEMPTS - cls._failed_attempts.get(throttle_key, {}).get("count", 0)
            if remaining > 0:
                raise AuthError(f"Invalid email or password. {remaining} attempt(s) remaining before lockout.")
            else:
                raise LockoutError(
                    f"Account locked due to consecutive failed attempts. Retry in {LOCKOUT_DURATION_SECONDS}s.",
                    retry_after=LOCKOUT_DURATION_SECONDS
                )

        # 3. Success: Reset rate limits and create session
        cls.reset_failed_attempts(throttle_key)
        cls.reset_failed_attempts(email)

        token = cls.create_session(email)
        return cls.safe_user(user), token

    @classmethod
    def create_session(cls, email: str) -> str:
        """Issue a cryptographically secure 7-day Bearer session token."""
        token = f"penta_sess_{secrets.token_hex(24)}"
        sessions = cls._load_sessions()
        sessions[token] = {
            "email": email,
            "created_at": time.time(),
            "expires_at": time.time() + (7 * 86400)
        }
        cls._save_sessions(sessions)
        return token

    @classmethod
    def validate_session(cls, token: str) -> Optional[Dict[str, Any]]:
        """Validate session token and return user profile if active."""
        if not token:
            return None
        cleaned = token.replace("Bearer ", "").strip()
        sessions = cls._load_sessions()
        sess = sessions.get(cleaned)
        if not sess:
            return None

        if time.time() > sess.get("expires_at", 0):
            sessions.pop(cleaned, None)
            cls._save_sessions(sessions)
            return None

        users = cls._load_users()
        user = users.get(sess.get("email"))
        return cls.safe_user(user) if user else None

    @classmethod
    def revoke_session(cls, token: str) -> bool:
        """Logout and invalidate active session token."""
        if not token:
            return False
        cleaned = token.replace("Bearer ", "").strip()
        sessions = cls._load_sessions()
        if cleaned in sessions:
            sessions.pop(cleaned)
            cls._save_sessions(sessions)
            DatabaseAdapter.delete_session(cleaned)
            return True
        return False

    @classmethod
    def safe_user(cls, user: Dict[str, Any]) -> Dict[str, Any]:
        """Strip password hash and sensitive keys before returning to client."""
        return {
            "id": user.get("id"),
            "name": user.get("name"),
            "email": user.get("email"),
            "role": user.get("role", "free_user"),
            "plan": user.get("plan", "free"),
            "license_key": user.get("license_key"),
            "expires_at": user.get("expires_at"),
            "created_at": user.get("created_at"),
            "paired_devices": user.get("paired_devices", []),
            "redeemed_coupons": user.get("redeemed_coupons", [])
        }

    @classmethod
    def list_users(cls) -> List[Dict[str, Any]]:
        """Return safe list of all registered users."""
        users = cls._load_users()
        return [cls.safe_user(u) for u in users.values()]

    @classmethod
    def get_user(cls, email: str) -> Optional[Dict[str, Any]]:
        """Retrieve safe user profile by email."""
        if not email:
            return None
        users = cls._load_users()
        user = users.get(email.lower().strip())
        return cls.safe_user(user) if user else None

    @classmethod
    def create_or_get_user(
        cls,
        email: str,
        name: Optional[str] = None,
        role: str = "free_user",
        plan: str = "free"
    ) -> Dict[str, Any]:
        """Fetch existing user or provision a new one."""
        email = email.lower().strip()
        users = cls._load_users()
        if email in users:
            return cls.safe_user(users[email])

        user = {
            "id": f"usr_{uuid.uuid4().hex[:10]}",
            "email": email,
            "name": name or email.split("@")[0].capitalize(),
            "password_hash": hash_password("PentaGuestPass2026!"),
            "role": role,
            "plan": plan,
            "license_key": None,
            "expires_at": None,
            "created_at": time.time(),
            "paired_devices": []
        }
        users[email] = user
        cls._save_users(users)
        return cls.safe_user(user)

    @classmethod
    def update_role(
        cls,
        email: str,
        role: str,
        plan: Optional[str] = None
    ) -> Dict[str, Any]:
        """Admin operation: update role and plan tier."""
        email = email.lower().strip()
        users = cls._load_users()
        if email not in users:
            cls.create_or_get_user(email, role=role, plan=plan or "free")
            users = cls._load_users()

        user = users[email]
        valid_roles = ["admin", "subscriber", "free_user"]
        if role not in valid_roles:
            raise ValueError(f"Invalid role '{role}'. Must be one of {valid_roles}")

        user["role"] = role
        if plan:
            user["plan"] = plan
            if plan in ["pro", "team", "enterprise"] and not user.get("license_key"):
                user["license_key"] = f"PENTA-GRANT-{uuid.uuid4().hex[:8].upper()}"
                user["expires_at"] = time.time() + (365 * 86400)
        elif role == "admin":
            user["plan"] = "enterprise"
            user["license_key"] = user.get("license_key") or f"PENTA-ADMIN-{uuid.uuid4().hex[:8].upper()}"
        elif role == "free_user":
            user["plan"] = "free"

        users[email] = user
        cls._save_users(users)
        return cls.safe_user(user)

    @classmethod
    def associate_coupon_redemption(
        cls,
        email: str,
        coupon_code: str,
        license_key: str,
        days: int
    ) -> Dict[str, Any]:
        """Link redeemed promo code to user account."""
        email = email.lower().strip()
        users = cls._load_users()
        if email not in users:
            cls.create_or_get_user(email)
            users = cls._load_users()

        user = users[email]
        user["role"] = "subscriber"
        user["plan"] = "pro"
        user["license_key"] = license_key
        user["expires_at"] = time.time() + (days * 86400)
        if "redeemed_coupons" not in user or not isinstance(user["redeemed_coupons"], list):
            user["redeemed_coupons"] = []
        if coupon_code not in user["redeemed_coupons"]:
            user["redeemed_coupons"].append(coupon_code)
        users[email] = user
        cls._save_users(users)
        return cls.safe_user(user)
