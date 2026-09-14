"""Wireless ADB Connection Helper for Android.

Enables Wi-Fi debugging so your phone can be controlled completely cable-free.
"""

import subprocess
import re
import sys
import time

def setup_wireless_adb():
    print("=" * 60)
    print("        SWITCHING ANDROID PHONE TO WIRELESS WI-FI MODE       ")
    print("=" * 60)

    # 1. Check if device is currently connected via USB
    res = subprocess.run(["adb", "devices", "-l"], capture_output=True, text=True)
    lines = [l.strip() for l in res.stdout.splitlines() if l.strip() and not l.startswith("List of")]

    usb_serial = None
    for l in lines:
        parts = l.split()
        if len(parts) >= 2 and parts[1] == "device" and ":" not in parts[0]:
            usb_serial = parts[0]
            break

    if not usb_serial:
        print("\n[ERROR] No USB-connected device detected. Please connect your phone via USB cable to enable wireless mode.")
        return False

    print(f"[FOUND] Detected USB device: {usb_serial}")

    # 2. Extract phone Wi-Fi IP address
    print("[1/3] Querying phone Wi-Fi IP address...")
    ip_res = subprocess.run(["adb", "-s", usb_serial, "shell", "ip", "route"], capture_output=True, text=True)
    phone_ip = None

    for line in ip_res.stdout.splitlines():
        if "src" in line and "wlan0" in line:
            parts = line.split()
            if "src" in parts:
                src_idx = parts.index("src")
                if src_idx + 1 < len(parts):
                    phone_ip = parts[src_idx + 1]
                    break

    if not phone_ip:
        ip_res2 = subprocess.run(["adb", "-s", usb_serial, "shell", "ip", "addr", "show", "wlan0"], capture_output=True, text=True)
        m = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", ip_res2.stdout)
        if m:
            phone_ip = m.group(1)

    if not phone_ip:
        print("[WARN] Could not automatically detect Wi-Fi IP.")
        print("Please check your phone: Settings > Wi-Fi > Tap connected network > IP Address.")
        return False

    print(f"[OK] Phone Wi-Fi IP address: {phone_ip}")

    # 3. Enable TCP/IP on port 5555
    print("[2/3] Switching ADB daemon to TCP/IP port 5555...")
    tcp_res = subprocess.run(["adb", "-s", usb_serial, "tcpip", "5555"], capture_output=True, text=True)
    print(f"ADB output: {tcp_res.stdout.strip()}")

    time.sleep(2)

    # 4. Connect over Wi-Fi
    print(f"[3/3] Connecting over Wi-Fi to {phone_ip}:5555...")
    conn_res = subprocess.run(["adb", "connect", f"{phone_ip}:5555"], capture_output=True, text=True)
    print(f"Connection result: {conn_res.stdout.strip()}")

    print("\n" + "=" * 60)
    if "connected" in conn_res.stdout.lower():
        print("SUCCESS! YOU CAN NOW UNPLUG THE USB CABLE!")
        print("Your phone is now connected wirelessly over Wi-Fi.")
        print("Both your AI Agent and scrcpy will work completely cable-free.")
    else:
        print(f"Note: Ensure both PC and phone are connected to the same Wi-Fi network.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    setup_wireless_adb()
