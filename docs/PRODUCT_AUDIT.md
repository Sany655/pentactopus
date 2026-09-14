# Pentactopus Product Audit

## Current Architecture
- **Frontend/Web UI**: Pure HTML/CSS/JS served via Python (`api/web_template.py`), deployed as serverless functions on Vercel.
- **Backend API**: Python serverless functions (`api/index.py`) handling auth, device registration, billing, and Stripe webhooks.
- **Windows Client**: Native Win32 desktop controller packaged via PyInstaller (`PentaAssistant-Setup.exe`), connecting to local ADB and screen capturing.
- **Android Client**: ADB-driven control from the host machine or via the standalone Tauri app.
- **AI Agent**: Orchestrator loop using `gemini-2.5-flash` for computer vision and reasoning (`models/gemini.py`).
- **WebRTC/Streaming**: Currently relies on HTTP polling via the `hub/device_hub.py` and local port 5050. Cloud streaming requires a dedicated relay.
- **Authentication**: PBKDF2-HMAC-SHA256 (100k rounds) with cryptographic session tokens.
- **Database**: PostgreSQL (via Supabase/Neon) adapter `api/db_adapter.py` with fallback to local JSON.
- **Payments**: Stripe Checkout integration with dynamic resource calculation.

## What Works
- Account registration, login, session management, and brute-force protection.
- Stripe checkout session generation and webhook license provisioning.
- Database auto-schema creation and persistence.
- Local Windows client compilation (`PentaAssistant-Setup.exe`).
- Multi-model fallback mechanism and local UI.

## What is Broken / Incomplete
- **Real-time Cloud Streaming**: HTTP polling on Vercel is insufficient for low-latency video streaming across NAT. Needs a WebRTC signaling server or WebSocket relay.
- **Tauri Android App**: The Android APK build process via Tauri requires manual CI configuration and signing.

## Critical Risks
- Vercel's 10-second timeout will kill any long-running AI task or persistent connection.
- Without a dedicated WebSocket/WebRTC relay, remote control over the internet is not real-time.

## UX Problems
- The landing page has repetitive sections regarding infrastructure pillars.
- "AnyDesk Viewport" references were removed from the user manual and documentation, but ensure no UI components still leak third-party brands.

## Technical Debt
- Local vs Cloud separation: The desktop runner (`ui.py`) and cloud API (`api/index.py`) duplicate some hub logic.
- Client binaries are large (~27MB PyInstaller bundles).

## Launch Blockers
- Connecting a production Supabase URL to Vercel environment variables.
- Deploying a lightweight signaling server (e.g., on Railway or Fly.io) if real-time cloud control is advertised.
- Removing repetitive content from the landing page.

## Recommended Priority
1. P0: Fix landing page copy to match the "Your computer. Controlled by you — or your AI" MVP.
2. P0: Connect live Supabase and Stripe keys to Vercel.
3. P1: Clean up `penta-app/src/App.jsx` UI and rebuild the Tauri app.

## Do NOT build list
- Custom WebRTC infrastructure from scratch (use LiveKit or standard signaling).
- Complex team management dashboards (stick to basic roles).
- Social features.
