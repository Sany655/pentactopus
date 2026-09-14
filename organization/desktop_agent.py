"""Windows Desktop Worker Agent.

Handles host filesystem operations, report generation, system audits, and desktop tasks.
"""

import os
import platform
import subprocess
from typing import Dict, Any, Optional
from organization.bus import Message, EventBus

class DesktopAgent:
    def __init__(self, bus: EventBus, agent_id: str = "agent.desktop", workspace_dir: Optional[str] = None):
        self.bus = bus
        self.agent_id = agent_id
        if workspace_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            workspace_dir = os.path.join(base_dir, "reports")
        self.workspace_dir = workspace_dir
        os.makedirs(self.workspace_dir, exist_ok=True)
        self.bus.register_agent(self.agent_id, self.handle_message)

    async def handle_message(self, msg: Message) -> Optional[Message]:
        action = msg.action
        payload = msg.payload
        print(f"[{self.agent_id}] Received action: {action}")

        result_payload = {}
        status = "success"

        try:
            if action == "WRITE_REPORT":
                filename = payload.get("filename", "report.md")
                content = payload.get("content", "")
                filepath = os.path.join(self.workspace_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                result_payload = {
                    "filepath": filepath,
                    "bytes_written": len(content.encode("utf-8")),
                    "message": f"Report successfully saved to {filepath}"
                }

            elif action == "GET_SYSTEM_INFO":
                result_payload = {
                    "os": platform.system(),
                    "release": platform.release(),
                    "architecture": platform.machine(),
                    "python_version": platform.python_version()
                }

            elif action == "READ_FILE":
                filepath = payload.get("filepath", "")
                if os.path.isfile(filepath):
                    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                        data = f.read()
                    result_payload = {"content": data}
                else:
                    status = "error"
                    result_payload = {"error": f"File not found: {filepath}"}

            else:
                status = "error"
                result_payload = {"error": f"Unknown desktop action: {action}"}

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
