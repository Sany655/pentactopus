# Pentactopus

Pentactopus is a personal, polling-only assistant for a user's own devices.
Each device runs its own agent, local model loop, credentials, and policy. The
server authenticates devices, routes tasks, enforces ownership, and stores
metadata; it does not make AI calls.

## v1 scope

The approved design excludes live screen viewing, WebRTC/TURN, direct
device-to-device connections, multi-hub networking, web chat, and billing.
The repository has been reset without rewriting Git history. No legacy
application implementation has been reused.

See [DESIGN.md](./DESIGN.md) for the architecture, API and database design,
threat model, and reset inventory. Security-relevant choices are tracked in
[DECISIONS.md](./DECISIONS.md).

## Server development

Requirements: Node.js 22.13+ (deployment target: Node.js 24.x) and a Neon
PostgreSQL database configured with its pooled connection string.

1. Copy `.env.example` to `.env.local` and fill the required deployment
   settings. Do not commit secrets.
2. Install the pinned dependencies with `npm ci`.
3. Apply the forward-only database migrations with `npm run db:migrate`.
4. Start the development server with `npm run dev`.

Required server settings are `DATABASE_URL`, `RESEND_API_KEY`,
`RESEND_FROM_EMAIL`, `UPSTASH_REDIS_REST_URL`,
`UPSTASH_REDIS_REST_TOKEN`, `RATE_LIMIT_HMAC_KEY`, and `APP_ORIGIN`.
`WINDOWS_DOWNLOAD_URL` and `ANDROID_DOWNLOAD_URL` are optional release links.
Use a random, high-entropy `RATE_LIMIT_HMAC_KEY` and provider credentials from
deployment secrets. Resend requires a verified sender domain.

## Privacy and safety

Message text and action content must be encrypted on the source device before
it reaches the server. Neon stores metadata only; Redis holds ciphertext with
a TTL, and endpoints independently enforce expiry and recipient ownership.
The server never receives model-provider keys or plaintext message content.
Set provider persistence/retention intentionally; TTL is logical expiry, not
a guarantee of physical-media erasure.

Message text may be processed by the model provider selected by the user.
Third parties who message the user are not party to that agreement; the user
is responsible for their provider account and key. The Android client permits
remote model connections over HTTPS, or an HTTP model endpoint on localhost
only for on-device inference.

Windows app automation is capability-based; WhatsApp was one example use case,
not a requirement for the Windows agent. The first real desktop action is
writing an unsent draft into Notepad. The user reviews and saves/sends it
manually. The agent does not currently integrate with WhatsApp or other
messaging apps.

## Implementation and validation status

The server and Windows client implementations are present; Phase 4 has
simulation coverage, not two-device acceptance. The Android client under
`android/` includes notification capture, BYOK chat, Keystore-backed settings
and device signing, local policy, exact-payload local T4 approval, server
pairing, and signed foreground polling. The Android client currently displays
server task metadata but does not claim or execute tasks; server-mediated
cross-device approval is also not integrated. These are remaining v1
implementation gaps, not verified features.

The [Android build workflow](./.github/workflows/android-build.yml) runs
Android unit tests and assembles an unsigned debug APK. A successful run and
real-device checks on Android 9 and one Android 8 device are still required
before declaring Android Phase 5 complete. Phase 4 also needs its real
two-device scenarios before end-to-end acceptance can be claimed.

The Windows agent is implemented in the `windows_agent/` package and keeps
policy decisions on-device. Its Notepad draft action types only locally
available text, logs metadata but not draft content, and blocks T6 forbidden
apps and 2FA/password-manager workflows locally before any action is attempted.

## Legacy reset record

Legacy application files and assets were removed from the working tree after
approval; Git history and the user-confirmed MIT `LICENSE` were preserved.
The path groups, original tracked file counts, and disposition are listed in
section 10 of [DESIGN.md](./DESIGN.md).
