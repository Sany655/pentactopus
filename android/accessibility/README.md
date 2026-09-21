# Pentactopus Android Accessibility Service

## Overview
The `PentaAccessibilityService` enables autonomous tactile touch, gesture dispatch, and UI navigation directly on Android devices **without requiring ADB or root access**.

## Architecture
1. **Service Registration**: Registered in `AndroidManifest.xml` with `BIND_ACCESSIBILITY_SERVICE` and configured via `accessibility_service_config.xml` (`canPerformGestures="true"`).
2. **Local Loopback IPC**: Upon connection, the service runs a background socket listener on `127.0.0.1:18888`.
3. **Dispatch Flow**:
   - `AndroidCompanionRelay` or Termux scripts issue a POST request to `http://127.0.0.1:18888/` with JSON payloads:
     - Tap: `{"action": "tap", "x": 540, "y": 960}`
     - Swipe: `{"action": "swipe", "x1": 500, "y1": 1200, "x2": 500, "y2": 400, "duration": 300}`
     - System navigation: `{"action": "nav", "key": "BACK" | "HOME" | "RECENTS"}`
   - The Accessibility Service dispatches gestures natively using Android's `dispatchGesture()` API.
   - If the service is not currently enabled in Android Accessibility Settings, `companion_relay.py` automatically falls back to standard shell `input tap / swipe`.

## Enabling the Service on Device
1. Build and install the companion APK.
2. On the Android device, go to:
   **Settings → Accessibility → Downloaded Apps → Pentactopus Remote Service**.
3. Toggle the switch to **On** and grant gesture permission.
