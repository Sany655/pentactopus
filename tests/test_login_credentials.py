"""Test login flow for registered user."""
import json
import urllib.request
import pytest
from api.user_store import UserStore


def test_api_login_credentials():
    """Verify backend authentication for user ustc79069@gmail.com."""
    user, token = UserStore.authenticate_user("ustc79069@gmail.com", "asddfasdf")
    assert user["email"] == "ustc79069@gmail.com"
    assert token.startswith("penta_sess_")
    assert user["role"] == "free_user"
