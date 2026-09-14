# Penta-Assistant: User Manual & Technical Guide

**Penta-Assistant** combines the agentic intelligence of **Google Antigravity** on Windows with **AnyDesk-style cross-platform remote viewing and tactile control** across your Windows PC and Android phone, backed by a **Vercel Cloud Serverless Hub** and local device daemons.

---

## 1. System Overview

Penta-Assistant operates as a unified mesh across three primary layers:
1. **Cloud Serverless Hub (Vercel)**:
   - Configured via `vercel.json` and `api/index.py`.
   - Accessible from any browser worldwide at `https://<your-project>.vercel.app`.
   - Maintains the global device registry, frame cache, action queues, and multi-model routing.
2. **Windows PC Node (Host)**:
   - Captures native Windows desktop frames (~15ms via Win32 GDI).
   - Injects mouse clicks, double clicks, right clicks, keyboard typing, hotkeys, volume, and app launches.
   - Hosts the Google Antigravity autonomous PC Computer-Use agent.
3. **Android Phone Node (Node)**:
   - Communicates via ADB over USB or Wi-Fi (Redmi Note 6 Pro).
   - Streams live phone screen frames and receives direct touch taps, directional swipes, hardware navigation keys (Back, Home, Recents, Power, Vol+/Vol-), and app launches.
   - Hosts the autonomous Mobile AI agent.

---

## 2. Deploying to Vercel (Cloud Relay)

To deploy the cloud serverless hub to Vercel:
```powershell
# 1. Install Vercel CLI (if not already installed)
npm install -g vercel

# 2. Deploy from the project root
cd C:\AI-Android-Agent
vercel
```
Once deployed:
* Access the web UI worldwide from any smartphone or computer without port forwarding!
* Run `python -m penta.penta_daemon` on your Windows PC to bridge local screen frames and execute remote commands dispatched from Vercel.

---

## 3. Web Dashboard Guide (`http://localhost:5050`)

### How to Start the Local Dashboard
Double-click `run_ui.bat` or run:
```powershell
cd C:\AI-Android-Agent
python ui.py
```

### Dashboard Sections
1. **Top Bar**:
   - **Connection Badges**: Displays device state and `🤖 Google Antigravity + 📡 AnyDesk` status.
   - **📱 Launch scrcpy Mirror**: Opens the low-latency native phone mirror window on Windows.
   - **📶 Switch to Wi-Fi**: Automatically pairs your USB-connected phone to Wi-Fi mode.
   - **🔄 Scan Devices**: Refreshes ADB and device mesh states.
2. **Left Panel**:
   - **Connected Devices & Mesh**: Shows model, battery, connection mode, and manual IP connect.
   - **Unified Model Configuration**: Switch between Gemini 2.5, Claude 3.5, GPT-4o, Groq Llama 3, DeepSeek, OpenRouter, and Ollama.
   - **Live Screen Capture**: Quick thumbnail preview of the active device.
3. **Right Panel (Tabs)**:
   - **📡 AnyDesk Remote Viewport**:
     - **Sub-Device Switcher**: Seamlessly toggle between `🖥️ Windows PC (Host)` and `📱 Android Phone (Node)`.
     - **When Windows PC is Active**:
       - Live desktop stream with tap-to-click.
       - Quick Action Bar: Win+D, Vol +, Vol -, Mute, Play/Pause, Lock.
       - App Launcher: Chrome, Notepad, Calculator, Explorer, Terminal, URL.
       - Remote Text Typing into active Windows window.
       - 🤖 **Google Antigravity PC Agent**: Prompt box to execute autonomous desktop tasks.
     - **When Android Phone is Active**:
       - Live phone screen with tap-to-touch (auto-scaled to physical phone resolution).
       - Hardware Navigation Bar: ◀️ Back, ⏺️ Home, 🔲 Recents, ⚡ Power/Wake, 🔊 Vol +, 🔉 Vol -.
       - Directional Gestures: ⬆️ Scroll Down (Swipe Up), ⬇️ Scroll Up (Swipe Down), ⬅️ Left, ➡️ Right.
       - Quick App Launchers: Settings, Chrome, Camera, YouTube, Calculator, Dialer, WhatsApp.
       - Remote Text Typing into active phone field.
       - 🤖 **Google Antigravity Mobile Agent**: Prompt box to execute autonomous phone tasks.
   - **🏢 5-Agent Org Room**: Dispatches missions across CEO, Mobile, Desktop, Browser, and Notifier agents.
   - **🎯 Phone Autonomous Agent**: Single-goal task runner with perception & action trace.
   - **📂 Mission Dossiers**: Report and documentation viewer.

---

## 4. Troubleshooting Reference

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| `error: more than one device/emulator` | Phone is connected via USB and Wi-Fi simultaneously. | Disconnect one link via `adb disconnect <IP>` or unplug USB, or specify `-s <serial>`. |
| `500 (Screenshot capture failed)` | Multiple devices attached or phone screen is locked. | Unlock phone and ensure a single device is active. |
| `❌ Failed to switch wireless` | Phone was not detected on USB when clicking the button. | Ensure USB cable is plugged in with "USB Debugging" turned ON in Developer Options. |
| Button click shows no response | Stale process or syntax error on old version. | Run `run_ui.bat` to launch the upgraded multi-threaded engine. |
| PC Screen preview not loading | Ensure port 5050 is accessible over your network/tunnel. | Check Wi-Fi IP or Tailscale IP connection from your phone's browser. |
