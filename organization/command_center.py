"""Interactive Multi-Agent Organization Command Center."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from organization.bus import EventBus
from organization.desktop_agent import DesktopAgent
from organization.mobile_agent import MobileAgent
from organization.browser_agent import BrowserAgent
from organization.notifier_agent import NotifierAgent
from organization.cognitive_orchestrator import CognitiveOrchestrator

async def main():
    print("="*75)
    print("       PERSONAL CROSS-PLATFORM AI ORGANIZATION COMMAND CENTER       ")
    print("="*75)

    # Initialize Bus
    bus = EventBus()

    # Register Full Organizational Team
    print("[BOOT] Assembling organizational divisions...")
    desktop = DesktopAgent(bus)
    mobile = MobileAgent(bus)
    browser = BrowserAgent(bus)
    notifier = NotifierAgent(bus)
    orchestrator = CognitiveOrchestrator(bus)

    print(f"[READY] 4 specialized agents connected and waiting on the Event Bus.")

    # Execute end-to-end multi-agent mission
    goal = "Synthesize mobile device state, web intelligence, and generate executive dossier"
    result = await orchestrator.execute_mission(goal)

    print("\n" + "="*75)
    print("ORGANIZATION MISSION COMPLETE!")
    print(f"Dossier Location: {result.get('dossier_path')}")
    print(f"Total Inter-Agent Messages Routed: {len(bus.get_log())}")
    print("="*75)

if __name__ == "__main__":
    asyncio.run(main())
