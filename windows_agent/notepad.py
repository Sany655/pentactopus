from __future__ import annotations

import ctypes
import os
import subprocess
import time
from ctypes import wintypes
from typing import Protocol


MAX_NOTEPAD_TEXT_CHARACTERS = 16_384


class NotepadController(Protocol):
    def open_and_type(self, text: str) -> None: ...


class WindowsNotepadController:
    """Launch Notepad and type only into the window created by this process."""

    def __init__(self, window_timeout_seconds: float = 10.0) -> None:
        self.window_timeout_seconds = window_timeout_seconds

    def open_and_type(self, text: str) -> None:
        if os.name != "nt":
            raise OSError("Notepad UI automation is supported only on Windows.")
        if not text:
            raise ValueError("Text to type must not be empty.")
        if len(text) > MAX_NOTEPAD_TEXT_CHARACTERS:
            raise ValueError(
                f"Text to type exceeds the {MAX_NOTEPAD_TEXT_CHARACTERS}-character local limit."
            )

        process = subprocess.Popen(["notepad.exe"])
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        window = self._wait_for_window(process, user32)
        if not user32.SetForegroundWindow(window):
            raise OSError(ctypes.get_last_error(), "Could not focus the Notepad window.")
        time.sleep(0.15)
        if user32.GetForegroundWindow() != window:
            raise RuntimeError("Notepad did not become the foreground window; text was not typed.")

        self._send_unicode_text(user32, text)

    def _wait_for_window(self, process: subprocess.Popen[bytes], user32: ctypes.WinDLL) -> int:
        window_result: list[int] = []
        window_callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

        def find_process_window(hwnd: int, _lparam: int) -> bool:
            process_id = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
            if process_id.value == process.pid and user32.IsWindowVisible(hwnd):
                window_result.append(hwnd)
                return False
            return True

        callback = window_callback_type(find_process_window)
        deadline = time.monotonic() + self.window_timeout_seconds
        while time.monotonic() < deadline:
            window_result.clear()
            user32.EnumWindows(callback, 0)
            if window_result:
                return window_result[0]
            if process.poll() is not None:
                raise RuntimeError("Notepad exited before its window became available.")
            time.sleep(0.1)
        raise TimeoutError("Timed out waiting for the Notepad window.")

    @staticmethod
    def _send_unicode_text(user32: ctypes.WinDLL, text: str) -> None:
        pointer_size = ctypes.sizeof(ctypes.c_void_p)
        pointer_uint = ctypes.c_uint64 if pointer_size == 8 else ctypes.c_uint32

        class KeyboardInput(ctypes.Structure):
            _fields_ = [
                ("virtual_key", wintypes.WORD),
                ("scan_code", wintypes.WORD),
                ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("extra_info", pointer_uint),
            ]

        class InputUnion(ctypes.Union):
            _fields_ = [("keyboard", KeyboardInput)]

        class Input(ctypes.Structure):
            _anonymous_ = ("data",)
            _fields_ = [("type", wintypes.DWORD), ("data", InputUnion)]

        input_keyboard = 1
        keyeventf_keyup = 0x0002
        keyeventf_unicode = 0x0004

        def send_key(scan_code: int, flags: int) -> None:
            event = Input(
                type=input_keyboard,
                keyboard=KeyboardInput(
                    virtual_key=0,
                    scan_code=scan_code,
                    flags=flags,
                    time=0,
                    extra_info=0,
                ),
            )
            sent = user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(Input))
            if sent != 1:
                raise OSError(ctypes.get_last_error(), "Windows rejected Notepad text input.")

        for character in text:
            encoded = character.encode("utf-16-le")
            for offset in range(0, len(encoded), 2):
                scan_code = int.from_bytes(encoded[offset : offset + 2], "little")
                send_key(scan_code, keyeventf_unicode)
                send_key(scan_code, keyeventf_unicode | keyeventf_keyup)


class MockNotepadController:
    """Test double that records the requested action without opening a window."""

    def __init__(self) -> None:
        self.opened = False
        self.text: str | None = None

    def open_and_type(self, text: str) -> None:
        self.opened = True
        self.text = text
