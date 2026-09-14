"""Launch and run the Cross-Platform AI Organization."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from organization.bus import EventBus
from organization.desktop_agent import DesktopAgent
from organization.mobile_agent import MobileAgent
from organization.orchestrator import ChiefOrchestrator

async def main():
    print("="*65)
    print("      PERSONAL CROSS-PLATFORM AI ORGANIZATION SYSTEM      ")
    print("="*65)

    # 1. Initialize Event Bus
    bus = EventBus()

    # 2. Spawn and register agents
    desktop_agent = DesktopAgent(bus)
    mobile_agent = MobileAgent(bus)
    orchestrator = ChiefOrchestrator(bus)

    # 3. Execute collaborative multi-agent mission
    goal = "Audit mobile phone state over ADB and generate official organizational audit report on Windows PC"
    result = await orchestrator.execute_cross_platform_audit(goal)

    print("\n" + "="*65)
    print("MISSION ACCOMPLISHED!")
    print(f"Report File: {result.get('report_file')}")
    print(f"Total Bus Messages Routed: {len(bus.get_log())}")
    print("="*65)

if __name__ == "__main__":
    asyncio.run(main())
