"""Unified Web UI Dashboard for Android Computer-Use AI Agent & Organization.

Features:
- Multi-threaded non-blocking HTTP server
- Multi-device management (USB & Wi-Fi device targeting)
- Real-time device connection pre-flight validation
- Live execution streaming and activity logs
- Direct Wi-Fi IP connection and wireless switching
- scrcpy mirror launcher with diagnostic feedback and serial targeting
- Safe screenshot capture with graceful SVG placeholder fallbacks
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sys
import subprocess
import threading
import webbrowser
import time
import re

PORT = 5050
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from adb.client import ADBClient, ADBError
from models.router import get_model_provider, PROVIDER_REGISTRY
from tools.cloud_tunnel import CloudTunnelManager
from organization.remote_bridge import RemoteDeviceRegistry
from pc_control.desktop_controller import DesktopController
from agent.pc_agent import PCAgent
from hub.device_hub import DeviceHub
from api.coupons import CouponManager
from api.billing import BillingManager, PLANS
from api.admin_dashboard import AdminDashboard
from api.user_store import UserStore

REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# Load .env into os.environ at startup
env_path = os.path.join(BASE_DIR, ".env")
if os.path.isfile(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    ACTIVE_SERIAL = None

    def log_message(self, format, *args):
        # Suppress verbose terminal logging of static polling
        pass

    @classmethod
    def get_target_serial(cls):
        adb = ADBClient()
        devices = adb.get_devices()
        active_devices = [d["serial"] for d in devices if d["state"] == "device"]
        if cls.ACTIVE_SERIAL and cls.ACTIVE_SERIAL in active_devices:
            return cls.ACTIVE_SERIAL
        return adb.get_active_serial()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ["/", "/index.html", "/dashboard"]:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))

        elif path == "/api/status":
            self.handle_get_status()

        elif path == "/api/screenshot":
            self.handle_get_screenshot()

        elif path == "/api/reports":
            self.handle_get_reports()

        elif path.startswith("/api/report/"):
            fname = os.path.basename(path)
            fpath = os.path.join(REPORTS_DIR, fname)
            if os.path.isfile(fpath):
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                self._send_json({"filename": fname, "content": content})
            else:
                self._send_json({"error": "Report not found"}, 404)

        elif path == "/api/tunnel/status":
            self._send_json(CloudTunnelManager.get_status())

        elif path == "/api/remote/devices":
            self._send_json({"devices": RemoteDeviceRegistry.get_active_devices()})

        elif path == "/api/pc/screen":
            self.handle_get_pc_screen()

        elif path == "/admin":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(AdminDashboard.render_admin_html().encode("utf-8"))

        elif path == "/api/admin/overview":
            self._send_json(AdminDashboard.get_overview_metrics())

        elif path == "/api/admin/users":
            self._send_json({"users": UserStore.list_users()})

        elif path == "/api/user/profile":
            query = urllib.parse.parse_qs(parsed.query)
            email = query.get("email", ["alex@pro.com"])[0]
            user = UserStore.get_user(email) or UserStore.create_or_get_user(email)
            self._send_json({"user": user})

        elif path == "/api/admin/coupons/list":
            self._send_json({"coupons": CouponManager.list_coupons()})

        elif path.startswith("/download/"):
            fname = os.path.basename(path)
            self.send_response(200)
            self.send_header("Content-Disposition", f'attachment; filename="{fname}"')
            self.send_header("Content-Type", "application/octet-stream")
            self.end_headers()
            self.wfile.write(f"Mock binary installer data for {fname}".encode("utf-8"))

        else:
            self.send_error(404, "Not found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        if path == "/api/config":
            self.handle_save_config(data)

        elif path == "/api/test-model":
            self.handle_test_model(data)

        elif path == "/api/pc/click":
            self.handle_pc_click(data)

        elif path == "/api/pc/action":
            self.handle_pc_action(data)

        elif path == "/api/pc/type":
            self.handle_pc_type(data)

        elif path == "/api/pc/agent":
            self.handle_pc_agent(data)
        elif path == "/api/mobile/click":
            self.handle_mobile_click(data)

        elif path == "/api/mobile/action":
            self.handle_mobile_action(data)

        elif path == "/api/mobile/swipe":
            self.handle_mobile_swipe(data)

        elif path == "/api/mobile/launch":
            self.handle_mobile_launch(data)

        elif path == "/api/mobile/type":
            self.handle_mobile_type(data)
        elif path == "/api/admin/coupons/create":
            try:
                c = CouponManager.create_coupon(
                    code=data.get("code", ""),
                    discount_type=data.get("discount_type", "percent"),
                    value=float(data.get("value", 100)),
                    max_uses=int(data.get("max_uses", 100))
                )
                self._send_json({"success": True, "coupon": c})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)})

        elif path == "/api/admin/coupons/toggle":
            ok = CouponManager.toggle_coupon(data.get("code", ""), data.get("enabled", True))
            self._send_json({"success": ok})

        elif path == "/api/admin/user/role":
            try:
                user = UserStore.update_role(data.get("email"), data.get("role"), data.get("plan"))
                self._send_json({"success": True, "user": user})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)})

        elif path == "/api/coupons/redeem":
            email = data.get("email")
            res = CouponManager.redeem_coupon(data.get("code", ""), email)
            if res.get("valid") and email:
                UserStore.associate_coupon_redemption(
                    email=email,
                    coupon_code=data.get("code", ""),
                    license_key=res.get("license_key", ""),
                    days=res.get("days", 365)
                )
            self._send_json(res)

        elif path == "/api/billing/calculate":
            res = BillingManager.calculate_resource_cost(
                devices=data.get("devices", 2),
                ai_tasks_per_day=data.get("ai_tasks", 15),
                stream_hours_per_week=data.get("stream_hours", 10)
            )
            self._send_json(res)

        elif path == "/api/stripe/create-checkout":
            res = BillingManager.create_checkout_session(
                plan_id=data.get("plan_id", "pro"),
                customer_email=data.get("email", "customer@example.com"),
                coupon_code=data.get("coupon_code")
            )
            self._send_json(res)



        elif path == "/api/tunnel/start":
            res = CloudTunnelManager.start_tunnel(local_port=PORT)
            self._send_json(res)

        elif path == "/api/tunnel/stop":
            CloudTunnelManager.stop_tunnel()
            self._send_json({"running": False, "message": "Tunnel stopped."})

        elif path == "/api/remote/telemetry":
            dev_id = data.get("device_id", "remote_phone")
            res = RemoteDeviceRegistry.register_or_update(dev_id, data)
            self._send_json(res)

        elif path == "/api/connect-ip":
            self.handle_connect_ip(data)

        elif path == "/api/disconnect-device":
            self.handle_disconnect_device(data)

        elif path == "/api/set-active-device":
            self.handle_set_active_device(data)

        elif path == "/api/wireless-switch":
            self.handle_wireless_switch()

        elif path == "/api/scrcpy":
            self.handle_scrcpy()

        elif path == "/api/run-agent":
            self.handle_run_agent(data)

        elif path == "/api/run-organization":
            self.handle_run_organization(data)

        else:
            self.send_error(404, "Not found")

    def _send_json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _get_connected_devices(self):
        try:
            adb = ADBClient()
            devices = adb.get_devices()
            result = []
            for d in devices:
                result.append({
                    "serial": d["serial"],
                    "state": d["state"],
                    "raw": d.get("raw", ""),
                    "is_wireless": ":" in d["serial"]
                })
            return result
        except Exception:
            return []

    def handle_get_status(self):
        devices = self._get_connected_devices()
        active_serial = self.get_target_serial()

        env_file = os.path.join(BASE_DIR, ".env")
        config = {
            "GEMINI_API_KEY": "",
            "OPENAI_API_KEY": "",
            "ANTHROPIC_API_KEY": "",
            "DEEPSEEK_API_KEY": "",
            "GROQ_API_KEY": "",
            "OPENROUTER_API_KEY": "",
            "MODEL_PROVIDER": "gemini",
            "MODEL_NAME": "gemini-2.5-flash"
        }
        if os.path.isfile(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        k, v = line.strip().split("=", 1)
                        config[k.strip()] = v.strip()

        masked_keys = {}
        for k in ["GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY"]:
            raw = config.get(k, "")
            if len(raw) > 8:
                masked_keys[k] = raw[:4] + "*" * (len(raw) - 8) + raw[-4:]
            elif raw:
                masked_keys[k] = "****"
            else:
                masked_keys[k] = ""

        device_details = {}
        if active_serial:
            adb = ADBClient(device_serial=active_serial)
            try:
                code, out, _ = adb.run_command(["shell", "dumpsys", "battery"], timeout_sec=3)
                for line in out.splitlines():
                    if "level:" in line:
                        device_details["battery"] = line.split(":")[-1].strip() + "%"
                        break
                _, m_out, _ = adb.run_command(["shell", "getprop", "ro.product.model"], timeout_sec=3)
                device_details["model"] = m_out.strip()
                _, os_out, _ = adb.run_command(["shell", "getprop", "ro.build.version.release"], timeout_sec=3)
                device_details["android_version"] = os_out.strip()
            except Exception:
                pass

        tunnel_status = CloudTunnelManager.get_status()
        remote_devices = RemoteDeviceRegistry.get_active_devices()

        self._send_json({
            "devices": devices,
            "connected": bool(active_serial),
            "active_serial": active_serial,
            "device_details": device_details,
            "tunnel": tunnel_status,
            "remote_devices": remote_devices,
            "config": {
                "MODEL_PROVIDER": config.get("MODEL_PROVIDER", "gemini"),
                "MODEL_NAME": config.get("MODEL_NAME", "gemini-2.5-flash"),
                "keys": {k: config.get(k, "") for k in masked_keys},
                "masked_keys": masked_keys,
                "available_providers": list(PROVIDER_REGISTRY.keys())
            }
        })

    def handle_get_screenshot(self):
        active_serial = self.get_target_serial()
        if not active_serial:
            self._send_svg_placeholder("No Android Device Connected", "Connect phone via USB or Wi-Fi to view screen")
            return

        adb = ADBClient(device_serial=active_serial)
        try:
            img_bytes = adb.capture_screenshot()
            if img_bytes.startswith(b"\x89PNG"):
                self.send_response(200)
                self.send_header("Content-type", "image/png")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.end_headers()
                self.wfile.write(img_bytes)
                return
        except Exception:
            pass

        self._send_svg_placeholder("Screen Preview (" + str(active_serial) + ")", "Press Refresh or check device lock screen")

    def handle_get_pc_screen(self):
        controller = DesktopController()
        try:
            jpeg_bytes = controller.capture_screen_jpeg(quality=70, max_width=1024)
            self.send_response(200)
            self.send_header("Content-type", "image/jpeg")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(jpeg_bytes)
        except Exception as e:
            self._send_svg_placeholder("PC Screen Error", str(e))

    def handle_pc_click(self, data):
        controller = DesktopController()
        try:
            norm_x = float(data.get("norm_x", 0.5))
            norm_y = float(data.get("norm_y", 0.5))
            btn = data.get("button", "left")
            x, y = controller.scale_coordinates(norm_x, norm_y)
            if data.get("double_click"):
                controller.double_click(x, y)
            else:
                controller.click(x, y, button=btn)
            self._send_json({"success": True, "x": x, "y": y, "button": btn, "message": f"Clicked at ({x}, {y}) on PC"})
        except Exception as e:
            self._send_json({"success": False, "error": str(e)})

    def handle_pc_action(self, data):
        controller = DesktopController()
        act = data.get("action", "").lower().strip()
        try:
            if act == "lock":
                controller.lock_pc()
                self._send_json({"success": True, "message": "Windows PC Locked."})
            elif act in ("win_d", "vol_up", "vol_down", "mute", "play_pause", "enter", "esc", "space", "tab"):
                ok = controller.send_hotkey(act)
                self._send_json({"success": ok, "message": f"Triggered {act} on PC."})
            elif act == "launch_app":
                app = data.get("app", "notepad")
                res = controller.launch_app(app)
                self._send_json(res)
            elif act == "open_url":
                url = data.get("url", "")
                controller.open_url(url)
                self._send_json({"success": True, "message": f"Opened {url} on PC."})
            else:
                self._send_json({"success": False, "error": f"Unknown action '{act}'"})
        except Exception as e:
            self._send_json({"success": False, "error": str(e)})

    def handle_pc_type(self, data):
        controller = DesktopController()
        text = data.get("text", "")
        try:
            if text:
                controller.type_text(text)
            self._send_json({"success": True, "message": f"Typed '{text}' on PC."})
        except Exception as e:
            self._send_json({"success": False, "error": str(e)})

    def handle_pc_agent(self, data):
        goal = data.get("goal", "Show PC desktop")
        provider = data.get("provider", "gemini")
        model_name = data.get("model")
        dry_run = data.get("dry_run", False)
        try:
            m = get_model_provider(provider, model_name=model_name)
            agent = PCAgent(model_provider=m, dry_run=dry_run)
            res = agent.run_goal(goal)
            self._send_json(res)
        except Exception as e:
            self._send_json({"success": False, "error": str(e)})

    def handle_mobile_click(self, data):
        active_serial = self.get_target_serial()
        if not active_serial:
            self._send_json({"success": False, "error": "No Android device connected"})
            return
        adb = ADBClient(device_serial=active_serial)
        try:
            norm_x = float(data.get("norm_x", 0.5))
            norm_y = float(data.get("norm_y", 0.5))
            w, h = adb.get_screen_size()
            x = int(round(norm_x * (w - 1)))
            y = int(round(norm_y * (h - 1)))
            res = adb.tap_point(x, y)
            self._send_json({"success": True, "x": x, "y": y, "message": f"Tapped ({x}, {y}) on Phone"})
        except Exception as e:
            self._send_json({"success": False, "error": str(e)})

    def handle_mobile_action(self, data):
        active_serial = self.get_target_serial()
        if not active_serial:
            self._send_json({"success": False, "error": "No Android device connected"})
            return
        adb = ADBClient(device_serial=active_serial)
        act = data.get("action", "").lower().strip()
        try:
            res = adb.press_key(act)
            self._send_json({"success": True, "action": act, "message": f"Triggered {act} on Phone"})
        except Exception as e:
            self._send_json({"success": False, "error": str(e)})

    def handle_mobile_swipe(self, data):
        active_serial = self.get_target_serial()
        if not active_serial:
            self._send_json({"success": False, "error": "No Android device connected"})
            return
        adb = ADBClient(device_serial=active_serial)
        d = data.get("direction", "up").lower().strip()
        try:
            res = adb.swipe_direction(d)
            self._send_json({"success": True, "direction": d, "message": f"Swiped {d} on Phone"})
        except Exception as e:
            self._send_json({"success": False, "error": str(e)})

    def handle_mobile_launch(self, data):
        active_serial = self.get_target_serial()
        if not active_serial:
            self._send_json({"success": False, "error": "No Android device connected"})
            return
        adb = ADBClient(device_serial=active_serial)
        app = data.get("app", "settings").lower().strip()
        pkg = DeviceHub.ANDROID_APP_PACKAGES.get(app, app)
        try:
            res = adb.launch_package(pkg)
            self._send_json({"success": True, "package": pkg, "message": f"Launched {app} ({pkg}) on Phone"})
        except Exception as e:
            self._send_json({"success": False, "error": str(e)})

    def handle_mobile_type(self, data):
        active_serial = self.get_target_serial()
        if not active_serial:
            self._send_json({"success": False, "error": "No Android device connected"})
            return
        adb = ADBClient(device_serial=active_serial)
        text = data.get("text", "")
        with_enter = data.get("with_enter", False)
        try:
            if text:
                adb.type_text(text)
            if with_enter:
                adb.press_key("enter")
            self._send_json({"success": True, "message": f"Typed '{text}' on Phone"})
        except Exception as e:
            self._send_json({"success": False, "error": str(e)})


    def _send_svg_placeholder(self, title, subtitle):
        svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 360 640">''' + \
              '''<rect width="100%" height="100%" fill="#161b22"/>''' + \
              '''<rect x="20" y="20" width="320" height="600" rx="20" fill="#0d1117" stroke="#30363d" stroke-width="2"/>''' + \
              '''<circle cx="180" cy="45" r="5" fill="#30363d"/>''' + \
              '''<rect x="140" y="42" width="40" height="6" rx="3" fill="#21262d"/>''' + \
              '''<text x="180" y="290" fill="#c9d1d9" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto" font-size="15" text-anchor="middle" font-weight="600">''' + str(title) + '''</text>''' + \
              '''<text x="180" y="320" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto" font-size="12" text-anchor="middle">''' + str(subtitle) + '''</text>''' + \
              '''<circle cx="180" cy="585" r="14" fill="none" stroke="#30363d" stroke-width="2"/>''' + \
              '''</svg>'''
        self.send_response(200)
        self.send_header("Content-type", "image/svg+xml")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(svg.encode("utf-8"))

    def handle_set_active_device(self, data):
        serial = data.get("serial", "").strip()
        DashboardHandler.ACTIVE_SERIAL = serial if serial else None
        self._send_json({"success": True, "active_serial": DashboardHandler.ACTIVE_SERIAL})

    def handle_disconnect_device(self, data):
        serial = data.get("serial", "").strip()
        if not serial:
            self._send_json({"success": False, "error": "No serial specified"})
            return
        res = subprocess.run(["adb", "disconnect", serial], capture_output=True, text=True)
        if DashboardHandler.ACTIVE_SERIAL == serial:
            DashboardHandler.ACTIVE_SERIAL = None
        self._send_json({"success": True, "output": res.stdout.strip()})

    def handle_get_reports(self):
        reports = []
        if os.path.isdir(REPORTS_DIR):
            for f in sorted(os.listdir(REPORTS_DIR), reverse=True):
                if f.endswith(".md"):
                    fpath = os.path.join(REPORTS_DIR, f)
                    reports.append({
                        "filename": f,
                        "size": os.path.getsize(fpath),
                        "mtime": time.ctime(os.path.getmtime(fpath))
                    })
        self._send_json({"reports": reports})

    def handle_save_config(self, data):
        env_file = os.path.join(BASE_DIR, ".env")
        provider = data.get("provider", "gemini").strip()
        model_name = data.get("model_name", "gemini-2.5-flash").strip()
        keys = data.get("keys", {})

        current_env = {}
        if os.path.isfile(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        k, v = line.strip().split("=", 1)
                        current_env[k.strip()] = v.strip()

        current_env["MODEL_PROVIDER"] = provider
        current_env["MODEL_NAME"] = model_name

        if data.get("api_key"):
            key_map = {
                "gemini": "GEMINI_API_KEY",
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "deepseek": "DEEPSEEK_API_KEY",
                "groq": "GROQ_API_KEY",
                "openrouter": "OPENROUTER_API_KEY"
            }
            target_var = key_map.get(provider, "GEMINI_API_KEY")
            current_env[target_var] = data.get("api_key").strip()

        for k, v in keys.items():
            if str(v).strip():
                current_env[k] = str(v).strip()

        with open(env_file, "w", encoding="utf-8") as f:
            for k, v in current_env.items():
                f.write(f"{k}={v}\n")

        for k, v in current_env.items():
            os.environ[k] = v

        self._send_json({"status": "saved", "message": "Unified Model Configuration saved to .env"})

    def handle_test_model(self, data):
        provider = data.get("provider", "gemini")
        model_name = data.get("model_name")
        try:
            p = get_model_provider(provider, model_name=model_name, enable_fallback=False)
            res = p.predict_action(
                goal="Test model connectivity",
                screen_state_text="Elements: [OK button at (500, 500)]"
            )
            self._send_json({"success": True, "action": res, "message": f"{provider} connected successfully!"})
        except Exception as e:
            self._send_json({"success": False, "error": str(e), "message": f"{provider} test error: {e}"})

    def handle_scrcpy(self):
        active_serial = self.get_target_serial()
        if not active_serial:
            self._send_json({
                "success": False,
                "error": "No Android device detected! Please connect phone via USB or Wi-Fi first."
            })
            return

        cmd = [sys.executable, os.path.join(BASE_DIR, "tools", "scrcpy_helper.py"), active_serial]
        subprocess.Popen(cmd)
        self._send_json({
            "success": True,
            "message": f"scrcpy window opened on Windows for {active_serial}!"
        })

    def handle_connect_ip(self, data):
        ip = data.get("ip", "").strip()
        if not ip:
            self._send_json({"success": False, "error": "Please enter a valid IP (e.g. 192.168.1.15)"})
            return
        if ":" not in ip:
            ip = f"{ip}:5555"

        res = subprocess.run(["adb", "connect", ip], capture_output=True, text=True, timeout=10)
        output = res.stdout.strip()
        success = "connected" in output.lower()
        self._send_json({
            "success": success,
            "output": output,
            "message": f"Connected to {ip}!" if success else f"Failed to connect: {output}"
        })

    def handle_wireless_switch(self):
        devices = self._get_connected_devices()
        usb_devices = [d for d in devices if not d["is_wireless"] and d["state"] == "device"]
        if not usb_devices:
            self._send_json({
                "success": False,
                "error": "No USB-connected phone found. Please plug your phone in via USB first to switch it to Wi-Fi mode."
            })
            return

        cmd = [sys.executable, os.path.join(BASE_DIR, "tools", "wireless_adb.py")]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            self._send_json({
                "success": "SUCCESS" in res.stdout,
                "output": res.stdout
            })
        except Exception as e:
            self._send_json({"success": False, "error": str(e)})

    def handle_run_agent(self, data):
        goal = data.get("goal", "Open Android Settings")
        provider = data.get("provider", "mock")
        dry_run = data.get("dry_run", False)
        active_serial = self.get_target_serial()

        cmd = [sys.executable, "-u", os.path.join(BASE_DIR, "main.py"), "--goal", goal, "--provider", provider]
        if dry_run:
            cmd.append("--dry-run")
        if active_serial:
            cmd.extend(["--serial", active_serial])

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
            self._send_json({
                "success": res.returncode == 0,
                "output": res.stdout + "\n" + res.stderr
            })
        except Exception as e:
            self._send_json({"success": False, "error": str(e), "output": str(e)})

    def handle_run_organization(self, data):
        cmd = [sys.executable, "-u", os.path.join(BASE_DIR, "organization", "command_center.py")]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=50)
            self._send_json({
                "success": res.returncode == 0,
                "output": res.stdout + "\n" + res.stderr
            })
        except Exception as e:
            self._send_json({"success": False, "error": str(e), "output": str(e)})

from api.web_template import HTML_PAGE

def main():
    with ThreadedTCPServer(("", PORT), DashboardHandler) as httpd:
        print("="*65)
        print(f"  AI-AGENT COMMAND HUB RUNNING AT http://localhost:{PORT}")
        print("="*65)
        webbrowser.open(f"http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    main()
