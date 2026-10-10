# Android agent

This Android app is the in-progress Phase 5 client for Pentactopus v1.

Scope:
- minSdk 26 (Android 8.0)
- Kotlin app with Android Keystore-backed key material
- NotificationListenerService for incoming notification reads
- Accessibility-based sending after T4 approval
- local policy enforcement for T0-T6 actions
- metadata-only audit trail; no raw message content persists in the server database

Notes:
- This is a lightweight v1 scaffold meant for Android Studio and real-device validation on Android 9 and one Android 8 device.
- The app keeps model keys and policy decisions on-device.
- The server is never trusted with message plaintext or provider keys.
- Server pairing, signed foreground polling, and heartbeat are wired to the
  server API. Sync pauses when the app is not visible and polls every five
  seconds, with a heartbeat every minute. The app displays queued/active task
  metadata but does not claim or execute tasks yet. Cross-device approval
  synchronization is not integrated; the current exact-send approval is local
  to this device and should be tested only with non-sensitive content.
- Remote model endpoints require HTTPS and a provider key. A localhost endpoint
  may use HTTP without a key for on-device inference; cleartext is denied for
  all other hosts.
- Message, pairing-code, approval, and provider-key fields are excluded from
  saved view state/autofill; message screens block screenshots and recents
  previews.
- Ed25519 support uses Bouncy Castle because the Android 8/API 26 baseline does
  not consistently provide the required JCA implementation. The private key
  is encrypted at rest with an Android Keystore-backed AES key.
- The workflow builds a debug APK; it does not publish a signed release.

## Manual Android smoke test

1. Install the `pentactopus-android-debug` artifact from a successful Android
   build workflow on an Android 9 or Android 8 device.
2. Launch the app, sign in on the web to create a pairing code, enter the
   server's HTTPS origin and a unique device name, then pair before the code
   expires. Confirm the status becomes online. A queued test task should be
   visible in the status line and remain unclaimed.
3. Enable WhatsApp notification access from its button. Send a test
   notification to the phone and confirm it appears in the
   in-memory notification list; dismiss it and confirm it is removed.
4. Enter a test provider endpoint/key only if you intend to send the test
   prompt to that provider. For local inference, enter the localhost Ollama
   OpenAI-compatible endpoint and leave the key empty. Accept the on-screen
   disclosure, save, and try a non-sensitive prompt.
5. For Accessibility smoke tests, use a non-sensitive test chat, enable the
   service, open the exact recipient chat in WhatsApp, return to Pentactopus,
   review and approve the exact recipient and text, then let the service return
   to WhatsApp. Confirm a mismatched chat, changed payload, or expired approval
   does not send.

## GitHub Actions build

[`../.github/workflows/android-build.yml`](../.github/workflows/android-build.yml)
builds and tests the Android app on
pull requests and pushes to `main` that change `android/`, and can also be
started manually with `workflow_dispatch`. It uses JDK 17, Gradle 8.9, and
Android SDK setup on a GitHub-hosted runner; it does not require a local Android
SDK or Gradle installation. The unsigned debug APK is uploaded as the
`pentactopus-android-debug` workflow artifact for 14 days.
