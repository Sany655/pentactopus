# SMS Webhook Bridge

A production-ready, transparent Android application designed for personal automation.
When an SMS arrives from one configured phone number, it automatically and securely forwards the message to your HTTPS web application webhook endpoint.

---

## Key Features

1. **Strict Sender Filtering**: Only messages from your explicitly configured sender phone number or alphanumeric ID are forwarded. All other SMS messages are completely ignored.
2. **Transparent Background Execution**:
   - Operates with a visible, persistent foreground service and status notification.
   - Clear Start / Stop controls in the app and on the persistent notification.
   - Fully visible in Android Settings and the system launcher (no stealth or evasion techniques).
3. **Secure Webhook Delivery**:
   - **HTTPS Only**: Plaintext HTTP is strictly rejected. TLS certificate verification is enforced.
   - **Authentication**: Supports `Authorization: Bearer <token>` header.
   - **Zero Secret Exposure**: Tokens are stored securely in Android Keystore / `EncryptedSharedPreferences` and masked in logs.
4. **Reliability & Offline Queue**:
   - Built on Android `WorkManager` with `NetworkType.CONNECTED` constraint.
   - Automatic retries with exponential backoff for network drops or 5xx server errors.
   - Permanent failures (4xx client errors) are marked appropriately without wasteful loops.
   - Built-in deduplication filter (5-minute window) to prevent duplicate event transmissions.
   - Unique persistent UUID (`event_id`) for every forwarded SMS.
5. **Content-Triggered Auto-Deletion**:
   - Optionally deletes matching SMS messages from your device inbox when a specific number/code is detected in the message text.
   - Explains Android system constraints: Android KitKat (4.4) through 14+ requires an app to hold the *Default SMS App* role to delete messages from the system inbox. A one-tap shortcut in Settings allows setting this role.

---

## Webhook API Format

### POST Request (`application/json`)

```http
POST /api/sms/incoming HTTP/1.1
Host: your-server.com
Content-Type: application/json; charset=utf-8
Authorization: Bearer <your_optional_token>
X-Device-Id: android-Pixel-7-a1b2c3d4
X-Event-Id: 9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d

{
  "event_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "sender": "+8801700000000",
  "message": "Your verification code is 849201",
  "received_at": "2026-10-05T13:30:00.000Z",
  "device_id": "android-Pixel-7-a1b2c3d4"
}
```

### GET Request (URL-Encoded Query Parameters)

```http
GET /api/sms/incoming?event_id=9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d&sender=%2B8801700000000&message=Your%20code%20is%20849201&received_at=2026-10-05T13%3A30%3A00.000Z&device_id=android-Pixel-7-a1b2c3d4 HTTP/1.1
Host: your-server.com
Authorization: Bearer <your_optional_token>
X-Device-Id: android-Pixel-7-a1b2c3d4
X-Event-Id: 9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

### Expected Server Response

- `200 OK` or `201 Created`: Message considered successfully delivered.
- `4xx Client Error` (e.g. `401 Unauthorized`, `400 Bad Request`): Marked as permanent failure.
- `429 Too Many Requests` or `5xx Server Error`: Automatically re-queued with exponential backoff.

---

## Permissions Explained

| Permission | Purpose |
|------------|---------|
| `RECEIVE_SMS` | Required to intercept and parse incoming SMS messages to filter for your allowed sender. |
| `READ_SMS` | Fallback read capability for multi-part concatenated SMS messages. |
| `INTERNET` | Required to transmit HTTPS webhooks to your server. |
| `ACCESS_NETWORK_STATE` | Used by WorkManager to defer webhook retries until network connectivity is active. |
| `POST_NOTIFICATIONS` | Displays the transparent background service notification on Android 13+. |
| `FOREGROUND_SERVICE` & `DATA_SYNC` | Ensures the service remains running transparently in the background on Android 14+. |
| `RECEIVE_BOOT_COMPLETED` | Restores service state automatically if the phone is rebooted. |

---

## Configuration Guide

1. **Install and Launch**: Open **SMS Webhook Bridge** from your app drawer.
2. **First Run Onboarding**: Review the purpose statement and grant the SMS and Notification permissions.
3. **Configure Settings**:
   - **Allowed Sender**: Enter the phone number (e.g., `+8801700000000` or `01700000000`) or alphanumeric sender ID (e.g., `MYBANK`).
   - **Webhook URL**: Enter your secure webhook endpoint (must begin with `https://`).
   - **HTTP Method**: Choose `POST` (recommended) or `GET`.
   - **Auth Token**: Enter your shared secret (optional). Transmitted as `Bearer <token>`.
   - **Max Retries / Delay**: Configure retry attempts (default: 3 retries, 10s initial delay).
   - **SMS Auto-Deletion**: Enable the toggle and specify the number or code (e.g., `849201`). Tap *Set as Default SMS App* if you wish the app to delete matching messages from the Android system inbox.
4. **Test Webhook**: Return to the **Dashboard** and tap **[Test Webhook]** to verify your endpoint.
5. **Start Service**: Tap **[Enable]** or use the status switch. A persistent notification will confirm the bridge is actively monitoring.

---

## Building and Running Tests

### Run Unit Tests
```bash
./gradlew test
```

### Build Debug APK
```bash
./gradlew assembleDebug
```
The generated APK will be located at:
`app/build/outputs/apk/debug/app-debug.apk`
