# Pentatopus Security Audit

## CRITICAL
*None currently identified post-refactor.* Password hashing, session tokens, and route guards have been successfully implemented and tested.

## HIGH
- **Cloud Signaling**: If users control PCs over the internet, a secure end-to-end encrypted WebRTC channel must be established. Currently, HTTP polling can expose frame data if not strictly secured over HTTPS with token validation on every request.

## MEDIUM
- **Local Agent Permissions**: The AI agent (`pc_agent.py`) executes commands with the privileges of the user running `PentaAssistant-Setup.exe`. There is no sandbox. Destructive commands (e.g., deleting files) requested by the user will be executed.

## LOW
- **Rate Limiting**: Brute force protection exists for login (5 attempts / 15 mins), but general API endpoints lack strict token-bucket rate limiting, which could lead to minor abuse.
