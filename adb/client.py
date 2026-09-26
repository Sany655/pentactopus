"""ADB client for communicating with physical or virtual Android devices."""

import os
import shutil
import subprocess
import time
from typing import List, Optional, Tuple, Dict, Any
from tools.action_schema import ValidatedAction
from tools.allowlist import sanitize_text_input, check_security_allowlist

class ADBError(Exception):
    pass

class ADBClient:
    def __init__(self, adb_path: Optional[str] = None, device_serial: Optional[str] = None):
        self.adb_path = adb_path or self._locate_adb()
        self.device_serial = device_serial

    def get_active_serial(self) -> Optional[str]:
        if self.device_serial:
            return self.device_serial
        try:
            devices = self.get_devices()
            if not devices:
                return None
            # Prioritize USB over wireless if both attached
            for d in devices:
                if d["state"] == "device" and ":" not in d["serial"]:
                    self.device_serial = d["serial"]
                    return self.device_serial
            for d in devices:
                if d["state"] == "device":
                    self.device_serial = d["serial"]
                    return self.device_serial
        except Exception:
            pass
        return None

    def _locate_adb(self) -> str:
        found = shutil.which("adb")
        if found:
            return found
        # Check known fallback locations dynamically
        candidates = []
        local_app_data = os.getenv("LOCALAPPDATA")
        if local_app_data:
            candidates.extend([
                os.path.join(local_app_data, "Microsoft", "WinGet", "Links", "adb.exe"),
                os.path.join(local_app_data, "Android", "Sdk", "platform-tools", "adb.exe"),
            ])
            # Check WinGet package directories
            winget_pkgs = os.path.join(local_app_data, "Microsoft", "WinGet", "Packages")
            if os.path.isdir(winget_pkgs):
                for root, _, files in os.walk(winget_pkgs):
                    if "adb.exe" in files:
                        candidates.append(os.path.join(root, "adb.exe"))
                        break

        android_home = os.getenv("ANDROID_HOME") or os.getenv("ANDROID_SDK_ROOT")
        if android_home:
            candidates.append(os.path.join(android_home, "platform-tools", "adb.exe"))
            candidates.append(os.path.join(android_home, "adb.exe"))

        for c in candidates:
            if os.path.isfile(c):
                return c
        raise ADBError("adb.exe not found on system. Please ensure platform-tools are installed.")

    def _build_cmd(self, subcommands: List[str]) -> List[str]:
        cmd = [self.adb_path]
        # Always resolve serial if not querying general devices
        if subcommands and subcommands[0] not in ("devices", "version", "start-server", "kill-server", "connect", "disconnect"):
            serial = self.get_active_serial()
            if serial:
                cmd.extend(["-s", serial])
        cmd.extend(subcommands)
        return cmd

    def run_command(self, subcommands: List[str], timeout_sec: int = 15) -> Tuple[int, str, str]:
        cmd = self._build_cmd(subcommands)
        try:
            kwargs = {
                "capture_output": True,
                "text": True,
                "timeout": timeout_sec,
                "encoding": "utf-8",
                "errors": "replace"
            }
            if os.name == 'nt':
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            res = subprocess.run(cmd, **kwargs)
            return res.returncode, res.stdout.strip(), res.stderr.strip()
        except subprocess.TimeoutExpired:
            raise ADBError(f"ADB command timed out after {timeout_sec}s: {' '.join(cmd)}")
        except Exception as e:
            raise ADBError(f"Failed to execute ADB command: {e}")

    def run_binary_command(self, subcommands: List[str], timeout_sec: int = 15) -> bytes:
        cmd = self._build_cmd(subcommands)
        try:
            kwargs = {
                "capture_output": True,
                "timeout": timeout_sec
            }
            if os.name == 'nt':
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            res = subprocess.run(cmd, **kwargs)
            if res.returncode != 0:
                raise ADBError(f"ADB binary command failed: {res.stderr.decode('utf-8', errors='replace')}")
            return res.stdout
        except Exception as e:
            raise ADBError(f"Failed binary ADB command: {e}")

    def get_devices(self) -> List[Dict[str, str]]:
        """List attached devices and their states."""
        code, out, err = self.run_command(["devices", "-l"])
        devices = []
        for line in out.splitlines()[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                devices.append({
                    "serial": parts[0],
                    "state": parts[1],
                    "raw": line
                })
        return devices

    def capture_screenshot(self) -> bytes:
        """Capture screen as PNG bytes directly via screencap -p."""
        raw_bytes = self.run_binary_command(["exec-out", "screencap", "-p"])
        # Fix Windows line ending normalization (CR-LF to LF) if needed
        if raw_bytes.startswith(b"\x89PNG"):
            return raw_bytes
        normalized = raw_bytes.replace(bytes.fromhex('0d0a'), bytes.fromhex('0a'))
        return normalized

    def dump_ui_hierarchy(self) -> str:
        """Dump UI hierarchy XML using uiautomator."""
        # Try direct exec-out first with quick 2s timeout
        try:
            raw = self.run_binary_command(["exec-out", "uiautomator", "dump", "/dev/tty"], timeout_sec=2)
            text = raw.decode("utf-8", errors="replace")
            if "<hierarchy" in text:
                return text[text.find("<hierarchy"):]
        except Exception:
            pass

        # Fallback via temporary file on sdcard with short timeout
        try:
            code, out, _ = self.run_command(["shell", "uiautomator", "dump", "--compressed", "/data/local/tmp/uidump.xml"], timeout_sec=4)
            if "dumped to" in out or code == 0:
                _, xml_content, _ = self.run_command(["shell", "cat", "/data/local/tmp/uidump.xml"], timeout_sec=3)
                return xml_content
        except Exception:
            pass
        return ""

    def get_focused_app(self) -> str:
        """Get the currently focused window / app package."""
        try:
            _, out, _ = self.run_command(["shell", "dumpsys", "window"], timeout_sec=4)
            for line in out.splitlines():
                if "mCurrentFocus=" in line or "mFocusedApp=" in line:
                    return line.strip()
        except Exception:
            pass
        return "Unknown"

    def get_screen_size(self) -> Tuple[int, int]:
        """Get display resolution (width, height)."""
        code, out, err = self.run_command(["shell", "wm", "size"])
        # Output format: 'Physical size: 1080x2400'
        for line in out.splitlines():
            if "size:" in line:
                dim = line.split(":")[-1].strip()
                if "x" in dim:
                    w, h = dim.split("x")
                    return int(w), int(h)
        return 1080, 2400

    def execute_action(self, action: ValidatedAction) -> Dict[str, Any]:
        """Execute a validated safe action on the device."""
        check_security_allowlist(action)
        t = action.action_type
        p = action.params

        if t == "tap":
            self.run_command(["shell", "input", "tap", str(p["x"]), str(p["y"])])
            return {"status": "executed", "details": f"Tapped at ({p['x']}, {p['y']})"}

        elif t == "type":
            sanitized = sanitize_text_input(p["text"])
            self.run_command(["shell", "input", "text", sanitized])
            return {"status": "executed", "details": f"Typed text: {p['text']}"}

        elif t == "swipe":
            self.run_command(["shell", "input", "swipe", str(p["x1"]), str(p["y1"]), str(p["x2"]), str(p["y2"]), str(p["duration_ms"])])
            return {"status": "executed", "details": f"Swiped from ({p['x1']},{p['y1']}) to ({p['x2']},{p['y2']})"}

        elif t == "key_event":
            self.run_command(["shell", "input", "keyevent", str(p["keycode"])])
            return {"status": "executed", "details": f"Sent key {p['key']} (code {p['keycode']})"}

        elif t == "launch_app":
            pkg = p["package"]
            # Safe launch using monkey launcher intent
            self.run_command(["shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"])
            return {"status": "executed", "details": f"Launched package: {pkg}"}

        elif t == "wait":
            time.sleep(p["seconds"])
            return {"status": "executed", "details": f"Waited {p['seconds']}s"}

        elif t == "run_command":
            cmd = p.get("command", "")
            code, out, err = self.run_command(["shell"] + (cmd.split() if isinstance(cmd, str) and not any(c in cmd for c in "\"'") else [cmd]))
            return {"status": "executed", "details": out or err or "Command executed."}

        elif t == "unsupported":
            msg = p.get("message", "Feature not supported on Android (Coming Soon).")
            return {"status": "skipped", "details": msg}

        elif t == "finish":
            return {"status": "completed", "details": p["message"]}

        raise ADBError(f"Unhandled action type: {t}")

    def tap_point(self, x: int, y: int) -> Dict[str, Any]:
        """Send direct touch tap to coordinates."""
        self.run_command(["shell", "input", "tap", str(int(x)), str(int(y))])
        return {"status": "executed", "action": "tap", "x": x, "y": y}

    def type_text(self, text: str) -> Dict[str, Any]:
        """Type text into active input field."""
        sanitized = sanitize_text_input(text)
        self.run_command(["shell", "input", "text", sanitized])
        return {"status": "executed", "action": "type", "text": text}

    def press_key(self, key_name: str) -> Dict[str, Any]:
        """Send hardware keyevent by name (home, back, recents, power, vol_up, vol_down, mute, enter)."""
        key_map = {
            "home": 3,
            "back": 4,
            "recents": 187,
            "app_switch": 187,
            "power": 26,
            "wake": 224,
            "vol_up": 24,
            "vol_down": 25,
            "mute": 164,
            "enter": 66,
            "tab": 61,
            "space": 62,
            "del": 67,
            "backspace": 67,
        }
        code = key_map.get(key_name.lower())
        if code is None:
            try:
                code = int(key_name)
            except ValueError:
                code = 3
        self.run_command(["shell", "input", "keyevent", str(code)])
        return {"status": "executed", "action": "key_event", "key": key_name, "keycode": code}

    def swipe_direction(self, direction: str) -> Dict[str, Any]:
        """Swipe screen in specified direction (up=scroll down, down=scroll up, left, right)."""
        d = direction.lower()
        if d == "up":
            self.run_command(["shell", "input", "swipe", "540", "1500", "540", "500", "300"])
        elif d == "down":
            self.run_command(["shell", "input", "swipe", "540", "500", "540", "1500", "300"])
        elif d == "left":
            self.run_command(["shell", "input", "swipe", "900", "1000", "150", "1000", "300"])
        elif d == "right":
            self.run_command(["shell", "input", "swipe", "150", "1000", "900", "1000", "300"])
        return {"status": "executed", "action": "swipe", "direction": direction}

    def launch_package(self, package_name: str) -> Dict[str, Any]:
        """Launch an app package via monkey intent."""
        self.run_command(["shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"])
        return {"status": "executed", "action": "launch", "package": package_name}

