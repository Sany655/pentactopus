import asyncio
import os
import sys

from organization.bus import EventBus, Message
from organization.desktop_agent import DesktopAgent
from organization.notifier_agent import NotifierAgent
from organization.browser_agent import BrowserAgent
from organization.mobile_agent import MobileAgent
from organization.cognitive_orchestrator import CognitiveOrchestrator

def test_bus_direct_routing():
    async def _run():
        bus = EventBus()
        desktop = DesktopAgent(bus)

        resp = await bus.call("agent.desktop", "GET_SYSTEM_INFO", {}, timeout=5.0)
        assert resp.sender == "agent.desktop"
        assert resp.payload["status"] == "success"
        assert "os" in resp.payload["result"]
    asyncio.run(_run())

def test_desktop_write_and_read():
    async def _run():
        bus = EventBus()
        desktop = DesktopAgent(bus)

        test_content = "Test report from test_organization.py"
        write_resp = await bus.call("agent.desktop", "WRITE_REPORT", {
            "filename": "unit_test_report.md",
            "content": test_content
        }, timeout=5.0)

        assert write_resp.payload["status"] == "success"
        filepath = write_resp.payload["result"]["filepath"]
        assert os.path.isfile(filepath)

        read_resp = await bus.call("agent.desktop", "READ_FILE", {"filepath": filepath}, timeout=5.0)
        assert read_resp.payload["status"] == "success"
        assert read_resp.payload["result"]["content"] == test_content
    asyncio.run(_run())

def test_notifier_alert():
    async def _run():
        bus = EventBus()
        notifier = NotifierAgent(bus)

        resp = await bus.call("agent.notifier", "SEND_ALERT", {"message": "Test Alert"}, timeout=5.0)
        assert resp.payload["status"] == "success"
        assert resp.payload["result"]["status"] == "displayed"
    asyncio.run(_run())

def test_end_to_end_cognitive_mission():
    async def _run():
        bus = EventBus()
        DesktopAgent(bus)
        MobileAgent(bus)
        BrowserAgent(bus)
        NotifierAgent(bus)
        orchestrator = CognitiveOrchestrator(bus)

        res = await orchestrator.execute_mission("Test End-to-End Organization Mission")
        assert res["success"] is True
        assert os.path.isfile(res["dossier_path"])
        assert len(bus.get_log()) >= 8
    asyncio.run(_run())
