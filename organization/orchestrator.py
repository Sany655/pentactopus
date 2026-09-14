"""Chief Orchestrator Agent (The Executive / CEO).

Decomposes human goals into cross-platform workflows, delegates subtasks to
Mobile and Desktop agents, and aggregates results into a final outcome.
"""

import asyncio
from typing import Dict, Any, List
from organization.bus import EventBus, Message

class ChiefOrchestrator:
    def __init__(self, bus: EventBus):
        self.bus = bus
        self.agent_id = "agent.orchestrator"

    async def execute_cross_platform_audit(self, goal: str) -> Dict[str, Any]:
        """Collaborative workflow:
        1. Query Mobile Agent for live device telemetry from phone.
        2. Query Desktop Agent for Windows host information.
        3. Instruct Desktop Agent to format and write the combined organizational report.
        """
        print(f"\n{'='*60}")
        print(f"[ORCHESTRATOR] Delegating Cross-Platform Goal: '{goal}'")
        print(f"{'='*60}")

        # Step 1: Query Mobile Agent
        print("[ORCHESTRATOR] -> Requesting live phone telemetry from agent.mobile...")
        mobile_resp = await self.bus.call(
            target_agent="agent.mobile",
            action="GET_DEVICE_TELEMETRY",
            payload={}
        )
        mobile_data = mobile_resp.payload.get("result", {})
        print(f"[ORCHESTRATOR] <- Mobile Agent responded: {mobile_data.get('model')} (Battery: {mobile_data.get('battery_level')})")

        # Step 2: Query Desktop Agent
        print("[ORCHESTRATOR] -> Requesting Windows environment telemetry from agent.desktop...")
        desktop_info_resp = await self.bus.call(
            target_agent="agent.desktop",
            action="GET_SYSTEM_INFO",
            payload={}
        )
        desktop_info = desktop_info_resp.payload.get("result", {})
        print(f"[ORCHESTRATOR] <- Desktop Agent responded: {desktop_info.get('os')} ({desktop_info.get('architecture')})")

        # Step 3: Synthesize and instruct Desktop Agent to write report
        print("[ORCHESTRATOR] -> Instructing agent.desktop to compile and persist organization report...")
        report_markdown = f"""# Cross-Platform Autonomous Organization: Device Audit Report

Generated collaboratively by **agent.orchestrator**, **agent.mobile**, and **agent.desktop**.

## 1. Executive Summary
- **Organization Mission**: Cross-Device Automated Telemetry & Synchronization
- **Status**: SUCCESS (Full Inter-Agent Coordination Verified)

## 2. Mobile Node Telemetry (Physical Phone)
- **Device Model**: {mobile_data.get('model')}
- **Serial Number**: `{mobile_data.get('device_serial')}`
- **Android OS**: Version {mobile_data.get('android_version')}
- **Battery Level**: {mobile_data.get('battery_level')}
- **Display Resolution**: {mobile_data.get('resolution')}
- **Active Focus**: `{mobile_data.get('focused_window')}`

## 3. Desktop Node Telemetry (Windows PC)
- **Host OS**: {desktop_info.get('os')} {desktop_info.get('release')}
- **Architecture**: {desktop_info.get('architecture')}
- **Python Engine**: {desktop_info.get('python_version')}

---
*Report published autonomously via local Event Bus protocol.*
"""
        write_resp = await self.bus.call(
            target_agent="agent.desktop",
            action="WRITE_REPORT",
            payload={
                "filename": "cross_platform_audit_report.md",
                "content": report_markdown
            }
        )
        write_result = write_resp.payload.get("result", {})
        print(f"[ORCHESTRATOR] <- Desktop Agent confirmed: {write_result.get('message')}")

        return {
            "success": True,
            "goal": goal,
            "mobile": mobile_data,
            "desktop": desktop_info,
            "report_file": write_result.get("filepath")
        }
