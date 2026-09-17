import os
import time
import pygetwindow as gw
import pyautogui

def main():
    screenshots_dir = os.path.join(os.path.dirname(__file__), '..', 'reports', 'screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)
    
    print("Searching for Pentactopus window...")
    # Find the window. The title is "Pentactopus — Remote Control & AI Agent"
    windows = gw.getWindowsWithTitle('Pentactopus')
    
    if not windows:
        print("Could not find the Pentactopus window. Make sure the app is running!")
        return
        
    window = windows[0]
    print(f"Found window: {window.title}")
    
    # Restore and activate window
    if window.isMinimized:
        window.restore()
    try:
        window.activate()
    except Exception as e:
        print(f"Warning activating window: {e}")
        
    time.sleep(1) # Wait for it to come to foreground
    
    # Take screenshot of the window's bounding box
    print("Taking main dashboard screenshot...")
    main_screenshot = os.path.join(screenshots_dir, 'native_dashboard.png')
    
    # Capture the specific region of the window
    screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
    screenshot.save(main_screenshot)
    
    # Since we can't easily click specific React elements without DOM access,
    # we'll capture just the main screen for the automated report.
    
    # Generate Markdown Report
    report_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'client_app_report.md')
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Client App Features & Screenshots\n\n")
        f.write("This document contains automated screenshots of the Pentactopus Native Client (Tauri/React).\n\n")
        f.write("## Main Interface\n")
        f.write("![Main Dashboard](../reports/screenshots/native_dashboard.png)\n\n")
        f.write("> Note: The automated script captures the native desktop window. Further UI interactions require DOM inspection or coordinate mapping.\n")
        
    print(f"Native report generated at {report_path}")

if __name__ == '__main__':
    main()
