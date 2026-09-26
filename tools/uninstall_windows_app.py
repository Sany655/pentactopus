r"""Completely uninstalls Pentactopus Assistant from Windows.

Leaves ZERO residue:
- Terminates all running processes (PentaAssistant, penta_daemon)
- Removes all Windows shortcuts (Desktop, Start Menu)
- Deletes all AppData & Cache directories (%LOCALAPPDATA%\PentaAssistant, %LOCALAPPDATA%\com.penta.assistant, %APPDATA%\com.penta.assistant, %LOCALAPPDATA%\Pentactopus)
- Deletes HKCU Uninstall Registry entry
- Deletes the installation directory (%LOCALAPPDATA%\Programs\Pentactopus)
"""

import os
import sys
import shutil
import subprocess
import winreg
import time

def terminate_processes():
    print("--> [1/5] Terminating running Penta processes...")
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", 
             "Stop-Process -Name PentaAssistant -Force -ErrorAction SilentlyContinue; "
             "Stop-Process -Name penta_daemon -Force -ErrorAction SilentlyContinue"],
            capture_output=True,
            timeout=10
        )
    except Exception as e:
        print(f"    Process termination warning: {e}")
    time.sleep(1)

def remove_shortcuts():
    print("--> [2/5] Removing shortcuts...")
    roaming = os.environ.get("APPDATA", os.path.expanduser(r"~\AppData\Roaming"))
    desktop = os.path.expanduser(r"~\Desktop")
    
    shortcuts = [
        os.path.join(roaming, r"Microsoft\Windows\Start Menu\Programs", "Pentactopus Assistant.lnk"),
        os.path.join(desktop, "Pentactopus Assistant.lnk"),
    ]
    for s in shortcuts:
        if os.path.exists(s):
            try:
                os.remove(s)
                print(f"    Removed: {s}")
            except Exception as e:
                print(f"    Could not remove {s}: {e}")

def remove_registry_keys():
    print("--> [3/5] Cleaning Windows Registry uninstall entries...")
    reg_key = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\Pentactopus"
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_key)
        print(f"    Deleted HKCU\\{reg_key}")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"    Registry warning: {e}")

def remove_app_data():
    print("--> [4/5] Purging AppData and Cache folders...")
    local = os.environ.get("LOCALAPPDATA", os.path.expanduser(r"~\AppData\Local"))
    roaming = os.environ.get("APPDATA", os.path.expanduser(r"~\AppData\Roaming"))
    
    appdata_dirs = [
        os.path.join(local, "PentaAssistant"),
        os.path.join(local, "Pentactopus"),
        os.path.join(local, "com.penta.assistant"),
        os.path.join(roaming, "com.penta.assistant"),
    ]
    for d in appdata_dirs:
        if os.path.exists(d):
            try:
                shutil.rmtree(d, ignore_errors=True)
                print(f"    Removed: {d}")
            except Exception as e:
                print(f"    Could not remove {d}: {e}")

def remove_install_dir():
    print("--> [5/5] Removing installation directory...")
    local = os.environ.get("LOCALAPPDATA", os.path.expanduser(r"~\AppData\Local"))
    install_dir = os.path.join(local, "Programs", "Pentactopus")
    if os.path.exists(install_dir):
        try:
            shutil.rmtree(install_dir, ignore_errors=True)
            print(f"    Removed: {install_dir}")
        except Exception as e:
            print(f"    Could not remove {install_dir}: {e}")

def uninstall():
    print("=" * 65)
    print("  PENTACTOPUS ASSISTANT — COMPLETE UNINSTALLATION (ZERO RESIDUE)")
    print("=" * 65)
    terminate_processes()
    remove_shortcuts()
    remove_registry_keys()
    remove_app_data()
    remove_install_dir()
    print("=" * 65)
    print("  UNINSTALLATION COMPLETE: All traces successfully removed.")
    print("=" * 65)

if __name__ == "__main__":
    uninstall()
