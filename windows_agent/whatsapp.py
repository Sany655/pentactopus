from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class WhatsAppMessage:
    message_id: str
    sender: str
    text: str
    timestamp: str
    is_unread: bool = True


class MockWhatsAppUI:
    """Simple UI-only mock used for tests and local development."""

    def __init__(self, messages: Iterable[Mapping[str, Any]] | None = None) -> None:
        self.messages = [
            WhatsAppMessage(
                message_id=str(item.get("message_id") or index),
                sender=str(item.get("sender") or "Unknown"),
                text=str(item.get("text") or ""),
                timestamp=str(item.get("timestamp") or "2026-01-01T00:00:00Z"),
                is_unread=bool(item.get("is_unread", True)),
            )
            for index, item in enumerate(messages or [
                {
                    "message_id": "msg-1",
                    "sender": "Alicia",
                    "text": "Can you pick up milk on the way home?",
                    "timestamp": "2026-01-01T08:00:00Z",
                    "is_unread": True,
                }
            ])
        ]

    def unread_messages(self) -> list[dict[str, Any]]:
        return [
            {
                "message_id": message.message_id,
                "sender": message.sender,
                "timestamp": message.timestamp,
                "preview": message.text[:80],
            }
            for message in self.messages
            if message.is_unread
        ]

    def read_message(self, message_id: str, *, full_text: bool = True) -> str:
        for message in self.messages:
            if message.message_id == message_id:
                if full_text:
                    return message.text
                return message.text[:120]
        raise KeyError(f"No WhatsApp message found for id '{message_id}'.")


class WhatsAppReader:
    """Restricted to official WhatsApp Desktop instrumentation and policy-gated reads."""

    def __init__(self, ui: MockWhatsAppUI | None = None) -> None:
        self.ui = ui or MockWhatsAppUI()

    def metadata(self) -> list[dict[str, Any]]:
        return self.ui.unread_messages()

    def read(self, message_id: str, *, full_text: bool = True) -> str:
        return self.ui.read_message(message_id, full_text=full_text)
