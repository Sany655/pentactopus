"""Admin Dashboard API & Management Console for Penta-Assistant.

Provides revenue telemetry, subscriber analytics, coupon code generation,
and device mesh monitoring protected by ADMIN_SECRET_KEY.
"""

import os
import json
import time
from typing import Dict, Any, List

from api.coupons import CouponManager
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
        """Aggregate high-level business and operational metrics."""
        licenses = CouponManager._load_licenses()
        coupons = CouponManager._load_coupons()
        active_devices = DeviceHub.get_active_devices()

        total_subscribers = len(licenses)
        # Mock paid vs coupon
        paid_subscribers = sum(1 for lic in licenses.values() if lic.get("redeemed_via") == "stripe_checkout")
        mrr = paid_subscribers * 12.0
        total_coupon_redemptions = sum(c.get("current_uses", 0) for c in coupons.values())

        return {
            "total_subscribers": total_subscribers,
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

        coupon_rows = ""
        for c in coupons:
            status_badge = '<span style="color:#7ee787;">Active</span>' if c.get("enabled") else '<span style="color:#f85149;">Disabled</span>'
            btn_action = 'Disable' if c.get("enabled") else 'Enable'
            btn_class = 'btn-danger' if c.get("enabled") else 'btn-success'
            coupon_rows += f"""
            <tr>
              <td><strong>{c.get('code')}</strong></td>
              <td>{c.get('discount_type')}</td>
              <td>{c.get('value')}</td>
              <td>{c.get('current_uses')} / {c.get('max_uses')}</td>
              <td>{status_badge}</td>
              <td>
                <button class="btn btn-sm {btn_class}" onclick="toggleCoupon('{c.get('code')}', {'false' if c.get('enabled') else 'true'})">{btn_action}</button>
              </td>
            </tr>
            """

        device_rows = ""
        for d in metrics["active_devices"]:
            device_rows += f"""
            <tr>
              <td><strong>{d.get('name')}</strong></td>
              <td>{d.get('platform')}</td>
              <td>{d.get('device_id')}</td>
              <td>{d.get('connection_type')}</td>
              <td><span style="color:#7ee787;">Online</span></td>
            </tr>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Penta-Assistant Admin Management Console</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{ background: #0d1117; color: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 20px; }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    h1 {{ color: #f0f6fc; font-size: 22px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #30363d; padding-bottom: 12px; margin-bottom: 20px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }}
    .stat-card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px; }}
    .stat-val {{ font-size: 26px; font-weight: 700; color: #58a6ff; margin-top: 6px; }}
    .stat-lbl {{ font-size: 12px; color: #8b949e; text-transform: uppercase; font-weight: 600; }}
    .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 18px; margin-bottom: 24px; }}
    h2 {{ color: #f0f6fc; font-size: 16px; margin-bottom: 14px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }}
    th, td {{ padding: 10px; border-bottom: 1px solid #30363d; }}
    th {{ color: #8b949e; font-weight: 600; }}
    .btn {{ background: #21262d; border: 1px solid #30363d; color: #c9d1d9; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; }}
    .btn:hover {{ background: #30363d; }}
    .btn-primary {{ background: #238636; color: #fff; border: none; }}
    .btn-primary:hover {{ background: #2ea043; }}
    .btn-sm {{ padding: 3px 8px; font-size: 11px; }}
    .btn-danger {{ background: #da3633; color: #fff; border: none; }}
    .btn-success {{ background: #238636; color: #fff; border: none; }}
    input, select {{ background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; padding: 7px 10px; border-radius: 6px; font-size: 13px; }}
    .form-row {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 14px; align-items: flex-end; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>
      <span>🛡️ Penta-Assistant Admin Console</span>
      <span style="font-size: 12px; color: #8b949e;"><a href="/" style="color: #58a6ff; text-decoration: none;">← Return to Main Web Hub</a></span>
    </h1>

    <!-- KPI Metric Cards -->
    <div class="grid">
      <div class="stat-card">
        <div class="stat-lbl">Monthly Recurring Revenue</div>
        <div class="stat-val">${metrics['mrr_usd']}</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Total Active Subscribers</div>
        <div class="stat-val">{metrics['total_subscribers']}</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Coupon Redemptions</div>
        <div class="stat-val">{metrics['total_coupon_redemptions']}</div>
      </div>
      <div class="stat-card">
        <div class="stat-lbl">Online Device Nodes</div>
        <div class="stat-val">{metrics['active_devices_count']}</div>
      </div>
    </div>

    <!-- Create Coupon Form -->
    <div class="card">
      <h2>🎟️ Generate New Authorized Coupon Code</h2>
      <div class="form-row">
        <div>
          <label style="display:block; font-size:11px; margin-bottom:4px;">Coupon Code</label>
          <input type="text" id="cp-code" placeholder="e.g. VIP2026" style="text-transform: uppercase;">
        </div>
        <div>
          <label style="display:block; font-size:11px; margin-bottom:4px;">Type</label>
          <select id="cp-type">
            <option value="free_trial">100% Free Trial (Days)</option>
            <option value="percent">Percentage Discount (% Off)</option>
            <option value="fixed">Fixed Dollar Off ($)</option>
          </select>
        </div>
        <div>
          <label style="display:block; font-size:11px; margin-bottom:4px;">Value (Days / % / $)</label>
          <input type="number" id="cp-val" value="365" style="width: 90px;">
        </div>
        <div>
          <label style="display:block; font-size:11px; margin-bottom:4px;">Max Uses</label>
          <input type="number" id="cp-max" value="500" style="width: 80px;">
        </div>
        <div>
          <button class="btn btn-primary" onclick="createCoupon()">+ Create Coupon</button>
        </div>
      </div>
    </div>

    <!-- Coupons Table -->
    <div class="card">
      <h2>📋 Active Coupon Codes & Redemption Limits</h2>
      <table>
        <thead>
          <tr>
            <th>Code</th>
            <th>Type</th>
            <th>Value</th>
            <th>Uses / Limit</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {coupon_rows if coupon_rows.strip() else '<tr><td colspan="6" style="text-align:center;">No coupons found.</td></tr>'}
        </tbody>
      </table>
    </div>

    <!-- Connected Device Mesh Table -->
    <div class="card">
      <h2>🌐 Global Device Mesh Nodes</h2>
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
          {device_rows if device_rows.strip() else '<tr><td colspan="5" style="text-align:center;">No active devices detected right now.</td></tr>'}
        </tbody>
      </table>
    </div>
  </div>

  <script>
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
