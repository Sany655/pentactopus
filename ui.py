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

        if path == "/" or path == "/index.html":
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

        elif path == "/api/coupons/redeem":
            res = CouponManager.redeem_coupon(data.get("code", ""), data.get("email"))
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

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Autonomous Cross-Platform AI Command Center</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    :root {
      --bg: #0d1117;
      --card-bg: #161b22;
      --border: #30363d;
      --text: #c9d1d9;
      --heading: #f0f6fc;
      --primary: #238636;
      --primary-hover: #2ea043;
      --accent: #58a6ff;
      --danger: #f85149;
      --warn: #d29922;
      --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--bg); color: var(--text); font-family: var(--font); padding: 18px; line-height: 1.5; }
    .container { max-width: 1250px; margin: 0 auto; }
    header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 16px; border-bottom: 1px solid var(--border); margin-bottom: 20px; flex-wrap: wrap; gap: 10px; }
    h1 { color: var(--heading); font-size: 20px; display: flex; align-items: center; gap: 10px; }
    .badge { font-size: 12px; padding: 4px 10px; border-radius: 12px; background: #238636; color: #fff; font-weight: 500; }
    .badge.offline { background: #484f58; color: #c9d1d9; }
    .badge.wireless { background: #1f6feb; }
    .grid { display: grid; grid-template-columns: 380px 1fr; gap: 20px; }
    @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
    .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 16px; margin-bottom: 18px; }
    .card h2 { color: var(--heading); font-size: 15px; margin-bottom: 12px; border-bottom: 1px solid var(--border); padding-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }
    label { display: block; font-size: 12px; margin-bottom: 5px; color: var(--heading); font-weight: 500; }
    input[type="text"], input[type="password"], select { width: 100%; padding: 8px 12px; background: #0d1117; border: 1px solid var(--border); border-radius: 6px; color: var(--text); font-size: 13px; margin-bottom: 12px; }
    input:focus, select:focus { outline: none; border-color: var(--accent); }
    .btn { background: #21262d; border: 1px solid var(--border); color: var(--heading); padding: 7px 14px; border-radius: 6px; font-size: 13px; font-weight: 500; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: 0.15s; }
    .btn:hover:not(:disabled) { background: #30363d; border-color: #8b949e; }
    .btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .btn-primary { background: var(--primary); border-color: rgba(240,246,252,0.1); color: #fff; }
    .btn-primary:hover:not(:disabled) { background: var(--primary-hover); }
    .btn-accent { background: #1f6feb; color: #fff; border: none; }
    .btn-accent:hover:not(:disabled) { background: #388bfd; }
    .btn-group { display: flex; gap: 8px; flex-wrap: wrap; }
    .device-info { font-size: 13px; }
    .device-info div { margin-bottom: 6px; display: flex; justify-content: space-between; }
    .device-info span.val { color: var(--heading); font-weight: 500; }
    pre { background: #090d13; border: 1px solid var(--border); padding: 12px; border-radius: 6px; font-size: 12px; color: #7ee787; overflow-x: auto; max-height: 280px; font-family: Consolas, monospace; white-space: pre-wrap; line-height: 1.4; }
    .nav-tabs { display: flex; gap: 6px; border-bottom: 1px solid var(--border); margin-bottom: 14px; }
    .tab { padding: 8px 14px; cursor: pointer; border-radius: 6px 6px 0 0; color: var(--text); border: 1px solid transparent; border-bottom: none; font-size: 13px; }
    .tab.active { background: var(--card-bg); border-color: var(--border); color: var(--accent); font-weight: 600; }
    .tab-content { display: none; }
    .tab-content.active { display: block; }
    #screen-preview { max-width: 100%; border-radius: 6px; border: 1px solid var(--border); display: block; margin: 8px auto; max-height: 320px; object-fit: contain; }
    .status-banner { padding: 10px 14px; border-radius: 6px; font-size: 13px; margin-bottom: 14px; display: none; }
    .status-banner.show { display: block; }
    .status-banner.error { background: rgba(248, 81, 73, 0.15); border: 1px solid var(--danger); color: #ff7b72; }
    .status-banner.success { background: rgba(35, 134, 54, 0.15); border: 1px solid var(--primary); color: #7ee787; }
    .status-banner.info { background: rgba(88, 166, 255, 0.15); border: 1px solid var(--accent); color: #79c0ff; }
    .device-badge-row { display: flex; align-items: center; justify-content: space-between; padding: 6px 8px; background: #0d1117; border-radius: 6px; margin-bottom: 6px; border: 1px solid var(--border); }
    .btn-sm { padding: 3px 8px; font-size: 11px; }
    .spinner { display: inline-block; width: 12px; height: 12px; border: 2px solid #fff; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>
        <span>⚡ Penta-Assistant</span><span class="badge" style="background:#58a6ff;color:#0d1117;font-weight:600;">🤖 Google Antigravity + 📡 AnyDesk</span>
        <span id="conn-badge" class="badge offline">Checking connection...</span>
        <span id="tunnel-badge" class="badge" style="display:none; background: #f0883e;">🌐 Cloud Tunnel Live</span>
      </h1>
      <div class="btn-group">
        <button class="btn btn-accent" id="btn-scrcpy" onclick="launchScrcpy()">📱 Launch scrcpy Mirror</button>
        <button class="btn" id="btn-wifi" onclick="switchWireless()">📶 Switch to Wi-Fi</button>
        <button class="btn" onclick="refreshStatus()">🔄 Scan Devices</button>
        <a href="/admin" target="_blank" class="btn btn-sm" style="background:#8957e5; color:#fff; text-decoration:none;">🛡️ Admin Console</a>
      </div>
    </header>

    <!-- Global Alert Banner -->
    <div id="status-banner" class="status-banner"></div>

    <div class="grid">
      <!-- Left Column: Controls & Device -->
      <div>
        <!-- Device Info Card -->
        <div class="card">
          <h2>📱 Android Phone Node</h2>
          <div class="device-info" id="device-box">Scanning for devices...</div>
          <div id="device-switcher-box" style="margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border); display: none;">
            <label>Connected ADB Targets (USB, Wi-Fi, Tailscale Mesh)</label>
            <div id="device-list-container"></div>
          </div>
          
          <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border);">
            <label>Connect to Phone via Wi-Fi or Tailscale IP</label>
            <div style="display: flex; gap: 6px;">
              <input type="text" id="manual-ip" placeholder="192.168.1.15 or 100.85.12.34" style="margin-bottom:0;">
              <button class="btn" onclick="connectManualIp()">Connect</button>
            </div>
            <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Tip: Enter Tailscale 100.x.y.z IP for 4G/5G remote control anywhere!</div>
          </div>
              <button class="btn" onclick="connectManualIp()">Connect</button>
            </div>
          </div>
        </div>

        <!-- AI Model & Unified Gateway -->
        <div class="card">
          <h2>🧠 Unified Multi-Model Gateway</h2>
          <label>Active Provider</label>
          <select id="cfg-provider" onchange="onProviderChanged()">
            <option value="gemini">Google Gemini (Multimodal Vision)</option>
            <option value="openai">OpenAI (GPT-4o, GPT-4o-mini)</option>
            <option value="anthropic">Anthropic Claude (Claude 3.5 Sonnet)</option>
            <option value="deepseek">DeepSeek (DeepSeek-V3, R1)</option>
            <option value="groq">Groq (Ultra-Fast Llama 3.3)</option>
            <option value="openrouter">OpenRouter (200+ Models Aggregator)</option>
            <option value="ollama">Local Offline Ollama</option>
            <option value="mock">Local Offline Mock (No API Key)</option>
          </select>

          <label>Model Identifier</label>
          <input type="text" id="cfg-model" value="gemini-2.5-flash">

          <label id="key-label">Active Provider API Key</label>
          <div style="display: flex; gap: 6px; margin-bottom: 8px;">
            <input type="password" id="cfg-key" placeholder="Enter API key..." style="margin-bottom: 0;">
            <button type="button" class="btn" onclick="toggleKeyVisibility()" id="btn-toggle-key">👁️</button>
          </div>
          <div id="cfg-key-status" style="font-size: 11px; margin-bottom: 12px; color: #8b949e;"></div>

          <div style="display: flex; gap: 8px;">
            <button class="btn btn-primary" style="flex: 1;" onclick="saveConfig()">💾 Save Config</button>
            <button class="btn" onclick="testModelConnectivity()">⚡ Test Model</button>
          </div>
        </div>

        <!-- Live Screenshot Preview -->
        <div class="card">
          <h2>📸 Live Screen Capture <button class="btn" style="padding: 2px 8px; font-size: 11px;" onclick="refreshScreenshot()">Refresh</button></h2>
          <img id="screen-preview" src="/api/screenshot" alt="Screen preview (connect phone to display)">
        </div>
      </div>

      <!-- Right Column: Operations & Workflows -->
      <div>
        <div class="card">
          <div class="nav-tabs">
            <div class="tab active" onclick="switchTab(event, 'viewport-tab')">📡 AnyDesk Remote Viewport</div>
            <div class="tab" onclick="switchTab(event, 'org-tab')">🏢 5-Agent Org Room</div>
            <div class="tab" onclick="switchTab(event, 'single-tab')">🎯 Phone Autonomous Agent</div>
            <div class="tab" onclick="switchTab(event, 'remote-tab')">🌐 Cloud & Vercel Relay</div>
            <div class="tab" onclick="switchTab(event, 'billing-tab')">💎 Pricing & Downloads</div>
            <div class="tab" onclick="switchTab(event, 'reports-tab')">📂 Mission Dossiers</div>
          </div>

                    <!-- Tab 0: AnyDesk Remote Viewport (Cross-Platform) -->
          <div id="viewport-tab" class="tab-content active">
            <!-- Device Sub-Switcher -->
            <div style="display: flex; gap: 8px; margin-bottom: 12px; background: #0d1117; padding: 4px; border-radius: 8px; border: 1px solid var(--border);">
              <button id="btn-sub-pc" class="btn btn-sm btn-accent" style="flex: 1; justify-content: center;" onclick="switchDeviceViewport('pc')">🖥️ Windows PC (Host)</button>
              <button id="btn-sub-phone" class="btn btn-sm" style="flex: 1; justify-content: center;" onclick="switchDeviceViewport('phone')">📱 Android Phone (Node)</button>
            </div>

            <!-- VIEWPORT 1: WINDOWS PC -->
            <div id="view-pc-container">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h3 style="font-size: 14px;">🖥️ Windows PC Live Desktop</h3>
                <div style="display: flex; gap: 6px;">
                  <button class="btn btn-sm" onclick="refreshPcScreen()">🔄 Refresh</button>
                  <label style="font-size: 11px; display: inline-flex; align-items: center; gap: 4px; margin-bottom: 0;">
                    <input type="checkbox" id="pc-auto-stream" onchange="togglePcStream()"> Auto-Stream (1.2s)
                  </label>
                </div>
              </div>

              <!-- Live PC Screen Canvas / Image with Tap-to-Click -->
              <div style="position: relative; background: #000; border: 1px solid var(--border); border-radius: 6px; overflow: hidden; margin-bottom: 8px;">
                <img id="pc-screen" src="/api/pc/screen" alt="PC Screen" style="width: 100%; display: block; cursor: crosshair; object-fit: contain; max-height: 380px;" onclick="onPcScreenClick(event)">
              </div>
              <div style="font-size: 11px; color: #8b949e; margin-bottom: 12px;">
                💡 <strong>Tap anywhere on the desktop above</strong> to click on your PC! Coordinates scale dynamically to your Windows native resolution.
              </div>

              <!-- Quick Action Deck -->
              <h4 style="font-size: 12px; margin-bottom: 6px;">⚡ Quick PC Remote Controls</h4>
              <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 14px;">
                <button class="btn btn-sm" onclick="sendPcAction('win_d')">🪟 Show Desktop</button>
                <button class="btn btn-sm" onclick="sendPcAction('vol_up')">🔊 Vol +</button>
                <button class="btn btn-sm" onclick="sendPcAction('vol_down')">🔉 Vol -</button>
                <button class="btn btn-sm" onclick="sendPcAction('mute')">🔇 Mute</button>
                <button class="btn btn-sm" onclick="sendPcAction('play_pause')">⏯️ Play / Pause</button>
                <button class="btn btn-sm btn-warn" onclick="sendPcAction('lock')">🔒 Lock PC</button>
              </div>

              <!-- App Launcher & URL Opener -->
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px;">
                <div>
                  <label>Launch PC Application</label>
                  <div style="display: flex; gap: 4px;">
                    <select id="pc-app-select" style="margin-bottom:0;">
                      <option value="chrome">Google Chrome</option>
                      <option value="notepad">Notepad</option>
                      <option value="calc">Calculator</option>
                      <option value="explorer">File Explorer</option>
                      <option value="terminal">PowerShell Terminal</option>
                    </select>
                    <button class="btn btn-sm" onclick="launchPcApp()">Open</button>
                  </div>
                </div>
                <div>
                  <label>Open URL in PC Browser</label>
                  <div style="display: flex; gap: 4px;">
                    <input type="text" id="pc-url-input" placeholder="youtube.com" style="margin-bottom:0;">
                    <button class="btn btn-sm" onclick="openPcUrl()">Go</button>
                  </div>
                </div>
              </div>

              <!-- Type into Active PC Window -->
              <div style="margin-bottom: 14px;">
                <label>Send Text to PC (Types into active window)</label>
                <div style="display: flex; gap: 6px;">
                  <input type="text" id="pc-type-input" placeholder="Type words or search queries..." style="margin-bottom:0;">
                  <button class="btn btn-sm" onclick="sendPcType(false)">Send</button>
                  <button class="btn btn-sm btn-primary" onclick="sendPcType(true)">Send + Enter</button>
                </div>
              </div>

              <!-- AI Autonomous PC Agent (Google Antigravity) -->
              <div style="border-top: 1px solid var(--border); padding-top: 12px;">
                <label>🤖 Google Antigravity PC Agent (Autonomous Computer-Use)</label>
                <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                  <input type="text" id="pc-agent-goal" value="Open Notepad and write today's plan" style="margin-bottom:0;">
                  <button class="btn btn-primary" id="btn-pc-agent" onclick="runPcAgent()">🚀 Execute on PC</button>
                </div>
                <pre id="pc-agent-output" style="max-height: 140px;">Ready for PC Antigravity directives...</pre>
              </div>
            </div>

            <!-- VIEWPORT 2: ANDROID PHONE -->
            <div id="view-phone-container" style="display: none;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h3 style="font-size: 14px;">📱 Android Phone Live Screen</h3>
                <div style="display: flex; gap: 6px;">
                  <button class="btn btn-sm" onclick="refreshMobileScreen()">🔄 Refresh</button>
                  <label style="font-size: 11px; display: inline-flex; align-items: center; gap: 4px; margin-bottom: 0;">
                    <input type="checkbox" id="mobile-auto-stream" onchange="toggleMobileStream()"> Auto-Stream (1.2s)
                  </label>
                </div>
              </div>

              <!-- Live Phone Screen Canvas with Tap-to-Touch -->
              <div style="position: relative; background: #000; border: 1px solid var(--border); border-radius: 6px; overflow: hidden; margin-bottom: 8px; text-align: center;">
                <img id="mobile-viewport-screen" src="/api/screenshot" alt="Phone Screen" style="width: 100%; max-height: 400px; display: inline-block; cursor: crosshair; object-fit: contain;" onclick="onMobileScreenClick(event)">
              </div>
              <div style="font-size: 11px; color: #8b949e; margin-bottom: 12px;">
                💡 <strong>Tap anywhere on the phone screen above</strong> to tap on your physical Android phone! Touch coordinates scale dynamically to phone display.
              </div>

              <!-- Hardware Navigation Bar -->
              <h4 style="font-size: 12px; margin-bottom: 6px;">🎮 Hardware Navigation & System Keys</h4>
              <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 14px;">
                <button class="btn btn-sm" onclick="sendMobileAction('back')">◀️ Back</button>
                <button class="btn btn-sm btn-accent" onclick="sendMobileAction('home')">⏺️ Home</button>
                <button class="btn btn-sm" onclick="sendMobileAction('recents')">🔲 Recents</button>
                <button class="btn btn-sm btn-warn" onclick="sendMobileAction('power')">⚡ Power / Wake</button>
                <button class="btn btn-sm" onclick="sendMobileAction('vol_up')">🔊 Vol +</button>
                <button class="btn btn-sm" onclick="sendMobileAction('vol_down')">🔉 Vol -</button>
              </div>

              <!-- Directional Swipes / Scroll Deck -->
              <h4 style="font-size: 12px; margin-bottom: 6px;">👆 Directional Swipes & Gestures</h4>
              <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 14px;">
                <button class="btn btn-sm" onclick="sendMobileSwipe('up')">⬆️ Scroll Down (Swipe Up)</button>
                <button class="btn btn-sm" onclick="sendMobileSwipe('down')">⬇️ Scroll Up (Swipe Down)</button>
                <button class="btn btn-sm" onclick="sendMobileSwipe('left')">⬅️ Swipe Left</button>
                <button class="btn btn-sm" onclick="sendMobileSwipe('right')">➡️ Swipe Right</button>
              </div>

              <!-- Mobile Quick App Launcher -->
              <div style="margin-bottom: 14px;">
                <label>Quick Launch App on Phone</label>
                <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 6px;">
                  <button class="btn btn-sm" onclick="launchMobileQuickApp('settings')">⚙️ Settings</button>
                  <button class="btn btn-sm" onclick="launchMobileQuickApp('chrome')">🌐 Chrome</button>
                  <button class="btn btn-sm" onclick="launchMobileQuickApp('camera')">📷 Camera</button>
                  <button class="btn btn-sm" onclick="launchMobileQuickApp('youtube')">▶️ YouTube</button>
                  <button class="btn btn-sm" onclick="launchMobileQuickApp('calculator')">🔢 Calculator</button>
                  <button class="btn btn-sm" onclick="launchMobileQuickApp('dialer')">📞 Phone</button>
                  <button class="btn btn-sm" onclick="launchMobileQuickApp('whatsapp')">💬 WhatsApp</button>
                </div>
              </div>

              <!-- Remote Text Input for Phone -->
              <div style="margin-bottom: 14px;">
                <label>Send Text to Phone (Types into active text field)</label>
                <div style="display: flex; gap: 6px;">
                  <input type="text" id="mobile-type-input" placeholder="Type message or search query..." style="margin-bottom:0;">
                  <button class="btn btn-sm" onclick="sendMobileType(false)">Send</button>
                  <button class="btn btn-sm btn-primary" onclick="sendMobileType(true)">Send + Enter</button>
                </div>
              </div>

              <!-- Google Antigravity Mobile AI Agent -->
              <div style="border-top: 1px solid var(--border); padding-top: 12px;">
                <label>🤖 Google Antigravity Mobile Agent (Autonomous Computer-Use)</label>
                <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                  <input type="text" id="mobile-agent-goal" value="Open Settings and check battery status" style="margin-bottom:0;">
                  <button class="btn btn-primary" onclick="runMobileAntigravityAgent()">🚀 Execute on Phone</button>
                </div>
                <pre id="mobile-agent-output" style="max-height: 140px;">Ready for Mobile Antigravity directives...</pre>
              </div>
            </div>
          </div>

          <!-- Tab 1: Organization -->
          <div id="org-tab" class="tab-content">
            <p style="font-size: 13px; margin-bottom: 12px; color: #8b949e;">
              Coordinates all 5 departments: <strong>CEO Orchestrator</strong>, <strong>Mobile Node</strong>, <strong>Desktop Node</strong>, <strong>Browser Node</strong>, and <strong>Notifier Node</strong> over the async bus.
            </p>
            <label>Mission Directive</label>
            <input type="text" id="org-goal" value="Audit mobile phone state over ADB, gather intelligence, and generate executive dossier">
            <button class="btn btn-primary" id="btn-org" onclick="runOrganization()">🚀 Run Multi-Agent Mission</button>
            
            <h3 style="font-size: 13px; margin-top: 16px; margin-bottom: 6px;">Live Event Bus Activity</h3>
            <pre id="org-output">Ready to dispatch organizational mission...</pre>
          </div>

          <!-- Tab 2: Single Agent -->
          <div id="single-tab" class="tab-content">
            <label>Target Goal</label>
            <input type="text" id="agent-goal" value="Open Android Settings">
            <div style="margin-bottom: 12px;">
              <input type="checkbox" id="agent-dryrun"> 
              <label for="agent-dryrun" style="display:inline; font-size: 12px;">Simulation Mode (Dry Run without physical touch)</label>
            </div>
            <button class="btn btn-primary" id="btn-single" onclick="runSingleAgent()">▶ Execute Phone Goal</button>
            
            <h3 style="font-size: 13px; margin-top: 16px; margin-bottom: 6px;">Perception & Action Trace</h3>
            <pre id="single-output">Awaiting task execution...</pre>
          </div>

          <!-- Tab 3: Cloud & Remote (4G/5G) -->
          <div id="remote-tab" class="tab-content">
            <h3 style="font-size: 14px; margin-bottom: 8px;">🌐 Cloudflare Public HTTPS Tunnel</h3>
            <p style="font-size: 12px; color: #8b949e; margin-bottom: 12px;">
              Generates an encrypted public HTTPS link so you can open this Command Hub on your phone's browser from anywhere in the world over 4G/5G!
            </p>
            <div style="display: flex; gap: 8px; margin-bottom: 12px;">
              <button class="btn btn-primary" id="btn-tunnel-start" onclick="startCloudTunnel()">🚀 Start Cloudflare Public Tunnel</button>
              <button class="btn" id="btn-tunnel-stop" onclick="stopCloudTunnel()">⏹ Stop Tunnel</button>
            </div>
            <div id="tunnel-info-box" style="padding: 10px; background: #090d13; border: 1px solid var(--border); border-radius: 6px; font-size: 12px; margin-bottom: 16px;">
              Tunnel Status: <strong>Offline</strong> (Local host only)
            </div>

            <h3 style="font-size: 14px; margin-bottom: 8px;">📶 4G/5G Remote ADB via Tailscale Mesh</h3>
            <p style="font-size: 12px; color: #8b949e; margin-bottom: 10px;">
              To control your phone when outside your home Wi-Fi:
              <ol style="margin-left: 20px; font-size: 12px; color: #c9d1d9; line-height: 1.6;">
                <li>Install <strong>Tailscale</strong> on both your PC and Android phone (free).</li>
                <li>Note your phone's Tailscale IP (e.g. <code>100.85.12.34</code>).</li>
                <li>Enter it in the <strong>Connect to Phone via Wi-Fi IP</strong> input box on the left.</li>
                <li>Full wireless ADB and scrcpy mirroring will work across any cellular network!</li>
              </ol>
            </p>
            <div style="margin-top: 14px; font-size: 12px;">
              <a href="/api/report/USER_MANUAL.md" target="_blank" style="color: var(--accent);">📖 Open Remote Access & Architecture Documentation</a>
            </div>
          </div>

          <!-- Tab 4: Reports -->
          <div id="reports-tab" class="tab-content">
            <div style="display: flex; gap: 10px; margin-bottom: 10px;">
              <select id="reports-list" style="margin-bottom:0;" onchange="loadReport()"></select>
              <button class="btn" onclick="fetchReports()">Refresh</button>
            </div>
            <pre id="report-viewer" style="max-height: 480px; color: #c9d1d9;">Select a report to view.</pre>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    let isConnected = false;

    function toggleKeyVisibility() {
      const inp = document.getElementById('cfg-key');
      const btn = document.getElementById('btn-toggle-key');
      if (inp.type === 'password') {
        inp.type = 'text';
        btn.innerText = '🔒 Hide';
      } else {
        inp.type = 'password';
        btn.innerText = '👁️ Show';
      }
    }

    // Save and restore user inputs across browser refreshes
    function restoreLocalInputs() {
      if (localStorage.getItem('org-goal')) {
        document.getElementById('org-goal').value = localStorage.getItem('org-goal');
      }
      if (localStorage.getItem('agent-goal')) {
        document.getElementById('agent-goal').value = localStorage.getItem('agent-goal');
      }
      if (localStorage.getItem('org-output')) {
        document.getElementById('org-output').innerText = localStorage.getItem('org-output');
      }
      if (localStorage.getItem('single-output')) {
        document.getElementById('single-output').innerText = localStorage.getItem('single-output');
      }
      document.getElementById('org-goal').addEventListener('input', (e) => localStorage.setItem('org-goal', e.target.value));
      document.getElementById('agent-goal').addEventListener('input', (e) => localStorage.setItem('agent-goal', e.target.value));
    }

    function showBanner(msg, type='info', timeout=6000) {
      const b = document.getElementById('status-banner');
      b.className = 'status-banner show ' + type;
      b.innerHTML = msg;
      if (timeout > 0) {
        setTimeout(() => { b.className = 'status-banner'; }, timeout);
      }
    }

    async function refreshStatus() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();
        
        const badge = document.getElementById('conn-badge');
        const devBox = document.getElementById('device-box');
        isConnected = data.connected;

        const switcherBox = document.getElementById('device-switcher-box');
        const listContainer = document.getElementById('device-list-container');
        if (data.connected && data.active_serial) {
          const isWireless = data.active_serial.includes(':');
          badge.className = isWireless ? 'badge wireless' : 'badge';
          badge.innerText = isWireless ? '📶 Active: Wi-Fi (' + data.active_serial + ')' : '🔌 Active: USB (' + data.active_serial + ')';

          devBox.innerHTML = `
            <div><span>Model:</span> <span class="val">${data.device_details.model || data.active_serial}</span></div>
            <div><span>Target Serial:</span> <span class="val">${data.active_serial}</span></div>
            <div><span>Connection:</span> <span class="val">${isWireless ? 'Wireless TCP/IP (Port 5555)' : 'USB Data Cable'}</span></div>
            <div><span>Android OS:</span> <span class="val">${data.device_details.android_version || '9'}</span></div>
            <div><span>Battery Level:</span> <span class="val">${data.device_details.battery || 'Checking...'}</span></div>
          `;
        } else {
          badge.className = 'badge offline';
          badge.innerText = '⚠️ No Device Connected';
          devBox.innerHTML = `
            <div style="color: var(--danger); font-weight: 500; margin-bottom: 4px;">No physical phone detected over ADB.</div>
            <div style="font-size: 12px; color: #8b949e;">1. Connect your phone via USB cable.<br>2. Ensure USB Debugging is ON in Settings.<br>3. Or enter phone Wi-Fi IP below.</div>
          `;
        }

        if (switcherBox && listContainer) {
          if (data.devices && data.devices.length > 0) {
            switcherBox.style.display = 'block';
            listContainer.innerHTML = '';
            data.devices.forEach(d => {
              const isTarget = d.serial === data.active_serial;
              const div = document.createElement('div');
              div.className = 'device-badge-row';
              div.innerHTML = `
                <div style="font-size: 12px; display: flex; align-items: center; gap: 6px;">
                  <span>${d.is_wireless ? '📶' : '🔌'}</span>
                  <strong>${d.serial}</strong>
                  <span style="color: ${d.state === 'device' ? '#7ee787' : '#d29922'};">(${d.state})</span>
                  ${isTarget ? '<span style="color: #58a6ff; font-weight: bold; margin-left: 4px;">★ ACTIVE</span>' : ''}
                </div>
                <div style="display: flex; gap: 4px;">
                  ${!isTarget && d.state === 'device' ? `<button class="btn btn-sm" onclick="setActiveDevice('${d.serial}')">Use</button>` : ''}
                  ${d.is_wireless ? `<button class="btn btn-sm" style="color: #ff7b72;" onclick="disconnectDevice('${d.serial}')">Disconnect</button>` : ''}
                </div>
              `;
              listContainer.appendChild(div);
            });
          } else {
            switcherBox.style.display = 'none';
          }
        }

        storedConfig = data.config;
        if (data.config && data.config.MODEL_PROVIDER) {
          document.getElementById('cfg-provider').value = data.config.MODEL_PROVIDER;
          document.getElementById('cfg-model').value = data.config.MODEL_NAME || DEFAULT_MODELS[data.config.MODEL_PROVIDER] || 'gemini-2.5-flash';
        }

        const tunnelBadge = document.getElementById('tunnel-badge');
        const tunnelBox = document.getElementById('tunnel-info-box');
        if (tunnelBadge && tunnelBox) {
          if (data.tunnel && data.tunnel.running && data.tunnel.url) {
            tunnelBadge.style.display = 'inline-block';
            tunnelBox.innerHTML = `
              🟢 Cloudflare Tunnel LIVE: <a href="${data.tunnel.url}" target="_blank" style="color: #58a6ff; font-weight: bold;">${data.tunnel.url}</a><br>
              <span style="color: #8b949e;">Open this exact link on your mobile phone on 4G/5G cellular data to access Command Hub!</span>
            `;
          } else {
            tunnelBadge.style.display = 'none';
            tunnelBox.innerHTML = `Tunnel Status: <strong>Offline</strong> (Local host only)`;
          }
        }
        updateKeyDisplay();
      } catch (e) {
        console.error(e);
      }
    }

    let storedConfig = {};

    const DEFAULT_MODELS = {
      "gemini": "gemini-2.5-flash",
      "openai": "gpt-4o-mini",
      "anthropic": "claude-3-5-sonnet-20241022",
      "deepseek": "deepseek-chat",
      "groq": "llama-3.3-70b-versatile",
      "openrouter": "google/gemini-2.5-flash",
      "ollama": "llama3.2",
      "mock": "mock-v1"
    };

    const PROVIDER_KEY_MAP = {
      "gemini": "GEMINI_API_KEY",
      "openai": "OPENAI_API_KEY",
      "anthropic": "ANTHROPIC_API_KEY",
      "deepseek": "DEEPSEEK_API_KEY",
      "groq": "GROQ_API_KEY",
      "openrouter": "OPENROUTER_API_KEY"
    };

    function onProviderChanged() {
      const p = document.getElementById('cfg-provider').value;
      const modelInput = document.getElementById('cfg-model');
      if (DEFAULT_MODELS[p]) {
        modelInput.value = DEFAULT_MODELS[p];
      }
      updateKeyDisplay();
    }

    function updateKeyDisplay() {
      if (!storedConfig) return;
      const p = document.getElementById('cfg-provider').value;
      const keyInput = document.getElementById('cfg-key');
      const keyLabel = document.getElementById('key-label');
      const keyStatus = document.getElementById('cfg-key-status');
      
      const keyName = PROVIDER_KEY_MAP[p];
      if (!keyName) {
        keyLabel.innerText = "API Key (Not required for " + p + ")";
        keyInput.value = "";
        keyInput.disabled = true;
        keyStatus.innerHTML = `<span style="color: #7ee787;">✅ No API key needed for ${p}</span>`;
        return;
      }

      keyInput.disabled = false;
      keyLabel.innerText = `${p.toUpperCase()} API Key (${keyName})`;
      const rawVal = (storedConfig.keys && storedConfig.keys[keyName]) || "";
      const maskedVal = (storedConfig.masked_keys && storedConfig.masked_keys[keyName]) || "";

      if (rawVal && document.activeElement !== keyInput && (!keyInput.value || keyInput.dataset.autofilled === "true")) {
        keyInput.value = rawVal;
        keyInput.dataset.autofilled = "true";
      }

      if (maskedVal) {
        keyStatus.innerHTML = `✅ Stored in .env: <code>${maskedVal}</code>`;
      } else {
        keyStatus.innerHTML = `<span style="color: var(--warn);">⚠️ No key saved for ${p} yet</span>`;
      }
    }

    async function testModelConnectivity() {
      const p = document.getElementById('cfg-provider').value;
      const model = document.getElementById('cfg-model').value;
      showBanner(`Testing ${p} connectivity...`, "info", 3000);
      try {
        const res = await fetch('/api/test-model', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ provider: p, model_name: model })
        });
        const data = await res.json();
        if (data.success) {
          showBanner(`⚡ Success! ${p} generated action: ` + JSON.stringify(data.action), "success", 6000);
        } else {
          showBanner(`❌ ${data.message}`, "error", 7000);
        }
      } catch (e) {
        showBanner("Test failed: " + e, "error");
      }
    }

    async function startCloudTunnel() {
      showBanner("Launching Cloudflare Public HTTPS Tunnel...", "info", 5000);
      try {
        const res = await fetch('/api/tunnel/start', { method: 'POST' });
        const data = await res.json();
        if (data.running && data.url) {
          showBanner("🌐 Public Tunnel Live: " + data.url, "success", 8000);
        } else {
          showBanner("⚠️ " + (data.message || data.error || "Tunnel starting..."), "info", 5000);
        }
        refreshStatus();
      } catch (e) {
        showBanner("Failed to launch tunnel: " + e, "error");
      }
    }

    async function stopCloudTunnel() {
      try {
        await fetch('/api/tunnel/stop', { method: 'POST' });
        showBanner("Tunnel stopped.", "info", 3000);
        refreshStatus();
      } catch (e) {
        showBanner("Error stopping tunnel: " + e, "error");
      }
    }

    
    async function setActiveDevice(serial) {
      try {
        const res = await fetch('/api/set-active-device', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ serial: serial })
        });
        showBanner(`Switched active target device to ${serial}`, 'info', 3000);
        refreshStatus();
        refreshScreenshot();
      } catch (e) {
        showBanner('Failed to set active device: ' + e, 'error');
      }
    }

    async function disconnectDevice(serial) {
      try {
        const res = await fetch('/api/disconnect-device', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ serial: serial })
        });
        showBanner(`Disconnected ${serial}`, 'info', 3000);
        refreshStatus();
        refreshScreenshot();
      } catch (e) {
        showBanner('Failed to disconnect: ' + e, 'error');
      }
    }
    async function launchScrcpy() {
      const btn = document.getElementById('btn-scrcpy');
      btn.disabled = true;
      showBanner("Initiating scrcpy screen mirror...", "info", 3000);
      try {
        const res = await fetch('/api/scrcpy', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
          showBanner("📱 " + data.message, "success", 4000);
        } else {
          showBanner("❌ " + data.error, "error", 7000);
        }
      } catch (e) {
        showBanner("❌ Failed to launch scrcpy: " + e, "error", 6000);
      } finally {
        btn.disabled = false;
      }
    }

    async function switchWireless() {
      const btn = document.getElementById('btn-wifi');
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span> Switching...';
      showBanner("Attempting to switch phone from USB to Wi-Fi mode...", "info", 4000);

      try {
        const res = await fetch('/api/wireless-switch', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
          showBanner("📶 Success! You can now unplug the USB cable. Phone is connected wirelessly!", "success", 8000);
        } else {
          showBanner("❌ " + (data.error || "Failed to switch wireless. Connect phone via USB first."), "error", 7000);
        }
        refreshStatus();
      } catch (e) {
        showBanner("❌ Error: " + e, "error");
      } finally {
        btn.disabled = false;
        btn.innerHTML = "📶 Switch to Wi-Fi";
      }
    }

    async function connectManualIp() {
      const ip = document.getElementById('manual-ip').value.trim();
      if (!ip) {
        showBanner("Please enter your phone's Wi-Fi IP address (e.g. 192.168.1.15)", "error");
        return;
      }
      showBanner(`Connecting to ${ip}:5555...`, "info", 3000);
      try {
        const res = await fetch('/api/connect-ip', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ip: ip })
        });
        const data = await res.json();
        if (data.success) {
          showBanner("✅ " + data.message, "success", 5000);
        } else {
          showBanner("❌ " + data.message, "error", 6000);
        }
        refreshStatus();
      } catch (e) {
        showBanner("Error: " + e, "error");
      }
    }

    async function saveConfig() {
      const p = document.getElementById('cfg-provider').value;
      const model = document.getElementById('cfg-model').value;
      const keyVal = document.getElementById('cfg-key').value;
      const keyName = PROVIDER_KEY_MAP[p];

      const keys = {};
      if (keyName && keyVal) {
        keys[keyName] = keyVal;
      }

      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: p, model_name: model, keys: keys })
      });
      const data = await res.json();
      showBanner("💾 " + (data.message || 'Configuration saved!'), "success", 4000);
      refreshStatus();
    }

    function refreshScreenshot() {
      const img = document.getElementById('screen-preview');
      img.src = '/api/screenshot?t=' + Date.now();
    }

    async function runOrganization() {
      const btn = document.getElementById('btn-org');
      const out = document.getElementById('org-output');
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span> Coordinating Agents...';
      out.innerText = `[RUNNING] Mission dispatched to Chief Orchestrator over the Event Bus...\n[RUNNING] Contacting Mobile, Desktop, Browser, and Notifier agents...\n`;

      try {
        const res = await fetch('/api/run-organization', { method: 'POST' });
        const data = await res.json();
        out.innerText = data.output || "Mission completed."; localStorage.setItem('org-output', out.innerText);
        if (data.success) {
          showBanner("🚀 Organization Mission Accomplished! Dossier saved to reports.", "success", 5000);
        } else {
          showBanner("⚠️ Mission finished with warnings. See output trace below.", "error", 6000);
        }
        fetchReports();
        refreshScreenshot();
      } catch (e) {
        out.innerText = "Error: " + e;
        showBanner("Execution error: " + e, "error");
      } finally {
        btn.disabled = false;
        btn.innerHTML = "🚀 Run Multi-Agent Mission";
      }
    }

    async function runSingleAgent() {
      const btn = document.getElementById('btn-single');
      const out = document.getElementById('single-output');
      const goal = document.getElementById('agent-goal').value;
      const provider = document.getElementById('cfg-provider').value;
      const dryRun = document.getElementById('agent-dryrun').checked;

      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span> Agent Executing...';
      out.innerText = `[RUNNING] Starting perception -> reasoning -> action loop for: "${goal}"...\n`;

      try {
        const res = await fetch('/api/run-agent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ goal: goal, provider: provider, dry_run: dryRun })
        });
        const data = await res.json();
        out.innerText = data.output || "Completed."; localStorage.setItem('single-output', out.innerText);
        if (data.success) {
          showBanner("✅ Action completed successfully!", "success", 4000);
        } else {
          showBanner("Action finished with output. Check trace.", "info", 5000);
        }
        refreshScreenshot();
      } catch (e) {
        out.innerText = "Error: " + e;
        showBanner("Error: " + e, "error");
      } finally {
        btn.disabled = false;
        btn.innerHTML = "▶ Execute Phone Goal";
      }
    }

    async function fetchReports() {
      try {
        const res = await fetch('/api/reports');
        const data = await res.json();
        const sel = document.getElementById('reports-list');
        sel.innerHTML = '';
        data.reports.forEach(r => {
          const opt = document.createElement('option');
          opt.value = r.filename;
          opt.innerText = `${r.filename} (${r.mtime})`;
          sel.appendChild(opt);
        });
        if (data.reports.length > 0) {
          loadReport();
        }
      } catch (e) {}
    }

    async function loadReport() {
      const sel = document.getElementById('reports-list');
      if (!sel.value) return;
      const res = await fetch('/api/report/' + sel.value);
      const data = await res.json();
      const contentEl = document.getElementById('report-content');
      if (contentEl) contentEl.innerText = data.content || '';
    }



    async function updateCalculator() {
      const dev = document.getElementById('calc-devices').value;
      const ai = document.getElementById('calc-ai').value;
      const hrs = document.getElementById('calc-hours').value;

      document.getElementById('calc-devices-val').innerText = dev;
      document.getElementById('calc-ai-val').innerText = ai;
      document.getElementById('calc-hours-val').innerText = hrs;

      try {
        const res = await fetch('/api/billing/calculate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ devices: dev, ai_tasks: ai, stream_hours: hrs })
        });
        const d = await res.json();
        document.getElementById('calc-res-ai').innerText = '$' + d.ai_operating_cost + '/mo';
        document.getElementById('calc-res-turn').innerText = '$' + d.turn_operating_cost + '/mo';
        document.getElementById('calc-res-total').innerText = '$' + d.total_operating_cost + '/mo';
        document.getElementById('calc-res-savings').innerText = '$' + d.monthly_savings + '/mo';
      } catch (e) {}
    }

    async function subscribeStripe(planId) {
      showBanner(`Initiating Stripe checkout session for ${planId}...`, "info", 3000);
      try {
        const res = await fetch('/api/stripe/create-checkout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ plan_id: planId, email: 'user@example.com' })
        });
        const d = await res.json();
        if (d.checkout_url) {
          showBanner("Redirecting to Stripe Checkout...", "success", 3000);
          window.open(d.checkout_url, '_blank');
        } else {
          showBanner("Payment session error: " + (d.error || 'unknown'), "error");
        }
      } catch (e) {
        showBanner("Checkout error: " + e, "error");
      }
    }

    async function redeemCouponUI() {
      const code = document.getElementById('coupon-redeem-input').value.trim();
      const resEl = document.getElementById('coupon-result');
      if (!code) return;

      resEl.innerText = "Validating coupon code...";
      resEl.style.color = "#8b949e";

      try {
        const res = await fetch('/api/coupons/redeem', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code: code })
        });
        const d = await res.json();
        if (d.success) {
          resEl.style.color = "#7ee787";
          resEl.innerText = `🎉 ${d.message} License Key: ${d.license_key}`;
          showBanner("🎉 Pro Access Unlocked via Coupon!", "success", 5000);
        } else {
          resEl.style.color = "#ff7b72";
          resEl.innerText = "❌ " + d.error;
          showBanner("Coupon redemption failed: " + d.error, "error");
        }
      } catch (e) {
        resEl.style.color = "#ff7b72";
        resEl.innerText = "Error: " + e;
      }
    }

    function switchDeviceViewport(dev) {
      const pcView = document.getElementById('view-pc-container');
      const phoneView = document.getElementById('view-phone-container');
      const btnPc = document.getElementById('btn-sub-pc');
      const btnPhone = document.getElementById('btn-sub-phone');

      if (dev === 'pc') {
        pcView.style.display = 'block';
        phoneView.style.display = 'none';
        btnPc.className = 'btn btn-sm btn-accent';
        btnPhone.className = 'btn btn-sm';
      } else {
        pcView.style.display = 'none';
        phoneView.style.display = 'block';
        btnPc.className = 'btn btn-sm';
        btnPhone.className = 'btn btn-sm btn-accent';
        refreshMobileScreen();
      }
    }

    function refreshMobileScreen() {
      const img = document.getElementById('mobile-viewport-screen');
      if (img) {
        img.src = '/api/screenshot?t=' + Date.now();
      }
    }

    function toggleMobileStream() {
      const chk = document.getElementById('mobile-auto-stream');
      if (chk && chk.checked) {
        mobileStreamInterval = setInterval(refreshMobileScreen, 1200);
      } else if (mobileStreamInterval) {
        clearInterval(mobileStreamInterval);
        mobileStreamInterval = null;
      }
    }

    async function onMobileScreenClick(event) {
      const img = document.getElementById('mobile-viewport-screen');
      if (!img) return;
      const rect = img.getBoundingClientRect();
      const norm_x = (event.clientX - rect.left) / rect.width;
      const norm_y = (event.clientY - rect.top) / rect.height;

      try {
        const res = await fetch('/api/mobile/click', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ norm_x: norm_x, norm_y: norm_y })
        });
        const data = await res.json();
        if (data.success) {
          showBanner(`📱 Tapped on Phone (${data.x}, ${data.y})`, 'info', 2000);
        } else {
          showBanner('Tap failed: ' + (data.error || 'unknown'), 'error');
        }
        setTimeout(refreshMobileScreen, 300);
      } catch (e) {
        showBanner('Tap error: ' + e, 'error');
      }
    }

    async function sendMobileAction(act) {
      try {
        const res = await fetch('/api/mobile/action', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: act })
        });
        const data = await res.json();
        if (data.success) {
          showBanner('⚡ ' + data.message, 'success', 2500);
        } else {
          showBanner('Action failed: ' + (data.error || 'unknown'), 'error');
        }
        setTimeout(refreshMobileScreen, 400);
      } catch (e) {
        showBanner('Action error: ' + e, 'error');
      }
    }

    async function sendMobileSwipe(dir) {
      try {
        const res = await fetch('/api/mobile/swipe', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ direction: dir })
        });
        const data = await res.json();
        if (data.success) {
          showBanner('👆 ' + data.message, 'info', 2000);
        }
        setTimeout(refreshMobileScreen, 500);
      } catch (e) {
        showBanner('Swipe error: ' + e, 'error');
      }
    }

    async function launchMobileQuickApp(app) {
      try {
        const res = await fetch('/api/mobile/launch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ app: app })
        });
        const data = await res.json();
        showBanner(data.message || data.error, data.success ? 'success' : 'error', 3000);
        setTimeout(refreshMobileScreen, 1200);
      } catch (e) {
        showBanner('Launch error: ' + e, 'error');
      }
    }

    async function sendMobileType(withEnter) {
      const text = document.getElementById('mobile-type-input').value;
      if (!text) return;
      try {
        const res = await fetch('/api/mobile/type', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: text, with_enter: withEnter })
        });
        const data = await res.json();
        if (data.success) {
          showBanner('⌨️ ' + data.message, 'success', 2500);
          document.getElementById('mobile-type-input').value = '';
        }
        setTimeout(refreshMobileScreen, 400);
      } catch (e) {
        showBanner('Typing error: ' + e, 'error');
      }
    }

    async function runMobileAntigravityAgent() {
      const goal = document.getElementById('mobile-agent-goal').value;
      const out = document.getElementById('mobile-agent-output');
      out.innerText = `[RUNNING] Antigravity perception -> reasoning loop for "${goal}"...
`;
      try {
        const provider = document.getElementById('cfg-provider').value;
        const res = await fetch('/api/run-agent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ goal: goal, provider: provider, dry_run: false })
        });
        const data = await res.json();
        out.innerText = data.output || "Completed.";
        if (data.success) {
          showBanner("✅ Mobile Agent task completed!", "success", 4000);
        }
        refreshMobileScreen();
      } catch (e) {
        out.innerText = "Error: " + e;
      }
    }

    let pcStreamInterval = null;
    let mobileStreamInterval = null;

    function refreshPcScreen() {
      const img = document.getElementById('pc-screen');
      if (img) {
        img.src = '/api/pc/screen?t=' + Date.now();
      }
    }

    function togglePcStream() {
      const chk = document.getElementById('pc-auto-stream');
      if (chk && chk.checked) {
        pcStreamInterval = setInterval(refreshPcScreen, 1200);
      } else if (pcStreamInterval) {
        clearInterval(pcStreamInterval);
        pcStreamInterval = null;
      }
    }

    async function onPcScreenClick(event) {
      const img = document.getElementById('pc-screen');
      if (!img) return;
      const rect = img.getBoundingClientRect();
      const norm_x = (event.clientX - rect.left) / rect.width;
      const norm_y = (event.clientY - rect.top) / rect.height;

      try {
        const res = await fetch('/api/pc/click', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ norm_x: norm_x, norm_y: norm_y, button: 'left' })
        });
        const data = await res.json();
        if (data.success) {
          showBanner(`🖱️ Clicked on PC (${data.x}, ${data.y})`, 'info', 2000);
        }
        setTimeout(refreshPcScreen, 200);
      } catch (e) {
        showBanner('Click error: ' + e, 'error');
      }
    }

    async function sendPcAction(act) {
      try {
        const res = await fetch('/api/pc/action', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: act })
        });
        const data = await res.json();
        if (data.success) {
          showBanner('⚡ ' + data.message, 'success', 3000);
        } else {
          showBanner('Action failed: ' + (data.error || 'unknown'), 'error');
        }
        setTimeout(refreshPcScreen, 300);
      } catch (e) {
        showBanner('Action error: ' + e, 'error');
      }
    }

    async function launchPcApp() {
      const app = document.getElementById('pc-app-select').value;
      try {
        const res = await fetch('/api/pc/action', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'launch_app', app: app })
        });
        const data = await res.json();
        showBanner(data.message || data.error, data.success ? 'success' : 'error', 3000);
        setTimeout(refreshPcScreen, 800);
      } catch (e) {}
    }

    async function openPcUrl() {
      const url = document.getElementById('pc-url-input').value.trim();
      if (!url) return;
      try {
        const res = await fetch('/api/pc/action', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'open_url', url: url })
        });
        const data = await res.json();
        showBanner(data.message, 'success', 3000);
        setTimeout(refreshPcScreen, 1000);
      } catch (e) {}
    }

    async function sendPcType(withEnter) {
      const text = document.getElementById('pc-type-input').value;
      if (!text && !withEnter) return;
      try {
        if (text) {
          await fetch('/api/pc/type', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
          });
        }
        if (withEnter) {
          await fetch('/api/pc/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'enter' })
          });
        }
        showBanner(`⌨️ Typed to PC: "${text}"`, 'info', 2000);
        document.getElementById('pc-type-input').value = '';
        setTimeout(refreshPcScreen, 300);
      } catch (e) {
        showBanner('Type error: ' + e, 'error');
      }
    }

    async function runPcAgent() {
      const btn = document.getElementById('btn-pc-agent');
      const out = document.getElementById('pc-agent-output');
      const goal = document.getElementById('pc-agent-goal').value;
      const provider = document.getElementById('cfg-provider').value;
      const model = document.getElementById('cfg-model').value;

      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span> PC Agent Thinking...';
      out.innerText = `[RUNNING] Dispatched PC Desktop directive: "${goal}" using ${provider}...\n`;

      try {
        const res = await fetch('/api/pc/agent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ goal: goal, provider: provider, model: model })
        });
        const data = await res.json();
        out.innerText = JSON.stringify(data, null, 2);
        showBanner(data.success ? '✅ PC Agent finished goal!' : '⚠️ PC Agent finished with trace.', data.success ? 'success' : 'info', 5000);
        refreshPcScreen();
      } catch (e) {
        out.innerText = 'Error: ' + e;
        showBanner('PC Agent error: ' + e, 'error');
      } finally {
        btn.disabled = false;
        btn.innerHTML = '🚀 Execute on PC';
      }
    }

    function switchTab(evt, tabId) {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      evt.currentTarget.classList.add('active');
      document.getElementById(tabId).classList.add('active');
      if (tabId === 'reports-tab') fetchReports();
    }

    // Auto-polling status every 3 seconds
    setInterval(refreshStatus, 3000);

    // Initial load
    restoreLocalInputs();
    refreshStatus();
    fetchReports();
  </script>
</body>
</html>
"""

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
