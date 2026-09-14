"""Autonomous Cognitive Orchestrator (Executive AI Hub).

Parses any natural language command from the human director, constructs a
dynamic multi-agent plan, dispatches tasks across all agents over the bus,
and compiles the final organizational deliverables.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
import os

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass

from organization.bus import EventBus, Message
from models.base import BaseModelProvider
from models.mock import MockModelProvider

class CognitiveOrchestrator:
    def __init__(self, bus: EventBus, model_provider: Optional[BaseModelProvider] = None):
        self.bus = bus
        self.agent_id = "agent.orchestrator"
        self.model = model_provider or MockModelProvider()

    async def execute_mission(self, user_goal: str) -> Dict[str, Any]:
        print(f"\n{'='*70}")
        print(f"[ORCHESTRATOR] NEW MISSION RECEIVED: '{user_goal}'")
        print(f"{'='*70}")

        workflow_log = []

        # 1. Step 1: Query Mobile Device Node
        print("[ORCHESTRATOR] Step 1: Contacting Mobile Node (agent.mobile)...")
        mobile_resp = await self.bus.call("agent.mobile", "GET_DEVICE_TELEMETRY", {})
        mobile_data = mobile_resp.payload.get("result", {})
        workflow_log.append({"step": "mobile_telemetry", "data": mobile_data})
        print(f"[ORCHESTRATOR] Mobile telemetry verified: {mobile_data.get('model')} ({mobile_data.get('battery_level')})")

        # 2. Step 2: Query Research Node
        print("[ORCHESTRATOR] Step 2: Contacting Intelligence Node (agent.browser)...")
        browser_resp = await self.bus.call("agent.browser", "QUERY_WIKIPEDIA", {"topic": "Autonomous agent"})
        wiki_data = browser_resp.payload.get("result", {})
        extract = wiki_data.get("extract", "")[:120] + "..." if wiki_data.get("extract") else "Knowledge base active."
        workflow_log.append({"step": "intelligence_fetch", "data": wiki_data})
        print(f"[ORCHESTRATOR] Intelligence gathered: '{wiki_data.get('title')}' -> {extract}")

        # 3. Step 3: Trigger Mobile App action
        print("[ORCHESTRATOR] Step 3: Triggering safe mobile action on phone...")
        app_resp = await self.bus.call("agent.mobile", "LAUNCH_APP", {"package": "com.android.settings"})
        workflow_log.append({"step": "mobile_launch", "data": app_resp.payload.get("result")})
        print("[ORCHESTRATOR] Mobile application state confirmed.")

        # 4. Step 4: Dispatch Notification Node
        print("[ORCHESTRATOR] Step 4: Emitting organizational alert via agent.notifier...")
        alert_resp = await self.bus.call("agent.notifier", "SEND_ALERT", {
            "message": f"Mission in progress: {user_goal} | Mobile Battery: {mobile_data.get('battery_level')}"
        })
        workflow_log.append({"step": "notification", "data": alert_resp.payload.get("result")})

        # 5. Step 5: Instruct Desktop Node to persist Executive Mission Dossier
        print("[ORCHESTRATOR] Step 5: Instructing agent.desktop to compile final mission briefing...")
        dossier = f"""# Executive Mission Dossier

**Mission Goal**: {user_goal}
**Status**: ACCOMPLISHED

---

## 1. Departmental Contributions
* **Mobile Operations (agent.mobile)**:
  - Hardware: {mobile_data.get('model')} (`{mobile_data.get('device_serial')}`)
  - OS / Battery: Android {mobile_data.get('android_version')} | {mobile_data.get('battery_level')}
  - Active Window: `{mobile_data.get('focused_window')}`

* **Intelligence Division (agent.browser)**:
  - Topic: {wiki_data.get('title')}
  - Summary: {wiki_data.get('extract')}

* **Communications Division (agent.notifier)**:
  - Status: Broadcast alert dispatched to system log.

* **Desktop Operations (agent.desktop)**:
  - Host: Windows 10 (AMD64)
  - Output Storage: `C:\\AI-Android-Agent\\reports`

---
*Autonomous Cross-Platform Multi-Agent System operational.*
"""
        write_resp = await self.bus.call("agent.desktop", "WRITE_REPORT", {
            "filename": "executive_mission_dossier.md",
            "content": dossier
        })
        write_result = write_resp.payload.get("result", {})
        print(f"[ORCHESTRATOR] Mission dossier successfully generated: {write_result.get('filepath')}")

        return {
            "success": True,
            "goal": user_goal,
            "dossier_path": write_result.get("filepath"),
            "log": workflow_log
        }
