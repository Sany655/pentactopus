"""Cloudflare Tunnel Manager for Remote Cross-Device Access.

Allows accessing the AI Command Hub (localhost:5050) from any mobile device,
tablet, or PC anywhere in the world over 4G/5G cellular data or remote Wi-Fi.
Zero router port forwarding required. End-to-end encrypted HTTPS.
"""

import subprocess
import shutil
import os
import sys
import re
import time
import urllib.request
import threading
from typing import Optional, Dict, Any

CLOUDFLARED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools", "bin")
os.makedirs(CLOUDFLARED_DIR, exist_ok=True)
CLOUDFLARED_EXE = os.path.join(CLOUDFLARED_DIR, "cloudflared.exe")

class CloudTunnelManager:
    _process = None
    _public_url = None
    _is_running = False

    @classmethod
    def locate_or_download_binary(cls, auto_download: bool = False) -> Optional[str]:
        # 1. System PATH
        which = shutil.which("cloudflared")
        if which:
            return which
        if os.path.isfile(CLOUDFLARED_EXE):
            return CLOUDFLARED_EXE

        if auto_download:
            print("[CLOUDFLARED] Downloading portable cloudflared for Windows...")
            dl_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
            try:
                urllib.request.urlretrieve(dl_url, CLOUDFLARED_EXE)
                print(f"[CLOUDFLARED] Downloaded successfully to {CLOUDFLARED_EXE}")
                return CLOUDFLARED_EXE
            except Exception as e:
                print(f"[CLOUDFLARED] Download error: {e}")
        return None

    @classmethod
    def start_tunnel(cls, local_port: int = 5050, auto_download: bool = True) -> Dict[str, Any]:
        if cls._is_running and cls._public_url:
            return {
                "running": True,
                "url": cls._public_url,
                "message": "Tunnel is already running."
            }

        binary = cls.locate_or_download_binary(auto_download=auto_download)
        if not binary:
            return {
                "running": False,
                "url": None,
                "error": "cloudflared binary not found. Install via 'winget install Cloudflare.cloudflared' or allow auto-download."
            }

        cmd = [binary, "tunnel", "--url", f"http://localhost:{local_port}", "--no-autoupdate"]
        
        try:
            cls._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1
            )
            cls._is_running = True

            # Read log stream to find trycloudflare.com URL
            start_time = time.time()
            found_url = None

            for line in cls._process.stdout:
                m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
                if m:
                    found_url = m.group(0)
                    cls._public_url = found_url
                    break
                if time.time() - start_time > 15:
                    break

            if found_url:
                return {
                    "running": True,
                    "url": found_url,
                    "message": f"Tunnel live at {found_url}"
                }
            else:
                return {
                    "running": cls._is_running,
                    "url": cls._public_url,
                    "message": "Tunnel launched. Detecting public URL..."
                }

        except Exception as e:
            cls._is_running = False
            return {"running": False, "error": str(e)}

    @classmethod
    def stop_tunnel(cls):
        if cls._process:
            try:
                cls._process.terminate()
            except Exception:
                pass
        cls._process = None
        cls._public_url = None
        cls._is_running = False

    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        return {
            "running": cls._is_running and bool(cls._public_url),
            "url": cls._public_url
        }

if __name__ == "__main__":
    print("=" * 60)
    print("       CLOUDFLARE PUBLIC HTTPS TUNNEL LAUNCHER        ")
    print("=" * 60)
    res = CloudTunnelManager.start_tunnel()
    print(res)
    if res.get("url"):
        print(f"\n>>> ACCESS YOUR HUB REMOTELY ON PHONE: {res['url']} <<<\n")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            CloudTunnelManager.stop_tunnel()
            print("Tunnel closed.")
