# Windows Agent

This package contains the approved Phase 3 Windows agent implementation for
Pentactopus v1. It runs entirely on the user's Windows device, keeps model
keys on the device, and enforces a local policy before any capability is used.

The Windows agent is a general desktop-agent foundation: apps are selected
through explicit local capabilities and policy, rather than assuming a single
messaging product. WhatsApp was an example use case, not a requirement for the
Windows agent.

- The first real desktop action is a T3 draft in Windows Notepad.
- Uses a local BYOK model flow or local-only model provider.
- Requires approval for T4 and T5 actions.
- Blocks T6 forbidden apps, password managers, and 2FA flows before execution.

The `draft_text_in_notepad` capability launches `notepad.exe` and types text
already available locally to the agent. It does not send or save the text;
Notepad remains open for the user to review. The action is allowlisted, limited
to 16,384 characters, and audited by app name and character count without
logging the text itself. In production, message/action content must be obtained
from a locally decrypted artifact or a local user input, not from server task
metadata.

Try it on Windows with:

```powershell
python -m windows_agent.demo
```

The demo prompts for text locally instead of putting it in the command-line
arguments or shell history.

The demo starts a separate Notepad process and types only into that process's
window. Keep the new Notepad window in the foreground while it starts; the
agent refuses to type if it cannot verify that window is focused.

Run the mocked tests from the repository root with:

```powershell
python -m unittest discover -s windows_agent/tests -v
```

The WhatsApp module is currently a mock demonstration only. There is no real
WhatsApp integration, unofficial Web client, or server-side AI decision making.
