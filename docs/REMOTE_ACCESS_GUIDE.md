# Cross-Device & Cloud Remote Access Guide

This guide explains how to control and monitor your Android devices from anywhere in the world — over **4G/5G mobile cellular data**, across different Wi-Fi networks, or when your Command Hub is hosted in the cloud.

---

## The Core Challenge: Why Local Wi-Fi Stops Outside the House

- **Standard ADB Wi-Fi (`192.168.0.100:5555`)**: Only functions when both your PC and phone are connected to the exact same Wi-Fi router on your home local subnet.
- **When phone switches to 4G/5G Cellular Data**: Cellular network providers assign private IPs behind **Carrier-Grade NAT (CGNAT)** and block incoming connection requests to port 5555. Direct `adb connect <cellular-ip>` will fail.

---

## Solution 1: Global Cable-Free Mesh with Tailscale (Recommended)

**Tailscale** provides a zero-config, encrypted peer-to-peer WireGuard mesh. It gives your PC and Android phone a permanent virtual IP in the `100.x.y.z` range that connects anywhere in the world.

### Step 1: Install Tailscale on PC & Android Phone
1. **PC (Windows)**: Download and install from [tailscale.com](https://tailscale.com) or run:
   ```powershell
   winget install Tailscale.Tailscale
   ```
2. **Android Phone**: Install the free **Tailscale** app from the Google Play Store.
3. Sign in with the same account (Google/GitHub/Microsoft) on both devices.

### Step 2: Enable ADB over Wireless Once
While plugged in via USB on your PC (or with phone Wi-Fi debugging active):
1. In the Command Hub UI, click **Switch to Wi-Fi** or run:
   ```bash
   adb tcpip 5555
   ```
2. Unplug the USB cable.

### Step 3: Connect via Tailscale Virtual IP
1. Open the Tailscale app on your phone and look at the assigned IP (e.g. `100.85.12.34`).
2. In the Command Hub UI, enter this IP in the **Connect to Phone via Wi-Fi IP** box (e.g. `100.85.12.34`) and click **Connect**.
3. **Done!** Even if your phone is 50 miles away on 4G LTE or 5G, ADB and scrcpy screen mirroring will connect seamlessly through the encrypted WireGuard tunnel!

---

## Solution 2: Accessing Command Hub Web UI from Phone Anywhere (Cloudflare Tunnel)

To view the dashboard and trigger AI missions directly from your phone's mobile browser while away from your PC:

1. **Launch Cloudflare Tunnel**:
   Run from the project root:
   ```bash
   python tools/cloud_tunnel.py
   ```
   Or click **Start Cloudflare Public Tunnel** in the Command Hub UI.
2. A secure public HTTPS URL will be generated:
   ```
   https://random-phrase-abc.trycloudflare.com
   ```
3. Open this link in Chrome/Safari on your mobile phone on 4G/5G.
4. You now have complete access to the Command Hub, live screen preview, multi-agent missions, and model controls from anywhere in the world!

---

## Solution 3: Outbound Mobile Companion Relay (Termux / Tasker)

If you cannot run Tailscale on the phone or need battery/status monitoring without ADB:

1. On your phone, install **Termux** from F-Droid.
2. Run the companion relay script:
   ```bash
   pkg install python -y
   python companion_relay.py https://your-tunnel.trycloudflare.com
   ```
3. The phone will continuously push battery and network telemetry outbound to your Command Hub.
