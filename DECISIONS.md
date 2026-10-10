# Security-Relevant Decisions

Decisions are recorded with the phase that established them. Proposals remain
pending until the user approves the phase gate.

## Phase 1 — approved

| ID | Decision | Security rationale / consequence |
|---|---|---|
| D-001 | The reset removes legacy files from the v1 branch but preserves Git history. | Avoids an irreversible history rewrite while establishing a clean v1 tree; user confirmed this reset interpretation. |
| D-002 | Next.js 16.4.0 with TypeScript/App Router; Vercel Node.js 24.x runtime, not Edge. | Node runtime supports the selected Neon driver and cryptographic operations; Next 16 requires Node 20.9+, and Vercel currently supports 24.x. |
| D-003 | Use `@neondatabase/serverless` `Pool` with Neon's pooled connection string for Node Route Handlers. | Supports transactional operations needed for auth and approval state; atomic task claim remains a conditional SQL update. Do not connect to an unpooled endpoint from Vercel. |
| D-004 | No password database. Use one-use hashed magic-link tokens and opaque server-side sessions in Neon; consume magic links through an explicit POST. | Limits credential persistence and avoids link-scanner consumption; cookie protections and rate limiting are mandatory. |
| D-005 | Devices generate Ed25519 keypairs and sign each API request over canonical request metadata, with unique nonce and bounded timestamp. | Server verifies possession without receiving private keys; nonce uniqueness prevents replay across serverless instances. |
| D-006 | Shared contracts are versioned JSON Schema under `/contracts/v1/`; every schema change increments its semantic version, and incompatible wire changes increment the major version. | One source of wire truth for TypeScript and Python prevents silent shape drift. |
| D-007 | Windows packaging proposal is PyInstaller one-folder (`onedir`); Android minSdk is 26. | One-folder avoids one-file self-extraction and improves inspectability; Android covers the stated supported baseline. |
| D-008 | Neon and audit logs contain metadata only; message/action plaintext is client-encrypted and ciphertext is held temporarily in Upstash Redis with per-key TTL. | Limits cloud exposure. Chosen over Vercel Blob because Blob's scheduled cleanup would not guarantee the required 10-minute logical expiry. Redis TTL controls key availability/expiry; verify provider persistence and physical deletion terms separately. |
| D-009 | T4 approvals bind one task to a digest of the exact action payload; T5 also requires a stronger local confirmation on the executing device. | Prevents edits/replay and preserves the stronger high-impact-action boundary. |
| D-010 | Local device policy is authoritative for capability checks and T6 blocks; model output and inbound messages are untrusted data. | Prevents server/model text from granting policy or approval. |
| D-011 | Preserve the existing MIT `LICENSE` unchanged; the user confirmed the named copyright holder owns or authorizes the v1 work under it. Do not reuse legacy application code absent explicit approval. | Prevents accidental reuse of unreviewed code or incorrect licensing during reset. |

## Phase 2 decisions — approved

| ID | Decision | Rationale / implementation boundary |
|---|---|---|
| D-012 | Conversation maximum is 20 turns, enforced transactionally in the pipeline row. | Prevents unbounded conversations and races. |
| D-013 | Use Ajv for TypeScript and Python `jsonschema` for shared JSON Schema Draft 2020-12 validation. | Both runtimes validate the same contract files; pin versions and test the same valid/invalid fixtures. |
| D-014 | Use Upstash Redis via `@upstash/redis` and its HTTPS REST transport to store message and artifact ciphertext with per-key millisecond TTL. Do not add `@vercel/blob`. | TTL-native storage avoids dependence on best-effort cron for logical expiry; API remains the authorization boundary. Review provider persistence, payload bounds, and deletion terms. |
| D-015 | Use Resend for email magic-link delivery through its HTTPS API and built-in `fetch`; do not add a Resend SDK. | Keeps provider integration narrow and avoids an additional runtime dependency; API keys remain deployment secrets. |
| D-016 | Cap each encrypted inbox/artifact object at 1 MiB. | Text-first v1 bounds request, Redis, memory, and cost exposure; attachments remain represented as metadata/links unless separately supported. |
| D-017 | Add `tsx` as a development-only dependency for Node's built-in test runner and TypeScript migration/test scripts. | Avoids adding a separate test framework while allowing direct execution of typed server logic tests. |
| D-018 | Runtime dependencies are Next.js 16.4.0/React 19.3.0, `@neondatabase/serverless` 1.2.0, `@upstash/redis` 1.39.0, and Ajv 8.20.0. Development dependencies are TypeScript 5.9.3, Node 24.19.0/React 19.3.0 types, ESLint 10.12.0, `eslint-config-next` 16.4.0, and `tsx` 4.23.15. | Versions are pinned in `package.json` and the npm lockfile. Python `jsonschema` is deferred to the Windows-agent phase and is not installed on the server. The npm audit currently reports a high-severity advisory in the lint-only transitive `braces@3.0.3`; the advisory has no published patched release. Recheck before deployment and do not expose pattern matching to user-controlled glob expressions. |
| D-019 | Bumped the unreleased API and task-envelope JSON Schemas from 1.0.0 to 1.0.1 before Phase 2 deployment when adding parent-task delegation, exact-approval execution, and metadata identifier constraints. | Maintains the required version bump before wire contracts are deployed. |
| D-020 | Task bodies are limited to 16 KiB and use a strict allowlist of enums, UUIDs, bounded numeric values, and technical app identifiers; arbitrary strings and properties are rejected. Message/action content must travel as device-encrypted inbox/artifact ciphertext. | Prevents task JSON from becoming a plaintext message or prompt store while leaving policy and AI decisions on the device. |
| D-021 | Bumped the unreleased API and task-envelope schemas from 1.0.1 to 1.0.2 when tightening task-body fields to typed metadata only. | Applies the mandatory contract-version increment before any v1 client is released. |
| D-022 | Bumped API and task-envelope schemas to 1.0.3 when removing caller-supplied device/artifact/step identifiers from the task body; identities and artifact refs have authoritative envelope fields. | Prevents shadow identity fields and mismatched artifact/step metadata. |

## Phase 3 — approved

| ID | Decision | Rationale / implementation boundary |
|---|---|---|
| D-023 | Windows agent policy is authoritative for capability gating, T-tier enforcement, and T6 blocks for password managers and 2FA flows. | The server stores metadata only; the device enforces local policy before any action. |
| D-024 | Local BYOK model calls remain on-device using provider credentials stored in Windows Credential Manager or equivalent local protection; local-only Ollama/HTTP endpoints remain a supported option. | Keeps provider keys off the server and supports a local-only inference mode. |
| D-025 | Windows WhatsApp support is limited to the official Desktop app for personal use; no unofficial Web client or automated bypass mechanisms are used. | Avoids prohibited third-party WhatsApp integrations and keeps the user aware of WhatsApp terms risk. |
| D-026 | The Windows agent records metadata-only local audit events and does not store raw message bodies, provider prompts, or recipient text in the server log path. | Preserves the privacy boundary even when local automation is in use. |

### Phase 2 implementation prerequisites

- Configure a verified Resend sender/domain in deployment; credentials remain
  deployment secrets and `.env.example` contains placeholders only.
- Configure Upstash persistence according to its retention controls. Redis TTL
  and server-side expiry checks enforce logical expiry; they are not a claim of
  physical-media erasure.
- Request bodies are bounded, API rate limits use a keyed digest of client
  identity, and encrypted inbox/artifact payloads are capped at 1 MiB.
- No package beyond the approved dependency ledger was added.

Phase 2 implementation was explicitly authorized after the approved legacy
reset. Work is in progress; do not begin Phase 3 until the user approves the
Phase 2 gate.
