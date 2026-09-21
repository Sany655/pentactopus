"""Unit tests for Dynamic STUN/TURN ICE resolution and Android Accessibility dispatch."""

import os
import json
import pytest
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from api.webrtc_signaling import SignalingHub
from android.companion_relay import AndroidCompanionRelay

def test_default_ice_servers():
    # Clear any custom environment variables
    os.environ.pop("TURN_SERVERS_JSON", None)
    os.environ.pop("COTURN_URL", None)
    
    servers = SignalingHub.get_ice_servers()
    assert len(servers) >= 1
    assert "stun:stun.l.google.com:19302" in servers[0]["urls"]

def test_coturn_environment_resolution():
    os.environ["COTURN_URL"] = "turn:turn.pentactopus.app:3478"
    os.environ["COTURN_USERNAME"] = "penta_user"
    os.environ["COTURN_CREDENTIAL"] = "penta_secret_pass"

    try:
        servers = SignalingHub.get_ice_servers()
        assert len(servers) == 2
        turn_entry = servers[1]
        assert turn_entry["urls"] == "turn:turn.pentactopus.app:3478"
        assert turn_entry["username"] == "penta_user"
        assert turn_entry["credential"] == "penta_secret_pass"
    finally:
        os.environ.pop("COTURN_URL", None)
        os.environ.pop("COTURN_USERNAME", None)
        os.environ.pop("COTURN_CREDENTIAL", None)

def test_turn_servers_json_resolution():
    custom_config = [
        {"urls": "turn:relay1.example.com:443", "username": "u1", "credential": "p1"},
        {"urls": "turn:relay2.example.com:443", "username": "u2", "credential": "p2"}
    ]
    os.environ["TURN_SERVERS_JSON"] = json.dumps(custom_config)

    try:
        servers = SignalingHub.get_ice_servers()
        assert len(servers) == 2
        assert servers[0]["urls"] == "turn:relay1.example.com:443"
    finally:
        os.environ.pop("TURN_SERVERS_JSON", None)

def test_companion_relay_accessibility_fallback():
    relay = AndroidCompanionRelay(hub_url="http://localhost:5050")
    # Loopback port 18888 is not running, so _try_accessibility_service should return None
    res = relay._try_accessibility_service({"action": "tap", "norm_x": 0.5, "norm_y": 0.5})
    assert res is None

def test_companion_relay_accessibility_service_dispatch():
    # Mock loopback server on 18888
    received_tasks = []

    class MockA11yHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            received_tasks.append(json.loads(body))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "message": "Gesture dispatched"}).encode("utf-8"))

        def log_message(self, format, *args):
            return

    server = HTTPServer(("127.0.0.1", 18888), MockA11yHandler)
    server_thread = threading.Thread(target=server.handle_request, daemon=True)
    server_thread.start()

    try:
        relay = AndroidCompanionRelay(hub_url="http://localhost:5050")
        success, message = relay.perform_accessibility_action({"action": "tap", "x": 300, "y": 600})
        assert success is True
        assert message == "Gesture dispatched"
        assert len(received_tasks) == 1
        assert received_tasks[0]["action"] == "tap"
    finally:
        server.server_close()
