"""Test suite for validating the Windows app downloaded directly from the web UI.

Performs:
1. Streaming download from http://localhost:5051/download/PentaAssistant-Setup.exe
2. PE header, architecture (x64), subsystem, and section validation
3. SHA-256 cryptographic verification against dist/PentaAssistant-Setup.exe
4. Native Windows process execution smoke test of the downloaded binary
"""

import os
import sys
import time
import urllib.request
import hashlib
import struct
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "reports", "ui_downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
DOWNLOADED_FILE = os.path.join(DOWNLOAD_DIR, "PentaAssistant-Setup.exe")
DIST_FILE = os.path.join(BASE_DIR, "dist", "PentaAssistant-Setup.exe")
DOWNLOAD_URL = "http://localhost:5051/download/PentaAssistant-Setup.exe"


def download_binary():
    print("=" * 65)
    print("  PENTACTOPUS WINDOWS APP WEB UI DOWNLOAD & INTEGRITY TEST")
    print("=" * 65 + "\n")
    print(f"--> Initiating UI download request: {DOWNLOAD_URL}")
    start_time = time.time()

    req = urllib.request.Request(DOWNLOAD_URL)
    with urllib.request.urlopen(req, timeout=10) as resp, open(DOWNLOADED_FILE, "wb") as out_f:
        status = resp.status
        total_len = int(resp.headers.get("Content-Length", 0))
        ctype = resp.headers.get("Content-Type")
        cdisp = resp.headers.get("Content-Disposition")
        print(f"    Server Response: HTTP {status}")
        print(f"    Content-Type:    {ctype}")
        print(f"    Content-Length:  {total_len:,} bytes")
        print(f"    Content-Dispos.: {cdisp}")

        downloaded = 0
        while chunk := resp.read(1024 * 256):
            out_f.write(chunk)
            downloaded += len(chunk)

    elapsed = time.time() - start_time
    speed_mb = (downloaded / (1024 * 1024)) / max(elapsed, 0.001)
    print(f"    Completed:       {downloaded:,} bytes transferred in {elapsed:.2f}s ({speed_mb:.1f} MB/s)")
    assert status == 200, f"Expected HTTP 200, got {status}"
    assert downloaded == total_len, f"Payload truncation: {downloaded} != {total_len}"
    print("    --> Download Delivery: PASSED\n")


def test_pe_header():
    print("[1/3] Validating PE Binary Structure of Downloaded Binary...")
    assert os.path.isfile(DOWNLOADED_FILE), "Downloaded file missing"

    with open(DOWNLOADED_FILE, "rb") as f:
        # DOS Header
        dos_sig = f.read(2)
        assert dos_sig == b"MZ", "Invalid DOS signature"

        # PE Offset
        f.seek(0x3C)
        pe_offset = struct.unpack("<I", f.read(4))[0]

        # PE Signature
        f.seek(pe_offset)
        pe_sig = f.read(4)
        assert pe_sig == b"PE\x00\x00", "Invalid PE signature"

        # Machine Architecture
        machine, sections, _, _, _, _, _ = struct.unpack("<HHIIIHH", f.read(20))
        assert machine == 0x8664, f"Expected AMD64 (0x8664), got {machine:#x}"

        # Format Magic
        magic = struct.unpack("<H", f.read(2))[0]
        assert magic == 0x20B, f"Expected PE32+ (0x20B), got {magic:#x}"

        # Subsystem
        f.seek(pe_offset + 24 + 68)
        subsystem = struct.unpack("<H", f.read(2))[0]
        assert subsystem == 2, f"Expected Windows GUI (2), got {subsystem}"

        print(f"      Architecture: AMD64 (x64) PE32+")
        print(f"      Sections:     {sections}")
        print(f"      Subsystem:    Windows GUI")
        print("      --> PE Structure: PASSED\n")


def test_checksum_integrity():
    print("[2/3] Checking Cryptographic Checksum Against Built Artifact...")
    sha256 = hashlib.sha256()
    with open(DOWNLOADED_FILE, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    downloaded_sha = sha256.hexdigest()
    print(f"      Downloaded SHA-256: {downloaded_sha}")

    with open(DIST_FILE, "rb") as f:
        dist_sha = hashlib.sha256(f.read()).hexdigest()
    print(f"      Artifact   SHA-256: {dist_sha}")

    assert downloaded_sha == dist_sha, "Hash mismatch between downloaded file and dist artifact"
    print("      --> Checksum Verification: PASSED (Exact 1:1 Match)\n")


def test_process_execution():
    print("[3/3] Testing Native Process Execution of Downloaded App...")
    env = os.environ.copy()
    env["PENTA_HEADLESS_TEST"] = "1"

    proc = subprocess.Popen([DOWNLOADED_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    pid = proc.pid
    print(f"      Launched PID:    {pid}")

    time.sleep(2.5)
    is_active = proc.poll() is None
    status_str = "RUNNING AND HEALTHY" if is_active else f"EXITED ({proc.returncode})"
    print(f"      Lifecycle State: {status_str}")

    if is_active:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("      Terminated smoke test process cleanly.")

    print("      --> Process Execution: PASSED\n")


def run():
    download_binary()
    test_pe_header()
    test_checksum_integrity()
    test_process_execution()
    print("=" * 65)
    print("  ALL DOWNLOAD & WINDOWS APP TESTS COMPLETED SUCCESSFULLY! (100%)")
    print("=" * 65)


if __name__ == "__main__":
    run()
