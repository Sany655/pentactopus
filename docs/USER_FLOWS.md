# User Flows & Journeys

## 1. Onboarding & Device Pairing Flow
1. **Cloud Registration**: User signs up on the Web Dashboard to get an account.
2. **Windows Installation**: User downloads the `.exe` and runs it. The daemon initializes automatically in the background.
3. **Android Pairing**: 
   - User installs the `.apk`.
   - The app asks for a Connection Code or signs in via OAuth.
   - The app establishes a connection to the Cloud Relay or local Windows Host.

## 2. AI Task Flow (Consistent across Web/Win/Android)
1. **Input**: User types a natural language goal in the Prompt Bar.
2. **State Change**: Button changes to "Running..." and is disabled.
3. **Action log**: Terminal/UI logs `[AGENT] Dispatched: <goal>`.
4. **Execution**: The AI performs vision processing and mouse/keyboard inputs.
5. **Success/Error**: UI logs `[AGENT] Task completed successfully` or displays inline red error text. Button resets.

## 3. Remote Control Flow
- **Windows Local**: Connects via USB ADB to phone -> launches `scrcpy` (native window pop-out).
- **Android Client**: Selects "Windows Host" -> Connects to Port 5050 -> Displays screen polling stream -> Sends clicks back.
