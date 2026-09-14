"""Admin Dashboard & Governance Console for Pentatopus.

Provides telemetry, user RBAC administration, promo code management,
and device mesh monitoring with session-based and secret-based authorization.
"""

import os
import json
import time
from typing import Dict, Any, List

from api.coupons import CouponManager
from api.user_store import UserStore
from hub.device_hub import DeviceHub

ADMIN_SECRET = os.getenv("ADMIN_SECRET_KEY", "penta_admin_secret_2026")

PENTATOPUS_LOGO_SVG = """<svg width="24" height="24" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="16" cy="16" r="5" fill="#3b82f6" stroke="#60a5fa" stroke-width="1.5"/>
  <circle cx="16" cy="5" r="2.5" fill="#94a3b8"/>
  <circle cx="26" cy="12" r="2.5" fill="#94a3b8"/>
  <circle cx="22" cy="25" r="2.5" fill="#94a3b8"/>
  <circle cx="10" cy="25" r="2.5" fill="#94a3b8"/>
  <circle cx="6" cy="12" r="2.5" fill="#94a3b8"/>
  <path d="M16 11V7.5M20 13.5L23.5 13M18.5 19.5L20.5 23M13.5 19.5L11.5 23M12 13.5L8.5 13" stroke="#475569" stroke-width="1.5" stroke-linecap="round"/>
</svg>"""

class AdminDashboard:
    @classmethod
    def verify_auth(cls, auth_header_or_key: str) -> bool:
        if not auth_header_or_key:
            return False
        cleaned = auth_header_or_key.replace("Bearer ", "").strip()
        if cleaned == ADMIN_SECRET:
            return True
        user = UserStore.validate_session(cleaned)
        if user and user.get("role") == "admin":
            return True
        return False

    @classmethod
    def get_overview_metrics(cls) -> Dict[str, Any]:
        """Aggregate business, user, and operational telemetry."""
        licenses = CouponManager._load_licenses()
        coupons = CouponManager._load_coupons()
        users = UserStore.list_users()
        active_devices = DeviceHub.get_active_devices()

        total_users = len(users)
        subscribers = [u for u in users if u.get("role") == "subscriber"]
        admins = [u for u in users if u.get("role") == "admin"]
        free_users = [u for u in users if u.get("role") == "free_user"]

        paid_subscribers = sum(1 for lic in licenses.values() if lic.get("redeemed_via") == "stripe_checkout")
        total_subscribers = len(subscribers) + paid_subscribers
        mrr = total_subscribers * 12.0
        total_coupon_redemptions = sum(c.get("current_uses", 0) for c in coupons.values())

        return {
            "total_users": total_users,
            "total_subscribers": total_subscribers,
            "subscribers_count": len(subscribers),
            "admins_count": len(admins),
            "free_users_count": len(free_users),
            "paid_subscribers": paid_subscribers,
            "mrr_usd": round(mrr, 2),
            "total_coupons": len(coupons),
            "total_coupon_redemptions": total_coupon_redemptions,
            "active_devices_count": len(active_devices),
            "active_devices": active_devices
        }

    @classmethod
    def render_admin_html(cls) -> str:
        metrics = cls.get_overview_metrics()
        coupons = CouponManager.list_coupons()
        users = UserStore.list_users()

        # Build User Rows
        user_rows = ""
        for u in users:
            role = u.get("role", "free_user")
            if role == "admin":
                role_badge = '<span style="background:rgba(168,85,247,0.15); color:#c084fc; border:1px solid rgba(168,85,247,0.3); padding:2px 8px; border-radius:12px; font-weight:600; font-size:11px;">ADMIN</span>'
            elif role == "subscriber":
                role_badge = '<span style="background:rgba(16,185,129,0.15); color:#34d399; border:1px solid rgba(16,185,129,0.3); padding:2px 8px; border-radius:12px; font-weight:600; font-size:11px;">PRO SUBSCRIBER</span>'
            else:
                role_badge = '<span style="background:rgba(113,113,122,0.15); color:#a1a1aa; border:1px solid rgba(113,113,122,0.3); padding:2px 8px; border-radius:12px; font-size:11px;">FREE</span>'

            email = u.get("email", "")
            plan = u.get("plan", "free").upper()
            lic = u.get("license_key") or '<span style="color:#71717a;">None</span>'

            actions = []
            if role != "admin":
                actions.append(f'<button class="btn btn-sm btn-accent" onclick="setUserRole(\'{email}\', \'admin\', \'enterprise\')">Make Admin</button>')
            else:
                if email != "admin@pentatopus.com":
                    actions.append(f'<button class="btn btn-sm" onclick="setUserRole(\'{email}\', \'subscriber\', \'pro\')">Demote</button>')

            if role != "subscriber":
                actions.append(f'<button class="btn btn-sm btn-success" onclick="setUserRole(\'{email}\', \'subscriber\', \'pro\')">Grant Pro</button>')
            else:
                actions.append(f'<button class="btn btn-sm btn-danger" onclick="setUserRole(\'{email}\', \'free_user\', \'free\')">Revoke Pro</button>')

            user_rows += f"""
            <tr>
              <td>
                <div style="font-weight:600; color:#f4f4f5;">{u.get('name', 'User')}</div>
                <div style="font-size:12px; color:#71717a;">{email}</div>
              </td>
              <td>{role_badge}</td>
              <td><span style="color:#60a5fa; font-weight:600;">{plan}</span></td>
              <td><code style="font-size:11px; background:#09090b; padding:2px 6px; border-radius:4px; border:1px solid rgba(255,255,255,0.08);">{lic}</code></td>
              <td style="display:flex; gap:6px; flex-wrap:wrap; padding-top:14px;">
                {' '.join(actions)}
              </td>
            </tr>
            """

        # Build Coupon Rows
        coupon_rows = ""
        for c in coupons:
            status_badge = '<span style="color:#10b981; font-weight:600;">Active</span>' if c.get("enabled") else '<span style="color:#ef4444; font-weight:600;">Disabled</span>'
            btn_action = 'Disable' if c.get("enabled") else 'Enable'
            btn_class = 'btn-danger' if c.get("enabled") else 'btn-success'
            coupon_rows += f"""
            <tr>
              <td><strong style="color:#f4f4f5; font-family:monospace; font-size:13px;">{c.get('code')}</strong></td>
              <td>{c.get('discount_type').replace('_', ' ').title()}</td>
              <td><span style="color:#60a5fa; font-weight:600;">{c.get('value')}{'%' if c.get('discount_type') == 'percent' else ' Days' if c.get('discount_type') == 'free_trial' else ' USD'}</span></td>
              <td>{c.get('current_uses')} / {c.get('max_uses')}</td>
              <td>{status_badge}</td>
              <td>
                <button class="btn btn-sm {btn_class}" onclick="toggleCoupon('{c.get('code')}', {'false' if c.get('enabled') else 'true'})">{btn_action}</button>
              </td>
            </tr>
            """

        # Build Device Rows
        device_rows = ""
        for d in metrics["active_devices"]:
            device_rows += f"""
            <tr>
              <td><strong>{d.get('name')}</strong></td>
              <td><span style="text-transform:uppercase; font-size:11px; color:#60a5fa;">{d.get('platform')}</span></td>
              <td><code style="font-size:11px;">{d.get('device_id')}</code></td>
              <td>{d.get('connection_type')}</td>
              <td><span style="color:#10b981; font-weight:600;">Online</span></td>
            </tr>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Pentatopus | Admin Governance Console</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #09090b;
      --card-bg: #111114;
      --border: rgba(255, 255, 255, 0.08);
      --text: #a1a1aa;
      --heading: #f4f4f5;
      --accent: #3b82f6;
      --green: #10b981;
      --red: #ef4444;
      --font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: var(--font);
      padding: 24px;
      margin: 0;
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
    }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      padding-bottom: 16px;
      margin-bottom: 24px;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .brand {{ display: flex; align-items: center; gap: 10px; }}
    .brand h1 {{ color: var(--heading); font-size: 18px; margin: 0; font-weight: 700; }}
    .nav-links {{ display: flex; align-items: center; gap: 14px; font-size: 13px; }}
    .nav-links a {{ color: var(--text); text-decoration: none; font-weight: 500; }}
    .nav-links a:hover {{ color: var(--heading); }}
    
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
    .stat-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
    }}
    .stat-val {{ font-size: 24px; font-weight: 700; color: var(--heading); margin-top: 4px; }}
    .stat-lbl {{ font-size: 11px; color: #71717a; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }}
    
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 24px;
    }}
    .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; border-bottom: 1px solid var(--border); padding-bottom: 10px; }}
    .card-header h2 {{ color: var(--heading); font-size: 15px; margin: 0; font-weight: 600; }}
    
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--border); vertical-align: middle; }}
    th {{ color: #71717a; font-weight: 600; text-transform: uppercase; font-size: 11px; }}
    tbody tr:hover {{ background: rgba(255,255,255,0.02); }}
    
    .btn {{
      background: #18181b;
      border: 1px solid var(--border);
      color: var(--heading);
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 12px;
      font-weight: 500;
      transition: 0.15s;
    }}
    .btn:hover {{ background: #27272a; }}
    .btn-primary {{ background: var(--heading); color: #09090b; border: 1px solid #fff; font-weight: 600; }}
    .btn-primary:hover {{ background: #e4e4e7; }}
    .btn-accent {{ background: var(--accent); color: #fff; border: none; }}
    .btn-accent:hover {{ background: #2563eb; }}
    .btn-success {{ background: #059669; color: #fff; border: none; }}
    .btn-success:hover {{ background: #10b981; }}
    .btn-danger {{ background: #dc2626; color: #fff; border: none; }}
    .btn-danger:hover {{ background: #ef4444; }}
    .btn-sm {{ padding: 4px 8px; font-size: 11px; }}
    
    input, select {{
      background: #09090b;
      border: 1px solid var(--border);
      color: var(--heading);
      padding: 7px 10px;
      border-radius: 6px;
      font-size: 13px;
    }}
    input:focus, select:focus {{ outline: none; border-color: var(--accent); }}
    .form-row {{ display: flex; gap: 10px; flex-wrap: wrap; align-items: flex-end; }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="brand">
        {PENTATOPUS_LOGO_SVG}
        <h1>Pentatopus Governance Console</h1>
      </div>
      <div class="nav-links">
        <a href="/">Platform Home</a>
        <span>•</span>
        <a href="/dashboard">Workstation View</a>
        <span>•</span>
        <span style="color:var(--green); font-size:12px;">● Root Authorized</span>
      </div>
    </header>

    <!-- Metrics -->
    <div class="grid">
      <div class="stat-card">
        <div class="stat-lbl">Monthly Recurring Revenue</div>
        <div class="stat-val" style="color:var(--green);">${metrics['mrr_usd']}</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Registered Accounts</div>
        <div class="stat-val">{metrics['total_users']}</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Active Subscribers</div>
        <div class="stat-val" style="color:var(--accent);">{metrics['subscribers_count']}</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Coupons Redeemed</div>
        <div class="stat-val">{metrics['total_coupon_redemptions']}</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Online Mesh Nodes</div>
        <div class="stat-val">{metrics['active_devices_count']}</div>
      </div>
    </div>

    <!-- User Accounts & Roles (RBAC) -->
    <div class="card">
      <div class="card-header">
        <h2>User Accounts & Roles (RBAC)</h2>
        <span style="font-size:12px; color:#71717a;">Enforce role governance and grant subscription tiers</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>User</th>
            <th>Role</th>
            <th>Plan</th>
            <th>License Key</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {user_rows}
        </tbody>
      </table>
    </div>

    <!-- Promo Code Engine -->
    <div class="card">
      <div class="card-header">
        <h2>Promo & Coupon Engine</h2>
        <span style="font-size:12px; color:#71717a;">Manage authorized discount and trial codes</span>
      </div>
      
      <div style="background:#09090b; padding:14px; border-radius:6px; border:1px solid var(--border); margin-bottom:16px;">
        <div class="form-row">
          <div>
            <label style="display:block; font-size:11px; color:#71717a; margin-bottom:4px;">CODE</label>
            <input type="text" id="cp-code" placeholder="e.g. ENTERPRISE26" style="text-transform:uppercase;">
          </div>
          <div>
            <label style="display:block; font-size:11px; color:#71717a; margin-bottom:4px;">TYPE</label>
            <select id="cp-type">
              <option value="free_trial">Free Trial (Days)</option>
              <option value="percent">Percentage Off (%)</option>
              <option value="fixed">Fixed Dollar Off ($)</option>
            </select>
          </div>
          <div>
            <label style="display:block; font-size:11px; color:#71717a; margin-bottom:4px;">VALUE</label>
            <input type="number" id="cp-val" value="365" style="width:80px;">
          </div>
          <div>
            <label style="display:block; font-size:11px; color:#71717a; margin-bottom:4px;">MAX REDEMPTIONS</label>
            <input type="number" id="cp-max" value="500" style="width:80px;">
          </div>
          <div>
            <button class="btn btn-primary" onclick="createCoupon()">Create Code</button>
          </div>
        </div>
      </div>

      <table>
        <thead>
          <tr>
            <th>Code</th>
            <th>Type</th>
            <th>Value</th>
            <th>Uses</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {coupon_rows}
        </tbody>
      </table>
    </div>

    <!-- Global Mesh Table -->
    <div class="card">
      <div class="card-header">
        <h2>Active Device Mesh Nodes</h2>
        <span style="font-size:12px; color:#71717a;">Live hardware endpoints and cloud relays</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Device</th>
            <th>Platform</th>
            <th>Identifier</th>
            <th>Transport</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {device_rows if device_rows.strip() else '<tr><td colspan="5" style="text-align:center; color:#71717a; padding:16px;">No live devices connected in this serverless session. Native clients connect on-demand.</td></tr>'}
        </tbody>
      </table>
    </div>
  </div>

  <script>
    function getAuthHeader() {{
      const token = localStorage.getItem('penta_auth_token');
      return token ? ('Bearer ' + token) : 'Bearer penta_admin_secret_2026';
    }}

    async function setUserRole(email, role, plan) {{
      if (!confirm('Are you sure you want to update role for ' + email + ' to ' + role + ' (' + plan + ')?')) return;

      const res = await fetch('/api/admin/user/role', {{
        method: 'POST',
        headers: {{
          'Content-Type': 'application/json',
          'Authorization': getAuthHeader()
        }},
        body: JSON.stringify({{ email: email, role: role, plan: plan }})
      }});
      const data = await res.json();
      if (data.success) {{
        window.location.reload();
      }} else {{
        alert('Action rejected: ' + (data.error || 'Unauthorized'));
      }}
    }}

    async function createCoupon() {{
      const code = document.getElementById('cp-code').value.trim();
      const type = document.getElementById('cp-type').value;
      const val = parseFloat(document.getElementById('cp-val').value) || 100;
      const max = parseInt(document.getElementById('cp-max').value) || 100;

      if (!code) {{ alert('Please specify a code.'); return; }}

      const res = await fetch('/api/admin/coupons/create', {{
        method: 'POST',
        headers: {{
          'Content-Type': 'application/json',
          'Authorization': getAuthHeader()
        }},
        body: JSON.stringify({{ code: code, discount_type: type, value: val, max_uses: max }})
      }});
      const data = await res.json();
      if (data.success) {{
        window.location.reload();
      }} else {{
        alert('Action rejected: ' + (data.error || 'Failed'));
      }}
    }}

    async function toggleCoupon(code, enable) {{
      const res = await fetch('/api/admin/coupons/toggle', {{
        method: 'POST',
        headers: {{
          'Content-Type': 'application/json',
          'Authorization': getAuthHeader()
        }},
        body: JSON.stringify({{ code: code, enabled: enable }})
      }});
      const data = await res.json();
      if (data.success) {{
        window.location.reload();
      }} else {{
        alert('Action rejected: ' + (data.error || 'Failed'));
      }}
    }}
  </script>
</body>
</html>
"""
