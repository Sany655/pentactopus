"""Web Research & Intelligence Agent (agent.browser).

Executes lightweight web queries, information retrieval, and data fetching for the organization.
"""

import urllib.request
import json
import re
from typing import Dict, Any, Optional
from organization.bus import Message, EventBus

class BrowserAgent:
    def __init__(self, bus: EventBus, agent_id: str = "agent.browser"):
        self.bus = bus
        self.agent_id = agent_id
        self.bus.register_agent(self.agent_id, self.handle_message)

    async def handle_message(self, msg: Message) -> Optional[Message]:
        action = msg.action
        payload = msg.payload
        print(f"[{self.agent_id}] Received action: {action}")

        result_payload = {}
        status = "success"

        try:
            if action == "FETCH_URL":
                url = payload.get("url", "")
                if not url.startswith("http"):
                    url = "https://" + url
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 AI-Org-Browser/1.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    html = resp.read().decode("utf-8", errors="replace")
                
                # Extract clean text
                text = re.sub(r"<[^>]+>", " ", html)
                clean_text = " ".join(text.split())[:1500]
                result_payload = {
                    "url": url,
                    "snippet": clean_text,
                    "status_code": resp.status
                }

            elif action == "QUERY_WIKIPEDIA":
                topic = payload.get("topic", "Artificial intelligence").replace(" ", "_")
                api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
                req = urllib.request.Request(api_url, headers={"User-Agent": "AI-Agent-Organization/1.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                result_payload = {
                    "title": data.get("title"),
                    "extract": data.get("extract", "No extract found")
                }

            else:
                status = "error"
                result_payload = {"error": f"Unknown browser action: {action}"}

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
