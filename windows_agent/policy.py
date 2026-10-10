from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping


class PolicyError(RuntimeError):
    """Raised when local policy denies an action."""


def _normalize(value: str | None) -> str:
    if value is None:
        return ""
    return "".join(ch.lower() for ch in value if ch.isalnum())


@dataclass
class LocalPolicy:
    """Authoritative local policy for the Windows agent."""

    capabilities: set[str] = field(default_factory=set)
    tier_map: dict[str, int] = field(default_factory=dict)
    blocked_apps: set[str] = field(default_factory=set)
    blocked_window_titles: set[str] = field(default_factory=set)

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "LocalPolicy":
        tier_map = {}
        for key, value in (raw.get("tier_map") or {}).items():
            tier_map[str(key)] = int(value)
        return cls(
            capabilities={str(item) for item in (raw.get("capabilities") or [])},
            tier_map=tier_map,
            blocked_apps={_normalize(str(item)) for item in (raw.get("blocked_apps") or [])},
            blocked_window_titles={
                _normalize(str(item)) for item in (raw.get("blocked_window_titles") or [])
            },
        )

    @classmethod
    def load(cls, path: str | Path) -> "LocalPolicy":
        with Path(path).open("r", encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle))

    def required_tier(self, capability: str) -> int:
        return int(self.tier_map.get(capability, 0))

    def is_blocked(self, app_name: str | None = None, window_title: str | None = None) -> bool:
        app_key = _normalize(app_name)
        title_key = _normalize(window_title)
        if app_key and app_key in self.blocked_apps:
            return True
        if title_key and any(
            title_key in candidate or candidate in title_key for candidate in self.blocked_window_titles
        ):
            return True
        return False

    def validate_action(
        self,
        capability: str,
        action_tier: int | None = None,
        app_name: str | None = None,
        window_title: str | None = None,
    ) -> int:
        normalized_capability = capability.strip()
        if not normalized_capability:
            raise PolicyError("Capability is required.")
        if normalized_capability not in self.capabilities:
            raise PolicyError(f"Capability '{normalized_capability}' is not enabled by policy.")
        if self.is_blocked(app_name=app_name, window_title=window_title):
            raise PolicyError(
                f"Action '{normalized_capability}' is blocked by the local policy for app '{app_name}' or window '{window_title}'."
            )
        required_tier = self.required_tier(normalized_capability)
        if action_tier is None:
            action_tier = required_tier
        if action_tier < required_tier:
            raise PolicyError(
                f"Action '{normalized_capability}' requires T{required_tier}, but the provided action tier is T{action_tier}."
            )
        return required_tier


def load_policy(path: str | Path) -> LocalPolicy:
    return LocalPolicy.load(path)


DEFAULT_POLICY = LocalPolicy.from_dict(
    {
        "capabilities": [
            "device_status",
            "read_message_metadata",
            "read_message_content",
            "draft_message",
            "draft_text_in_notepad",
            "send_message",
            "delete_item",
            "install_app",
            "system_settings",
        ],
        "tier_map": {
            "device_status": 0,
            "read_message_metadata": 1,
            "read_message_content": 2,
            "draft_message": 3,
            "draft_text_in_notepad": 3,
            "send_message": 4,
            "delete_item": 5,
            "install_app": 5,
            "system_settings": 5,
        },
        "blocked_apps": [
            "1password",
            "bitwarden",
            "dashlane",
            "lastpass",
            "authy",
            "google authenticator",
            "microsoft authenticator",
            "keepass",
            "keepassxc",
            "passkey",
            "password manager",
        ],
        "blocked_window_titles": [
            "authenticator",
            "two-factor",
            "2fa",
            "password manager",
        ],
    }
)
