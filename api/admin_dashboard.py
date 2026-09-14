"""Admin Dashboard API & Management Console for Penta-Assistant.

Provides revenue telemetry, user role administration, subscriber analytics,
coupon code generation, and device mesh monitoring.
"""

import os
import json
import time
from typing import Dict, Any, List

from api.coupons import CouponManager
from api.user_store import UserStore
from hub.device_hub import DeviceHub

ADMIN_SECRET = os.getenv("ADMIN_SECRET_KEY", "penta_admin_secret_2026")

class AdminDashboard:
    @classmethod
    def verify_auth(cls, auth_header_or_key: str) -> bool:
        if not auth_header_or_key:
            return False
        cleaned = auth_header_or_key.replace("Bearer ", "").strip()
        return cleaned == ADMIN_SECRET

    @classmethod
    def get_overview_metrics(cls) -> Dict[str, Any]:
        """Aggregate high-level business, user, and operational metrics."""
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

        # Build User Table Rows
        user_rows = ""
        for u in users:
            role = u.get("role", "free_user")
            if role == "admin":
                role_badge = '<span style="background:rgba(163,113,247,0.2); color:#d2a8ff; border:1px solid #a371f7; padding:2px 8px; border-radius:12px; font-weight:600; font-size:11px;">🛡️ ADMIN</span>'
            elif role == "subscriber":
                role_badge = '<span style="background:rgba(46,160,67,0.2); color:#7ee787; border:1px solid #3fb950; padding:2px 8px; border-radius:12px; font-weight:600; font-size:11px;">⭐ PRO SUBSCRIBER</span>'
            else:
                role_badge = '<span style="background:rgba(110,118,129,0.2); color:#8b949e; border:1px solid #6e7681; padding:2px 8px; border-radius:12px; font-size:11px;">FREE USER</span>'

            email = u.get("email", "")
            plan = u.get("plan", "free").upper()
            lic = u.get("license_key") or '<span style="color:#8b949e;">None</span>'

            # Action Buttons
            actions = []
            if role != "admin":
                actions.append(f'<button class="btn btn-sm btn-accent" onclick="setUserRole(\'{email}\', \'admin\', \'enterprise\')">Make Admin</button>')
            else:
                if email != "admin@pentactopus.com":
                    actions.append(f'<button class="btn btn-sm" onclick="setUserRole(\'{email}\', \'subscriber\', \'pro\')">Demote to Pro</button>')

            if role != "subscriber":
                actions.append(f'<button class="btn btn-sm btn-success" onclick="setUserRole(\'{email}\', \'subscriber\', \'pro\')">Grant 1-Yr Pro</button>')
            else:
                actions.append(f'<button class="btn btn-sm btn-danger" onclick="setUserRole(\'{email}\', \'free_user\', \'free\')">Reset to Free</button>')

            user_rows += f"""
            <tr>
              <td>
                <div style="font-weight:600; color:#f0f6fc;">{u.get('name', 'User')}</div>
                <div style="font-size:12px; color:#8b949e;">{email}</div>
              </td>
              <td>{role_badge}</td>
              <td><span style="color:#58a6ff; font-weight:600;">{plan}</span></td>
              <td><code style="font-size:11px; background:#0d1117; padding:2px 6px; border-radius:4px; border:1px solid #30363d;">{lic}</code></td>
              <td style="display:flex; gap:6px; flex-wrap:wrap; padding-top:14px;">
                {' '.join(actions)}
              </td>
            </tr>
            """

        # Build Coupon Table Rows
        coupon_rows = ""
        for c in coupons:
            status_badge = '<span style="color:#7ee787; font-weight:600;">● Active</span>' if c.get("enabled") else '<span style="color:#f85149; font-weight:600;">○ Disabled</span>'
            btn_action = 'Disable' if c.get("enabled") else 'Enable'
            btn_class = 'btn-danger' if c.get("enabled") else 'btn-success'
            coupon_rows += f"""
            <tr>
              <td><strong style="color:#f0f6fc; font-family:monospace; font-size:14px;">{c.get('code')}</strong></td>
              <td>{c.get('discount_type').replace('_', ' ').title()}</td>
              <td><span style="color:#58a6ff; font-weight:600;">{c.get('value')}{'%' if c.get('discount_type') == 'percent' else ' Days' if c.get('discount_type') == 'free_trial' else ' USD'}</span></td>
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
              <td><span style="text-transform:uppercase; font-size:11px; color:#58a6ff;">{d.get('platform')}</span></td>
              <td><code style="font-size:11px;">{d.get('device_id')}</code></td>
              <td>{d.get('connection_type')}</td>
              <td><span style="color:#7ee787; font-weight:600;">● Online</span></td>
            </tr>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Penta-Assistant Admin Management Portal</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    :root {{
      --bg: #090d16;
      --card-bg: rgba(22, 27, 34, 0.85);
      --border: #30363d;
      --text: #c9d1d9;
      --heading: #f0f6fc;
      --accent: #58a6ff;
      --purple: #bc8cff;
      --green: #3fb950;
      --red: #f85149;
    }}
    body {{
      background: radial-gradient(circle at 10% 20%, #111927 0%, var(--bg) 90%);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      padding: 24px;
      margin: 0;
      min-height: 100vh;
    }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      padding-bottom: 18px;
      margin-bottom: 24px;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .brand {{ display: flex; align-items: center; gap: 12px; }}
    .brand h1 {{ color: var(--heading); font-size: 22px; margin: 0; display: flex; align-items: center; gap: 8px; }}
    .badge-admin {{ background: linear-gradient(135deg, #8957e5, #bc8cff); color: #fff; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }}
    .nav-links {{ display: flex; align-items: center; gap: 14px; font-size: 13px; }}
    .nav-links a {{ color: var(--accent); text-decoration: none; font-weight: 500; transition: 0.2s; }}
    .nav-links a:hover {{ text-decoration: underline; color: #79c0ff; }}
    
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 28px; }}
    .stat-card {{
      background: var(--card-bg);
      backdrop-filter: blur(10px);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 18px;
      position: relative;
      overflow: hidden;
    }}
    .stat-card::before {{
      content: '';
      position: absolute;
      top: 0; left: 0; width: 4px; height: 100%;
      background: var(--accent);
    }}
    .stat-card.purple::before {{ background: var(--purple); }}
    .stat-card.green::before {{ background: var(--green); }}
    .stat-val {{ font-size: 28px; font-weight: 800; color: var(--heading); margin-top: 6px; }}
    .stat-lbl {{ font-size: 12px; color: #8b949e; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }}
    
    .card {{
      background: var(--card-bg);
      backdrop-filter: blur(10px);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 22px;
      margin-bottom: 28px;
    }}
    .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 1px solid var(--border); padding-bottom: 12px; }}
    .card-header h2 {{ color: var(--heading); font-size: 17px; margin: 0; display: flex; align-items: center; gap: 8px; }}
    
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid var(--border); vertical-align: middle; }}
    th {{ color: #8b949e; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; }}
    tbody tr:hover {{ background: rgba(255,255,255,0.02); }}
    
    .btn {{
      background: #21262d;
      border: 1px solid var(--border);
      color: var(--heading);
      padding: 7px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 12px;
      font-weight: 600;
      transition: 0.15s;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .btn:hover {{ background: #30363d; border-color: #8b949e; }}
    .btn-primary {{ background: #238636; border-color: rgba(240,246,252,0.1); color: #fff; }}
    .btn-primary:hover {{ background: #2ea043; }}
    .btn-accent {{ background: #1f6feb; border: none; color: #fff; }}
    .btn-accent:hover {{ background: #388bfd; }}
    .btn-success {{ background: #238636; border: none; color: #fff; }}
    .btn-success:hover {{ background: #2ea043; }}
    .btn-danger {{ background: #da3633; border: none; color: #fff; }}
    .btn-danger:hover {{ background: #f85149; }}
    .btn-sm {{ padding: 4px 10px; font-size: 11px; }}
    
    input, select {{
      background: #0d1117;
      border: 1px solid var(--border);
      color: var(--heading);
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 13px;
    }}
    input:focus, select:focus {{ outline: none; border-color: var(--accent); }}
    .form-row {{ display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="brand">
        <h1>⚡ Penta-Assistant</h1>
        <span class="badge-admin">Admin Control Room</span>
      </div>
      <div class="nav-links">
        <a href="/">🌐 Public Landing Page</a>
        <span>•</span>
        <a href="/dashboard">💻 User Dashboard View</a>
        <span>•</span>
        <span style="color: #7ee787;">● Admin Authenticated</span>
      </div>
    </header>

    <!-- KPI Metric Cards -->
    <div class="grid">
      <div class="stat-card green">
        <div class="stat-lbl">Monthly Recurring Revenue</div>
        <div class="stat-val" style="color: #7ee787;">${metrics['mrr_usd']}</div>
      </div>
      <div class="stat-card purple">
        <div class="stat-lbl">Total Registered Users</div>
        <div class="stat-val">{metrics['total_users']}</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Pro Subscribers</div>
        <div class="stat-val" style="color: #58a6ff;">{metrics['subscribers_count']}</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Coupons Redeemed</div>
        <div class="stat-val">{metrics['total_coupon_redemptions']}</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Online Device Mesh Nodes</div>
        <div class="stat-val">{metrics['active_devices_count']}</div>
      </div>
    </div>

    <!-- 1. User Role & Subscription Management -->
    <div class="card">
      <div class="card-header">
        <h2>👥 User Accounts & Roles (RBAC)</h2>
        <span style="font-size: 12px; color: #8b949e;">Manage user roles, subscriptions, and license allocations</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>User</th>
            <th>Role</th>
            <th>Plan Tier</th>
            <th>License Key</th>
            <th>Role & Access Actions</th>
          </tr>
        </thead>
        <tbody>
          {user_rows}
        </tbody>
      </table>
    </div>

    <!-- 2. Coupons & Promo Code Engine -->
    <div class="card">
      <div class="card-header">
        <h2>🎟️ Coupons & Promo Engine</h2>
        <span style="font-size: 12px; color: #8b949e;">Create, toggle, and audit redemption limits</span>
      </div>
      
      <div style="background: #0d1117; padding: 16px; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 20px;">
        <h3 style="font-size: 13px; color: var(--heading); margin-top:0; margin-bottom: 10px;">➕ Create New Promo / Coupon Code</h3>
        <div class="form-row">
          <div>
            <label style="display:block; font-size:11px; color:#8b949e; margin-bottom:4px;">CODE</label>
            <input type="text" id="cp-code" placeholder="e.g. SUMMER2026" style="text-transform:uppercase;">
          </div>
          <div>
            <label style="display:block; font-size:11px; color:#8b949e; margin-bottom:4px;">DISCOUNT TYPE</label>
            <select id="cp-type">
              <option value="free_trial">Free Trial (Days)</option>
              <option value="percent">Percentage Off (%)</option>
              <option value="fixed">Fixed Dollar Off ($)</option>
            </select>
          </div>
          <div>
            <label style="display:block; font-size:11px; color:#8b949e; margin-bottom:4px;">VALUE</label>
            <input type="number" id="cp-val" value="365" style="width: 100px;">
          </div>
          <div>
            <label style="display:block; font-size:11px; color:#8b949e; margin-bottom:4px;">MAX USES</label>
            <input type="number" id="cp-max" value="500" style="width: 100px;">
          </div>
          <div>
            <button class="btn btn-primary" onclick="createCoupon()">Create Promo Code</button>
          </div>
        </div>
      </div>

      <table>
        <thead>
          <tr>
            <th>Coupon Code</th>
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

    <!-- 3. Connected Device Mesh Table -->
    <div class="card">
      <div class="card-header">
        <h2>🌐 Global Device Mesh Nodes</h2>
        <span style="font-size: 12px; color: #8b949e;">Live telemetry of paired Windows and Android endpoints</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Device Name</th>
            <th>Platform</th>
            <th>Device ID</th>
            <th>Connection</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {device_rows if device_rows.strip() else '<tr><td colspan="5" style="text-align:center; color:#8b949e; padding:18px;">No active devices registered in this serverless session. Native clients connect on-demand.</td></tr>'}
        </tbody>
      </table>
    </div>
  </div>

  <script>
    async function setUserRole(email, role, plan) {{
      if (!confirm('Are you sure you want to change role for ' + email + ' to ' + role + ' (' + plan + ')?')) return;

      const res = await fetch('/api/admin/user/role', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ email: email, role: role, plan: plan }})
      }});
      const data = await res.json();
      if (data.success) {{
        alert(`Successfully updated ${email} to ${role}!`);
        window.location.reload();
      }} else {{
        alert('Error: ' + (data.error || 'Failed to update user role'));
      }}
    }}

    async function createCoupon() {{
      const code = document.getElementById('cp-code').value.trim();
      const type = document.getElementById('cp-type').value;
      const val = parseFloat(document.getElementById('cp-val').value) || 100;
      const max = parseInt(document.getElementById('cp-max').value) || 100;

      if (!code) {{ alert('Please enter a coupon code.'); return; }}

      const res = await fetch('/api/admin/coupons/create', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ code: code, discount_type: type, value: val, max_uses: max }})
      }});
      const data = await res.json();
      if (data.success) {{
        alert('Coupon ' + code + ' created successfully!');
        window.location.reload();
      }} else {{
        alert('Error: ' + data.error);
      }}
    }}

    async function toggleCoupon(code, enable) {{
      const res = await fetch('/api/admin/coupons/toggle', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ code: code, enabled: enable }})
      }});
      const data = await res.json();
      if (data.success) {{
        window.location.reload();
      }}
    }}
  </script>
</body>
</html>
"""
