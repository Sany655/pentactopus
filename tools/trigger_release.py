"""Automated Release Trigger & Monitor for Pentactopus.

1. Reads the latest version from penta-app/src-tauri/tauri.conf.json
2. Tags the release or dispatches GitHub Actions workflow
3. Proactively launches background monitoring loop
"""

import os
import sys
import json
import subprocess
import urllib.request
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAURI_CONF = os.path.join(BASE_DIR, "penta-app", "src-tauri", "tauri.conf.json")

def get_current_version():
    with open(TAURI_CONF, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("version", "2.7.2")

def get_github_token():
    try:
        p = subprocess.run(["cmd.exe", "/c", "echo protocol=https&echo host=github.com&echo."], capture_output=True, text=True)
        p2 = subprocess.run(["git", "credential", "fill"], input=p.stdout, capture_output=True, text=True)
        for line in p2.stdout.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return None

def trigger_release(version=None):
    if not version:
        version = get_current_version()
    tag = f"v{version}"
    print(f"=== Triggering Release: {tag} ===")

    # 1. Check git status
    st = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if st.stdout.strip():
        print("Note: Working directory has changes, committing or stash recommended.")

    # 2. Push git tag to origin
    print(f"--> Creating & pushing tag {tag}...")
    subprocess.run(["git", "tag", "-f", tag], check=True)
    subprocess.run(["git", "push", "origin", tag, "-f"], check=True)
    print(f"--> Tag {tag} pushed to GitHub successfully.")

    # 3. Launch automated monitoring
    monitor_script = os.path.join(BASE_DIR, "scripts", "monitor_ci.ps1")
    if os.path.exists(monitor_script):
        print(f"--> Launching automated background CI monitor for {tag}...")
        proc = subprocess.Popen(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", monitor_script, "-Tag", tag],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        print(f"--> CI Monitor PID: {proc.pid}")
    return tag

if __name__ == "__main__":
    v = sys.argv[1] if len(sys.argv) > 1 else None
    trigger_release(v)
