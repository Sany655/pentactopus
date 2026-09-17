# 🐙 PENTACTOPUS — Master Documentation Tree

> **Objective**: Combine the power of AnyDesk + Antigravity into a unified cross-platform system for **Windows** and **Android**, featuring AI agents, remote desktop control, and multi-device communication.

> **Methodology**: Agile | **Sequence**: Web → Windows → Android

---

## 📌 System Identity

| Field | Value |
|---|---|
| **Project Name** | Pentactopus |
| **Version** | 2.5.0 |
| **Repo** | [github.com/Sany655/pentactopus](https://github.com/Sany655/pentactopus) |
| **Production URL** | [pentactopus.vercel.app](https://pentactopus.vercel.app) |
| **Platforms** | Web (Vercel) • Windows (Tauri v2) • Android (Tauri v2) |
| **Stack** | Python 3.10+ (backend/agent) • React 18 + Vite (frontend) • Rust/Tauri v2 (native shell) • Vercel Serverless (cloud) |

---

## 🎯 Core Features Matrix

| ID | Feature | Description | Status |
|---|---|---|---|
| **F1** | AI Agent (Antigravity-like) | Multi-model autonomous computer-use agent with model selector & API key config | ✅ Built |
| **F2** | Remote Control (AnyDesk-like) | P2P WebRTC remote desktop streaming with mouse/keyboard/touch injection | 🟡 Partial |
| **F3** | Multi-Device Communication | Agent/user communication: audio, video, remote control levels, admin modes across devices | 🔴 Not started |
| **F4** | Auth & Authorization | PBKDF2 passwords, brute-force lockout, RBAC (guest/user/admin), route guards | ✅ Built |

### Feature Status Legend
- ✅ **Built** — Code exists and tests pass
- 🟡 **Partial** — Core logic exists, needs enhancement
- 🔴 **Not started** — No implementation yet

---

## 🏗️ Existing Codebase Map

### Directory Tree (What Exists Now)

```
pentactopus/                         # Project Root
│
├── .github/workflows/               # CI/CD
│   ├── build-clients.yml            # ✅ Tauri binary build pipeline (Win+Android)
│   └── build-android.yml            # ✅ Android-specific build
│
├── agent/                           # 🧠 AI Agent Core
│   ├── __init__.py
│   ├── core.py                      # ✅ AndroidAgent — perception→reasoning→validation→action loop
│   └── pc_agent.py                  # ✅ PCAgent — Windows desktop computer-use agent
│
├── adb/                             # 📱 Android Debug Bridge Client
│   ├── __init__.py
│   └── client.py                    # ✅ ADB wrapper (device discovery, screenshot, input, UI dump)
│
├── android/                         # 📱 Android Helpers
│   ├── __init__.py
│   ├── companion_relay.py           # 🟡 Companion app relay stub
│   └── uiautomator.py              # ✅ UIHierarchyParser — parses XML UI tree
│
├── api/                             # 🌐 Vercel Serverless Backend
│   ├── index.py                     # ✅ Main request router (466 lines, all routes)
│   ├── web_template.py              # ✅ Landing page + Auth UI (1174 lines, HTML/CSS/JS)
│   ├── admin_dashboard.py           # ✅ Admin console renderer
│   ├── user_store.py                # ✅ PBKDF2 auth, sessions, brute-force defense
│   ├── billing.py                   # ✅ Stripe checkout, pricing plans
│   ├── coupons.py                   # ✅ Promo code engine
│   └── db_adapter.py               # ✅ Postgres/Upstash KV persistence layer
│
├── data/                            # 💾 Local JSON Data Store
│   ├── users.json                   # ✅ Seeded user records
│   ├── sessions.json                # ✅ Session tokens
│   ├── licenses.json                # ✅ License keys
│   └── coupons.json                 # ✅ Promo codes
│
├── docs/                            # 📚 Documentation (18 files)
│   ├── ARCHITECTURE.md              # ✅ System architecture diagram
│   ├── REMOTE_ACCESS_GUIDE.md       # ✅ Remote control setup guide
│   ├── USER_MANUAL.md               # ✅ End-user manual
│   ├── SECURITY_AUDIT.md            # ✅ Security review
│   ├── PRODUCT_AUDIT.md             # ✅ Product readiness audit
│   └── ... (13 more docs)          # ✅ Various guides & audits
│
├── hub/                             # 🔗 Device Mesh Hub
│   ├── __init__.py
│   └── device_hub.py               # ✅ Device registry, action queues, frame buffer, KV persistence
│
├── marketing/                       # 📣 Marketing Assets
│   ├── demo-script.md              # ✅ Demo talking points
│   ├── landing-page-copy.md        # ✅ Marketing copy
│   ├── launch-post.md              # ✅ Launch announcement
│   └── Pentactopus_Commercial_Demo.mp4  # ✅ Video demo
│
├── models/                          # 🤖 Multi-Model AI Gateway
│   ├── __init__.py                  # ✅ Provider registry
│   ├── base.py                      # ✅ BaseModelProvider abstract class
│   ├── router.py                    # ✅ Unified gateway + fallback chain
│   ├── gemini.py                    # ✅ Google Gemini 2.5 Flash
│   ├── anthropic.py                 # ✅ Claude 3.5 Sonnet
│   ├── openai_compatible.py         # ✅ OpenAI/DeepSeek/Groq/OpenRouter
│   ├── ollama.py                    # ✅ Local Ollama (Llama 3.2)
│   └── mock.py                     # ✅ Mock provider for testing
│
├── organization/                    # 🏢 Multi-Agent Organization
│   ├── __init__.py
│   ├── bus.py                       # ✅ EventBus — async message routing
│   ├── orchestrator.py              # ✅ ChiefOrchestrator — cross-platform audit workflow
│   ├── cognitive_orchestrator.py    # ✅ CognitiveOrchestrator — NL→plan→dispatch→compile
│   ├── desktop_agent.py             # ✅ Desktop agent (bus-connected)
│   ├── mobile_agent.py              # ✅ Mobile agent (bus-connected)
│   ├── browser_agent.py             # ✅ Browser/research agent
│   ├── notifier_agent.py            # ✅ Notification agent
│   ├── command_center.py            # ✅ Command dispatch center
│   ├── remote_bridge.py             # ✅ Remote device bridge registry
│   └── run_organization.py          # ✅ Organization entry point
│
├── pc_control/                      # 🖥️ Windows Desktop Controller
│   └── desktop_controller.py       # ✅ Native Win32 GDI capture, mouse/keyboard/hotkeys
│
├── penta/                           # 👹 Local Daemon
│   ├── __init__.py
│   └── penta_daemon.py             # ✅ PentaDaemon — bridge local devices to cloud hub
│
├── penta-app/                       # 📦 Native Client App (Tauri v2 + React)
│   ├── package.json                 # ✅ React 18 + Vite 5 + Tauri API v2
│   ├── vite.config.js               # ✅ Vite bundler config
│   ├── index.html                   # ✅ HTML entry
│   ├── src/
│   │   ├── App.jsx                  # ✅ Full client app (523 lines): login, chat, anydesk, settings
│   │   └── main.jsx                 # ✅ React root mount
│   └── src-tauri/
│       ├── tauri.conf.json          # ✅ Tauri v2 config (NSIS+MSI targets, sidecar binary)
│       ├── Cargo.toml               # ✅ Rust deps (tauri 2.0, tokio, serde, shell plugin)
│       └── src/                     # ✅ Rust backend code
│
├── tools/                           # 🔧 Utilities & Scripts
│   ├── action_schema.py             # ✅ Action validation schema
│   ├── allowlist.py                 # ✅ Security allowlist for ADB commands
│   ├── cloud_tunnel.py              # ✅ Cloud tunnel manager
│   ├── wireless_adb.py              # ✅ Wireless ADB connection helper
│   ├── scrcpy_helper.py             # ✅ scrcpy mirror launcher
│   ├── install_and_test_windows_app.py  # ✅ Windows app installation tester
│   ├── test_windows_binary.py       # ✅ Binary verification
│   ├── test_ui_downloaded_app.py    # ✅ UI download verification
│   ├── package_apk.py              # ✅ APK packager
│   ├── generate_commercial_video.py # ✅ Marketing video generator
│   └── sync_db_seeds.py            # ✅ Database seeder
│
├── tests/                           # 🧪 Test Suite (50/50 passing)
│   ├── test_action_validation.py    # ✅ 4 tests
│   ├── test_adb_security.py         # ✅ 3 tests
│   ├── test_auth_and_rbac.py        # ✅ 6 tests
│   ├── test_billing_and_coupons.py  # ✅ 7 tests
│   ├── test_multi_models.py         # ✅ 6 tests
│   ├── test_organization.py         # ✅ 4 tests
│   ├── test_pc_control.py           # ✅ 5 tests
│   ├── test_penta_hub.py            # ✅ 6 tests
│   ├── test_ui_hierarchy.py         # ✅ 2 tests
│   ├── test_user_roles_and_admin.py # ✅ 5 tests
│   ├── test_open_calculator.py      # ✅ 1 test
│   ├── test_open_settings.py        # ✅ 1 test
│   ├── test_native_tauri_ui.py      # ✅ Tauri UI tests
│   ├── test_playwright_ui.py        # ✅ Playwright browser tests
│   ├── test_cloud_daemon_and_downloads.py  # ✅ Cloud integration tests
│   ├── test_production_readiness.py # ✅ Prod readiness checks
│   └── take_screenshots.py          # ✅ Screenshot capture utility
│
├── vision/                          # 👁️ Vision Module (placeholder)
│   └── __init__.py                  # 🔴 Empty — needs implementation
│
├── main.py                          # ✅ CLI entry point for AndroidAgent
├── ui.py                            # ✅ Local dev server (900 lines, port 5050)
├── local_ui_template.py             # ✅ Local UI HTML template
├── run_sidecar.py                   # ✅ Sidecar process launcher
├── build_sidecar.ps1                # ✅ PowerShell sidecar build script
├── vercel.json                      # ✅ Vercel deployment config
├── requirements.txt                 # ✅ Python dependencies
├── .env.example                     # ✅ Environment variable template
├── .env                             # 🔒 Live secrets (not committed)
├── pentactopus.db                   # 💾 SQLite database
└── PentaAssistant-Setup-latest.exe  # 📦 Pre-built Windows installer (20.5 MB)
```

---

## 🎨 UI/UX Page Inventory

### Windows + Android Native App (penta-app)

| # | Page/View | Description | Status |
|---|---|---|---|
| 1 | **Login Page** | Email/password auth, register link to website | ✅ Built |
| 2 | **Agent Chat Page** | AI agent with goal input, chat history, model selector, API key | ✅ Built |
| 3 | **Remote Portal (AnyDesk)** | Live frame viewport, click/touch injection, device switcher | 🟡 Basic |
| 4 | **Settings** | Server URL, LLM provider, API key, vision quality | ✅ Built |
| 5 | **Plan/Service** | Pricing tiers, upgrade CTA | 🔴 Not in app |
| 6 | **Usage/History** | Session history, usage metrics | 🔴 Not in app |

### Website (Vercel Cloud)

| # | Page/View | Description | Status |
|---|---|---|---|
| 1 | **Landing Page** | Marketing pitch, feature showcase, download CTAs, pricing | ✅ Built |
| 2 | **Login / Register** | Auth modals with brute-force protection | ✅ Built |
| 3 | **Dashboard** | Authenticated user dashboard | ✅ Built |
| 4 | **Admin Panel** | User management, RBAC, coupons, MRR metrics | ✅ Built |
| 5 | **Download Center** | .exe + .apk download links | ✅ Built |

### Backend Infrastructure

| # | Component | Description | Status |
|---|---|---|---|
| 1 | **Database** | Postgres (Supabase/Neon) + Upstash Redis KV + local JSON fallback | ✅ Built |
| 2 | **WebRTC Signaling** | Device pairing & session exchange via DeviceHub | 🟡 Partial |
| 3 | **Local LLM** | Ollama provider integration | ✅ Built |
| 4 | **Auth Server** | PBKDF2, sessions, lockout, RBAC | ✅ Built |
| 5 | **Stripe Billing** | Checkout, webhooks, subscription management | ✅ Built |

---

## 🔍 Gap Analysis: What Exists vs. What's Needed

### ✅ KEEP (Production-Ready)

| Component | Why Keep |
|---|---|
| `models/*` (entire gateway) | 8 providers with fallback chain — fully tested |
| `api/user_store.py` | Enterprise-grade PBKDF2 auth with brute-force defense |
| `api/billing.py` + `api/coupons.py` | Stripe integration + promo engine |
| `api/admin_dashboard.py` | Admin governance panel |
| `api/index.py` | Vercel serverless router (25+ endpoints verified) |
| `api/web_template.py` | Full landing + auth UI (1174 lines) |
| `hub/device_hub.py` | Device mesh with KV persistence |
| `agent/core.py` | Android agent loop (perception→action) |
| `agent/pc_agent.py` | Windows PC agent loop |
| `pc_control/desktop_controller.py` | Native Win32 GDI capture + input injection |
| `adb/client.py` | ADB wrapper with security sanitization |
| `organization/*` | Multi-agent bus + orchestrators |
| `penta/penta_daemon.py` | Local device daemon |
| `tests/*` (all 50) | Full test suite — all passing |
| `penta-app/` (Tauri shell) | React + Vite + Tauri v2 native client |
| `.github/workflows/*` | CI/CD pipelines |
| `tools/*` | Utility scripts |

### 🟡 MODIFY / ENHANCE

| Component | What Needs Work |
|---|---|
| `penta-app/src/App.jsx` | Remote portal needs real-time WebRTC instead of frame polling; add plan/usage/history pages |
| `api/web_template.py` | Landing page needs richer marketing pitch with step-by-step onboarding |
| `hub/device_hub.py` | Needs WebRTC signaling server for true P2P streaming |
| `penta/penta_daemon.py` | Add audio/video stream channels |
| `android/companion_relay.py` | Stub only — needs real companion app communication |

### 🔴 ADD (Missing Features)

| Feature | What to Build |
|---|---|
| **F3: Communication** | Audio/video calls, chat between agents/users, admin remote control levels |
| **WebRTC Signaling Server** | STUN/TURN relay for true P2P connections |
| **Guest Role** | Public routes for unauthenticated visitors |
| **Plan/Service Page** | In-app subscription management |
| **Usage/History Page** | Session logs, AI step usage tracking |
| **Vision Module** | `vision/` is empty — needs screen analysis pipeline |
| **Android Companion App** | Native Android app with accessibility service for remote control |

### 🗑️ REMOVE / CLEAN UP

| Item | Reason |
|---|---|
| `scratch_screen.png` | Temporary debug artifact |
| `recordings/` (empty) | Unused empty directory |
| `logs/` (empty) | Unused empty directory |
| `__pycache__/` dirs | Build artifacts (already gitignored) |

---

## 🔄 Agile Development Roadmap

### Sprint Sequence: Web → Windows → Android

---

### 🌐 Phase 1: WEB (Vercel Fullstack)

#### Sprint 1.1: Landing Page Enhancement
- [ ] Redesign landing page with exceptional marketing pitch
- [ ] Add step-by-step onboarding flow to hook users
- [ ] Add animated feature showcase (AnyDesk + AI Agent demo)
- [ ] Add tech walkthrough section (how the system works)
- [ ] Polish mobile responsiveness

#### Sprint 1.2: Auth & Backend Hardening
- [ ] Review and harden guest/user/admin route guards
- [ ] Add public routes for guests (unauthenticated visitors)
- [ ] Verify Stripe webhook flow end-to-end
- [ ] Add usage tracking / quota enforcement per plan

#### Sprint 1.3: Admin Panel Enhancement
- [ ] Add system overview dashboard (live device count, active sessions, MRR)
- [ ] Add user session management (force logout, ban)
- [ ] Add audit log viewer

#### Sprint 1.4: WebRTC Signaling Server
- [ ] Implement WebRTC signaling endpoint for device pairing
- [ ] Add ICE candidate exchange
- [ ] Add session lifecycle (offer → answer → connected → disconnected)
- [ ] Test cross-device P2P connectivity

---

### 🪟 Phase 2: WINDOWS APP (Tauri v2)

#### Sprint 2.1: Core App Enhancement
- [x] Login page — connect to production auth API
- [x] Register link — opens website registration page
- [x] Model selector with API key configuration UI

#### Sprint 2.2: AI Agent Page
- [x] Full chat interface with streaming responses
- [x] Configurable access levels (what the agent can control)
- [x] Action history & undo capability
- [x] Vision preview (screenshot + overlay)

#### Sprint 2.3: Remote Portal (AnyDesk System)
- [x] Replace frame polling with WebRTC DataChannel streaming
- [x] Real-time mouse/keyboard event forwarding
- [x] Display latency indicator
- [x] Connection status & quality metrics

#### Sprint 2.4: Communication Features (F3)
- [x] Audio channel between devices
- [x] Video stream capability
- [x] Remote control permission levels (view-only, input, full admin)
- [x] Text chat between connected devices

#### Sprint 2.5: Additional Pages
- [x] Plan/Service page — show current plan, upgrade options
- [x] Usage/History page — session logs, AI step count
- [x] Settings page — full configuration panel

---

### 📱 Phase 3: ANDROID APP (Tauri v2)

#### Sprint 3.1: Core App Port
- [ ] Login page adapted for mobile UX
- [ ] Agent chat page with touch-optimized input
- [ ] Settings page

#### Sprint 3.2: Remote Portal Mobile
- [ ] Touch-to-click coordinate mapping
- [ ] Pinch-to-zoom on remote screen
- [ ] Gesture-to-swipe forwarding

#### Sprint 3.3: Communication Features
- [ ] Mirror F3 features from Windows app
- [ ] Push notification integration
- [ ] Background service for always-on connection

#### Sprint 3.4: Android-Specific
- [ ] Accessibility Service for local screen control
- [ ] Battery optimization exemption setup
- [ ] Companion app for device-to-device relay

---

## 🏛️ Agent Management Structure (3-Level Hierarchy)

```
┌─────────────────────────────────────────────────┐
│              LEVEL 1: SUPERVISOR                │
│        (This conversation / Main Agent)         │
│                                                 │
│  Responsibilities:                              │
│  • Overall task planning & prioritization        │
│  • Global task list maintenance                  │
│  • Quality gate enforcement                      │
│  • Cross-sprint dependency management            │
│  • Final verification & sign-off                 │
│                                                 │
│  Rules:                                         │
│  ✗ DO NOT hallucinate file contents              │
│  ✗ DO NOT rewrite working code unnecessarily     │
│  ✓ ALWAYS inspect before editing                 │
│  ✓ ALWAYS run tests after changes                │
│  ✓ ALWAYS update this doc with results           │
└───────────┬─────────────────────┬───────────────┘
            │                     │
            ▼                     ▼
┌─────────────────────┐ ┌─────────────────────────┐
│  LEVEL 2: LEADS     │ │  LEVEL 2: LEADS         │
│  (Feature Leads)    │ │  (Platform Leads)        │
│                     │ │                          │
│  • Web Lead         │ │  • Windows Lead          │
│  • Backend Lead     │ │  • Android Lead          │
│  • UI/UX Lead       │ │  • DevOps Lead           │
│                     │ │                          │
│  Responsibilities:  │ │  Responsibilities:       │
│  • Sprint planning  │ │  • Platform-specific     │
│  • Code review      │ │    implementation        │
│  • Integration test │ │  • Build & deploy        │
└───────┬─────────────┘ └──────┬──────────────────┘
        │                      │
        ▼                      ▼
┌─────────────────────────────────────────────────┐
│              LEVEL 3: WORKERS                   │
│            (Subagent Executors)                  │
│                                                 │
│  Responsibilities:                              │
│  • Single file / single component changes        │
│  • Unit test writing                             │
│  • CSS/UI polish                                 │
│  • Bug fixing                                    │
│                                                 │
│  ⚠️  CRITICAL RULES FOR ALL WORKERS:            │
│  ✗ DO NOT hallucinate — inspect files first      │
│  ✗ DO NOT modify files outside assigned scope    │
│  ✗ DO NOT skip running tests                     │
│  ✗ DO NOT make assumptions about existing code   │
│  ✓ ALWAYS verify changes compile/run             │
│  ✓ ALWAYS report results back to Lead            │
└─────────────────────────────────────────────────┘
```

---

## 📋 Task Tracking Policy

### Per-Task Workflow
```
1. OBJECTIVE/TASK → Define clear scope & acceptance criteria
2. CODEBASE OBSERVE → Read relevant files, understand current state
3. PLAN → Write required changes in this MD file
4. IMPLEMENT → Make targeted code changes
5. RUN → Execute the code / start the server
6. TEST → Run relevant tests (pytest, manual verification)
7. UPDATE → Append results to this MD file
8. REPEAT → Loop steps 4-7 until acceptance criteria met
```

### Task List Locations
- **Global Tasks**: This document (`pentactopus_doctree.md`)
- **Local Tasks**: Per-sprint task files as needed
- **Priority**: P0 (blocking) → P1 (critical) → P2 (important) → P3 (nice-to-have)

---

## 🔐 Environment & Secrets

| Variable | Purpose | Required |
|---|---|---|
| `DATABASE_URL` | Postgres connection string | For production |
| `STRIPE_SECRET_KEY` | Stripe payments | For billing |
| `STRIPE_PUBLISHABLE_KEY` | Stripe frontend | For billing |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhooks | For billing |
| `GEMINI_API_KEY` | Google Gemini AI | For AI agent |
| `OPENAI_API_KEY` | OpenAI GPT-4o | Optional AI |
| `ANTHROPIC_API_KEY` | Claude 3.5 | Optional AI |
| `DEEPSEEK_API_KEY` | DeepSeek | Optional AI |
| `GROQ_API_KEY` | Groq Llama 3 | Optional AI |
| `OPENROUTER_API_KEY` | OpenRouter | Optional AI |
| `UPSTASH_REDIS_REST_URL` | Upstash KV store | For cloud state |
| `UPSTASH_REDIS_REST_TOKEN` | Upstash auth | For cloud state |
| `RELEASE_DOWNLOAD_EXE_URL` | Windows installer CDN | For downloads |
| `RELEASE_DOWNLOAD_APK_URL` | Android APK CDN | For downloads |

---

## 🎯 Deliverables Checklist

| # | Deliverable | Format | Deploy Target |
|---|---|---|---|
| 1 | **Windows Desktop App** | `PentaAssistant-Setup.exe` (NSIS/MSI) | GitHub Releases |
| 2 | **Android App** | `PentaAssistant.apk` | GitHub Releases |
| 3 | **Fullstack Landing Page** | Python serverless + HTML/CSS/JS | Vercel |
| 4 | **Web Backend Server** | API routes + DB + auth + billing | Vercel |
| 5 | **Admin Panel** | Protected admin dashboard | Vercel (`/admin`) |

---

## 📊 Current Health Metrics

| Metric | Value |
|---|---|
| **Test Suite** | 50/50 passing ✅ |
| **Production Endpoints** | 25/25 verified ✅ |
| **Model Providers** | 8 configured ✅ |
| **Python Files** | ~45 source files |
| **Total LOC (est.)** | ~8,000+ lines |
| **Installer Size** | 20.5 MB (Windows) |
| **App RAM Usage** | ~35 MB |

---

> [!IMPORTANT]
> **This document is the single source of truth.** Every agent working on this project MUST read this file before making any changes. Update the status columns and append results after every sprint.

> [!CAUTION]
> **Anti-Hallucination Rule**: If you haven't read a file, DO NOT assume its contents. Use `view_file` first. If you aren't sure about something, ASK — don't guess.
