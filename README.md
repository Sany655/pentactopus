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
[DECISIONS.md](./DECISIONS.md). Phase 2 server implementation is underway;
the Windows, end-to-end, and Android phases remain gated on approval.

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
is responsible for their provider account and key. A local-only model option
keeps content on the user's devices.

Windows WhatsApp support is planned to read the official WhatsApp Desktop app
for personal use only. Automation may be restricted by WhatsApp's terms.
Review the current terms and accept that risk before enabling WhatsApp support.
v1 does not use unofficial WhatsApp Web libraries.

## Phase gates

Phase 1 design and Phase 2 implementation are approved. Phase 3 Windows-agent
work is now in progress with device-local policy, BYOK model handling, and
approval-gated outbound actions. End-to-end and Android phases remain gated on
separate approval.

The Windows agent is implemented in the `windows_agent/` package and keeps all
model credentials and policy decisions on-device. It reads official WhatsApp
Desktop metadata/content for personal use only and blocks T6 forbidden apps and
2FA/password-manager workflows locally before any action is attempted.

## Legacy reset record

Legacy application files and assets were removed from the working tree after
approval; Git history and the user-confirmed MIT `LICENSE` were preserved.
The path groups, original tracked file counts, and disposition are listed in
section 10 of [DESIGN.md](./DESIGN.md).
