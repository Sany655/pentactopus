"""Helper for launching scrcpy with optimal low-resource flags for low-spec PCs."""

import subprocess
import shutil
import sys

from typing import Optional

def launch_scrcpy(
    serial: Optional[str] = None,
    max_size: int = 1024,
    bit_rate_mb: int = 2,
    max_fps: int = 30,
    no_audio: bool = True
):
    scrcpy_bin = shutil.which("scrcpy") or r"C:\Users\Sany\AppData\Local\Microsoft\WinGet\Links\scrcpy.cmd"
    cmd = [
        scrcpy_bin,
        f"--max-size={max_size}",
        f"--video-bit-rate={bit_rate_mb}M",
        f"--max-fps={max_fps}"
    ]
    if no_audio:
        cmd.append("--no-audio")
    if serial:
        cmd.extend(["-s", serial])

    print(f"Starting low-spec optimized scrcpy: {' '.join(cmd)}")
    subprocess.Popen(cmd)

if __name__ == "__main__":
    serial_arg = sys.argv[1] if len(sys.argv) > 1 else None
    launch_scrcpy(serial=serial_arg)

