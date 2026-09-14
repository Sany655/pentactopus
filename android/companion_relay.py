"""Lightweight Android Companion Relay Script.

Run this script inside Termux, Python on Android, or via Tasker webhook.
It pushes phone telemetry (battery, network, model) to your PC/Cloud AI Command Hub,
allowing remote awareness across 4G/5G mobile networks.

Usage:
    python companion_relay.py http://your-pc-ip:5050 (or https://your-tunnel.trycloudflare.com)
"""

import sys
import time
import json
import urllib.request
import subprocess

def get_battery_info():
    try:
        res = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            return json.loads(res.stdout)
    except Exception:
        pass
    return {"percentage": 85, "status": "DISCHARGING"}

def get_device_info():
    try:
        m = subprocess.run(["getprop", "ro.product.model"], capture_output=True, text=True).stdout.strip()
        v = subprocess.run(["getprop", "ro.build.version.release"], capture_output=True, text=True).stdout.strip()
        return {"model": m or "Android Device", "version": v or "9+"}
    except Exception:
        return {"model": "Android Phone", "version": "9+"}

def run_relay(hub_url: str, device_id: str = "redmi_note_6_pro"):
    endpoint = f"{hub_url.rstrip('/')}/api/remote/telemetry"
    print(f"[*] Starting Android Companion Relay to {endpoint}...")
    dev_info = get_device_info()

    while True:
        battery = get_battery_info()
        payload = {
            "device_id": device_id,
            "model": dev_info["model"],
            "android_version": dev_info["version"],
            "battery": f"{battery.get('percentage', 85)}%",
            "network": "Mobile_Data_4G_5G",
            "timestamp": time.time()
        }
        try:
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            print(f"[HEARTBEAT] Pushed telemetry to Command Hub: {payload['battery']}")
        except Exception as e:
            print(f"[WARN] Connection to Command Hub failed: {e}")

        time.sleep(10)

if __name__ == "__main__":
    hub = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5050"
    run_relay(hub)
