"""Lightweight In-Process & Network Asynchronous Event Bus.

Routes structured JSON messages between Desktop, Mobile, and Orchestrator agents.
"""

import asyncio
import json
import uuid
import time
from typing import Dict, Any, Callable, Awaitable, Optional, List

class Message:
    def __init__(
        self,
        sender: str,
        recipient: str,
        action: str,
        payload: Dict[str, Any],
        msg_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        self.msg_id = msg_id or str(uuid.uuid4())[:8]
        self.sender = sender
        self.recipient = recipient
        self.action = action
        self.payload = payload
        self.correlation_id = correlation_id or self.msg_id
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "msg_id": self.msg_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "action": self.action,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        m = cls(
            sender=data["sender"],
            recipient=data["recipient"],
            action=data["action"],
            payload=data["payload"],
            msg_id=data.get("msg_id"),
            correlation_id=data.get("correlation_id")
        )
        m.timestamp = data.get("timestamp", time.time())
        return m

HandlerFunc = Callable[[Message], Awaitable[Optional[Message]]]

class EventBus:
    def __init__(self):
        self._handlers: Dict[str, HandlerFunc] = {}
        self._pending_responses: Dict[str, asyncio.Future] = {}
        self._message_log: List[Dict[str, Any]] = []

    def register_agent(self, agent_id: str, handler: HandlerFunc):
        """Register an agent and its message handler callback."""
        self._handlers[agent_id] = handler
        print(f"[BUS] Agent registered: '{agent_id}'")

    async def send_message(self, message: Message) -> None:
        """Route message to recipient agent."""
        self._message_log.append(message.to_dict())
        print(f"[BUS] Routing msg [{message.msg_id}] {message.sender} -> {message.recipient} ({message.action})")

        # Check if this is a response to a pending call
        if (
            message.correlation_id in self._pending_responses
            and not self._pending_responses[message.correlation_id].done()
            and message.msg_id != message.correlation_id
        ):
            self._pending_responses[message.correlation_id].set_result(message)
            return

        recipient = message.recipient
        if recipient in self._handlers:
            resp = await self._handlers[recipient](message)
            if resp:
                await self.send_message(resp)
        elif recipient == "broadcast":
            for aid, h in self._handlers.items():
                if aid != message.sender:
                    asyncio.create_task(h(message))
        else:
            print(f"[BUS WARN] No agent registered with id '{recipient}'")

    async def call(self, target_agent: str, action: str, payload: Dict[str, Any], timeout: float = 15.0) -> Message:
        """Request-response pattern: sends message and awaits reply with matching correlation_id."""
        msg = Message(
            sender="orchestrator",
            recipient=target_agent,
            action=action,
            payload=payload
        )
        future = asyncio.get_event_loop().create_future()
        self._pending_responses[msg.msg_id] = future

        await self.send_message(msg)
        try:
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        finally:
            self._pending_responses.pop(msg.msg_id, None)

    def get_log(self) -> List[Dict[str, Any]]:
        return self._message_log
