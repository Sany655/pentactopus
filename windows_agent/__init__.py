"""Windows agent package for Pentactopus v1.

This package contains the local Windows implementation for the approved Phase 3
work. The server remains the source of truth for routing/task state; the local
agent only enforces policy and runs device-local model actions.
"""

from .agent import ApprovalRequired, WindowsAgent
from .model import LocalModelClient
from .notepad import MockNotepadController, WindowsNotepadController
from .policy import LocalPolicy, PolicyError, load_policy
from .whatsapp import MockWhatsAppUI, WhatsAppReader

__all__ = [
    "ApprovalRequired",
    "LocalModelClient",
    "LocalPolicy",
    "MockWhatsAppUI",
    "MockNotepadController",
    "PolicyError",
    "WhatsAppReader",
    "WindowsNotepadController",
    "WindowsAgent",
    "load_policy",
]
