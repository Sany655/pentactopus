"""Vercel Serverless API & Web Handler for Penta-Assistant.

Provides global cloud-hosted endpoints for device discovery, AnyDesk-style
screen streaming, action dispatch, and Google Antigravity multi-model AI.
"""

from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import os
import sys

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from hub.device_hub import DeviceHub
from api.coupons import CouponManager
from api.billing import BillingManager
from api.admin_dashboard import AdminDashboard

class handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_cors(self, code=200, content_type="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_OPTIONS(self):
        self._send_cors(200)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("", "/", "/index.html"):
            self._send_cors(200, "text/html; charset=utf-8")
            html = "<!-- Penta-Assistant Cloud Relay --><html><body><h1>Penta-Assistant Cloud Relay Active</h1></body></html>"
            self.wfile.write(html.encode("utf-8"))
            return

        if path == "/admin":
            self._send_cors(200, "text/html; charset=utf-8")
            self.wfile.write(AdminDashboard.render_admin_html().encode("utf-8"))
            return

        if path == "/api/admin/overview":
            self._send_cors(200)
            self.wfile.write(json.dumps(AdminDashboard.get_overview_metrics()).encode("utf-8"))
            return

        if path == "/api/admin/coupons/list":
            self._send_cors(200)
            self.wfile.write(json.dumps({"coupons": CouponManager.list_coupons()}).encode("utf-8"))
            return

        if path == "/api/devices":
            devices = DeviceHub.get_active_devices()
            self._send_cors(200)
            self.wfile.write(json.dumps({"devices": devices}).encode("utf-8"))
            return

        if path.startswith("/api/device/") and path.endswith("/frame"):
            parts = path.split("/")
            if len(parts) >= 4:
                dev_id = parts[3]
                frame = DeviceHub.get_frame(dev_id)
                if frame:
                    self._send_cors(200, "image/jpeg")
                    self.wfile.write(frame)
                    return
                else:
                    self._send_cors(404)
                    self.wfile.write(json.dumps({"error": "No frame available"}).encode("utf-8"))
                    return

        if path.startswith("/api/device/") and path.endswith("/tasks"):
            parts = path.split("/")
            if len(parts) >= 4:
                dev_id = parts[3]
                tasks = DeviceHub.poll_actions(dev_id)
                self._send_cors(200)
                self.wfile.write(json.dumps({"tasks": tasks}).encode("utf-8"))
                return

        self._send_cors(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length) if length > 0 else b""

        # Binary frame upload
        if path.startswith("/api/device/") and path.endswith("/frame"):
            parts = path.split("/")
            if len(parts) >= 4:
                dev_id = parts[3]
                DeviceHub.set_frame(dev_id, raw_body)
                self._send_cors(200)
                self.wfile.write(json.dumps({"success": True, "size": len(raw_body)}).encode("utf-8"))
                return

        try:
            data = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except Exception:
            data = {}

        if path == "/api/device/register":
            dev = DeviceHub.register_device(
                device_id=data.get("device_id", "unknown"),
                name=data.get("name", "Device"),
                platform=data.get("platform", "windows"),
                resolution=tuple(data.get("resolution", [1080, 2400])),
                capabilities=data.get("capabilities", []),
                connection_type=data.get("connection_type", "cloud_relay")
            )
            self._send_cors(200)
            self.wfile.write(json.dumps({"success": True, "device": dev}).encode("utf-8"))
            return

        if path.startswith("/api/device/") and path.endswith("/action"):
            parts = path.split("/")
            if len(parts) >= 4:
                dev_id = parts[3]
                task_id = DeviceHub.queue_action(dev_id, data)
                self._send_cors(200)
                self.wfile.write(json.dumps({"success": True, "task_id": task_id}).encode("utf-8"))
                return

        if path == "/api/coupons/redeem":
            res = CouponManager.redeem_coupon(data.get("code", ""), data.get("email"))
            self._send_cors(200)
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        if path == "/api/billing/calculate":
            res = BillingManager.calculate_resource_cost(
                devices=data.get("devices", 2),
                ai_tasks_per_day=data.get("ai_tasks", 15),
                stream_hours_per_week=data.get("stream_hours", 10)
            )
            self._send_cors(200)
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        if path == "/api/stripe/create-checkout":
            res = BillingManager.create_checkout_session(
                plan_id=data.get("plan_id", "pro"),
                customer_email=data.get("email", "customer@example.com"),
                coupon_code=data.get("coupon_code")
            )
            self._send_cors(200)
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        if path == "/api/admin/coupons/create":
            try:
                c = CouponManager.create_coupon(
                    code=data.get("code", ""),
                    discount_type=data.get("discount_type", "percent"),
                    value=float(data.get("value", 100)),
                    max_uses=int(data.get("max_uses", 100))
                )
                self._send_cors(200)
                self.wfile.write(json.dumps({"success": True, "coupon": c}).encode("utf-8"))
            except Exception as e:
                self._send_cors(400)
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
            return

        if path == "/api/admin/coupons/toggle":
            ok = CouponManager.toggle_coupon(data.get("code", ""), data.get("enabled", True))
            self._send_cors(200)
            self.wfile.write(json.dumps({"success": ok}).encode("utf-8"))
            return

        self._send_cors(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))
