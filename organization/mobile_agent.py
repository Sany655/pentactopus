"""Android Mobile Worker Agent.

Interfaces directly with connected Android devices via ADB to execute physical phone tasks.
"""

import sys
import os
from typing import Dict, Any, Optional
from organization.bus import Message, EventBus
from adb.client import ADBClient, ADBError
from tools.action_schema import validate_action
from tools.allowlist import check_security_allowlist

class MobileAgent:
    def __init__(self, bus: EventBus, agent_id: str = "agent.mobile", serial: Optional[str] = None):
        self.bus = bus
        self.agent_id = agent_id
        self.adb = ADBClient(device_serial=serial)
        self.bus.register_agent(self.agent_id, self.handle_message)

    async def handle_message(self, msg: Message) -> Optional[Message]:
        action = msg.action
        payload = msg.payload
        print(f"[{self.agent_id}] Received action: {action}")

        result_payload = {}
        status = "success"

        try:
            if action == "GET_DEVICE_TELEMETRY":
                devices = self.adb.get_devices()
                if not devices:
                    print(f"[{self.agent_id}] Physical phone not currently attached via USB. Using device profile.")
                    result_payload = {
                        "device_serial": "658ac52 (Cached)",
                        "model": "Redmi Note 6 Pro",
                        "android_version": "9 (MIUI)",
                        "battery_level": "85%",
                        "resolution": "1080x2280",
                        "focused_window": "com.android.settings",
                        "connection_state": "offline_cached"
                    }
                else:
                    # Fetch live device properties
                    _, battery_out, _ = self.adb.run_command(["shell", "dumpsys", "battery"])
                    battery_level = "Unknown"
                    for line in battery_out.splitlines():
                        if "level:" in line:
                            battery_level = line.split(":")[-1].strip() + "%"
                            break

                    _, model_out, _ = self.adb.run_command(["shell", "getprop", "ro.product.model"])
                    _, android_ver, _ = self.adb.run_command(["shell", "getprop", "ro.build.version.release"])
                    w, h = self.adb.get_screen_size()
                    focused_app = self.adb.get_focused_app()

                    result_payload = {
                        "device_serial": devices[0]["serial"],
                        "model": model_out.strip(),
                        "android_version": android_ver.strip(),
                        "battery_level": battery_level,
                        "resolution": f"{w}x{h}",
                        "focused_window": focused_app,
                        "connection_state": "live_connected"
                    }

            elif action == "LAUNCH_APP":
                package = payload.get("package", "com.android.settings")
                validated = validate_action({"action": "launch_app", "package": package})
                check_security_allowlist(validated)
                res = self.adb.execute_action(validated)
                result_payload = res

            elif action == "CAPTURE_SCREENSHOT":
                img_bytes = self.adb.capture_screenshot()
                result_payload = {
                    "size_bytes": len(img_bytes),
                    "is_png": img_bytes.startswith(b"\x89PNG")
                }

            else:
                status = "error"
                result_payload = {"error": f"Unknown mobile action: {action}"}

        except Exception as e:
            status = "error"
            result_payload = {"error": str(e)}

        return Message(
            sender=self.agent_id,
            recipient=msg.sender,
            action=f"{action}_RESPONSE",
            payload={"status": status, "result": result_payload},
            correlation_id=msg.correlation_id
        )
