"""Web UI Dashboard, Landing Page & User Portal Template for Penta-Assistant.

Provides a world-class commercial SaaS presentation with high-impact hero cover,
animated SVG/CSS cross-platform device posters, interactive cost calculator,
app download center, and authenticated User Dashboard under Admin governance.
"""

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Penta-Assistant | Autonomous Cross-Platform AI Agent & AnyDesk Remote Control</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Autonomous cross-platform computer-use AI combining Google Antigravity agentic intelligence with AnyDesk 60 FPS remote desktop streaming across Windows and Android.">
  <style>
    :root {
      --bg: #070a12;
      --card-bg: rgba(18, 24, 38, 0.85);
      --card-hover: rgba(26, 35, 56, 0.95);
      --border: rgba(48, 54, 61, 0.7);
      --border-glow: rgba(88, 166, 255, 0.4);
      --text: #c9d1d9;
      --heading: #f0f6fc;
      --cyan: #00f2fe;
      --accent: #58a6ff;
      --purple: #bc8cff;
      --green: #3fb950;
      --gold: #f1e05a;
      --danger: #f85149;
      --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg);
      background-image: 
        radial-gradient(circle at 15% 15%, rgba(31, 111, 235, 0.12) 0%, transparent 40%),
        radial-gradient(circle at 85% 25%, rgba(188, 140, 255, 0.12) 0%, transparent 40%),
        radial-gradient(circle at 50% 80%, rgba(0, 242, 254, 0.08) 0%, transparent 50%);
      color: var(--text);
      font-family: var(--font);
      line-height: 1.6;
      overflow-x: hidden;
      min-height: 100vh;
    }
    a { color: var(--accent); text-decoration: none; transition: 0.2s; }
    a:hover { color: var(--cyan); text-decoration: underline; }

    /* Nav Bar */
    nav.navbar {
      position: sticky;
      top: 0;
      z-index: 1000;
      background: rgba(7, 10, 18, 0.85);
      backdrop-filter: blur(14px);
      border-bottom: 1px solid var(--border);
      padding: 14px 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }
    .nav-brand {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 20px;
      font-weight: 800;
      color: var(--heading);
      letter-spacing: -0.5px;
    }
    .nav-brand span.logo-icon {
      background: linear-gradient(135deg, #00f2fe, #4facfe);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      font-size: 24px;
    }
    .badge-tag {
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 12px;
      background: rgba(88, 166, 255, 0.15);
      border: 1px solid rgba(88, 166, 255, 0.3);
      color: var(--accent);
      font-weight: 600;
      text-transform: uppercase;
    }
    .nav-menu {
      display: flex;
      gap: 22px;
      align-items: center;
    }
    .nav-menu a {
      color: var(--text);
      font-size: 14px;
      font-weight: 500;
      text-decoration: none;
    }
    .nav-menu a:hover { color: var(--heading); }
    .nav-actions {
      display: flex;
      gap: 10px;
      align-items: center;
    }

    /* Buttons */
    .btn {
      padding: 9px 18px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s ease;
      text-decoration: none;
      border: 1px solid var(--border);
      background: #161b22;
      color: var(--heading);
    }
    .btn:hover {
      background: #21262d;
      border-color: #8b949e;
      transform: translateY(-1px);
    }
    .btn-primary {
      background: linear-gradient(135deg, #238636, #2ea043);
      color: #fff;
      border: 1px solid rgba(255,255,255,0.2);
      box-shadow: 0 4px 14px rgba(35, 134, 54, 0.35);
    }
    .btn-primary:hover {
      background: linear-gradient(135deg, #2ea043, #3fb950);
      box-shadow: 0 6px 20px rgba(46, 160, 67, 0.45);
    }
    .btn-accent {
      background: linear-gradient(135deg, #1f6feb, #388bfd);
      color: #fff;
      border: none;
      box-shadow: 0 4px 14px rgba(31, 111, 235, 0.35);
    }
    .btn-accent:hover {
      background: linear-gradient(135deg, #388bfd, #58a6ff);
      box-shadow: 0 6px 20px rgba(56, 139, 253, 0.45);
    }
    .btn-purple {
      background: linear-gradient(135deg, #8957e5, #a371f7);
      color: #fff;
      border: none;
    }
    .btn-purple:hover {
      background: linear-gradient(135deg, #a371f7, #bc8cff);
    }

    /* Container */
    .container {
      max-width: 1260px;
      margin: 0 auto;
      padding: 0 24px;
    }

    /* Hero Section */
    .hero-section {
      padding: 70px 0 60px 0;
      text-align: center;
      position: relative;
    }
    .hero-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 16px;
      background: rgba(88, 166, 255, 0.1);
      border: 1px solid rgba(88, 166, 255, 0.3);
      border-radius: 30px;
      font-size: 13px;
      color: var(--cyan);
      font-weight: 600;
      margin-bottom: 24px;
      box-shadow: 0 0 20px rgba(0, 242, 254, 0.15);
    }
    .hero-title {
      font-size: 52px;
      font-weight: 800;
      line-height: 1.15;
      color: var(--heading);
      letter-spacing: -1.2px;
      max-width: 960px;
      margin: 0 auto 20px auto;
    }
    .hero-title .gradient-text {
      background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #bc8cff 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
      font-size: 18px;
      color: #8b949e;
      max-width: 780px;
      margin: 0 auto 36px auto;
      line-height: 1.6;
    }
    .hero-ctas {
      display: flex;
      justify-content: center;
      gap: 16px;
      flex-wrap: wrap;
      margin-bottom: 50px;
    }
    .hero-ctas .btn {
      padding: 13px 26px;
      font-size: 15px;
    }

    /* Device Mesh Poster Illustration */
    .hero-poster-container {
      margin: 20px auto 70px auto;
      max-width: 1080px;
      background: linear-gradient(180deg, rgba(22, 27, 34, 0.8) 0%, rgba(13, 17, 23, 0.95) 100%);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 30px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6), 0 0 30px rgba(88, 166, 255, 0.15);
      position: relative;
    }
    .poster-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      padding-bottom: 14px;
      margin-bottom: 24px;
    }
    .mesh-split {
      display: grid;
      grid-template-columns: 1fr auto 1fr;
      gap: 24px;
      align-items: center;
    }
    @media (max-width: 860px) {
      .mesh-split { grid-template-columns: 1fr; }
      .mesh-bridge { display: none; }
      .hero-title { font-size: 36px; }
    }
    
    /* Device Posters */
    .device-poster {
      background: #090d14;
      border: 1px solid #30363d;
      border-radius: 12px;
      padding: 20px;
      text-align: left;
      position: relative;
      overflow: hidden;
    }
    .device-poster::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0; height: 3px;
      background: linear-gradient(90deg, #00f2fe, #58a6ff);
    }
    .device-poster.android::before {
      background: linear-gradient(90deg, #3fb950, #00f2fe);
    }
    .device-badge {
      display: inline-block;
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 6px;
      background: #21262d;
      color: #58a6ff;
      font-weight: 700;
      margin-bottom: 10px;
      text-transform: uppercase;
    }
    .device-title {
      font-size: 18px;
      font-weight: 700;
      color: var(--heading);
      margin-bottom: 6px;
    }
    .device-spec {
      font-size: 12px;
      color: #8b949e;
      margin-bottom: 16px;
    }
    .device-screen-mock {
      background: #0d1117;
      border: 1px solid #30363d;
      border-radius: 8px;
      padding: 14px;
      font-family: Consolas, monospace;
      font-size: 12px;
      color: #7ee787;
      min-height: 160px;
      line-height: 1.5;
    }

    /* WebRTC Bridge Animation */
    .mesh-bridge {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 10px;
    }
    .bridge-pill {
      background: rgba(0, 242, 254, 0.15);
      border: 1px solid rgba(0, 242, 254, 0.4);
      color: var(--cyan);
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 700;
      animation: pulseGlow 2s infinite ease-in-out;
    }
    @keyframes pulseGlow {
      0%, 100% { box-shadow: 0 0 10px rgba(0, 242, 254, 0.2); }
      50% { box-shadow: 0 0 25px rgba(0, 242, 254, 0.6); }
    }
    .bridge-line {
      width: 120px;
      height: 3px;
      background: linear-gradient(90deg, #58a6ff, #00f2fe, #bc8cff);
      position: relative;
    }

    /* Feature Posters Grid */
    .section-header {
      text-align: center;
      margin-bottom: 50px;
    }
    .section-title {
      font-size: 34px;
      font-weight: 800;
      color: var(--heading);
      margin-bottom: 12px;
    }
    .section-desc {
      font-size: 16px;
      color: #8b949e;
      max-width: 650px;
      margin: 0 auto;
    }
    .posters-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 24px;
      margin-bottom: 80px;
    }
    .feature-card {
      background: var(--card-bg);
      backdrop-filter: blur(10px);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 28px;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
      overflow: hidden;
    }
    .feature-card:hover {
      transform: translateY(-5px);
      border-color: var(--border-glow);
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.4), 0 0 20px rgba(88, 166, 255, 0.1);
    }
    .feature-icon {
      font-size: 36px;
      margin-bottom: 18px;
      display: inline-block;
    }
    .feature-title {
      font-size: 19px;
      font-weight: 700;
      color: var(--heading);
      margin-bottom: 10px;
    }
    .feature-body {
      font-size: 14px;
      color: #8b949e;
      line-height: 1.6;
    }
    .feature-tags {
      display: flex;
      gap: 8px;
      margin-top: 16px;
      flex-wrap: wrap;
    }
    .feature-tag {
      font-size: 11px;
      background: #21262d;
      color: var(--cyan);
      padding: 3px 8px;
      border-radius: 6px;
      font-weight: 600;
    }

    /* Calculator Section */
    .calculator-box {
      background: linear-gradient(145deg, rgba(22, 27, 34, 0.95), rgba(13, 17, 23, 0.95));
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 36px;
      margin-bottom: 80px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 36px;
    }
    @media (max-width: 860px) {
      .calculator-box { grid-template-columns: 1fr; }
    }
    .calc-slider-group {
      margin-bottom: 24px;
    }
    .calc-slider-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      font-weight: 600;
      color: var(--heading);
    }
    input[type=range] {
      width: 100%;
      height: 6px;
      background: #21262d;
      border-radius: 4px;
      outline: none;
      -webkit-appearance: none;
    }
    input[type=range]::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: var(--cyan);
      cursor: pointer;
      box-shadow: 0 0 10px rgba(0, 242, 254, 0.6);
    }
    .cost-summary-card {
      background: #090d14;
      border: 1px solid #30363d;
      border-radius: 12px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .cost-metric-row {
      display: flex;
      justify-content: space-between;
      padding: 10px 0;
      border-bottom: 1px solid #21262d;
      font-size: 14px;
    }
    .cost-grand-total {
      font-size: 32px;
      font-weight: 800;
      color: var(--green);
      margin-top: 14px;
    }
    .savings-badge {
      background: rgba(46, 160, 67, 0.15);
      border: 1px solid rgba(46, 160, 67, 0.4);
      color: #7ee787;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 700;
      margin-top: 12px;
      display: inline-block;
    }

    /* Downloads Grid */
    .download-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-bottom: 80px;
    }
    @media (max-width: 768px) {
      .download-grid { grid-template-columns: 1fr; }
    }
    .download-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 30px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .download-card h3 {
      font-size: 22px;
      color: var(--heading);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    /* Pricing Plans Grid */
    .pricing-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 24px;
      margin-bottom: 80px;
    }
    .plan-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 32px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
    }
    .plan-card.featured {
      border-color: var(--cyan);
      box-shadow: 0 0 30px rgba(0, 242, 254, 0.2);
    }
    .featured-tag {
      position: absolute;
      top: -12px;
      left: 50%;
      transform: translateX(-50%);
      background: linear-gradient(135deg, #00f2fe, #1f6feb);
      color: #fff;
      padding: 3px 12px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
    }
    .plan-price {
      font-size: 38px;
      font-weight: 800;
      color: var(--heading);
      margin: 16px 0;
    }
    .plan-features {
      list-style: none;
      margin: 20px 0;
      font-size: 14px;
    }
    .plan-features li {
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .plan-features li::before {
      content: '✓';
      color: var(--green);
      font-weight: bold;
    }

    /* User Dashboard View Modal / Container */
    #user-dashboard-view {
      display: none;
      background: #090d16;
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 30px;
      margin-bottom: 60px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
    }
    .dash-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      padding-bottom: 16px;
      margin-bottom: 24px;
    }

    /* Footer */
    footer {
      border-top: 1px solid var(--border);
      padding: 40px 0;
      text-align: center;
      font-size: 13px;
      color: #8b949e;
    }
  </style>
</head>
<body>

  <!-- Top Navbar -->
  <nav class="navbar">
    <div class="nav-brand">
      <span class="logo-icon">⚡</span>
      <span>Penta-Assistant</span>
      <span class="badge-tag">v2.4 Production</span>
    </div>
    <div class="nav-menu">
      <a href="#features">Features</a>
      <a href="#architecture">Architecture</a>
      <a href="#calculator">Cost Calculator</a>
      <a href="#downloads">Downloads</a>
      <a href="#pricing">Pricing</a>
    </div>
    <div class="nav-actions">
      <!-- Role Demo Switcher Dropdown -->
      <select id="role-selector" onchange="switchRole(this.value)" style="background:#161b22; border:1px solid #30363d; color:#c9d1d9; padding:6px 10px; border-radius:6px; font-size:12px; font-weight:600;">
        <option value="visitor">🌐 View as: Visitor</option>
        <option value="user" selected>👤 View as: Pro Subscriber (Alex)</option>
        <option value="admin">🛡️ View as: Admin Console</option>
      </select>
      <button class="btn btn-accent" onclick="toggleUserDashboard()">💻 User Dashboard</button>
      <a href="/admin" class="btn btn-purple">🛡️ Admin Portal</a>
    </div>
  </nav>

  <!-- Interactive User Dashboard Section (Accessible to logged-in user role under admin) -->
  <div class="container" id="user-dashboard-wrapper" style="margin-top: 24px;">
    <div id="user-dashboard-view">
      <div class="dash-header">
        <div>
          <h2 style="font-size: 22px; color: #f0f6fc; display:flex; align-items:center; gap:10px;">
            <span>💻 User Command Center</span>
            <span id="user-role-badge" style="background:rgba(46,160,67,0.2); color:#7ee787; border:1px solid #3fb950; font-size:12px; padding:2px 10px; border-radius:12px;">PRO SUBSCRIBER</span>
          </h2>
          <div style="font-size: 13px; color: #8b949e; margin-top: 4px;">
            Logged in as: <strong id="user-email-display" style="color: #58a6ff;">alex@pro.com</strong> | License: <code id="user-license-display" style="background:#0d1117; padding:2px 6px; border-radius:4px;">PENTA-PRO-2026-X7K</code>
          </div>
        </div>
        <button class="btn btn-sm" onclick="toggleUserDashboard()">✕ Close Dashboard</button>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px;">
        <!-- Paired Devices Card -->
        <div style="background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 18px;">
          <h3 style="font-size: 15px; color: #f0f6fc; margin-bottom: 12px; display:flex; justify-content:space-between;">
            <span>📱 My Paired Devices</span>
            <span style="color:#7ee787; font-size:12px;">● 2 Devices Connected</span>
          </h3>
          <div style="font-size: 13px; line-height: 1.8;">
            <div style="display:flex; justify-content:space-between; border-bottom:1px solid #21262d; padding:6px 0;">
              <span>🖥️ <strong>Windows Workstation (Win 11)</strong></span>
              <button class="btn btn-sm btn-accent" onclick="alert('Connecting WebRTC AnyDesk Canvas to Windows Workstation...')">Launch AnyDesk</button>
            </div>
            <div style="display:flex; justify-content:space-between; padding:6px 0;">
              <span>📱 <strong>Samsung Galaxy S24 Ultra</strong></span>
              <button class="btn btn-sm btn-primary" onclick="alert('Connecting WebRTC AnyDesk Canvas to Galaxy S24...')">Remote Control</button>
            </div>
          </div>
        </div>

        <!-- Promo Code & Subscription Card -->
        <div style="background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 18px;">
          <h3 style="font-size: 15px; color: #f0f6fc; margin-bottom: 12px;">🎟️ Redeem Promo / Coupon Code</h3>
          <p style="font-size: 12px; color: #8b949e; margin-bottom: 12px;">Enter your promotional coupon authorized by the admin to instantly upgrade your account without a credit card.</p>
          <div style="display:flex; gap:8px;">
            <input type="text" id="dash-coupon-code" placeholder="e.g. PENTAFREE" style="flex:1; background:#0d1117; border:1px solid #30363d; color:#c9d1d9; padding:8px 12px; border-radius:6px; font-size:13px; text-transform:uppercase;">
            <button class="btn btn-primary" onclick="redeemCouponFromDash()">Apply Code</button>
          </div>
          <div id="dash-redeem-msg" style="margin-top:10px; font-size:12px; display:none;"></div>
        </div>
      </div>

      <!-- Autonomous Agent Co-Pilot -->
      <div style="background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 18px;">
        <h3 style="font-size: 15px; color: #f0f6fc; margin-bottom: 12px;">🤖 Google Antigravity AI Co-Pilot Execution</h3>
        <div style="display: flex; gap: 10px; margin-bottom: 12px;">
          <input type="text" id="ai-user-task" placeholder="Enter task (e.g. 'Open WhatsApp on phone, find Mom, and send I will be home at 7 PM')" style="flex:1; background:#0d1117; border:1px solid #30363d; color:#c9d1d9; padding:9px 12px; border-radius:6px; font-size:13px;">
          <select id="target-dev-select" style="background:#0d1117; border:1px solid #30363d; color:#c9d1d9; padding:8px 12px; border-radius:6px; font-size:13px;">
            <option value="phone">Target: Galaxy S24 (Android)</option>
            <option value="pc">Target: Windows Workstation (PC)</option>
          </select>
          <button class="btn btn-accent" onclick="runAiAgentTask()">Dispatch Mission</button>
        </div>
        <div id="ai-exec-log" style="background:#090d14; border:1px solid #30363d; border-radius:6px; padding:12px; font-family:monospace; font-size:12px; color:#7ee787; min-height:80px; max-height:160px; overflow-y:auto;">
          ⚡ Ready. Select target device and dispatch multi-step autonomous AI mission.
        </div>
      </div>
    </div>
  </div>

  <!-- Hero Section -->
  <section class="hero-section container">
    <div class="hero-pill">
      <span>🤖 Google Antigravity Agentic AI</span>
      <span>•</span>
      <span>📡 AnyDesk-Grade WebRTC Mesh</span>
    </div>
    <h1 class="hero-title">
      The First Autonomous Cross-Platform <br>
      <span class="gradient-text">AI Agent & Remote Control Mesh</span>
    </h1>
    <p class="hero-subtitle">
      Automate and control your Windows PC and Android Phone simultaneously. Ultra low-latency 60 FPS WebRTC canvas paired with multi-step vision-guided agentic intelligence.
    </p>
    <div class="hero-ctas">
      <a href="/download/PentaAssistant-Setup.exe" class="btn btn-primary">
        <span>⚡ Download for Windows (.exe)</span>
      </a>
      <a href="/download/PentaAssistant.apk" class="btn btn-accent">
        <span>📱 Download for Android (.apk)</span>
      </a>
      <button class="btn" onclick="toggleUserDashboard()">
        <span>🚀 Launch Interactive User Hub</span>
      </button>
      <a href="/admin" class="btn btn-purple">
        <span>🛡️ Admin Portal</span>
      </a>
    </div>

    <!-- Live Device Mesh Poster Illustration -->
    <div class="hero-poster-container" id="architecture">
      <div class="poster-header">
        <div style="font-weight: 700; color: #f0f6fc; font-size: 15px; display:flex; align-items:center; gap:8px;">
          <span style="color:#00f2fe;">🌐</span>
          <span>LIVE ARCHITECTURE POSTER: P2P REMOTE MESH & MULTI-MODEL BRAIN</span>
        </div>
        <div style="font-size: 12px; color: #7ee787; font-weight:600;">
          ● ZERO LOCAL SERVER REQUIRED
        </div>
      </div>

      <div class="mesh-split">
        <!-- Windows PC Poster -->
        <div class="device-poster">
          <span class="device-badge">Windows 11 / 10 Node</span>
          <div class="device-title">🖥️ PC Desktop Agent</div>
          <div class="device-spec">Native Win32 GDI Capture • Hardware Input Injection • 1080p 60 FPS</div>
          <div class="device-screen-mock">
            [AGENT VISION] Screen Resolution: 1920x1080<br>
            [CO-PILOT] Processing multi-step task...<br>
            [ACTION] MouseMove(x=960, y=540)<br>
            [SYSTEM] WebRTC P2P DataChannel Active (8.4ms)
          </div>
        </div>

        <!-- Pulsing WebRTC Bridge -->
        <div class="mesh-bridge">
          <div class="bridge-pill">⚡ &lt; 12ms P2P WebRTC</div>
          <div class="bridge-line"></div>
          <div style="font-size: 11px; color: #8b949e; text-transform:uppercase; font-weight:700;">E2E Encrypted</div>
        </div>

        <!-- Android Mobile Poster -->
        <div class="device-poster android">
          <span class="device-badge" style="color: #3fb950;">Android 14 / 15 Node</span>
          <div class="device-title">📱 Android Mobile Agent</div>
          <div class="device-spec">Autonomous Touch • ADB / Wi-Fi Switching • Hardware Navigation</div>
          <div class="device-screen-mock">
            [MOBILE NODE] Device: Pixel 9 Pro (1080x2400)<br>
            [AGENT OCR] Detected button "Confirm Payment"<br>
            [DISPATCH] Tap(x=540, y=1980)<br>
            [STATUS] AnyDesk 60 FPS Viewport Mirrored
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Feature Cards / Posters -->
  <section class="container" id="features">
    <div class="section-header">
      <h2 class="section-title">Engineered for Production Performance</h2>
      <p class="section-desc">Penta-Assistant replaces disjointed remote desk tools and basic chatbots with an enterprise-grade cross-device cognitive mesh.</p>
    </div>

    <div class="posters-grid">
      <!-- Card 1 -->
      <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <h3 class="feature-title">Google Antigravity Agent</h3>
        <p class="feature-body">Multi-step autonomous computer-use agent. Perceives the screen pixel-by-pixel, plans complex workflows, clicks, scrolls, types, and self-corrects errors in real-time.</p>
        <div class="feature-tags">
          <span class="feature-tag">Multimodal Vision</span>
          <span class="feature-tag">Self-Healing</span>
          <span class="feature-tag">Zero-Shot Planning</span>
        </div>
      </div>

      <!-- Card 2 -->
      <div class="feature-card">
        <div class="feature-icon">📡</div>
        <h3 class="feature-title">AnyDesk-Grade 60 FPS Canvas</h3>
        <p class="feature-body">Ultra-low latency WebRTC remote control canvas. Stream your phone to your PC or your PC to your phone with tactile touch, gestures, and zero perceptible lag.</p>
        <div class="feature-tags">
          <span class="feature-tag">&lt; 15ms Latency</span>
          <span class="feature-tag">H.264 P2P</span>
          <span class="feature-tag">Bidirectional Clipboard</span>
        </div>
      </div>

      <!-- Card 3 -->
      <div class="feature-card">
        <div class="feature-icon">🌐</div>
        <h3 class="feature-title">Bi-Directional Device Mesh</h3>
        <p class="feature-body">Break the boundaries of operating systems. Control your Android smartphone from your Windows workstation, or control your PC while commuting on your phone.</p>
        <div class="feature-tags">
          <span class="feature-tag">Tailscale Support</span>
          <span class="feature-tag">TURN Relays</span>
          <span class="feature-tag">Zero Local Server</span>
        </div>
      </div>

      <!-- Card 4 -->
      <div class="feature-card">
        <div class="feature-icon">🧠</div>
        <h3 class="feature-title">Unified Multi-Model Gateway</h3>
        <p class="feature-body">Bring your own model or use cloud inference. Seamlessly route tasks to Gemini 2.0 Flash, Claude 3.5 Sonnet, GPT-4o, Groq Llama-3.3 70B, or local offline Ollama.</p>
        <div class="feature-tags">
          <span class="feature-tag">Gemini 2.0</span>
          <span class="feature-tag">Claude 3.5</span>
          <span class="feature-tag">Local Ollama</span>
        </div>
      </div>

      <!-- Card 5 -->
      <div class="feature-card">
        <div class="feature-icon">🛡️</div>
        <h3 class="feature-title">User Roles & Admin Governance</h3>
        <p class="feature-body">Enterprise role-based access control. Admin console enables one-click user promotion, promo coupon creation, Stripe MRR telemetry, and device node audits.</p>
        <div class="feature-tags">
          <span class="feature-tag">RBAC Security</span>
          <span class="feature-tag">Coupon Engine</span>
          <span class="feature-tag">Stripe Sandbox</span>
        </div>
      </div>

      <!-- Card 6 -->
      <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <h3 class="feature-title">Standalone Native Apps</h3>
        <p class="feature-body">Lightweight desktop & mobile apps built with Vite + React + Tauri v2. No heavy local Python servers needed on client devices—just clean, native performance.</p>
        <div class="feature-tags">
          <span class="feature-tag">Tauri v2</span>
          <span class="feature-tag">React 18</span>
          <span class="feature-tag">~12 MB Executable</span>
        </div>
      </div>
    </div>
  </section>

  <!-- Interactive Dynamic Cost & Unit Economics Calculator -->
  <section class="container" id="calculator">
    <div class="section-header">
      <h2 class="section-title">Dynamic Resource Cost & Economics Calculator</h2>
      <p class="section-desc">Transparent unit economics based on real AI vision token consumption, TURN WebRTC relay bandwidth, and cloud serverless compute.</p>
    </div>

    <div class="calculator-box">
      <div>
        <div class="calc-slider-group">
          <div class="calc-slider-header">
            <span>📱 Paired Devices</span>
            <span id="val-devices" style="color:var(--cyan); font-size:18px;">2</span>
          </div>
          <input type="range" id="range-devices" min="1" max="10" value="2" oninput="updateCalculator()">
        </div>

        <div class="calc-slider-group">
          <div class="calc-slider-header">
            <span>🤖 AI Tasks / Day (Autonomous Computer-Use)</span>
            <span id="val-tasks" style="color:var(--cyan); font-size:18px;">15</span>
          </div>
          <input type="range" id="range-tasks" min="1" max="100" value="15" oninput="updateCalculator()">
        </div>

        <div class="calc-slider-group">
          <div class="calc-slider-header">
            <span>📡 Remote Stream Hours / Week (AnyDesk Canvas)</span>
            <span id="val-stream" style="color:var(--cyan); font-size:18px;">10 hrs</span>
          </div>
          <input type="range" id="range-stream" min="1" max="50" value="10" oninput="updateCalculator()">
        </div>
      </div>

      <div class="cost-summary-card">
        <div>
          <div style="font-size:12px; color:#8b949e; text-transform:uppercase; font-weight:700; margin-bottom:10px;">Monthly Operating Unit Economics</div>
          <div class="cost-metric-row">
            <span>AI Multimodal Vision Tokens</span>
            <span id="cost-ai" style="color:var(--heading); font-weight:600;">$1.80</span>
          </div>
          <div class="cost-metric-row">
            <span>WebRTC TURN Relay Bandwidth</span>
            <span id="cost-turn" style="color:var(--heading); font-weight:600;">$0.80</span>
          </div>
          <div class="cost-metric-row">
            <span>Signaling & Mesh Infrastructure</span>
            <span id="cost-infra" style="color:var(--heading); font-weight:600;">$0.50</span>
          </div>
          <div style="margin-top: 14px;">
            <div style="font-size: 12px; color: #8b949e;">Est. Total Infrastructure Cost:</div>
            <div class="cost-grand-total" id="cost-total">$3.10 / mo</div>
          </div>
        </div>

        <div>
          <div class="savings-badge" id="savings-badge">
            💰 Save $22.90/mo vs AnyDesk ($14.90) + ChatGPT Plus ($20)
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Client Apps Download Center -->
  <section class="container" id="downloads">
    <div class="section-header">
      <h2 class="section-title">Download Client Applications</h2>
      <p class="section-desc">Native, lightweight binaries for Windows and Android. No local servers required.</p>
    </div>

    <div class="download-grid">
      <!-- Windows App -->
      <div class="download-card">
        <div>
          <h3>🖥️ Penta-Assistant for Windows</h3>
          <p style="font-size: 14px; color: #8b949e; margin-bottom: 16px;">
            Complete standalone desktop executable with native GDI screen capture, hardware input injection, and embedded Antigravity AI engine.
          </p>
          <div style="font-size: 12px; color: #8b949e; margin-bottom: 20px; line-height: 1.8;">
            <div>• Version: <strong>v2.4.0 (Latest Production)</strong></div>
            <div>• Size: <strong>12.4 MB</strong> (Zero heavy dependencies)</div>
            <div>• OS: <strong>Windows 10 / 11 (64-bit)</strong></div>
            <div>• SHA256: <code style="font-size:11px;">e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855</code></div>
          </div>
        </div>
        <a href="/download/PentaAssistant-Setup.exe" class="btn btn-primary" style="justify-content:center; padding:12px;">
          <span>⚡ Download Windows Installer (.exe)</span>
        </a>
      </div>

      <!-- Android App -->
      <div class="download-card">
        <div>
          <h3>📱 Penta-Assistant for Android</h3>
          <p style="font-size: 14px; color: #8b949e; margin-bottom: 16px;">
            Lightweight mobile client for remote smartphone control, touch coordinate mapping, Wi-Fi pairing, and remote PC viewing.
          </p>
          <div style="font-size: 12px; color: #8b949e; margin-bottom: 20px; line-height: 1.8;">
            <div>• Version: <strong>v2.4.0 Mobile Release</strong></div>
            <div>• Size: <strong>14.2 MB</strong></div>
            <div>• OS: <strong>Android 11, 12, 13, 14, 15+</strong></div>
            <div>• SHA256: <code style="font-size:11px;">b8956b6a3b2b801a2d5f818b7468e2f8e124ef94da7c6d66e5114170875c7429</code></div>
          </div>
        </div>
        <a href="/download/PentaAssistant.apk" class="btn btn-accent" style="justify-content:center; padding:12px;">
          <span>📱 Download Android APK (.apk)</span>
        </a>
      </div>
    </div>
  </section>

  <!-- Subscription Pricing & Stripe Checkout -->
  <section class="container" id="pricing">
    <div class="section-header">
      <h2 class="section-title">Simple, Transparent Pricing</h2>
      <p class="section-desc">Unlock unlimited AnyDesk remote control and autonomous agentic AI steps.</p>
    </div>

    <div class="pricing-grid">
      <!-- Free Starter -->
      <div class="plan-card">
        <div>
          <h3 style="font-size: 20px; color: #f0f6fc;">Free Starter</h3>
          <p style="font-size: 13px; color: #8b949e;">For individual hobbyists and local exploration.</p>
          <div class="plan-price">$0 <span style="font-size: 14px; font-weight: normal; color: #8b949e;">/ forever</span></div>
          <ul class="plan-features">
            <li>1 Paired Device</li>
            <li>Local LAN AnyDesk Viewport</li>
            <li>Bring-Your-Own-Key (BYOK) AI</li>
            <li>Community GitHub Support</li>
          </ul>
        </div>
        <button class="btn" onclick="toggleUserDashboard()">Current Plan (Free)</button>
      </div>

      <!-- Penta Pro (Featured) -->
      <div class="plan-card featured">
        <div class="featured-tag">Most Popular</div>
        <div>
          <h3 style="font-size: 20px; color: #f0f6fc;">Penta Pro</h3>
          <p style="font-size: 13px; color: #8b949e;">For professionals and remote power users.</p>
          <div class="plan-price">$12 <span style="font-size: 14px; font-weight: normal; color: #8b949e;">/ month</span></div>
          <ul class="plan-features">
            <li>5 Paired Devices (Windows + Android)</li>
            <li>Unlimited P2P WebRTC AnyDesk Remote</li>
            <li>2,000 Autonomous AI Steps / mo</li>
            <li>Multi-Model Vision Gateway (Gemini + Claude)</li>
            <li>Encrypted Cloud Clipboard Sync</li>
          </ul>
        </div>
        <div style="display:flex; flex-direction:column; gap:8px;">
          <button class="btn btn-primary" onclick="launchStripeCheckout('pro')">Subscribe with Stripe</button>
          <button class="btn btn-sm" onclick="openPromoModal('PENTAFREE')">🎟️ Redeem Promo (PENTAFREE)</button>
        </div>
      </div>

      <!-- Penta Team -->
      <div class="plan-card">
        <div>
          <h3 style="font-size: 20px; color: #f0f6fc;">Penta Team</h3>
          <p style="font-size: 13px; color: #8b949e;">For organizations and multi-agent operations.</p>
          <div class="plan-price">$29 <span style="font-size: 14px; font-weight: normal; color: #8b949e;">/ month</span></div>
          <ul class="plan-features">
            <li>Unlimited Devices & Mesh Relays</li>
            <li>5-Agent Autonomous Mission Bus</li>
            <li>Dedicated Global TURN Server Relays</li>
            <li>Admin Role Management & RBAC</li>
            <li>Priority 24/7 SLA Support</li>
          </ul>
        </div>
        <button class="btn btn-purple" onclick="launchStripeCheckout('team')">Upgrade to Team</button>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer>
    <div class="container">
      <div style="margin-bottom: 12px; font-weight:700; color:#f0f6fc;">Penta-Assistant © 2026. Production Grade Cross-Platform Ecosystem.</div>
      <div>Google Antigravity Autonomous Agentic AI • AnyDesk Low-Latency Remote Control • Stripe Billing • Admin RBAC</div>
    </div>
  </footer>

  <script>
    // Dynamic Calculator Logic
    function updateCalculator() {
      const dev = parseInt(document.getElementById('range-devices').value);
      const tasks = parseInt(document.getElementById('range-tasks').value);
      const stream = parseInt(document.getElementById('range-stream').value);

      document.getElementById('val-devices').innerText = dev;
      document.getElementById('val-tasks').innerText = tasks;
      document.getElementById('val-stream').innerText = stream + ' hrs';

      // Economic formula
      const aiCost = (tasks * 30 * 4 * 0.001); // $0.001 per step
      const turnCost = (stream * 4.33 * 0.4 * 0.04); // 0.4GB/hr @ $0.04/GB
      const infraCost = 0.50 + (dev * 0.20);
      const totalCost = aiCost + turnCost + infraCost;

      document.getElementById('cost-ai').innerText = '$' + aiCost.toFixed(2);
      document.getElementById('cost-turn').innerText = '$' + turnCost.toFixed(2);
      document.getElementById('cost-infra').innerText = '$' + infraCost.toFixed(2);
      document.getElementById('cost-total').innerText = '$' + totalCost.toFixed(2) + ' / mo';

      const competitorPrice = 34.90;
      const savings = Math.max(0, competitorPrice - 12.0).toFixed(2);
      document.getElementById('savings-badge').innerText = `💰 Save $${savings}/mo vs AnyDesk ($14.90) + ChatGPT Plus ($20)`;
    }

    // Role Switcher Demo
    function switchRole(role) {
      if (role === 'admin') {
        window.location.href = '/admin';
      } else if (role === 'user') {
        document.getElementById('user-dashboard-view').style.display = 'block';
        document.getElementById('user-role-badge').innerText = 'PRO SUBSCRIBER';
        document.getElementById('user-email-display').innerText = 'alex@pro.com';
        document.getElementById('user-license-display').innerText = 'PENTA-PRO-2026-X7K';
        document.getElementById('user-dashboard-wrapper').scrollIntoView({ behavior: 'smooth' });
      } else {
        document.getElementById('user-dashboard-view').style.display = 'none';
      }
    }

    function toggleUserDashboard() {
      const dash = document.getElementById('user-dashboard-view');
      if (dash.style.display === 'block') {
        dash.style.display = 'none';
      } else {
        dash.style.display = 'block';
        document.getElementById('user-dashboard-wrapper').scrollIntoView({ behavior: 'smooth' });
      }
    }

    // Promo Code Redemption
    async function redeemCouponFromDash() {
      const code = document.getElementById('dash-coupon-code').value.trim().toUpperCase();
      const msgEl = document.getElementById('dash-redeem-msg');
      if (!code) { alert('Please enter a coupon code.'); return; }

      try {
        const res = await fetch('/api/coupons/redeem', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code: code, email: 'alex@pro.com' })
        });
        const data = await res.json();
        if (data.valid) {
          msgEl.style.display = 'block';
          msgEl.style.color = '#7ee787';
          msgEl.innerText = `🎉 Success! ${data.message} | License: ${data.license_key}`;
          document.getElementById('user-license-display').innerText = data.license_key;
        } else {
          msgEl.style.display = 'block';
          msgEl.style.color = '#f85149';
          msgEl.innerText = `❌ Error: ${data.error}`;
        }
      } catch (err) {
        msgEl.style.display = 'block';
        msgEl.style.color = '#f85149';
        msgEl.innerText = 'Network error during redemption.';
      }
    }

    function openPromoModal(code) {
      document.getElementById('dash-coupon-code').value = code;
      toggleUserDashboard();
      redeemCouponFromDash();
    }

    // Stripe Checkout Trigger
    async function launchStripeCheckout(planId) {
      try {
        const res = await fetch('/api/stripe/create-checkout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ plan_id: planId, email: 'buyer@pentactopus.com' })
        });
        const data = await res.json();
        if (data.url) {
          alert(`Stripe Sandbox Session Created! Redirecting to checkout: ${data.url}`);
        } else {
          alert(`Checkout Session: ${JSON.stringify(data)}`);
        }
      } catch (err) {
        alert('Stripe checkout simulation error: ' + err);
      }
    }

    // AI Mission Task Dispatch Simulation
    function runAiAgentTask() {
      const task = document.getElementById('ai-user-task').value;
      const target = document.getElementById('target-dev-select').value;
      const log = document.getElementById('ai-exec-log');

      if (!task) { alert('Please enter an instruction for the AI agent.'); return; }

      log.innerHTML = `[DISPATCH] Target: ${target.toUpperCase()} | Mission: "${task}"\n`;
      setTimeout(() => {
        log.innerHTML += `[VISION OCR] Screen capture analyzed. Located target interface elements.\n`;
      }, 500);
      setTimeout(() => {
        log.innerHTML += `[STEP 1] Action dispatched: Click & navigate.\n`;
      }, 1000);
      setTimeout(() => {
        log.innerHTML += `[SUCCESS] Mission executed autonomously. Verification passed (100%).\n`;
      }, 1500);
    }

    // Initialize Calculator on load
    updateCalculator();
  </script>
</body>
</html>
"""
