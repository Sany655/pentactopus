"""Lightweight Android Companion Relay Script & Daemon.

Runs as a background foreground service, inside Termux, Python on Android, or via companion app.
Pushes phone telemetry (battery, network, model, screen frames) to the PC/Cloud AI Command Hub,
and executes remote commands (tap, swipe, text, key) dispatched by AI agents or operators.

Usage:
    python companion_relay.py http://your-pc-ip:5050 (or https://pentactopus.vercel.app)
"""

import sys
import time
import json
import urllib.request
import subprocess
import os
from typing import Dict, Any, Optional, Tuple

class AndroidCompanionRelay:
    def __init__(self, hub_url: str = "http://localhost:5050", device_id: str = "phone_android_node", auth_token: str = "mock_token"):
        self.hub_url = hub_url.rstrip("/")
        self.device_id = device_id
        self.auth_token = auth_token
        self.running = False
        self.resolution = (1080, 2400)

    def get_battery_info(self) -> Dict[str, Any]:
        """Fetch real battery status from Termux API or mock fallback."""
        try:
            res = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=2)
            if res.returncode == 0:
                return json.loads(res.stdout)
        except Exception:
            pass
        return {"percentage": 88, "status": "DISCHARGING", "temperature": 31.5}

    def get_device_info(self) -> Dict[str, Any]:
        """Get Android model and OS version."""
        try:
            m = subprocess.run(["getprop", "ro.product.model"], capture_output=True, text=True).stdout.strip()
            v = subprocess.run(["getprop", "ro.build.version.release"], capture_output=True, text=True).stdout.strip()
            return {"model": m or "Android Device", "version": v or "14"}
        except Exception:
            return {"model": "Android Phone Node", "version": "14"}

    def notify_user(self, title: str, content: str) -> None:
        """Push system notification via Termux or notification service."""
        try:
            subprocess.run(["termux-notification", "--title", title, "--content", content], timeout=2)
        except Exception:
            pass

    def capture_screen_frame(self) -> Optional[bytes]:
        """Capture screenshot via native Android screencap."""
        try:
            res = subprocess.run(["screencap", "-p"], capture_output=True, timeout=3)
            if res.returncode == 0 and res.stdout:
                return res.stdout
        except Exception:
            pass
        return None

    def register(self) -> bool:
        """Register device with the central DeviceHub."""
        dev_info = self.get_device_info()
        battery = self.get_battery_info()
        payload = {
            "device_id": self.device_id,
            "name": f"{dev_info.get('model')} (Android)",
            "platform": "android",
            "resolution": list(self.resolution),
            "capabilities": ["screen_capture", "input_injection", "ai_agent", "telemetry"],
            "connection_type": "companion_relay",
            "battery": battery.get("percentage", 88)
        }
        try:
            req = urllib.request.Request(
                f"{self.hub_url}/api/device/register",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return bool(data.get("success"))
        except Exception:
            return False

    def push_frame(self, frame_bytes: bytes) -> bool:
        """Upload latest screen frame to the hub for remote viewing."""
        if not frame_bytes:
            return False
        try:
            req = urllib.request.Request(
                f"{self.hub_url}/api/device/{self.device_id}/frame",
                data=frame_bytes,
                headers={
                    "Content-Type": "image/png",
                    "Authorization": f"Bearer {self.auth_token}"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                return resp.status == 200
        except Exception:
            return False

    def perform_accessibility_action(self, task: Dict[str, Any]) -> Tuple[bool, str]:
        """Execute touch, gesture, or text input on the Android device."""
        task_type = task.get("type", task.get("action", ""))
        try:
            if task_type in ("tap", "click"):
                norm_x = float(task.get("norm_x", 0.5))
                norm_y = float(task.get("norm_y", 0.5))
                x = int(norm_x * self.resolution[0])
                y = int(norm_y * self.resolution[1])
                subprocess.run(["input", "tap", str(x), str(y)], timeout=2)
                return True, f"Tapped at ({x}, {y})"

            elif task_type == "swipe":
                dx = int(task.get("dx", 0))
                dy = int(task.get("dy", 0))
                start_x = self.resolution[0] // 2
                start_y = self.resolution[1] // 2
                end_x = max(0, min(self.resolution[0], start_x + dx * 2))
                end_y = max(0, min(self.resolution[1], start_y + dy * 2))
                subprocess.run(["input", "swipe", str(start_x), str(start_y), str(end_x), str(end_y), "300"], timeout=2)
                return True, f"Swiped to ({end_x}, {end_y})"

            elif task_type in ("type", "text"):
                text = str(task.get("text", "")).replace(" ", "%s")
                subprocess.run(["input", "text", text], timeout=3)
                return True, f"Typed text: {task.get('text', '')}"

            elif task_type in ("key", "hotkey"):
                key_code = str(task.get("key", "KEYCODE_BACK"))
                subprocess.run(["input", "keyevent", key_code], timeout=2)
                return True, f"Sent key: {key_code}"

        except Exception as e:
            return False, str(e)

        return False, f"Unknown task action: {task_type}"

    def poll_and_execute(self) -> int:
        """Poll once for queued tasks from hub and execute them."""
        endpoint = f"{self.hub_url}/api/device/{self.device_id}/tasks"
        try:
            req = urllib.request.Request(
                endpoint,
                headers={"Authorization": f"Bearer {self.auth_token}"},
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            
            tasks = data.get("tasks", [])
            for task in tasks:
                if "goal" in task:
                    self.notify_user("Pentactopus AI Directive", task.get("goal", ""))
                    success, msg = True, f"Goal acknowledged: {task.get('goal')}"
                else:
                    success, msg = self.perform_accessibility_action(task)

                task_id = task.get("task_id")
                if task_id:
                    res_req = urllib.request.Request(
                        f"{self.hub_url}/api/device/{self.device_id}/task/{task_id}/result",
                        data=json.dumps({"success": success, "message": msg}).encode("utf-8"),
                        headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.auth_token}"},
                        method="POST"
                    )
                    try:
                        urllib.request.urlopen(res_req, timeout=3)
                    except Exception:
                        pass
            return len(tasks)
        except Exception:
            return 0

    def run(self, poll_interval: float = 2.0, max_iterations: Optional[int] = None) -> None:
        """Main service loop."""
        self.running = True
        print(f"[*] Starting Android Companion Relay for {self.device_id} -> {self.hub_url}...")
        self.register()
        self.notify_user("Pentactopus Service", "Connected to device mesh.")

        iterations = 0
        while self.running:
            self.poll_and_execute()

            # Periodic frame push if screenshot available
            frame = self.capture_screen_frame()
            if frame:
                self.push_frame(frame)

            iterations += 1
            if max_iterations and iterations >= max_iterations:
                break

            time.sleep(poll_interval)


def run_relay(hub_url: str, device_id: str, auth_token: str):
    relay = AndroidCompanionRelay(hub_url, device_id, auth_token)
    relay.run()


if __name__ == "__main__":
    hub = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5050"
    token = os.environ.get("PENTA_AUTH_TOKEN", "mock_token")
    dev_id = os.environ.get("PENTA_DEVICE_ID", "phone_android_node")
    run_relay(hub, dev_id, token)
