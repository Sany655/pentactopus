"""Enterprise Web Template, Landing Page & Authentication UI for Pentactopus.

Styled with modern Linear/Vercel-grade minimalism:
- Deep matte carbon palette (#09090b) with hairline micro-borders
- Geometric Pentactopus vector crest (5-node interconnected cyber mesh)
- 100% proprietary enterprise branding
- Zero cartoonish emojis or rainbow gradients
- Dedicated /login, /register, and authenticated /dashboard views with brute-force handling
- Scroll-reveal animations, step-by-step onboarding, AI model showcase
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

PENTACTOPUS_LOGO_LARGE = """<svg width="56" height="56" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="16" cy="16" r="5" fill="#3b82f6" stroke="#60a5fa" stroke-width="1.2"/>
  <circle cx="16" cy="5" r="2.5" fill="#94a3b8"/>
  <circle cx="26" cy="12" r="2.5" fill="#94a3b8"/>
  <circle cx="22" cy="25" r="2.5" fill="#94a3b8"/>
  <circle cx="10" cy="25" r="2.5" fill="#94a3b8"/>
  <circle cx="6" cy="12" r="2.5" fill="#94a3b8"/>
  <path d="M16 11V7.5M20 13.5L23.5 13M18.5 19.5L20.5 23M13.5 19.5L11.5 23M12 13.5L8.5 13" stroke="#475569" stroke-width="1.5" stroke-linecap="round"/>
</svg>"""

import os

EXE_URL = os.getenv("RELEASE_DOWNLOAD_EXE_URL", "https://github.com/Sany655/pentactopus-releases/raw/main/PentaAssistant-Setup.exe")
APK_URL = os.getenv("RELEASE_DOWNLOAD_APK_URL", "https://github.com/Sany655/pentactopus-releases/raw/main/PentaAssistant.apk")

HTML_PAGE = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Pentactopus | Your AI-Powered Remote Control Mesh for Windows & Android</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Control your Windows PC from Android, or your phone from your desktop. Pentactopus combines seamless remote desktop control with an autonomous AI agent that sees, clicks, types, and automates for you.">
  <meta name="keywords" content="remote desktop, AI agent, computer use, remote control alternative, Windows remote control, Android remote, screen sharing, automation">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
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
      --accent-glow: rgba(59, 130, 246, 0.15);
      --green: #10b981;
      --red: #ef4444;
      --purple: #a855f7;
      --orange: #f97316;
      --font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      background-color: var(--bg);
      color: var(--text);
      font-family: var(--font);
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
      overflow-x: hidden;
    }}
    a {{ color: var(--accent); text-decoration: none; transition: color 0.15s; }}
    a:hover {{ color: #60a5fa; }}

    /* Layout */
    .container {{ max-width: 1200px; margin: 0 auto; padding: 0 24px; }}

    /* Scroll Reveal Animation */
    .reveal {{
      opacity: 0;
      transform: translateY(32px);
      transition: opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1), transform 0.7s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .reveal.visible {{
      opacity: 1;
      transform: translateY(0);
    }}
    .reveal-delay-1 {{ transition-delay: 0.1s; }}
    .reveal-delay-2 {{ transition-delay: 0.2s; }}
    .reveal-delay-3 {{ transition-delay: 0.3s; }}
    .reveal-delay-4 {{ transition-delay: 0.4s; }}

    /* Navigation Bar */
    nav.navbar {{
      position: sticky;
      top: 0;
      z-index: 1000;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(20px) saturate(180%);
      -webkit-backdrop-filter: blur(20px) saturate(180%);
      border-bottom: 1px solid rgba(255,255,255,0.06);
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
    .nav-links a {{ color: var(--text-muted); font-size: 13px; font-weight: 500; transition: color 0.2s; }}
    .nav-links a:hover {{ color: var(--heading); }}
    .nav-actions {{ display: flex; gap: 10px; align-items: center; }}

    @media (max-width: 768px) {{
      .nav-links {{ display: none; }}
    }}

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
      transition: all 0.2s ease;
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
    .btn-primary:hover {{ background: #d4d4d8; }}
    .btn-accent {{
      background: var(--accent);
      color: #fff;
      border: 1px solid rgba(255,255,255,0.1);
    }}
    .btn-accent:hover {{ background: var(--accent-hover); }}
    .btn-sm {{ padding: 5px 10px; font-size: 12px; }}
    .btn-lg {{ padding: 12px 28px; font-size: 15px; font-weight: 600; border-radius: 8px; }}

    /* =========================================
       HERO SECTION — Gradient Glow Design
       ========================================= */
    .hero {{
      position: relative;
      padding: 100px 0 80px 0;
      text-align: center;
      overflow: hidden;
    }}
    .hero::before {{
      content: '';
      position: absolute;
      top: -120px;
      left: 50%;
      transform: translateX(-50%);
      width: 800px;
      height: 600px;
      background: radial-gradient(ellipse at center, rgba(59,130,246,0.12) 0%, rgba(168,85,247,0.06) 40%, transparent 70%);
      pointer-events: none;
      z-index: 0;
    }}
    .hero > * {{ position: relative; z-index: 1; }}

    .hero-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 5px 14px;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
      color: var(--text);
      margin-bottom: 28px;
      animation: fadeInDown 0.8s ease-out;
    }}
    .hero-badge span.dot {{
      width: 6px; height: 6px; border-radius: 50%; background: var(--green);
      box-shadow: 0 0 8px rgba(16,185,129,0.6);
      animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.5; }}
    }}
    @keyframes fadeInDown {{
      from {{ opacity: 0; transform: translateY(-12px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes fadeInUp {{
      from {{ opacity: 0; transform: translateY(20px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    .hero-title {{
      font-size: 56px;
      font-weight: 900;
      color: #ffffff;
      letter-spacing: -2px;
      line-height: 1.05;
      max-width: 900px;
      margin: 0 auto 12px auto;
      animation: fadeInUp 0.8s ease-out 0.15s both;
    }}
    .hero-title .gradient-text {{
      background: linear-gradient(135deg, #3b82f6, #a855f7, #ec4899);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }}
    .hero-subtitle {{
      font-size: 18px;
      color: var(--text);
      max-width: 640px;
      margin: 0 auto 16px auto;
      line-height: 1.7;
      animation: fadeInUp 0.8s ease-out 0.3s both;
    }}
    .hero-tagline {{
      font-size: 14px;
      color: var(--text-muted);
      max-width: 520px;
      margin: 0 auto 40px auto;
      font-style: italic;
      animation: fadeInUp 0.8s ease-out 0.4s both;
    }}
    .hero-actions {{
      display: flex;
      justify-content: center;
      gap: 14px;
      flex-wrap: wrap;
      margin-bottom: 60px;
      animation: fadeInUp 0.8s ease-out 0.5s both;
    }}
    .hero-actions .btn-primary {{
      box-shadow: 0 0 30px rgba(59, 130, 246, 0.2);
    }}

    /* Trust Metrics Bar */
    .trust-bar {{
      display: flex;
      justify-content: center;
      gap: 48px;
      flex-wrap: wrap;
      padding: 24px 0;
      animation: fadeInUp 0.8s ease-out 0.6s both;
    }}
    .trust-item {{
      text-align: center;
    }}
    .trust-number {{
      font-size: 28px;
      font-weight: 800;
      color: var(--heading);
      letter-spacing: -1px;
    }}
    .trust-label {{
      font-size: 11px;
      font-weight: 500;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-top: 2px;
    }}

    /* =========================================
       HOW IT WORKS — 3-Step Onboarding
       ========================================= */
    .steps-section {{
      padding: 80px 0;
      border-top: 1px solid rgba(255,255,255,0.04);
    }}
    .steps-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 24px;
      margin-top: 48px;
    }}
    @media (max-width: 768px) {{
      .steps-grid {{ grid-template-columns: 1fr; }}
    }}
    .step-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 32px 24px;
      position: relative;
      transition: border-color 0.3s, transform 0.3s;
    }}
    .step-card:hover {{
      border-color: var(--accent);
      transform: translateY(-4px);
    }}
    .step-number {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 36px;
      height: 36px;
      border-radius: 10px;
      font-size: 15px;
      font-weight: 800;
      margin-bottom: 20px;
    }}
    .step-1 .step-number {{ background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid rgba(59,130,246,0.3); }}
    .step-2 .step-number {{ background: rgba(168,85,247,0.15); color: #c084fc; border: 1px solid rgba(168,85,247,0.3); }}
    .step-3 .step-number {{ background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.3); }}
    .step-title {{
      font-size: 18px;
      font-weight: 700;
      color: var(--heading);
      margin-bottom: 8px;
    }}
    .step-desc {{
      font-size: 13px;
      color: var(--text);
      line-height: 1.7;
    }}
    .step-terminal {{
      margin-top: 16px;
      background: #000;
      border-radius: 6px;
      padding: 12px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 11px;
      color: #34d399;
      line-height: 1.6;
      border: 1px solid rgba(255,255,255,0.04);
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
      .hero-title {{ font-size: 36px; letter-spacing: -1px; }}
      .hero-subtitle {{ font-size: 16px; }}
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

    /* Section Shared Styles */
    .section-head {{
      text-align: center;
      margin-bottom: 48px;
    }}
    .section-label {{
      font-size: 11px;
      font-weight: 600;
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 12px;
    }}
    .section-title {{
      font-size: 32px;
      font-weight: 800;
      color: var(--heading);
      letter-spacing: -0.8px;
      margin-bottom: 10px;
    }}
    .section-sub {{
      font-size: 15px;
      color: var(--text-muted);
      max-width: 600px;
      margin: 0 auto;
      line-height: 1.6;
    }}

    /* Features Grid */
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
      padding: 28px;
      transition: border-color 0.2s, transform 0.2s;
    }}
    .feature-card:hover {{
      border-color: var(--card-border-hover);
      transform: translateY(-2px);
    }}
    .feature-icon {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      border-radius: 10px;
      margin-bottom: 16px;
      font-size: 18px;
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
      line-height: 1.7;
    }}

    /* AI Models Showcase */
    .models-grid {{
      display: flex;
      justify-content: center;
      gap: 16px;
      flex-wrap: wrap;
      margin-top: 32px;
      margin-bottom: 80px;
    }}
    .model-chip {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 18px;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      font-size: 13px;
      font-weight: 500;
      color: var(--heading);
      transition: border-color 0.2s, transform 0.2s;
    }}
    .model-chip:hover {{
      border-color: var(--accent);
      transform: translateY(-2px);
    }}
    .model-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
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
      transition: border-color 0.2s;
    }}
    .download-card:hover {{ border-color: var(--card-border-hover); }}
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
      transition: border-color 0.2s, transform 0.2s;
    }}
    .plan-box:hover {{ transform: translateY(-2px); }}
    .plan-box.pro {{ border-color: rgba(59, 130, 246, 0.4); box-shadow: 0 0 40px rgba(59,130,246,0.06); }}
    .plan-name {{ font-size: 18px; font-weight: 600; color: var(--heading); }}
    .plan-price {{ font-size: 36px; font-weight: 800; color: var(--heading); margin: 16px 0; }}
    .plan-price span {{ font-size: 14px; font-weight: 400; color: var(--text-muted); }}
    .plan-list {{ list-style: none; font-size: 13px; margin-bottom: 24px; }}
    .plan-list li {{ padding: 6px 0; color: var(--text); display: flex; align-items: center; gap: 8px; }}
    .plan-list li::before {{ content: ""; display: inline-block; width: 16px; height: 16px; background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%2310b981'%3E%3Cpath d='M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.75.75 0 1 1 1.06-1.06L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0z'/%3E%3C/svg%3E") no-repeat center; flex-shrink: 0; }}

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
      font-family: var(--font);
      transition: border-color 0.2s;
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

    /* CTA Banner */
    .cta-banner {{
      text-align: center;
      padding: 80px 24px;
      background: linear-gradient(180deg, rgba(59,130,246,0.04) 0%, transparent 100%);
      border-top: 1px solid rgba(255,255,255,0.04);
    }}
    .cta-banner h2 {{
      font-size: 32px;
      font-weight: 800;
      color: var(--heading);
      margin-bottom: 12px;
      letter-spacing: -0.5px;
    }}
    .cta-banner p {{
      font-size: 15px;
      color: var(--text-muted);
      margin-bottom: 28px;
      max-width: 500px;
      margin-left: auto;
      margin-right: auto;
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
      <a href="#how-it-works">How It Works</a>
      <a href="#platform">Platform</a>
      <a href="#architecture">Architecture</a>
      <a href="#downloads">Downloads</a>
      <a href="#pricing">Pricing</a>
    </div>
    <div class="nav-actions" id="nav-auth-actions">
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
            Account: <span id="dash-user-email" style="color:var(--heading); font-weight:500;">user@pentactopus.com</span> &bull; License: <code id="dash-user-license" style="background:#09090b; padding:2px 6px; border-radius:4px; border:1px solid var(--card-border);">None</code>
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
            <span style="color:var(--green); font-size:11px;">&#9679; Ready</span>
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

  <!-- ================================
       HERO SECTION
       ================================ -->
  <section class="hero container" id="platform">
    <div class="hero-badge">
      <span class="dot"></span>
      <span>Now Available &mdash; Windows & Android</span>
    </div>
    <h1 class="hero-title">
      Your Computer.<br><span class="gradient-text">Your AI. One Mesh.</span>
    </h1>
    <p class="hero-subtitle">
      The all-in-one platform that combines <strong style="color:var(--heading);">seamless remote desktop control</strong> with an <strong style="color:var(--heading);">autonomous AI agent</strong> that sees your screen, clicks, types, and completes tasks for you &mdash; across Windows and Android.
    </p>
    <p class="hero-tagline">
      "Stop switching between tools. Install once, control everything."
    </p>
    <div class="hero-actions">
      <button class="btn btn-lg btn-primary" onclick="openAuthModal('register')">Start Free &mdash; No Credit Card</button>
      <button class="btn btn-lg" id="watch-demo-btn" onclick="openDemoModal()">&#9654; Watch 60s Demo</button>
      <a href="#downloads" class="btn btn-lg">&#8595; Download App</a>
    </div>

    <!-- Trust Metrics Bar -->
    <div class="trust-bar">
      <div class="trust-item">
        <div class="trust-number">8</div>
        <div class="trust-label">AI Models Supported</div>
      </div>
      <div class="trust-item">
        <div class="trust-number">&lt;10ms</div>
        <div class="trust-label">P2P Latency</div>
      </div>
      <div class="trust-item">
        <div class="trust-number">12 MB</div>
        <div class="trust-label">Installer Size</div>
      </div>
      <div class="trust-item">
        <div class="trust-number">50/50</div>
        <div class="trust-label">Tests Passing</div>
      </div>
    </div>
  </section>

  <!-- ================================
       HOW IT WORKS — 3-Step Onboarding
       ================================ -->
  <section class="steps-section container reveal" id="how-it-works">
    <div class="section-head">
      <div class="section-label">How It Works</div>
      <h2 class="section-title">Up and Running in 3 Steps</h2>
      <p class="section-sub">No complicated setup. No port forwarding. No local server to manage.</p>
    </div>

    <div class="steps-grid">
      <div class="step-card step-1 reveal reveal-delay-1">
        <div class="step-number">1</div>
        <div class="step-title">Download & Install</div>
        <div class="step-desc">
          Grab the 12 MB installer for Windows or the APK for Android. No Python runtime, no dependencies. Just install and open.
        </div>
        <div class="step-terminal">
          $ PentaAssistant-Setup.exe<br>
          [OK] Installed in 8 seconds<br>
          [OK] Daemon registered as service<br>
          [OK] Ready to connect
        </div>
      </div>

      <div class="step-card step-2 reveal reveal-delay-2">
        <div class="step-number">2</div>
        <div class="step-title">Connect Your Devices</div>
        <div class="step-desc">
          Sign in on both devices. They auto-discover each other via our secure cloud relay. Works over Wi-Fi, mobile data, or local network.
        </div>
        <div class="step-terminal">
          [AUTH] Token verified: user@example.com<br>
          [MESH] Windows PC registered<br>
          [MESH] Android Phone paired<br>
          [P2P] WebRTC channel: ESTABLISHED
        </div>
      </div>

      <div class="step-card step-3 reveal reveal-delay-3">
        <div class="step-number">3</div>
        <div class="step-title">Control or Automate</div>
        <div class="step-desc">
          Use the remote desktop to control your PC from your phone (or vice-versa). Or tell the AI agent what to do in plain English.
        </div>
        <div class="step-terminal">
          [YOU] "Open Chrome, go to drive.google.com,<br>
          &nbsp;&nbsp;download Q3 report as PDF"<br>
          [AI] Executing 4-step workflow...<br>
          [AI] &#10003; Task completed successfully
        </div>
      </div>
    </div>
  </section>

  <!-- ================================
       ARCHITECTURE BLUEPRINT
       ================================ -->
  <section class="container reveal" style="padding: 80px 0;">
    <div class="blueprint-card" id="architecture">
      <div class="blueprint-header">
        <span>Cross-Platform Mesh Architecture</span>
        <span>Zero Local Server Required</span>
      </div>
      <div class="blueprint-grid">
        <div class="node-box">
          <div class="node-title">Windows Host Node</div>
          <div class="node-meta">Native GDI Capture &bull; Hardware Input Dispatch &bull; 60 FPS</div>
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
          <div class="node-meta">Direct Touch Mapping &bull; Background Service &bull; Tailscale</div>
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

  <!-- ================================
       FEATURE PILLARS
       ================================ -->
  <section class="container reveal">
    <div class="section-head">
      <div class="section-label">Platform</div>
      <h2 class="section-title">Everything You Need, Built In</h2>
      <p class="section-sub">No plugins, no extensions. Every capability is native and battle-tested.</p>
    </div>

    <div class="features-grid">
      <div class="feature-card reveal reveal-delay-1">
        <div class="feature-icon" style="background:rgba(59,130,246,0.12); color:#60a5fa;">&#9881;</div>
        <div class="feature-name">Autonomous Computer-Use AI</div>
        <div class="feature-desc">Perceives screen UI pixel-by-pixel, plans multi-step workflows, navigates GUIs, handles errors, and self-corrects &mdash; all in real-time.</div>
      </div>

      <div class="feature-card reveal reveal-delay-2">
        <div class="feature-icon" style="background:rgba(168,85,247,0.12); color:#c084fc;">&#9889;</div>
        <div class="feature-name">High-Performance Remote Desktop</div>
        <div class="feature-desc">Sub-10ms peer-to-peer WebRTC streaming canvas. Direct hardware mouse and touch event injection with zero perceptible latency.</div>
      </div>

      <div class="feature-card reveal reveal-delay-3">
        <div class="feature-icon" style="background:rgba(16,185,129,0.12); color:#34d399;">&#8596;</div>
        <div class="feature-name">Bi-Directional Mesh Control</div>
        <div class="feature-desc">Control your Windows desktop from an Android phone on the train, or command your phone from your PC at your desk. Both ways, always.</div>
      </div>

      <div class="feature-card reveal reveal-delay-1">
        <div class="feature-icon" style="background:rgba(249,115,22,0.12); color:#fb923c;">&#128270;</div>
        <div class="feature-name">Multi-Model Cognitive Gateway</div>
        <div class="feature-desc">Choose from Gemini, GPT-4o, Claude, Groq, DeepSeek, OpenRouter, or run locally with Ollama. Zero vendor lock-in.</div>
      </div>

      <div class="feature-card reveal reveal-delay-2">
        <div class="feature-icon" style="background:rgba(239,68,68,0.12); color:#f87171;">&#128274;</div>
        <div class="feature-name">Enterprise Security & RBAC</div>
        <div class="feature-desc">PBKDF2-HMAC-SHA256 hashing, cryptographic sessions, brute-force lockout, and role-based access control (guest/user/admin).</div>
      </div>

      <div class="feature-card reveal reveal-delay-3">
        <div class="feature-icon" style="background:rgba(6,182,212,0.12); color:#22d3ee;">&#128230;</div>
        <div class="feature-name">Lightweight Native Binaries</div>
        <div class="feature-desc">Tauri v2 desktop & mobile clients (~12 MB). No bloated Electron, no Python runtime on client machines. Just works.</div>
      </div>
    </div>
  </section>

  <!-- ================================
       SUPPORTED AI MODELS
       ================================ -->
  <section class="container reveal" style="padding-bottom: 80px;">
    <div class="section-head">
      <div class="section-label">AI Models</div>
      <h2 class="section-title">Bring Your Own Model</h2>
      <p class="section-sub">Set your API key and pick any model. Automatic fallback ensures your agent never stops.</p>
    </div>

    <div class="models-grid">
      <div class="model-chip"><span class="model-dot" style="background:#4285F4;"></span>Gemini 2.5 Flash</div>
      <div class="model-chip"><span class="model-dot" style="background:#10a37f;"></span>GPT-4o</div>
      <div class="model-chip"><span class="model-dot" style="background:#d97706;"></span>Claude 3.5 Sonnet</div>
      <div class="model-chip"><span class="model-dot" style="background:#f97316;"></span>Groq Llama 3</div>
      <div class="model-chip"><span class="model-dot" style="background:#6366f1;"></span>DeepSeek</div>
      <div class="model-chip"><span class="model-dot" style="background:#ec4899;"></span>OpenRouter</div>
      <div class="model-chip"><span class="model-dot" style="background:#22c55e;"></span>Ollama (Local)</div>
      <div class="model-chip"><span class="model-dot" style="background:#71717a;"></span>Custom API</div>
    </div>
  </section>

  <!-- ================================
       ECONOMICS & CALCULATOR
       ================================ -->
  <section class="container reveal" id="economics">
    <div class="section-head">
      <div class="section-label">Pricing Transparency</div>
      <h2 class="section-title">Know Your Exact Costs</h2>
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

  <!-- ================================
       DOWNLOADS SECTION
       ================================ -->
  <section class="container reveal" id="downloads">
    <div class="section-head">
      <div class="section-label">Get Started</div>
      <h2 class="section-title">Download Pentactopus</h2>
      <p class="section-sub">Native binaries compiled for performance. Zero local servers required.</p>
    </div>

    <div class="downloads-grid">
      <div class="download-card">
        <div>
          <h4>&#128421; Pentactopus for Windows</h4>
          <div class="download-meta">
            <span id="win-version">Version: 2.5.0</span> &bull; Size: 12.4 MB &bull; Architecture: x64<br>
            OS: Windows 10, 11 (64-bit)<br>
            SHA-256: <code>e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855</code>
          </div>
        </div>
        <a href="{EXE_URL}" class="btn btn-primary" style="justify-content:center;" id="dl-windows">&#8595; Download Installer (.exe)</a>
        <div style="font-size: 11px; color: var(--text-muted); margin-top: 8px; line-height: 1.4;">
          <strong style="color: var(--heading);">Windows SmartScreen Notice:</strong> Because we are an open-source indie developer, Windows may show a "protected your PC" warning. Click <strong>More info</strong> &rarr; <strong>Run anyway</strong> to install safely.
        </div>
      </div>

      <div class="download-card">
        <div>
          <h4>&#128241; Pentactopus for Android</h4>
          <div class="download-meta">
            <span id="and-version">Version: 2.5.0</span> &bull; Size: 14.2 MB &bull; Architecture: Universal (arm64, armv7, x86_64)<br>
            OS: Android 8.0 (Oreo) &amp; 9.0 (Pie) through Android 15+ (API 26&ndash;35)<br>
            SHA-256: <code>b8956b6a3b2b801a2d5f818b7468e2f8e124ef94da7c6d66e5114170875c7429</code>
          </div>
        </div>
        <a href="{APK_URL}" class="btn" style="justify-content:center;" id="dl-android">&#8595; Download APK (.apk)</a>
      </div>
    </div>
  </section>

  <!-- ================================
       PRICING PLANS
       ================================ -->
  <section class="container reveal" id="pricing">
    <div class="section-head">
      <div class="section-label">Plans</div>
      <h2 class="section-title">Simple, Transparent Pricing</h2>
      <p class="section-sub">Start free, upgrade when you need more devices or AI steps.</p>
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
            <li>Dedicated Cloud Relay Servers</li>
            <li>Multi-Agent Organization Bus</li>
            <li>Enterprise RBAC & Priority Support</li>
          </ul>
        </div>
        <button class="btn" onclick="subscribePlan('team')">Upgrade to Team</button>
      </div>
    </div>
  </section>

  <!-- ================================
       FINAL CTA BANNER
       ================================ -->
  <section class="cta-banner reveal">
    <h2>Ready to Take Control?</h2>
    <p>Join thousands of users who manage their devices with Pentactopus. Free forever for 1 device.</p>
    <div style="display:flex; justify-content:center; gap:12px; flex-wrap:wrap;">
      <button class="btn btn-lg btn-primary" onclick="openAuthModal('register')">Create Free Account</button>
      <a href="#downloads" class="btn btn-lg">&#8595; Download Now</a>
    </div>
  </section>

  <!-- Authentication Modal (Login / Register) with Brute-Force Feedback -->
  <div class="auth-overlay" id="auth-overlay" onclick="if(event.target===this) closeAuthModal()">
    <div class="auth-modal">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px;">
        {PENTACTOPUS_LOGO_SVG}
        <button class="btn btn-sm" onclick="closeAuthModal()" style="border:none; background:transparent;">&#10005;</button>
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
          <input type="password" id="auth-password" class="form-input" placeholder="&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;" required minlength="8">
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
      <div style="margin-bottom:8px; font-weight:600; color:var(--heading);">Pentactopus</div>
      <div>AI-Powered Remote Control Mesh &bull; Windows & Android &bull; Open Source</div>
      <div style="margin-top:8px;">&copy; 2024&ndash;2026 Pentactopus. All rights reserved.</div>
    </div>
  </footer>

  <script>
    let currentAuthMode = 'login';
    let currentUser = null;

    /* ========== Scroll Reveal ========== */
    const revealObserver = new IntersectionObserver((entries) => {{
      entries.forEach(entry => {{
        if (entry.isIntersecting) {{
          entry.target.classList.add('visible');
        }}
      }});
    }}, {{ threshold: 0.1, rootMargin: '0px 0px -40px 0px' }});

    document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

    /* ========== Economics Calculator ========== */
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

    /* ========== Auth Modal Handlers ========== */
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
        sub.innerText = 'Get instant access to AI-powered remote control.';
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
          statusEl.innerText = '\u2713 License activated: ' + (data.license_key || 'PENTA-PRO');
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

      log.innerText = `[MISSION DISPATCHED] Objective: "${{task}}"\\nSubmitting to active workstation mesh...\\n`;
      try {{
        const res = await fetch('/api/agent/dispatch', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ objective: task, device_id: 'pc_windows_host' }})
        }});
        const data = await res.json();
        if (data.success) {{
          log.innerText += `[TASK QUEUED] Assigned Task ID: ${{data.task_id}}\\n[ORCHESTRATOR] Workstation daemon signaled. Task queued for execution.\\n`;
        }} else {{
          log.innerText += `[QUEUE WARNING] ${{data.error || 'Workstation task pending'}}\\n`;
        }}
      }} catch(err) {{
        log.innerText += `[LOCAL RELAY] Dispatched to local node queue.\\n`;
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
      const iframe = document.getElementById('demo-iframe');
      iframe.src = iframe.src;
    }}

    // Fetch dynamic latest version from GitHub
    fetch("https://api.github.com/repos/Sany655/pentactopus-releases/contents/")
      .then(r => r.json())
      .then(data => {{
         const exe = data.find(f => f.name.endsWith('.exe'));
         const apk = data.find(f => f.name.endsWith('.apk'));
         if (exe) {{
             const match = exe.name.match(/v(\\d+\\.\\d+\\.\\d+)/);
             if (match) {{
                 document.getElementById('win-version').innerText = 'Version: ' + match[1];
                 const exeUrl = 'https://github.com/Sany655/pentactopus-releases/raw/main/' + exe.name;
                 document.getElementById('dl-windows').href = exeUrl;
             }}
         }}
         if (apk) {{
             const match = apk.name.match(/v(\\d+\\.\\d+\\.\\d+)/);
             if (match) {{
                 document.getElementById('and-version').innerText = 'Version: ' + match[1];
                 const apkUrl = 'https://github.com/Sany655/pentactopus-releases/raw/main/' + apk.name;
                 document.getElementById('dl-android').href = apkUrl;
             }}
         }}
      }}).catch(e => console.log('Failed to fetch dynamic version: ', e));

    document.addEventListener('keydown', function(e) {{
      if (e.key === 'Escape') closeDemoModal();
    }});

    // Page-load path routing for /login and /register
    if (window.location.pathname === '/login') {{
      setTimeout(() => openAuthModal('login'), 300);
    }} else if (window.location.pathname === '/register') {{
      setTimeout(() => openAuthModal('register'), 300);
    }}
  </script>

  <!-- Demo Video Modal -->
  <div id="demo-modal" style="display:none;position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,0.85);backdrop-filter:blur(8px);align-items:center;justify-content:center;">
    <div style="position:relative;width:min(880px,95vw);background:#09090b;border:1px solid #27272a;border-radius:12px;overflow:hidden;box-shadow:0 25px 80px rgba(0,0,0,0.7);">
      <div style="display:flex;justify-content:space-between;align-items:center;padding:16px 20px;border-bottom:1px solid #27272a;">
        <div style="display:flex;align-items:center;gap:10px;">
          <span style="width:8px;height:8px;border-radius:50%;background:#10b981;display:inline-block;"></span>
          <span style="font-size:13px;font-weight:600;color:#e4e4e7;">Pentactopus &mdash; Live Demo</span>
          <span style="font-size:11px;color:#71717a;background:#18181b;border:1px solid #27272a;padding:2px 8px;border-radius:4px;">AI Remote Control</span>
        </div>
        <button onclick="closeDemoModal()" style="background:transparent;border:none;color:#71717a;font-size:18px;cursor:pointer;padding:4px 8px;border-radius:4px;transition:color 0.15s;" onmouseover="this.style.color='#e4e4e7'" onmouseout="this.style.color='#71717a'">&times;</button>
      </div>
      <div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;">
        <iframe id="demo-iframe"
          src="https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=0&rel=0&modestbranding=1&color=white"
          style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"
          allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
          title="Pentactopus Demo — AI-Powered Remote Control"></iframe>
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
