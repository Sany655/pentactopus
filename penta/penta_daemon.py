"""Local Device Daemon & Antigravity Bridge for Penta-Assistant.

Bridges the local Windows PC and connected Android Phone to the DeviceHub
(and optional Vercel Cloud Relay).
Handles local screen capturing, action polling, and hardware input dispatching.
"""

import time
import threading
import json
import urllib.request
import os
import sys
from typing import Optional, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from hub.device_hub import DeviceHub
from pc_control.desktop_controller import DesktopController
from adb.client import ADBClient, ADBError
from tools.action_schema import ValidatedAction

class PentaDaemon:
    def __init__(self, cloud_url: Optional[str] = None):
        self.cloud_url = cloud_url.rstrip("/") if cloud_url else None
        self.running = False
        self.win_controller = DesktopController()
        self.adb = ADBClient()
        self._worker_thread: Optional[threading.Thread] = None

    def start(self):
        if self.running:
            return
        self.running = True
        self._register_local_nodes()
        self._worker_thread = threading.Thread(target=self._run_loop, daemon=True)
        self._worker_thread.start()

    def stop(self):
        self.running = False

    def _register_local_nodes(self):
        w, h = self.win_controller.screen_size
        DeviceHub.register_device(
            device_id="pc_windows_host",
            name="Windows PC (Host)",
            platform="windows",
            resolution=(w, h),
            capabilities=["screen_capture", "mouse_click", "keyboard", "ai_agent", "app_launcher"],
            connection_type="local"
        )
        
        serial = self.adb.get_active_serial()
        if serial:
            DeviceHub.register_device(
                device_id="phone_android_node",
                name=f"Android Phone ({serial})",
                platform="android",
                resolution=(1080, 2160),
                capabilities=["screen_capture", "touch_tap", "swipe", "hardware_keys", "ai_agent", "app_launcher"],
                connection_type="adb"
            )

    def _run_loop(self):
        while self.running:
            try:
                # 1. Capture and buffer PC frame
                pc_frame = self.win_controller.capture_screen_jpeg(quality=65, target_width=1024)
                if pc_frame:
                    DeviceHub.set_frame("pc_windows_host", pc_frame)
                    if self.cloud_url:
                        self._push_cloud_frame("pc_windows_host", pc_frame)

                # 2. Capture and buffer Android frame if device attached
                if self.adb.get_active_serial():
                    try:
                        png_bytes = self.adb.capture_screenshot()
                        if png_bytes:
                            DeviceHub.set_frame("phone_android_node", png_bytes)
                            if self.cloud_url:
                                self._push_cloud_frame("phone_android_node", png_bytes)
                    except Exception:
                        pass

                # 3. Poll and execute pending actions for PC
                pc_tasks = DeviceHub.poll_actions("pc_windows_host")
                for task in pc_tasks:
                    self._execute_pc_task(task)

                # 4. Poll and execute pending actions for Android
                android_tasks = DeviceHub.poll_actions("phone_android_node")
                for task in android_tasks:
                    self._execute_android_task(task)

            except Exception:
                pass
            time.sleep(1.0)

    def _execute_pc_task(self, task: Dict[str, Any]):
        action_type = task.get("type", "")
        if action_type == "click":
            norm_x = float(task.get("norm_x", 0.5))
            norm_y = float(task.get("norm_y", 0.5))
            button = task.get("button", "left")
            self.win_controller.click(norm_x, norm_y, button=button)
        elif action_type == "type":
            text = task.get("text", "")
            self.win_controller.type_text(text)
        elif action_type == "action":
            act = task.get("action", "")
            self.win_controller.execute_action(act)
        elif action_type == "launch":
            app = task.get("app", "")
            self.win_controller.launch_app(app)

    def _execute_android_task(self, task: Dict[str, Any]):
        action_type = task.get("type", "")
        if action_type == "tap":
            norm_x = float(task.get("norm_x", 0.5))
            norm_y = float(task.get("norm_y", 0.5))
            px, py = DeviceHub.normalize_coordinates("android", norm_x, norm_y, (1080, 2160))
            self.adb.run_command(["shell", "input", "tap", str(px), str(py)])
        elif action_type == "type":
            text = task.get("text", "")
            self.adb.run_command(["shell", "input", "text", text])
        elif action_type == "key":
            code = task.get("keycode", 3)
            self.adb.run_command(["shell", "input", "keyevent", str(code)])
        elif action_type == "swipe":
            d = task.get("direction", "up")
            # Up = scroll down, Down = scroll up
            if d == "up":
                self.adb.run_command(["shell", "input", "swipe", "540", "1600", "540", "400", "300"])
            elif d == "down":
                self.adb.run_command(["shell", "input", "swipe", "540", "400", "540", "1600", "300"])
            elif d == "left":
                self.adb.run_command(["shell", "input", "swipe", "900", "1000", "100", "1000", "300"])
            elif d == "right":
                self.adb.run_command(["shell", "input", "swipe", "100", "1000", "900", "1000", "300"])
        elif action_type == "launch":
            pkg = task.get("package", "")
            if pkg:
                self.adb.run_command(["shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"])

    def _push_cloud_frame(self, device_id: str, frame_bytes: bytes):
        if not self.cloud_url:
            return
        try:
            req = urllib.request.Request(
                f"{self.cloud_url}/api/device/{device_id}/frame",
                data=frame_bytes,
                headers={"Content-Type": "image/jpeg"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=3)
        except Exception:
            pass
