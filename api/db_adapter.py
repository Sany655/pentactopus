"""Persistent Cloud Database Adapter for Pentatopus.

Provides transparent multi-backend persistence:
- Managed PostgreSQL (Supabase, Neon, AWS RDS, Railway, Render) via DATABASE_URL
- Ephemeral / Local File fallback (users.json, sessions.json, coupons.json) for offline dev & CI/CD
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("pentatopus.db")

try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


class DatabaseAdapter:
    """Unified database interface with auto-table schema creation and fallback."""

    _connection_failed = False
    _initialized = False

    @classmethod
    def get_database_url(cls) -> Optional[str]:
        return os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")

    @classmethod
    def is_postgres_configured(cls) -> bool:
        url = cls.get_database_url()
        return bool(url and PSYCOPG2_AVAILABLE and not cls._connection_failed)

    @classmethod
    def _get_connection(cls):
        if not cls.is_postgres_configured():
            return None
        try:
            url = cls.get_database_url()
            conn = psycopg2.connect(url, connect_timeout=5)
            conn.autocommit = True
            return conn
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed, falling back to local file store: {e}")
            cls._connection_failed = True
            return None

    @classmethod
    def init_schema(cls) -> bool:
        """Create necessary tables if they do not already exist."""
        if not cls.is_postgres_configured() or cls._initialized:
            return False

        conn = cls._get_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS penta_users (
                        email TEXT PRIMARY KEY,
                        id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        password_hash TEXT NOT NULL,
                        role TEXT NOT NULL DEFAULT 'free_user',
                        plan TEXT NOT NULL DEFAULT 'free',
                        license_key TEXT,
                        expires_at DOUBLE PRECISION,
                        created_at DOUBLE PRECISION NOT NULL,
                        paired_devices JSONB DEFAULT '[]'::jsonb
                    );

                    CREATE TABLE IF NOT EXISTS penta_sessions (
                        token TEXT PRIMARY KEY,
                        email TEXT NOT NULL,
                        created_at DOUBLE PRECISION NOT NULL,
                        expires_at DOUBLE PRECISION NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS penta_coupons (
                        code TEXT PRIMARY KEY,
                        discount_type TEXT NOT NULL,
                        value DOUBLE PRECISION NOT NULL,
                        max_uses INT NOT NULL,
                        current_uses INT NOT NULL DEFAULT 0,
                        expires_at DOUBLE PRECISION NOT NULL,
                        enabled BOOLEAN NOT NULL DEFAULT true,
                        created_at DOUBLE PRECISION NOT NULL,
                        notes TEXT
                    );

                    CREATE TABLE IF NOT EXISTS penta_licenses (
                        license_key TEXT PRIMARY KEY,
                        plan TEXT NOT NULL DEFAULT 'pro',
                        redeemed_via TEXT,
                        user_email TEXT NOT NULL,
                        activated_at DOUBLE PRECISION NOT NULL,
                        expires_at DOUBLE PRECISION,
                        active BOOLEAN NOT NULL DEFAULT true
                    );
                """)
            cls._initialized = True
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error initializing database schema: {e}")
            conn.close()
            return False

    # -------------------------------------------------------------------------
    # Users Repository
    # -------------------------------------------------------------------------
    @classmethod
    def load_users(cls) -> Optional[Dict[str, Dict[str, Any]]]:
        if not cls.is_postgres_configured():
            return None
        cls.init_schema()
        conn = cls._get_connection()
        if not conn:
            return None

        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM penta_users")
                rows = cur.fetchall()
                users = {}
                for row in rows:
                    u = dict(row)
                    if isinstance(u.get("paired_devices"), str):
                        try:
                            u["paired_devices"] = json.loads(u["paired_devices"])
                        except Exception:
                            u["paired_devices"] = []
                    users[u["email"]] = u
                conn.close()
                return users
        except Exception as e:
            logger.error(f"Failed to load users from DB: {e}")
            conn.close()
            return None

    @classmethod
    def save_user(cls, user: Dict[str, Any]) -> bool:
        if not cls.is_postgres_configured():
            return False
        cls.init_schema()
        conn = cls._get_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO penta_users (email, id, name, password_hash, role, plan, license_key, expires_at, created_at, paired_devices)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (email) DO UPDATE SET
                        id = EXCLUDED.id,
                        name = EXCLUDED.name,
                        password_hash = EXCLUDED.password_hash,
                        role = EXCLUDED.role,
                        plan = EXCLUDED.plan,
                        license_key = EXCLUDED.license_key,
                        expires_at = EXCLUDED.expires_at,
                        paired_devices = EXCLUDED.paired_devices;
                """, (
                    user["email"],
                    user.get("id", ""),
                    user.get("name", ""),
                    user.get("password_hash", ""),
                    user.get("role", "free_user"),
                    user.get("plan", "free"),
                    user.get("license_key"),
                    user.get("expires_at"),
                    user.get("created_at", time.time()),
                    json.dumps(user.get("paired_devices", []))
                ))
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save user to DB: {e}")
            conn.close()
            return False

    # -------------------------------------------------------------------------
    # Sessions Repository
    # -------------------------------------------------------------------------
    @classmethod
    def load_sessions(cls) -> Optional[Dict[str, Dict[str, Any]]]:
        if not cls.is_postgres_configured():
            return None
        cls.init_schema()
        conn = cls._get_connection()
        if not conn:
            return None

        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM penta_sessions")
                rows = cur.fetchall()
                sessions = {r["token"]: dict(r) for r in rows}
                conn.close()
                return sessions
        except Exception as e:
            logger.error(f"Failed to load sessions from DB: {e}")
            conn.close()
            return None

    @classmethod
    def save_session(cls, session: Dict[str, Any]) -> bool:
        if not cls.is_postgres_configured():
            return False
        cls.init_schema()
        conn = cls._get_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO penta_sessions (token, email, created_at, expires_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (token) DO UPDATE SET
                        email = EXCLUDED.email,
                        expires_at = EXCLUDED.expires_at;
                """, (
                    session["token"],
                    session["email"],
                    session.get("created_at", time.time()),
                    session.get("expires_at", time.time() + 7 * 86400)
                ))
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save session to DB: {e}")
            conn.close()
            return False

    @classmethod
    def delete_session(cls, token: str) -> bool:
        if not cls.is_postgres_configured():
            return False
        cls.init_schema()
        conn = cls._get_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM penta_sessions WHERE token = %s", (token,))
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            conn.close()
            return False
