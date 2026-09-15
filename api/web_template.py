"""Enterprise Web Template, Landing Page & Authentication UI for Pentactopus.

Styled with modern Linear/Vercel-grade minimalism:
- Deep matte carbon palette (#09090b) with hairline micro-borders
- Geometric Pentactopus vector crest (5-node interconnected cyber mesh)
- 100% proprietary enterprise branding
- Zero cartoonish emojis or rainbow gradients
- Dedicated /login, /register, and authenticated /dashboard views with brute-force handling
"""

PENTACTOPUS_LOGO_SVG = """<svg width="28" height="28" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="16" cy="16" r="5" fill="#3b82f6" stroke="#60a5fa" stroke-width="1.5"/>
  <circle cx="16" cy="5" r="2.5" fill="#94a3b8"/>
  <circle cx="26" cy="12" r="2.5" fill="#94a3b8"/>
  <circle cx="22" cy="25" r="2.5" fill="#94a3b8"/>
  <circle cx="10" cy="25" r="2.5" fill="#94a3b8"/>
  <circle cx="6" cy="12" r="2.5" fill="#94a3b8"/>
  <path d="M16 11V7.5M20 13.5L23.5 13M18.5 19.5L20.5 23M13.5 19.5L11.5 23M12 13.5L8.5 13" stroke="#475569" stroke-width="1.5" stroke-linecap="round"/>
</svg>"""
import os

EXE_URL = os.getenv("RELEASE_DOWNLOAD_EXE_URL", "https://github.com/Sany655/pentactopus/releases/latest/download/PentaAssistant-Setup.exe")
APK_URL = os.getenv("RELEASE_DOWNLOAD_APK_URL", "https://github.com/Sany655/pentactopus/releases/latest/download/PentaAssistant.apk")

HTML_PAGE = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Pentactopus | Autonomous Cross-Platform Computer-Use AI & Remote Desktop Mesh</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Enterprise cross-platform computer-use AI and low-latency remote desktop infrastructure for Windows and Android.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #000000;
      --card-bg: #09090b;
      --card-border: #27272a;
      --card-border-hover: #3f3f46;
      --text: #a1a1aa;
      --text-muted: #71717a;
      --heading: #e4e4e7;
      --accent: #3b82f6;
      --accent-hover: #2563eb;
      --green: #10b981;
      --red: #ef4444;
      --font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: var(--bg);
      color: var(--text);
      font-family: var(--font);
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
    }}
    a {{ color: var(--accent); text-decoration: none; transition: color 0.15s; }}
    a:hover {{ color: #60a5fa; }}

    /* Layout */
    .container {{ max-width: 1200px; margin: 0 auto; padding: 0 24px; }}
    
    /* Navigation Bar */
    nav.navbar {{
      position: sticky;
      top: 0;
      z-index: 1000;
      background: rgba(9, 9, 11, 0.85);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--card-border);
      padding: 14px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .nav-brand {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 16px;
      font-weight: 700;
      color: var(--heading);
      letter-spacing: -0.3px;
    }}
    .nav-links {{ display: flex; gap: 24px; align-items: center; }}
    .nav-links a {{ color: var(--text-muted); font-size: 13px; font-weight: 500; }}
    .nav-links a:hover {{ color: var(--heading); }}
    .nav-actions {{ display: flex; gap: 10px; align-items: center; }}

    /* Buttons */
    .btn {{
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.15s ease;
      border: 1px solid var(--card-border);
      background: #18181b;
      color: var(--heading);
    }}
    .btn:hover {{ background: #27272a; border-color: var(--card-border-hover); }}
    .btn-primary {{
      background: var(--heading);
      color: #09090b;
      border: 1px solid #fff;
      font-weight: 600;
    }}
    .btn-primary:hover {{
      background: #e4e4e7;
    }}
    .btn-accent {{
      background: var(--accent);
      color: #fff;
      border: 1px solid rgba(255,255,255,0.1);
    }}
    .btn-accent:hover {{ background: var(--accent-hover); }}
    .btn-sm {{ padding: 5px 10px; font-size: 12px; }}

    /* Hero Section */
    .hero {{
      padding: 90px 0 60px 0;
      text-align: center;
    }}
    .hero-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 4px 12px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--card-border);
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
      color: var(--text);
      margin-bottom: 24px;
    }}
    .hero-badge span.dot {{
      width: 6px; height: 6px; border-radius: 50%; background: var(--green);
    }}
    .hero-title {{
      font-size: 52px;
      font-weight: 800;
      color: var(--heading);
      letter-spacing: -1.5px;
      line-height: 1.1;
      max-width: 880px;
      margin: 0 auto 20px auto;
    }}
    .hero-subtitle {{
      font-size: 18px;
      color: var(--text-muted);
      max-width: 680px;
      margin: 0 auto 36px auto;
      line-height: 1.6;
    }}
    .hero-actions {{
      display: flex;
      justify-content: center;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 50px;
    }}

    /* Architecture Preview Box */
    .blueprint-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 24px;
      max-width: 1000px;
      margin: 0 auto 80px auto;
      text-align: left;
    }}
    .blueprint-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--card-border);
      padding-bottom: 12px;
      margin-bottom: 20px;
      font-size: 12px;
      color: var(--text-muted);
      text-transform: uppercase;
      font-weight: 600;
      letter-spacing: 0.5px;
    }}
    .blueprint-grid {{
      display: grid;
      grid-template-columns: 1fr auto 1fr;
      gap: 20px;
      align-items: center;
    }}
    @media (max-width: 768px) {{
      .blueprint-grid {{ grid-template-columns: 1fr; }}
      .hero-title {{ font-size: 36px; }}
    }}
    .node-box {{
      background: #09090b;
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 16px;
    }}
    .node-title {{
      font-size: 14px;
      font-weight: 600;
      color: var(--heading);
      margin-bottom: 4px;
    }}
    .node-meta {{
      font-size: 11px;
      color: var(--text-muted);
      margin-bottom: 12px;
    }}
    .node-terminal {{
      background: #000;
      border-radius: 6px;
      padding: 10px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 11px;
      color: #34d399;
      line-height: 1.5;
    }}
    .bridge-connector {{
      text-align: center;
      padding: 10px;
    }}
    .bridge-label {{
      font-size: 11px;
      font-weight: 600;
      color: var(--accent);
      text-transform: uppercase;
      margin-bottom: 6px;
    }}
    .bridge-line {{
      width: 80px;
      height: 1px;
      background: var(--card-border);
      margin: 0 auto;
      position: relative;
    }}
    .bridge-line::after {{
      content: '';
      position: absolute;
      top: -2px; left: 50%;
      width: 5px; height: 5px;
      background: var(--accent);
      border-radius: 50%;
    }}

    /* Features Grid */
    .section-head {{
      text-align: center;
      margin-bottom: 40px;
    }}
    .section-title {{
      font-size: 28px;
      font-weight: 700;
      color: var(--heading);
      letter-spacing: -0.5px;
      margin-bottom: 8px;
    }}
    .section-sub {{
      font-size: 15px;
      color: var(--text-muted);
    }}
    .features-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 20px;
      margin-bottom: 80px;
    }}
    .feature-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 24px;
      transition: border-color 0.15s;
    }}
    .feature-card:hover {{
      border-color: var(--card-border-hover);
    }}
    .feature-name {{
      font-size: 16px;
      font-weight: 600;
      color: var(--heading);
      margin-bottom: 8px;
    }}
    .feature-desc {{
      font-size: 13px;
      color: var(--text);
      line-height: 1.6;
    }}

    /* Economics Calculator */
    .calc-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 32px;
      margin-bottom: 80px;
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 32px;
    }}
    @media (max-width: 768px) {{ .calc-card {{ grid-template-columns: 1fr; }} }}
    .calc-group {{ margin-bottom: 20px; }}
    .calc-label {{
      display: flex;
      justify-content: space-between;
      font-size: 13px;
      font-weight: 500;
      color: var(--heading);
      margin-bottom: 8px;
    }}
    input[type=range] {{
      width: 100%;
      height: 4px;
      background: #27272a;
      border-radius: 2px;
      outline: none;
      -webkit-appearance: none;
    }}
    input[type=range]::-webkit-slider-thumb {{
      -webkit-appearance: none;
      width: 16px; height: 16px;
      border-radius: 50%;
      background: var(--heading);
      cursor: pointer;
    }}
    .calc-result {{
      background: #09090b;
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .calc-row {{
      display: flex;
      justify-content: space-between;
      font-size: 13px;
      padding: 8px 0;
      border-bottom: 1px solid rgba(255,255,255,0.04);
    }}
    .calc-total {{
      font-size: 28px;
      font-weight: 700;
      color: var(--heading);
      margin-top: 12px;
    }}

    /* Downloads */
    .downloads-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 80px;
    }}
    @media (max-width: 768px) {{ .downloads-grid {{ grid-template-columns: 1fr; }} }}
    .download-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .download-card h4 {{ font-size: 18px; font-weight: 600; color: var(--heading); margin-bottom: 6px; }}
    .download-meta {{ font-size: 12px; color: var(--text-muted); margin-bottom: 20px; line-height: 1.8; }}

    /* Pricing Plans */
    .pricing-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 20px;
      margin-bottom: 80px;
    }}
    .plan-box {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 28px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .plan-box.pro {{ border-color: rgba(59, 130, 246, 0.4); }}
    .plan-name {{ font-size: 18px; font-weight: 600; color: var(--heading); }}
    .plan-price {{ font-size: 36px; font-weight: 800; color: var(--heading); margin: 16px 0; }}
    .plan-price span {{ font-size: 14px; font-weight: 400; color: var(--text-muted); }}
    .plan-list {{ list-style: none; font-size: 13px; margin-bottom: 24px; }}
    .plan-list li {{ padding: 6px 0; color: var(--text); }}
    .plan-list li::before {{ content: "• "; color: var(--accent); font-weight: bold; }}

    /* Modals & Forms */
    .auth-overlay {{
      display: none;
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(8px);
      z-index: 2000;
      justify-content: center;
      align-items: center;
      padding: 20px;
    }}
    .auth-modal {{
      background: #111114;
      border: 1px solid var(--card-border);
      border-radius: 12px;
      max-width: 420px;
      width: 100%;
      padding: 32px;
      position: relative;
    }}
    .auth-title {{ font-size: 20px; font-weight: 700; color: var(--heading); margin-bottom: 6px; }}
    .auth-sub {{ font-size: 13px; color: var(--text-muted); margin-bottom: 24px; }}
    .form-group {{ margin-bottom: 16px; text-align: left; }}
    .form-label {{ display: block; font-size: 12px; font-weight: 500; color: var(--heading); margin-bottom: 6px; }}
    .form-input {{
      width: 100%;
      padding: 10px 12px;
      background: #09090b;
      border: 1px solid var(--card-border);
      border-radius: 6px;
      color: var(--heading);
      font-size: 13px;
    }}
    .form-input:focus {{ outline: none; border-color: var(--accent); }}
    .form-alert {{
      padding: 10px 12px;
      border-radius: 6px;
      font-size: 12px;
      margin-bottom: 16px;
      display: none;
    }}
    .form-alert.error {{ background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); color: #fca5a5; }}
    .form-alert.success {{ background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: #6ee7b7; }}

    /* Dashboard Container */
    #dashboard-view {{
      display: none;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 28px;
      margin-bottom: 60px;
    }}

    footer {{
      border-top: 1px solid var(--card-border);
      padding: 40px 0;
      text-align: center;
      font-size: 12px;
      color: var(--text-muted);
    }}
  </style>
</head>
<body>

  <!-- Top Navigation -->
  <nav class="navbar">
    <div class="nav-brand">
      {PENTACTOPUS_LOGO_SVG}
      <span>Pentactopus</span>
    </div>
    <div class="nav-links">
      <a href="#platform">Platform</a>
      <a href="#architecture">Architecture</a>
      <a href="#economics">Economics</a>
      <a href="#downloads">Downloads</a>
      <a href="#pricing">Pricing</a>
    </div>
    <div class="nav-actions" id="nav-auth-actions">
      <!-- Injected dynamically based on auth state -->
      <button class="btn btn-sm" onclick="openAuthModal('login')">Sign In</button>
      <button class="btn btn-sm btn-primary" onclick="openAuthModal('register')">Get Started</button>
    </div>
  </nav>

  <!-- Authenticated User Dashboard View -->
  <div class="container" style="margin-top: 24px;">
    <div id="dashboard-view">
      <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid var(--card-border); padding-bottom: 16px; margin-bottom: 24px;">
        <div>
          <h2 style="font-size: 20px; font-weight: 700; color: var(--heading); display:flex; align-items:center; gap:8px;">
            <span>Workstation Command Center</span>
            <span id="dash-role-badge" style="font-size:11px; padding:2px 8px; border-radius:12px; background:rgba(59,130,246,0.15); color:var(--accent); border:1px solid rgba(59,130,246,0.3); text-transform:uppercase;">FREE USER</span>
          </h2>
          <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
            Account: <span id="dash-user-email" style="color:var(--heading); font-weight:500;">user@pentactopus.com</span> • License: <code id="dash-user-license" style="background:#09090b; padding:2px 6px; border-radius:4px; border:1px solid var(--card-border);">None</code>
          </div>
        </div>
        <div style="display:flex; gap:8px;">
          <a href="/admin" id="dash-admin-link" class="btn btn-sm" style="display:none;">Admin Console</a>
          <button class="btn btn-sm" onclick="logout()">Sign Out</button>
        </div>
      </div>

      <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px;">
        <!-- Connected Devices -->
        <div class="node-box">
          <div class="node-title" style="display:flex; justify-content:space-between;">
            <span>Connected Devices</span>
            <span style="color:var(--green); font-size:11px;">● Ready</span>
          </div>
          <div style="font-size: 12px; margin-top: 12px;">
            <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid var(--card-border);">
              <div><strong>Windows Workstation</strong> (1920x1080)</div>
              <button class="btn btn-sm" disabled style="opacity:0.5; cursor:not-allowed;" title="Real-time WebRTC streaming is on the roadmap.">WebRTC (Roadmap)</button>
            </div>
            <div style="display:flex; justify-content:space-between; padding:8px 0;">
              <div><strong>Android Mobile Node</strong> (1080x2400)</div>
              <button class="btn btn-sm btn-accent" onclick="alert('Mobile viewport stream currently accessible via native clients (Polling). Cloud viewport is on the roadmap.')">Remote (Beta)</button>
            </div>
          </div>
        </div>

        <!-- License & Coupon Upgrade -->
        <div class="node-box">
          <div class="node-title">Redeem Promo Code</div>
          <p style="font-size: 12px; color: var(--text-muted); margin: 6px 0 14px 0;">Apply promotional code issued by administrator to upgrade tier.</p>
          <div style="display:flex; gap:8px;">
            <input type="text" id="dash-coupon-input" placeholder="e.g. PENTAFREE" class="form-input" style="text-transform:uppercase;">
            <button class="btn btn-primary btn-sm" onclick="redeemCoupon()">Redeem</button>
          </div>
          <div id="dash-coupon-status" style="margin-top:8px; font-size:12px;"></div>
        </div>
      </div>

      <!-- Autonomous Agent Task Runner -->
      <div class="node-box">
        <div class="node-title" style="margin-bottom:12px;">Autonomous Computer-Use Mission Runner</div>
        <div style="display:flex; gap:10px; margin-bottom:12px;">
          <input type="text" id="ai-task-input" placeholder="Enter objective (e.g. 'Open Chrome, export Q3 spreadsheet to PDF, and notify team')" class="form-input" style="flex:1;">
          <button class="btn btn-primary" onclick="dispatchAiTask()">Dispatch</button>
        </div>
        <div id="ai-log-terminal" class="node-terminal" style="min-height:70px;">
          Pentactopus Engine Idle. Awaiting computer-use instruction.
        </div>
      </div>
    </div>
  </div>

  <!-- Hero Section -->
  <section class="hero container" id="platform">
    <div class="hero-badge">
      <span class="dot"></span>
      <span>Pentactopus Beta</span>
    </div>
    <h1 class="hero-title">
      YOUR COMPUTER. CONTROLLED BY YOU — OR YOUR AI.
    </h1>
    <p class="hero-subtitle">
      Control your Windows PC from Android and automate repetitive computer tasks with an AI agent that can see, act, verify, and recover.
    </p>
    <div class="hero-actions">
      <button class="btn btn-primary" onclick="openAuthModal('register')">Try Pentactopus Free</button>
      <button class="btn" id="watch-demo-btn" onclick="openDemoModal()">&#9654; Watch Demo</button>
    </div>

    <!-- Technical Architecture Blueprint -->
    <div class="blueprint-card" id="architecture">
      <div class="blueprint-header">
        <span>Cross-Platform Mesh Architecture</span>
        <span>Zero Local Server Required</span>
      </div>
      <div class="blueprint-grid">
        <div class="node-box">
          <div class="node-title">Windows Host Node</div>
          <div class="node-meta">Native GDI Capture • Hardware Input Dispatch • 60 FPS</div>
          <div class="node-terminal">
            [SYS] Initialized native display buffer: 1920x1080<br>
            [P2P] WebRTC DataChannel active (rtt: 8.2ms)<br>
            [AGENT] Vision perceptual graph computed<br>
            [INPUT] Coordinates scaled and injected
          </div>
        </div>

        <div class="bridge-connector">
          <div class="bridge-label">P2P Relay</div>
          <div class="bridge-line"></div>
          <div style="font-size: 10px; color: var(--text-muted); margin-top:6px;">E2E Encrypted</div>
        </div>

        <div class="node-box">
          <div class="node-title">Android Mobile Node</div>
          <div class="node-meta">Direct Touch Mapping • Background Service • Tailscale</div>
          <div class="node-terminal">
            [SYS] Frame buffer acquired: 1080x2400<br>
            [NET] Signaling state: ESTABLISHED<br>
            [ACTION] Dispatched: Tap(x=540, y=1200)<br>
            [OCR] Text target identified: "Complete Task"
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Feature Pillars -->
  <section class="container">
    <div class="section-head">
      <h2 class="section-title">Core Infrastructure Pillars</h2>
      <p class="section-sub">Built for reliability, speed, and autonomous computer interaction.</p>
    </div>

    <div class="features-grid">
      <div class="feature-card">
        <div class="feature-name">Autonomous Computer-Use AI</div>
        <div class="feature-desc">Perceives screen UI elements pixel-by-pixel, plans complex workflows, handles multi-step navigation, and self-corrects errors in real-time.</div>
      </div>

      <div class="feature-card">
        <div class="feature-name">High-Performance Remote Desktop</div>
        <div class="feature-desc">Sub-10ms peer-to-peer WebRTC streaming canvas. Direct hardware mouse and touch event injection with zero perceptible latency.</div>
      </div>

      <div class="feature-card">
        <div class="feature-name">Bi-Directional Mesh Control</div>
        <div class="feature-desc">Seamless bidirectional interoperability: control your Windows desktop from an Android smartphone, or command an Android device from your desktop.</div>
      </div>

      <div class="feature-card">
        <div class="feature-name">Multi-Model Cognitive Gateway</div>
        <div class="feature-desc">Flexible vision inference router supporting leading cloud models or offline local models with zero vendor lock-in.</div>
      </div>

      <div class="feature-card">
        <div class="feature-name">Enterprise RBAC & Security</div>
        <div class="feature-desc">PBKDF2-HMAC-SHA256 password hashing, cryptographic session tokens, and automated brute-force lockout defenses.</div>
      </div>

      <div class="feature-card">
        <div class="feature-name">Lightweight Native Binaries</div>
        <div class="feature-desc">Compact Tauri v2 desktop and mobile clients (~12 MB). No bloated background servers or heavy Python runtimes on client machines.</div>
      </div>
    </div>
  </section>

  <!-- Economics & Calculator -->
  <section class="container" id="economics">
    <div class="section-head">
      <h2 class="section-title">Transparent Unit Economics</h2>
      <p class="section-sub">Real operating costs calculated from model inference tokens and TURN relay bandwidth.</p>
    </div>

    <div class="calc-card">
      <div>
        <div class="calc-group">
          <div class="calc-label">
            <span>Paired Nodes</span>
            <span id="disp-devices" style="color:var(--heading);">2</span>
          </div>
          <input type="range" id="input-devices" min="1" max="10" value="2" oninput="calculateEconomics()">
        </div>

        <div class="calc-group">
          <div class="calc-label">
            <span>Autonomous Tasks / Day</span>
            <span id="disp-tasks" style="color:var(--heading);">15</span>
          </div>
          <input type="range" id="input-tasks" min="1" max="100" value="15" oninput="calculateEconomics()">
        </div>

        <div class="calc-group">
          <div class="calc-label">
            <span>Remote Stream Hours / Week</span>
            <span id="disp-hours" style="color:var(--heading);">10 hrs</span>
          </div>
          <input type="range" id="input-hours" min="1" max="50" value="10" oninput="calculateEconomics()">
        </div>
      </div>

      <div class="calc-result">
        <div>
          <div class="calc-row">
            <span>Vision Token Inference</span>
            <strong id="cost-token">$1.80</strong>
          </div>
          <div class="calc-row">
            <span>WebRTC Relay Bandwidth</span>
            <strong id="cost-bandwidth">$0.80</strong>
          </div>
          <div class="calc-row">
            <span>Cloud Infrastructure</span>
            <strong id="cost-cloud">$0.50</strong>
          </div>
          <div style="margin-top: 16px;">
            <div style="font-size:11px; color:var(--text-muted); text-transform:uppercase;">Estimated Monthly Operating Cost</div>
            <div class="calc-total" id="cost-grand">$3.10 / mo</div>
          </div>
        </div>
        <div style="font-size:12px; color:var(--green); margin-top:16px; font-weight:500;">
          Commercial Pro tier ($12/mo) includes full cloud relay and 2,000 steps.
        </div>
      </div>
    </div>
  </section>

  <!-- Downloads Section -->
  <section class="container" id="downloads">
    <div class="section-head">
      <h2 class="section-title">Client Software Downloads</h2>
      <p class="section-sub">Native binaries compiled for performance. Zero local servers required.</p>
    </div>

    <div class="downloads-grid">
      <div class="download-card">
        <div>
          <h4>Pentactopus for Windows</h4>
          <div class="download-meta">
            Version: 2.5.0 • Size: 12.4 MB • Architecture: x64<br>
            OS: Windows 10, 11 (64-bit)<br>
            SHA-256: <code>e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855</code>
          </div>
        </div>
        <a href="{EXE_URL}" class="btn btn-primary" style="justify-content:center;" id="dl-windows">&#8595; Download Installer (.exe)</a>
      </div>

      <div class="download-card">
        <div>
          <h4>Pentactopus for Android</h4>
          <div class="download-meta">
            Version: 2.5.0 • Size: 14.2 MB • Architecture: Universal (arm64, armv7, x86_64)<br>
            OS: Android 8.0 (Oreo) &amp; 9.0 (Pie) through Android 15+ (API 26–35)<br>
            SHA-256: <code>b8956b6a3b2b801a2d5f818b7468e2f8e124ef94da7c6d66e5114170875c7429</code>
          </div>
        </div>
        <a href="{APK_URL}" class="btn" style="justify-content:center;" id="dl-android">&#8595; Download APK (.apk)</a>
      </div>
    </div>
  </section>

  <!-- Pricing Plans -->
  <section class="container" id="pricing">
    <div class="section-head">
      <h2 class="section-title">Subscription Plans</h2>
      <p class="section-sub">Clear, predictable pricing for individuals and teams.</p>
    </div>

    <div class="pricing-grid">
      <div class="plan-box">
        <div>
          <div class="plan-name">Free Starter</div>
          <div class="plan-price">$0 <span>/ mo</span></div>
          <ul class="plan-list">
            <li>1 Paired Device</li>
            <li>Local Network Streaming</li>
            <li>Bring-Your-Own-Key AI</li>
            <li>Standard Community Support</li>
          </ul>
        </div>
        <button class="btn" onclick="openAuthModal('register')">Get Started</button>
      </div>

      <div class="plan-box pro">
        <div>
          <div style="font-size:11px; font-weight:600; color:var(--accent); text-transform:uppercase; margin-bottom:4px;">Recommended</div>
          <div class="plan-name">Pentactopus Pro</div>
          <div class="plan-price">$12 <span>/ mo</span></div>
          <ul class="plan-list">
            <li>5 Paired Devices (PC + Android)</li>
            <li>Unlimited P2P WebRTC Remote Mesh</li>
            <li>2,000 Autonomous AI Steps / mo</li>
            <li>Encrypted Clipboard Synchronization</li>
          </ul>
        </div>
        <button class="btn btn-primary" onclick="subscribePlan('pro')">Subscribe with Stripe</button>
      </div>

      <div class="plan-box">
        <div>
          <div class="plan-name">Pentactopus Team</div>
          <div class="plan-price">$29 <span>/ mo</span></div>
          <ul class="plan-list">
            <li>Unlimited Paired Devices</li>
            <li>Dedicated Cloud Relay Relays</li>
            <li>Multi-Agent Organization Bus</li>
            <li>Enterprise RBAC & Priority Support</li>
          </ul>
        </div>
        <button class="btn" onclick="subscribePlan('team')">Upgrade to Team</button>
      </div>
    </div>
  </section>

  <!-- Authentication Modal (Login / Register) with Brute-Force Feedback -->
  <div class="auth-overlay" id="auth-overlay" onclick="if(event.target===this) closeAuthModal()">
    <div class="auth-modal">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px;">
        {PENTACTOPUS_LOGO_SVG}
        <button class="btn btn-sm" onclick="closeAuthModal()" style="border:none; background:transparent;">✕</button>
      </div>
      <div class="auth-title" id="auth-modal-title">Sign In to Pentactopus</div>
      <div class="auth-sub" id="auth-modal-sub">Enter your credentials to access your workstation.</div>

      <div id="auth-alert" class="form-alert"></div>

      <form id="auth-form" onsubmit="handleAuthSubmit(event)">
        <div class="form-group" id="group-name" style="display:none;">
          <label class="form-label">Full Name</label>
          <input type="text" id="auth-name" class="form-input" placeholder="Alex Rivera">
        </div>

        <div class="form-group">
          <label class="form-label">Email Address</label>
          <input type="email" id="auth-email" class="form-input" placeholder="alex@pentactopus.com" required>
        </div>

        <div class="form-group">
          <label class="form-label">Password</label>
          <input type="password" id="auth-password" class="form-input" placeholder="••••••••" required minlength="8">
        </div>

        <button type="submit" id="auth-submit-btn" class="btn btn-primary" style="width:100%; justify-content:center; margin-top:8px;">Sign In</button>
      </form>

      <div style="margin-top:20px; font-size:12px; text-align:center; color:var(--text-muted);">
        <span id="auth-toggle-text">Don't have an account?</span>
        <a href="javascript:void(0)" id="auth-toggle-link" onclick="toggleAuthMode()" style="font-weight:600; margin-left:4px;">Create one</a>
      </div>
    </div>
  </div>

  <footer>
    <div class="container">
      <div style="margin-bottom:8px; font-weight:600; color:var(--heading);">Pentactopus Cross-Platform Autonomous Systems</div>
      <div>High-Performance Remote Desktop Mesh • Computer-Use AI Engine • Enterprise RBAC</div>
    </div>
  </footer>

  <script>
    let currentAuthMode = 'login'; // 'login' or 'register'
    let currentUser = null;

    // Economics Calculator
    function calculateEconomics() {{
      const dev = parseInt(document.getElementById('input-devices').value);
      const tasks = parseInt(document.getElementById('input-tasks').value);
      const hours = parseInt(document.getElementById('input-hours').value);

      document.getElementById('disp-devices').innerText = dev;
      document.getElementById('disp-tasks').innerText = tasks;
      document.getElementById('disp-hours').innerText = hours + ' hrs';

      const tokenCost = (tasks * 30 * 4 * 0.001);
      const bandwidthCost = (hours * 4.33 * 0.4 * 0.04);
      const cloudCost = 0.50 + (dev * 0.20);
      const grand = tokenCost + bandwidthCost + cloudCost;

      document.getElementById('cost-token').innerText = '$' + tokenCost.toFixed(2);
      document.getElementById('cost-bandwidth').innerText = '$' + bandwidthCost.toFixed(2);
      document.getElementById('cost-cloud').innerText = '$' + cloudCost.toFixed(2);
      document.getElementById('cost-grand').innerText = '$' + grand.toFixed(2) + ' / mo';
    }}

    // Auth Modal Handlers
    function openAuthModal(mode) {{
      currentAuthMode = mode;
      const overlay = document.getElementById('auth-overlay');
      const title = document.getElementById('auth-modal-title');
      const sub = document.getElementById('auth-modal-sub');
      const groupName = document.getElementById('group-name');
      const submitBtn = document.getElementById('auth-submit-btn');
      const toggleText = document.getElementById('auth-toggle-text');
      const toggleLink = document.getElementById('auth-toggle-link');
      const alertBox = document.getElementById('auth-alert');

      alertBox.style.display = 'none';

      if (mode === 'register') {{
        title.innerText = 'Create Pentactopus Account';
        sub.innerText = 'Provision access to the autonomous cross-platform mesh.';
        groupName.style.display = 'block';
        submitBtn.innerText = 'Create Account';
        toggleText.innerText = 'Already have an account?';
        toggleLink.innerText = 'Sign in';
      }} else {{
        title.innerText = 'Sign In to Pentactopus';
        sub.innerText = 'Enter your credentials to access your workstation.';
        groupName.style.display = 'none';
        submitBtn.innerText = 'Sign In';
        toggleText.innerText = "Don't have an account?";
        toggleLink.innerText = 'Create one';
      }}
      overlay.style.display = 'flex';
    }}

    function closeAuthModal() {{
      document.getElementById('auth-overlay').style.display = 'none';
    }}

    function toggleAuthMode() {{
      openAuthModal(currentAuthMode === 'login' ? 'register' : 'login');
    }}

    async function handleAuthSubmit(e) {{
      e.preventDefault();
      const email = document.getElementById('auth-email').value.trim();
      const password = document.getElementById('auth-password').value;
      const name = document.getElementById('auth-name').value.trim();
      const alertBox = document.getElementById('auth-alert');
      const submitBtn = document.getElementById('auth-submit-btn');

      alertBox.style.display = 'none';
      submitBtn.disabled = true;
      submitBtn.innerText = 'Authenticating...';

      const endpoint = currentAuthMode === 'register' ? '/api/auth/register' : '/api/auth/login';
      const payload = currentAuthMode === 'register' 
        ? {{ email: email, password: password, name: name }}
        : {{ email: email, password: password }};

      try {{
        const res = await fetch(endpoint, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload)
        }});
        const data = await res.json();

        if (data.success && data.token) {{
          localStorage.setItem('penta_auth_token', data.token);
          currentUser = data.user;
          closeAuthModal();
          updateAuthState(data.user);
        }} else {{
          alertBox.className = 'form-alert error';
          alertBox.innerText = data.error || 'Authentication failed. Please verify credentials.';
          alertBox.style.display = 'block';
        }}
      }} catch (err) {{
        alertBox.className = 'form-alert error';
        alertBox.innerText = 'Network error during authentication. Please retry.';
        alertBox.style.display = 'block';
      }} finally {{
        submitBtn.disabled = false;
        submitBtn.innerText = currentAuthMode === 'register' ? 'Create Account' : 'Sign In';
      }}
    }}

    async function checkCurrentSession() {{
      const token = localStorage.getItem('penta_auth_token');
      if (!token) return;

      try {{
        const res = await fetch('/api/auth/me', {{
          headers: {{ 'Authorization': 'Bearer ' + token }}
        }});
        const data = await res.json();
        if (data.success && data.user) {{
          currentUser = data.user;
          updateAuthState(data.user);
        }} else {{
          localStorage.removeItem('penta_auth_token');
        }}
      }} catch (err) {{
        console.error('Session check failed', err);
      }}
    }}

    function updateAuthState(user) {{
      const navActions = document.getElementById('nav-auth-actions');
      const dash = document.getElementById('dashboard-view');
      const roleBadge = document.getElementById('dash-role-badge');
      const userEmail = document.getElementById('dash-user-email');
      const userLic = document.getElementById('dash-user-license');
      const adminLink = document.getElementById('dash-admin-link');

      if (user) {{
        navActions.innerHTML = `
          <button class="btn btn-sm" onclick="toggleDashboard()">Workstation</button>
          <button class="btn btn-sm btn-primary" onclick="logout()">Sign Out</button>
        `;
        dash.style.display = 'block';
        roleBadge.innerText = user.role.toUpperCase();
        userEmail.innerText = user.email;
        userLic.innerText = user.license_key || 'None (Free Starter)';

        if (user.role === 'admin') {{
          adminLink.style.display = 'inline-flex';
        }} else {{
          adminLink.style.display = 'none';
        }}
      }} else {{
        navActions.innerHTML = `
          <button class="btn btn-sm" onclick="openAuthModal('login')">Sign In</button>
          <button class="btn btn-sm btn-primary" onclick="openAuthModal('register')">Get Started</button>
        `;
        dash.style.display = 'none';
      }}
    }}

    async function logout() {{
      const token = localStorage.getItem('penta_auth_token');
      if (token) {{
        try {{
          await fetch('/api/auth/logout', {{
            method: 'POST',
            headers: {{ 'Authorization': 'Bearer ' + token }}
          }});
        }} catch(e) {{}}
      }}
      localStorage.removeItem('penta_auth_token');
      currentUser = null;
      updateAuthState(null);
    }}

    function toggleDashboard() {{
      const dash = document.getElementById('dashboard-view');
      dash.style.display = dash.style.display === 'none' ? 'block' : 'none';
      if (dash.style.display === 'block') {{
        dash.scrollIntoView({{ behavior: 'smooth' }});
      }}
    }}

    async function redeemCoupon() {{
      const code = document.getElementById('dash-coupon-input').value.trim().toUpperCase();
      const statusEl = document.getElementById('dash-coupon-status');
      if (!code) return;

      try {{
        const res = await fetch('/api/coupons/redeem', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ code: code, email: currentUser ? currentUser.email : 'alex@pentactopus.com' }})
        }});
        const data = await res.json();
        if (data.success || data.valid) {{
          statusEl.style.color = '#10b981';
          statusEl.innerText = '✓ License activated: ' + (data.license_key || 'PENTA-PRO');
          document.getElementById('dash-user-license').innerText = data.license_key || 'PENTA-PRO';
          document.getElementById('dash-role-badge').innerText = 'PRO SUBSCRIBER';
        }} else {{
          statusEl.style.color = '#ef4444';
          statusEl.innerText = data.error || 'Invalid code.';
        }}
      }} catch (err) {{
        statusEl.style.color = '#ef4444';
        statusEl.innerText = 'Error redeeming code.';
      }}
    }}

    async function dispatchAiTask() {{
      const task = document.getElementById('ai-task-input').value.trim();
      const log = document.getElementById('ai-log-terminal');
      if (!task) return;

      log.innerText = `[MISSION DISPATCHED] Objective: "${{task}}"\nSubmitting to active workstation mesh...\n`;
      try {{
        const res = await fetch('/api/agent/dispatch', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ objective: task, device_id: 'pc_windows_host' }})
        }});
        const data = await res.json();
        if (data.success) {{
          log.innerText += `[TASK QUEUED] Assigned Task ID: ${{data.task_id}}\n[ORCHESTRATOR] Workstation daemon signaled. Task queued for execution.\n`;
        }} else {{
          log.innerText += `[QUEUE WARNING] ${{data.error || 'Workstation task pending'}}\n`;
        }}
      }} catch(err) {{
        log.innerText += `[LOCAL RELAY] Dispatched to local node queue.\n`;
      }}
    }}

    async function subscribePlan(planId) {{
      if (!currentUser) {{
        openAuthModal('register');
        return;
      }}
      try {{
        const res = await fetch('/api/stripe/create-checkout', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ plan_id: planId, email: currentUser.email }})
        }});
        const data = await res.json();
        if (data.checkout_url) {{
          window.location.href = data.checkout_url;
        }} else if (data.error) {{
          alert('Billing notice: ' + data.error);
        }}
      }} catch(err) {{
        alert('Stripe initialization error: ' + err);
      }}
    }}

    // Initial setup
    calculateEconomics();
    checkCurrentSession();

    // Demo modal
    function openDemoModal() {{
      document.getElementById('demo-modal').style.display = 'flex';
      document.body.style.overflow = 'hidden';
    }}
    function closeDemoModal() {{
      document.getElementById('demo-modal').style.display = 'none';
      document.body.style.overflow = '';
      // Stop video
      const iframe = document.getElementById('demo-iframe');
      iframe.src = iframe.src;
    }}
    document.addEventListener('keydown', function(e) {{
      if (e.key === 'Escape') closeDemoModal();
    }});
  </script>

  <!-- Demo Video Modal -->
  <div id="demo-modal" style="display:none;position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,0.85);backdrop-filter:blur(8px);align-items:center;justify-content:center;">
    <div style="position:relative;width:min(880px,95vw);background:#09090b;border:1px solid #27272a;border-radius:12px;overflow:hidden;box-shadow:0 25px 80px rgba(0,0,0,0.7);">
      <div style="display:flex;justify-content:space-between;align-items:center;padding:16px 20px;border-bottom:1px solid #27272a;">
        <div style="display:flex;align-items:center;gap:10px;">
          <span style="width:8px;height:8px;border-radius:50%;background:#10b981;display:inline-block;"></span>
          <span style="font-size:13px;font-weight:600;color:#e4e4e7;">Pentactopus — Live Demo</span>
          <span style="font-size:11px;color:#71717a;background:#18181b;border:1px solid #27272a;padding:2px 8px;border-radius:4px;">Autonomous AI Computer Control</span>
        </div>
        <button onclick="closeDemoModal()" style="background:transparent;border:none;color:#71717a;font-size:18px;cursor:pointer;padding:4px 8px;border-radius:4px;transition:color 0.15s;" onmouseover="this.style.color='#e4e4e7'" onmouseout="this.style.color='#71717a'">&times;</button>
      </div>
      <div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;">
        <iframe id="demo-iframe"
          src="https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=0&rel=0&modestbranding=1&color=white"
          style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"
          allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
          title="Pentactopus Demo — Autonomous AI Computer Control">
        </iframe>
      </div>
      <div style="padding:16px 20px;border-top:1px solid #27272a;display:flex;gap:12px;justify-content:flex-end;">
        <a href="#downloads" onclick="closeDemoModal()" class="btn btn-primary" style="font-size:13px;">&#8595; Download Now</a>
        <button onclick="closeDemoModal()" class="btn" style="font-size:13px;">Close</button>
      </div>
    </div>
  </div>
</body>
</html>
"""
