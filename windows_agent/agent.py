from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .model import LocalModelClient
from .notepad import (
    MAX_NOTEPAD_TEXT_CHARACTERS,
    NotepadController,
    WindowsNotepadController,
)
from .policy import DEFAULT_POLICY, LocalPolicy, PolicyError
from .whatsapp import WhatsAppReader


class ApprovalRequired(RuntimeError):
    """Raised when a task requires an explicit user approval."""


@dataclass
class LocalAuditEvent:
    event_type: str
    metadata: dict[str, Any]


class WindowsAgent:
    """Device-local orchestrator for Windows tasks.

    The agent does not make server-side decisions; it enforces the device's local
    policy before running a task, then emits a metadata-only audit record.
    """

    def __init__(
        self,
        policy: LocalPolicy | None = None,
        model_client: LocalModelClient | None = None,
        whatsapp_reader: WhatsAppReader | None = None,
        notepad_controller: NotepadController | None = None,
        audit_sink: Any | None = None,
    ) -> None:
        self.policy = policy or DEFAULT_POLICY
        self.model_client = model_client or LocalModelClient(provider="mock")
        self.whatsapp_reader = whatsapp_reader or WhatsAppReader()
        self.notepad_controller = notepad_controller or WindowsNotepadController()
        self.audit_sink = audit_sink

    @property
    def is_local_only(self) -> bool:
        return self.model_client.provider in {"mock", "local", "ollama"}

    def audit(self, event_type: str, **metadata: Any) -> None:
        event = LocalAuditEvent(event_type=event_type, metadata=dict(metadata))
        if self.audit_sink is not None:
            self.audit_sink(event)

    def run_task(self, task: Mapping[str, Any]) -> dict[str, Any]:
        capability = str(task.get("capability") or task.get("action") or "")
        action_tier = int(task.get("tier", self.policy.required_tier(capability) if capability else 0))
        app_name = "notepad.exe" if capability == "draft_text_in_notepad" else (
            str(task.get("app_name") or task.get("app") or "") or None
        )
        window_title = str(task.get("window_title") or "") or None
        requires_confirmation = bool(task.get("requires_confirmation", False))

        self.policy.validate_action(capability, action_tier=action_tier, app_name=app_name, window_title=window_title)

        if capability == "device_status":
            self.audit("device_status", status="online")
            return {"status": "done", "result": {"online": True, "capabilities": sorted(self.policy.capabilities)}}

        if capability == "read_message_metadata":
            self.audit("read_message_metadata", count=len(self.whatsapp_reader.metadata()))
            return {"status": "done", "result": self.whatsapp_reader.metadata()}

        if capability == "read_message_content":
            message_id = str(task.get("message_id") or "")
            if not message_id:
                raise ValueError("message_id is required for read_message_content tasks.")
            self.audit("read_message_content", message_id=message_id)
            return {"status": "done", "result": {"message_id": message_id, "text": self.whatsapp_reader.read(message_id)}}

        if capability == "draft_message":
            prompt = str(task.get("prompt") or task.get("message") or "")
            self.audit("draft_message", prompt_length=len(prompt))
            draft = self.model_client.draft_message(prompt)
            return {"status": "done", "result": {"draft": draft, "provider": self.model_client.provider}}

        if capability == "draft_text_in_notepad":
            text = task.get("text")
            if not isinstance(text, str) or not text.strip():
                raise ValueError("Non-empty locally available text is required for Notepad.")
            if len(text) > MAX_NOTEPAD_TEXT_CHARACTERS:
                raise ValueError(
                    f"Notepad text must not exceed {MAX_NOTEPAD_TEXT_CHARACTERS} characters."
                )
            self.notepad_controller.open_and_type(text)
            self.audit("draft_text_in_notepad", app="notepad.exe", character_count=len(text))
            return {"status": "done", "result": {"app": "notepad.exe", "character_count": len(text)}}

        if capability == "send_message":
            if requires_confirmation:
                raise ApprovalRequired("T4 approval is required before sending outbound WhatsApp or email.")
            self.audit("send_message", recipient=str(task.get("recipient") or "unknown"))
            return {"status": "done", "result": {"queued": True, "message": str(task.get("payload") or "")}}

        if capability in {"delete_item", "install_app", "system_settings"}:
            if action_tier < 5:
                raise PolicyError("High-impact action requires a T5 confirmation and local OS prompt.")
            self.audit("high_impact_action", capability=capability)
            return {"status": "done", "result": {"allowed": True, "capability": capability}}

        raise ValueError(f"Unsupported local capability '{capability}'.")
