"""PC Hardware & Remote Desktop Controller for Windows.

Provides native Windows screen capture, mouse control, keyboard typing,
media controls, and application launching without heavy third-party dependencies.
"""

import ctypes
try:
    from ctypes import wintypes
except (ImportError, ValueError, AttributeError):
    wintypes = None

if wintypes is None:
    class _DummyWintypes:
        DWORD = ctypes.c_uint32
        LONG = ctypes.c_int32
        WORD = ctypes.c_uint16
    wintypes = _DummyWintypes()
import io
import time
import subprocess
import os
import webbrowser
from typing import Tuple, Optional, Dict, Any
from PIL import Image

# Win32 Constants
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 0x8000

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002

# Virtual Key Codes
VK_RETURN = 0x0D
VK_ESCAPE = 0x1B
VK_BACK = 0x08
VK_TAB = 0x09
VK_SPACE = 0x20
VK_LWIN = 0x5B
VK_MENU = 0x12  # Alt
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_PLAY_PAUSE = 0xB3

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', wintypes.DWORD),
        ('biWidth', wintypes.LONG),
        ('biHeight', wintypes.LONG),
        ('biPlanes', wintypes.WORD),
        ('biBitCount', wintypes.WORD),
        ('biCompression', wintypes.DWORD),
        ('biSizeImage', wintypes.DWORD),
        ('biXPelsPerMeter', wintypes.LONG),
        ('biYPelsPerMeter', wintypes.LONG),
        ('biClrUsed', wintypes.DWORD),
        ('biClrImportant', wintypes.DWORD)
    ]

class DesktopController:
    def __init__(self):
        if hasattr(ctypes, "windll"):
            self.user32 = ctypes.windll.user32
            self.gdi32 = ctypes.windll.gdi32
        else:
            self.user32 = None
            self.gdi32 = None

    def get_screen_resolution(self) -> Tuple[int, int]:
        w = self.user32.GetSystemMetrics(0)
        h = self.user32.GetSystemMetrics(1)
        return w, h

    def capture_screen_image(self) -> Image.Image:
        """Capture Windows screen using fast native GDI."""
        w, h = self.get_screen_resolution()
        hwnd = self.user32.GetDesktopWindow()
        hdc_screen = self.user32.GetDC(hwnd)
        hdc_mem = self.gdi32.CreateCompatibleDC(hdc_screen)

        hbmp = self.gdi32.CreateCompatibleBitmap(hdc_screen, w, h)
        self.gdi32.SelectObject(hdc_mem, hbmp)

        # BitBlt SRCCOPY = 0x00CC0020
        self.gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc_screen, 0, 0, 0x00CC0020)

        bmi = BITMAPINFOHEADER()
        bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.biWidth = w
        bmi.biHeight = -h  # top-down DIB
        bmi.biPlanes = 1
        bmi.biBitCount = 32
        bmi.biCompression = 0  # BI_RGB

        buffer_size = w * h * 4
        buf = (ctypes.c_char * buffer_size)()
        res = self.gdi32.GetDIBits(hdc_mem, hbmp, 0, h, buf, ctypes.byref(bmi), 0)

        # Cleanup GDI resources
        self.gdi32.DeleteObject(hbmp)
        self.gdi32.DeleteDC(hdc_mem)
        self.user32.ReleaseDC(hwnd, hdc_screen)

        if res == 0:
            raise RuntimeError("GDI GetDIBits failed to capture screen.")

        # Create PIL Image from BGRA buffer and convert to RGB
        img = Image.frombuffer('RGBA', (w, h), buf, 'raw', 'BGRA', 0, 1)
        return img.convert('RGB')

    def capture_screen_jpeg(self, quality: int = 75, max_width: Optional[int] = 1024) -> bytes:
        img = self.capture_screen_image()
        if max_width and img.width > max_width:
            ratio = max_width / float(img.width)
            new_h = int(img.height * ratio)
            img = img.resize((max_width, new_h), Image.Resampling.LANCZOS)

        out = io.BytesIO()
        img.save(out, format="JPEG", quality=quality)
        return out.getvalue()

    def get_cursor_pos(self) -> Tuple[int, int]:
        pt = wintypes.POINT()
        self.user32.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y

    def set_cursor_pos(self, x: int, y: int):
        self.user32.SetCursorPos(int(x), int(y))

    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left"):
        if x is not None and y is not None:
            self.set_cursor_pos(x, y)
        time.sleep(0.02)

        if button == "left":
            self.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.02)
            self.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        elif button == "right":
            self.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.02)
            self.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        elif button == "middle":
            self.user32.mouse_event(MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0)
            time.sleep(0.02)
            self.user32.mouse_event(MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0)

    def double_click(self, x: Optional[int] = None, y: Optional[int] = None):
        self.click(x, y, button="left")
        time.sleep(0.08)
        self.click(x, y, button="left")

    def scroll(self, clicks: int = 3):
        # 120 units per notch
        self.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, clicks * 120, 0)

    def send_key(self, vk_code: int):
        self.user32.keybd_event(vk_code, 0, 0, 0)
        time.sleep(0.02)
        self.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)

    def send_hotkey(self, hotkey_name: str) -> bool:
        name = hotkey_name.lower().replace("-", "_")
        if name in ("win_d", "desktop"):
            self.user32.keybd_event(VK_LWIN, 0, 0, 0)
            self.user32.keybd_event(ord('D'), 0, 0, 0)
            time.sleep(0.03)
            self.user32.keybd_event(ord('D'), 0, KEYEVENTF_KEYUP, 0)
            self.user32.keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)
            return True
        elif name in ("enter", "return"):
            self.send_key(VK_RETURN)
            return True
        elif name in ("esc", "escape"):
            self.send_key(VK_ESCAPE)
            return True
        elif name in ("backspace", "back"):
            self.send_key(VK_BACK)
            return True
        elif name in ("tab",):
            self.send_key(VK_TAB)
            return True
        elif name in ("space",):
            self.send_key(VK_SPACE)
            return True
        elif name in ("vol_up", "volume_up"):
            self.send_key(VK_VOLUME_UP)
            return True
        elif name in ("vol_down", "volume_down"):
            self.send_key(VK_VOLUME_DOWN)
            return True
        elif name in ("mute", "volume_mute"):
            self.send_key(VK_VOLUME_MUTE)
            return True
        elif name in ("play_pause", "media_play"):
            self.send_key(VK_MEDIA_PLAY_PAUSE)
            return True
        return False

    def type_text(self, text: str):
        # Send text via PowerShell SendKeys to support full Unicode & symbols
        # Escape special characters in SendKeys (+, ^, %, ~, (, ), [, ])
        escaped = ""
        for c in text:
            if c in "+^%~(){}[]":
                escaped += f"{{{c}}}"
            else:
                escaped += c
        cmd = ["powershell", "-Command", f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{escaped}')"]
        subprocess.run(cmd, capture_output=True)

    def lock_pc(self):
        """Locks the Windows workstation instantly."""
        self.user32.LockWorkStation()

    def open_url(self, url: str):
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"
        webbrowser.open(url)

    def launch_app(self, app_name: str) -> Dict[str, Any]:
        app_map = {
            "chrome": ["start", "chrome"],
            "browser": ["start", "chrome"],
            "edge": ["start", "msedge"],
            "notepad": ["notepad.exe"],
            "calc": ["calc.exe"],
            "calculator": ["calc.exe"],
            "explorer": ["explorer.exe"],
            "terminal": ["start", "powershell"],
            "cmd": ["start", "cmd"]
        }
        cmd = app_map.get(app_name.lower())
        if not cmd:
            return {"success": False, "error": f"App '{app_name}' not in safe launch allowlist."}
        try:
            subprocess.Popen(cmd, shell=True)
            return {"success": True, "message": f"Launched {app_name} on PC."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def scale_coordinates(self, norm_x: float, norm_y: float) -> Tuple[int, int]:
        """Convert 0.0-1.0 normalized mobile touch coordinates to native PC pixels."""
        w, h = self.get_screen_resolution()
        x = int(norm_x * w)
        y = int(norm_y * h)
        x = max(0, min(w - 1, x))
        y = max(0, min(h - 1, y))
        return x, y
