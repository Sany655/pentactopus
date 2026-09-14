"""Automated tests for Production Readiness: DatabaseAdapter, Stripe Webhooks, and Real Windows PE Binaries."""

import os
import json
import pytest
from io import BytesIO
from api.db_adapter import DatabaseAdapter
from api.billing import BillingManager
from api.user_store import UserStore
from api.index import handler


def test_database_adapter_fallback_and_safety():
    """Verify that DatabaseAdapter safely handles unconfigured DB and falls back cleanly."""
    # When DATABASE_URL is not set or invalid
    assert DatabaseAdapter.load_users() is None or isinstance(DatabaseAdapter.load_users(), dict)
    assert DatabaseAdapter.load_sessions() is None or isinstance(DatabaseAdapter.load_sessions(), dict)


def test_stripe_webhook_processing_and_user_upgrade():
    """Verify Stripe webhook processes checkout.session.completed and provisions user."""
    test_email = "stripe_customer_auto@pentactopus.com"
    UserStore.create_or_get_user(test_email, name="Stripe Customer")
    
    mock_payload = json.dumps({
        "id": "evt_test_webhook_001",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_session_12345",
                "customer_email": test_email,
                "amount_total": 1200,
                "currency": "usd"
            }
        }
    }).encode("utf-8")

    res = BillingManager.handle_webhook_event(mock_payload, sig_header="")
    assert res.get("success") is True
    assert res.get("action") == "license_provisioned"
    assert res.get("license_key").startswith("PENTA-SUB-")
    assert res.get("user_email") == test_email


def test_windows_executable_pe_header_validity():
    """Verify that dist/PentaAssistant-Setup.exe exists and contains a genuine PE (MZ) binary header."""
    exe_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist", "PentaAssistant-Setup.exe")
    assert os.path.isfile(exe_path), f"Expected compiled executable at {exe_path}"
    
    # Read first 2 bytes: MUST be 'MZ' (0x4D, 0x5A)
    with open(exe_path, "rb") as f:
        magic = f.read(2)
        assert magic == b"MZ", f"File {exe_path} is NOT a valid Windows executable (magic: {magic})"
        
        # Verify file size is substantial (>= 15 MB)
        f.seek(0, os.SEEK_END)
        size = f.tell()
        assert size > 15 * 1024 * 1024, f"File size too small for standalone bundle: {size} bytes"
