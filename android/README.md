# Android agent

This Android app is the Phase 5 implementation for Pentactopus v1.

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

## GitHub Actions build

[`../.github/workflows/android-build.yml`](../.github/workflows/android-build.yml)
builds and tests the Android app on
pull requests and pushes to `main` that change `android/`, and can also be
started manually with `workflow_dispatch`. It uses JDK 17, Gradle 8.9, and
Android SDK setup on a GitHub-hosted runner; it does not require a local Android
SDK or Gradle installation. The unsigned debug APK is uploaded as the
`pentactopus-android-debug` workflow artifact for 14 days.
