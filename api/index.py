"""Vercel Serverless API & Web Handler for Pentactopus.

Provides enterprise endpoints for:
- User Authentication (PBKDF2 salted hashing, 7-day session tokens)
- Brute-Force Rate Limiting & Account Lockout Defense
- Enterprise RBAC Role Administration & Route Protection Guards
- P2P Remote Desktop Device Mesh & Autonomous Computer-Use Vision AI
- Dynamic Unit Economics Calculation & Stripe Billing Engine
"""

from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import urllib.request
import os
import sys

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from hub.device_hub import DeviceHub
from api.coupons import CouponManager
from api.billing import BillingManager
from api.user_store import UserStore
from api.admin_dashboard import AdminDashboard
from api.webrtc_signaling import SignalingHub
from api.user_store import UserStore, AuthError, LockoutError
from api.support_store import SupportStore
from api.web_template import HTML_PAGE

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
        path = parsed.path.rstrip("/") or "/"
        query = urllib.parse.parse_qs(parsed.query)

        # Web UI pages
        if path in ("", "/", "/index.html", "/dashboard", "/login", "/register"):
            self._send_cors(200, "text/html; charset=utf-8")
            self.wfile.write(HTML_PAGE.encode("utf-8"))
            return

        if path == "/admin":
            loader_html = """
            <!DOCTYPE html>
            <html>
            <head><title>Admin Auth</title></head>
            <body style="background:#000; color:#fff; font-family:sans-serif; text-align:center; padding-top:50px;">
              <h2>Authenticating...</h2>
              <script>
                const token = localStorage.getItem('penta_auth_token') || localStorage.getItem('penta_admin_secret');
                fetch('/api/admin/render', {
                  headers: { 'Authorization': 'Bearer ' + token }
                }).then(res => {
                  if(res.ok) {
                    res.text().then(html => {
                      document.open();
                      document.write(html);
                      document.close();
                    });
                  } else {
                    document.body.innerHTML = '<h2>Access Denied</h2><p>You do not have administrative privileges.</p><a href="/" style="color:#3b82f6;">Return Home</a>';
                  }
                });
              </script>
            </body>
            </html>
            """
            self._send_cors(200, "text/html; charset=utf-8")
            self.wfile.write(loader_html.encode("utf-8"))
            return

        if path == "/api/admin/render":
            auth_header = self.headers.get("Authorization", "")
            if not AdminDashboard.verify_auth(auth_header):
                self._send_cors(403)
                self.wfile.write(b"Unauthorized")
                return
            self._send_cors(200, "text/html; charset=utf-8")
            self.wfile.write(AdminDashboard.render_admin_html().encode("utf-8"))
            return

        if path.startswith("/download/"):
            fname = os.path.basename(path)
            # 1. Dynamic GitHub API Redirection for versioned filenames
            if fname in ["windows", "android"]:
                try:
                    req = urllib.request.Request("https://api.github.com/repos/Sany655/pentactopus-releases/contents/")
                    # Adding a fake User-Agent because GitHub API requires it
                    req.add_header('User-Agent', 'Pentactopus-Vercel-App')
                    with urllib.request.urlopen(req) as response:
                        contents = json.loads(response.read().decode('utf-8'))
                        
                        target_ext = ".exe" if fname == "windows" else ".apk"
                        
                        # Find the first file matching the extension
                        target_url = None
                        for item in contents:
                            if item.get("type") == "file" and item.get("name", "").endswith(target_ext):
                                target_url = item.get("download_url")
                                break
                        
                        if target_url:
                            self.send_response(302)
                            self.send_header("Location", target_url)
                            self.end_headers()
                            return
                except Exception as e:
                    print(f"Failed to fetch dynamic github release: {e}")

            # 2. Custom URL overrides via environment variables
            if fname.endswith(".exe") and os.getenv("RELEASE_DOWNLOAD_EXE_URL"):
                self.send_response(302)
                self.send_header("Location", os.getenv("RELEASE_DOWNLOAD_EXE_URL"))
                self.end_headers()
                return

            if fname.endswith(".apk") and os.getenv("RELEASE_DOWNLOAD_APK_URL"):
                self.send_response(302)
                self.send_header("Location", os.getenv("RELEASE_DOWNLOAD_APK_URL"))
                self.end_headers()
                return

            # 3. Check local dist, root, or public/static downloads directory
            local_paths = [
                os.path.join(BASE_DIR, fname),
                os.path.join(BASE_DIR, "dist", fname),
                os.path.join(BASE_DIR, "public", "download", fname),
                os.path.join(BASE_DIR, "static", "downloads", fname)
            ]
            for lp in local_paths:
                if os.path.isfile(lp):
                    content_type = "application/vnd.microsoft.portable-executable" if fname.endswith(".exe") else "application/vnd.android.package-archive"
                    file_size = os.path.getsize(lp)
                    self.send_response(200)
                    self.send_header("Content-Disposition", f'attachment; filename="{fname}"')
                    self.send_header("Content-Type", content_type)
                    self.send_header("Content-Length", str(file_size))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    with open(lp, "rb") as bf:
                        while chunk := bf.read(65536):
                            self.wfile.write(chunk)
                    return

            # 3. Default redirect to official GitHub Releases for production
            repo_release_url = f"https://github.com/Sany655/pentactopus-releases/releases/latest/download/{fname}"
            self.send_response(302)
            self.send_header("Location", repo_release_url)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            return

        # Auth Session Validation
        if path == "/api/auth/me":
            auth_header = self.headers.get("Authorization", "")
            user = UserStore.validate_session(auth_header)
            if user:
                self._send_cors(200)
                self.wfile.write(json.dumps({"success": True, "user": user}).encode("utf-8"))
            else:
                self._send_cors(401)
                self.wfile.write(json.dumps({"success": False, "error": "Invalid or expired session token"}).encode("utf-8"))
            return

        if path == "/api/admin/overview":
            self._send_cors(200)
            self.wfile.write(json.dumps(AdminDashboard.get_overview_metrics()).encode("utf-8"))
            return

        if path == "/api/admin/users":
            self._send_cors(200)
            self.wfile.write(json.dumps({"users": UserStore.list_users()}).encode("utf-8"))
            return

        if path == "/api/user/profile":
            email = query.get("email", ["alex@pentactopus.com"])[0]
            user = UserStore.get_user(email) or UserStore.create_or_get_user(email)
            self._send_cors(200)
            self.wfile.write(json.dumps({"user": user}).encode("utf-8"))
            return

        if path == "/api/admin/coupons/list":
            self._send_cors(200)
            self.wfile.write(json.dumps({"coupons": CouponManager.list_coupons()}).encode("utf-8"))
            return

        if path == "/api/devices":
            auth_header = self.headers.get("Authorization", "")
            if not UserStore.validate_session(auth_header):
                self._send_cors(401)
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
                return
            devices = DeviceHub.get_active_devices()
            self._send_cors(200)
            self.wfile.write(json.dumps({"devices": devices}).encode("utf-8"))
            return

        if path.startswith("/api/device/") and path.endswith("/frame"):
            auth_header = self.headers.get("Authorization", "")
            if not UserStore.validate_session(auth_header):
                self._send_cors(401)
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
                return
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
            auth_header = self.headers.get("Authorization", "")
            if not UserStore.validate_session(auth_header):
                self._send_cors(401)
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
                return
            parts = path.split("/")
            if len(parts) >= 4:
                dev_id = parts[3]
                tasks = DeviceHub.poll_actions(dev_id)
                self._send_cors(200)
                self.wfile.write(json.dumps({"tasks": tasks}).encode("utf-8"))
                return
        if path == "/api/webrtc/poll":
            auth_header = self.headers.get("Authorization", "")
            if not UserStore.validate_session(auth_header):
                self._send_cors(401)
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
                return
            target_id = query.get("target_id", [""])[0]
            signals = SignalingHub.poll_signals(target_id)
            self._send_cors(200)
            self.wfile.write(json.dumps({"signals": signals}).encode("utf-8"))
            return

        self._send_cors(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length) if length > 0 else b""
        client_ip = self.client_address[0] if hasattr(self, "client_address") and self.client_address else "127.0.0.1"

        # Frame upload
        if path.startswith("/api/device/") and path.endswith("/frame"):
            auth_header = self.headers.get("Authorization", "")
            if not UserStore.validate_session(auth_header):
                self._send_cors(401)
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
                return
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

        # ----------------------------------------------------------------------
        # Authentication & Registration Endpoints
        # ----------------------------------------------------------------------
        if path == "/api/auth/register":
            try:
                user, token = UserStore.register_user(
                    name=data.get("name", ""),
                    email=data.get("email", ""),
                    password=data.get("password", "")
                )
                self._send_cors(200)
                self.wfile.write(json.dumps({"success": True, "user": user, "token": token}).encode("utf-8"))
            except AuthError as e:
                self._send_cors(400)
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
            except Exception as e:
                self._send_cors(500)
                self.wfile.write(json.dumps({"success": False, "error": "Internal registration error"}).encode("utf-8"))
            return

        if path == "/api/auth/login":
            try:
                user, token = UserStore.authenticate_user(
                    email=data.get("email", ""),
                    password=data.get("password", ""),
                    client_ip=client_ip
                )
                self._send_cors(200)
                self.wfile.write(json.dumps({"success": True, "user": user, "token": token}).encode("utf-8"))
            except LockoutError as e:
                self._send_cors(429)  # 429 Too Many Requests (Brute-Force Lockout)
                self.wfile.write(json.dumps({"success": False, "error": str(e), "retry_after": e.retry_after}).encode("utf-8"))
            except AuthError as e:
                self._send_cors(401)
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
            except Exception as e:
                self._send_cors(500)
                self.wfile.write(json.dumps({"success": False, "error": "Internal login error"}).encode("utf-8"))
            return

        if path == "/api/auth/logout":
            auth_header = self.headers.get("Authorization", "")
            UserStore.revoke_session(auth_header)
            self._send_cors(200)
            self.wfile.write(json.dumps({"success": True, "message": "Session invalidated"}).encode("utf-8"))
            return

        if path == "/api/auth/guest":
            user_data = UserStore._get_seed_users()["guest@pentactopus.com"]
            token = UserStore.create_session("guest@pentactopus.com")
            self._send_cors(200)
            self.wfile.write(json.dumps({"success": True, "user": UserStore.safe_user(user_data), "token": token}).encode("utf-8"))
            return

        # ----------------------------------------------------------------------
        # Device Mesh & Remote Control
        # ----------------------------------------------------------------------
        if path == "/api/device/register":
            auth_header = self.headers.get("Authorization", "")
            if not UserStore.validate_session(auth_header):
                self._send_cors(401)
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
                return
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
            auth_header = self.headers.get("Authorization", "")
            if not UserStore.validate_session(auth_header):
                self._send_cors(401)
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
                return
            parts = path.split("/")
            if len(parts) >= 4:
                dev_id = parts[3]
                task_id = DeviceHub.queue_action(dev_id, data)
                self._send_cors(200)
                self.wfile.write(json.dumps({"success": True, "task_id": task_id}).encode("utf-8"))
                return

        if path.startswith("/api/device/") and "/task/" in path and path.endswith("/result"):
            self._send_cors(200)
            self.wfile.write(json.dumps({"success": True, "acknowledged": True}).encode("utf-8"))
            return

        if path in ("/api/agent/dispatch", "/api/organization/dispatch"):
            auth_header = self.headers.get("Authorization", "")
            user = UserStore.validate_session(auth_header)
            if not user:
                self._send_cors(401)
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
                return
            
            try:
                UserStore.track_usage(user["email"], "ai_tasks", 1)
            except AuthError as e:
                self._send_cors(403)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            goal = data.get("goal") or data.get("objective", "")
            dev_id = data.get("device_id", "pc_windows_host")
            task_id = DeviceHub.queue_action(dev_id, {
                "type": "goal",
                "goal": goal,
                "provider": data.get("provider"),
                "api_key": data.get("api_key")
            })
            self._send_cors(200)
            self.wfile.write(json.dumps({
                "success": True,
                "task_id": task_id,
                "message": f"Mission queued for {dev_id}: {goal}"
            }).encode("utf-8"))
            return

        if path == "/api/webrtc/signal":
            auth_header = self.headers.get("Authorization", "")
            if not UserStore.validate_session(auth_header):
                self._send_cors(401)
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
                return
            target_id = data.get("target_id")
            sender_id = data.get("sender_id")
            signal_type = data.get("type")
            payload = data.get("payload")
            
            if not all([target_id, sender_id, signal_type, payload]):
                self._send_cors(400)
                self.wfile.write(json.dumps({"error": "Missing parameters"}).encode("utf-8"))
                return
                
            SignalingHub.push_signal(target_id, sender_id, signal_type, payload)
            self._send_cors(200)
            self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
            return

        if path == "/api/webrtc/signal":
            auth_header = self.headers.get("Authorization", "")
            if not UserStore.validate_session(auth_header):
                self._send_cors(401)
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode("utf-8"))
                return
            target_id = data.get("target_id")
            sender_id = data.get("sender_id")
            signal_type = data.get("type")
            payload = data.get("payload")
            
            if not all([target_id, sender_id, signal_type, payload]):
                self._send_cors(400)
                self.wfile.write(json.dumps({"error": "Missing parameters"}).encode("utf-8"))
                return
                
            SignalingHub.push_signal(target_id, sender_id, signal_type, payload)
            self._send_cors(200)
            self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
            return

        # ----------------------------------------------------------------------
        # Billing & Coupons
        # ----------------------------------------------------------------------
        if path == "/api/coupons/redeem":
            email = data.get("email")
            res = CouponManager.redeem_coupon(data.get("code", ""), email)
            if res.get("valid") and email:
                UserStore.associate_coupon_redemption(
                    email=email,
                    coupon_code=data.get("code", ""),
                    license_key=res.get("license_key", ""),
                    days=res.get("days", 365)
                )
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

        if path == "/api/stripe/webhook":
            sig_header = self.headers.get("Stripe-Signature", "")
            res = BillingManager.handle_webhook_event(raw_body, sig_header)
            if res.get("success"):
                if res.get("action") == "license_provisioned":
                    try:
                        email = res.get("user_email")
                        if email:
                            UserStore.update_role(email, role="subscriber", plan="pro")
                    except Exception:
                        pass
                self._send_cors(200)
            else:
                self._send_cors(400)
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        # ----------------------------------------------------------------------
        # Support Tickets
        # ----------------------------------------------------------------------
        if path == "/api/support/submit":
            try:
                name = data.get("name", "")
                email = data.get("email", "")
                message = data.get("message", "")
                
                if not name or not email or not message:
                    self._send_cors(400)
                    self.wfile.write(json.dumps({"success": False, "error": "Missing required fields"}).encode("utf-8"))
                    return
                
                ticket = SupportStore.create_ticket(name, email, message)
                self._send_cors(200)
                self.wfile.write(json.dumps({"success": True, "ticket_id": ticket["id"]}).encode("utf-8"))
            except Exception as e:
                self._send_cors(500)
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
            return

        # ----------------------------------------------------------------------
        # Admin Operations
        # ----------------------------------------------------------------------
        if path.startswith("/api/admin/"):
            auth_header = self.headers.get("Authorization", "")
            if not AdminDashboard.verify_auth(auth_header):
                self._send_cors(403)
                self.wfile.write(json.dumps({"success": False, "error": "Admin privileges required"}).encode("utf-8"))
                return

            if path == "/api/admin/user/role":
                email = data.get("email")
                role = data.get("role")
                plan = data.get("plan")
                if email and role:
                    try:
                        user = UserStore.update_role(email, role, plan)
                        self._send_cors(200)
                        self.wfile.write(json.dumps({"success": True, "user": user}).encode("utf-8"))
                    except Exception as e:
                        self._send_cors(400)
                        self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
                else:
                    self._send_cors(400)
                    self.wfile.write(json.dumps({"success": False, "error": "Missing parameters"}).encode("utf-8"))
                return

            if path == "/api/admin/coupons/create":
                try:
                    c = CouponManager.create_coupon(
                        code=data.get("code"),
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
                try:
                    code = data.get("code")
                    # data.get("enabled") might be a boolean or a string depending on JS
                    enable_str = str(data.get("enabled", "")).lower()
                    enable = enable_str == "true" or enable_str == "1"
                    
                    c = CouponManager.toggle_coupon(code, enable)
                    self._send_cors(200)
                    self.wfile.write(json.dumps({"success": True, "coupon": c}).encode("utf-8"))
                except Exception as e:
                    self._send_cors(400)
                    self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
                return

        # ----------------------------------------------------------------------
        # Admin Operations (Protected by RBAC / Secret Key)
        # ----------------------------------------------------------------------
        auth_header = self.headers.get("Authorization", "")
        is_admin_auth = AdminDashboard.verify_auth(auth_header)

        if path == "/api/admin/user/role":
            if not is_admin_auth:
                self._send_cors(403)
                self.wfile.write(json.dumps({"success": False, "error": "Unauthorized. Admin credentials required."}).encode("utf-8"))
                return

            try:
                email = data.get("email", "")
                role = data.get("role", "subscriber")
                plan = data.get("plan")
                user = UserStore.update_role(email, role, plan)
                self._send_cors(200)
                self.wfile.write(json.dumps({"success": True, "user": user}).encode("utf-8"))
            except Exception as e:
                self._send_cors(400)
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
            return

        if path == "/api/admin/coupons/create":
            if not is_admin_auth:
                self._send_cors(403)
                self.wfile.write(json.dumps({"success": False, "error": "Unauthorized. Admin credentials required."}).encode("utf-8"))
                return

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
            if not is_admin_auth:
                self._send_cors(403)
                self.wfile.write(json.dumps({"success": False, "error": "Unauthorized. Admin credentials required."}).encode("utf-8"))
                return

            try:
                code = data.get("code", "")
                enabled = data.get("enabled", True)
                if isinstance(enabled, str):
                    enabled = enabled.lower() == "true"
                ok = CouponManager.toggle_coupon(code, enabled)
                self._send_cors(200)
                self.wfile.write(json.dumps({"success": ok}).encode("utf-8"))
            except Exception as e:
                self._send_cors(400)
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
            return

        if path == "/api/admin/support/resolve":
            if not is_admin_auth:
                self._send_cors(403)
                self.wfile.write(json.dumps({"success": False, "error": "Unauthorized. Admin credentials required."}).encode("utf-8"))
                return
            
            try:
                ticket_id = data.get("ticket_id")
                if not ticket_id:
                    self._send_cors(400)
                    self.wfile.write(json.dumps({"success": False, "error": "Missing ticket_id"}).encode("utf-8"))
                    return
                
                ticket = SupportStore.resolve_ticket(ticket_id)
                if ticket:
                    self._send_cors(200)
                    self.wfile.write(json.dumps({"success": True, "ticket": ticket}).encode("utf-8"))
                else:
                    self._send_cors(404)
                    self.wfile.write(json.dumps({"success": False, "error": "Ticket not found"}).encode("utf-8"))
            except Exception as e:
                self._send_cors(500)
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
            return

        self._send_cors(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))
