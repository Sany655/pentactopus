# Windows Agent

This package contains the approved Phase 3 Windows agent implementation for
Pentactopus v1. It runs entirely on the user's Windows device, keeps model
keys on the device, and enforces a local policy before any capability is used.

The agent is intentionally limited to the approved v1 scope:

- Reads official WhatsApp Desktop metadata and message content for personal use.
- Uses a local BYOK model flow or local-only model provider.
- Requires approval for T4 and T5 actions.
- Blocks T6 forbidden apps, password managers, and 2FA flows before execution.

No unofficial WhatsApp Web libraries or server-side AI decision making are used.
