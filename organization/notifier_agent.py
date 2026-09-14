"""Notification & Clipboard Relay Agent (agent.notifier).

Bridges notifications and clipboard synchronizations between Windows PC and Android phone.
"""

import subprocess
import os
from typing import Dict, Any, Optional
from organization.bus import Message, EventBus
from adb.client import ADBClient

class NotifierAgent:
    def __init__(self, bus: EventBus, agent_id: str = "agent.notifier"):
        self.bus = bus
        self.agent_id = agent_id
        self.adb = ADBClient()
        self.bus.register_agent(self.agent_id, self.handle_message)

    async def handle_message(self, msg: Message) -> Optional[Message]:
        action = msg.action
        payload = msg.payload
        print(f"[{self.agent_id}] Received action: {action}")

        result_payload = {}
        status = "success"

        try:
            if action == "COPY_TO_PHONE":
                # Copies text to phone input
                text = payload.get("text", "")
                if text:
                    self.adb.run_command(["shell", "input", "text", text.replace(" ", "%s")])
                    result_payload = {"message": f"Pushed {len(text)} characters to active phone field"}
                else:
                    status = "error"
                    result_payload = {"error": "No text provided"}

            elif action == "GET_PHONE_NOTIFICATIONS":
                # Extract recent notification packages from dumpsys
                _, notif_out, _ = self.adb.run_command(["shell", "dumpsys", "notification", "--noredact"], timeout_sec=5)
                packages = set()
                for line in notif_out.splitlines():
                    if "pkg=" in line:
                        for part in line.split():
                            if part.startswith("pkg="):
                                packages.add(part.split("=")[-1])
                result_payload = {
                    "active_notification_packages": list(packages)[:10],
                    "raw_length": len(notif_out)
                }

            elif action == "SEND_ALERT":
                alert_text = payload.get("message", "Organization Alert")
                print(f"\n>>> [ORGANIZATION ALERT] {alert_text} <<<\n")
                result_payload = {"status": "displayed", "message": alert_text}

            else:
                status = "error"
                result_payload = {"error": f"Unknown action: {action}"}

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
