import os
import subprocess
import time
import pytest
from playwright.sync_api import sync_playwright

def find_tauri_executable():
    """Find the native Windows Tauri executable."""
    candidates = [
        os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "PentaAssistant", "PentaAssistant.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "PentaAssistant", "PentaAssistant.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "PentaAssistant", "penta-assistant.exe"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "penta-app", "src-tauri", "target", "debug", "penta-assistant.exe"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "penta-app", "src-tauri", "target", "release", "penta-assistant.exe")
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None

def test_native_windows_app():
    exe_path = find_tauri_executable()
    if not exe_path:
        pytest.skip("Native Tauri executable not found. Please build or install PentaAssistant first.")
        return

    print(f"Testing native Windows app at: {exe_path}")

    # Launch native Windows app with WebView2 remote debugging enabled
    env = os.environ.copy()
    env["WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"] = "--remote-debugging-port=9222"
    
    process = subprocess.Popen([exe_path], env=env)
    
    # Wait for the native app and debugging port to initialize
    time.sleep(5)
    
    with sync_playwright() as p:
        try:
            # Connect Playwright to the native WebView2 container via CDP
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            
            # The Tauri app has a single context and a single page
            context = browser.contexts[0]
            page = context.pages[0]
            
            # 1. Wait for App to load
            page.wait_for_timeout(2000) # Give React a moment to render
            
            # Check if we are on the login screen
            login_header = page.locator("text=Welcome Back")
            if login_header.is_visible():
                print("Native App UI: Login screen rendered.")
                # 2. Login
                page.fill("input[type='email']", "alex@pentactopus.com")
                page.fill("input[type='password']", "PentaPro2026!")
                page.click("button:has-text('Sign In')")
            else:
                print("Native App UI: Already logged in, skipping login screen.")
            
            # 3. Wait for Chat Dashboard
            page.wait_for_selector("text=Pentactopus", timeout=10000)
            page.wait_for_selector("text=New Chat", timeout=10000)
            print("Native App UI: Dashboard loaded.")
            
            # 4. Verify Chat Message Dispatch
            page.fill("input[placeholder*='Ask the AI agent']", "Open calculator")
            page.locator("button", has_text="Send").click()
            
            # Ensure it dispatches correctly by verifying the user's message appears in the chat window
            page.wait_for_selector("text=Open calculator", timeout=10000, state="attached")
            print("Native App UI: Agent directive dispatched and displayed in chat history.")

        except Exception as e:
            print(f"Error during native test: {repr(e)}")
            raise e
        finally:
            if 'browser' in locals():
                browser.close()
            process.terminate()
            process.wait()

if __name__ == "__main__":
    test_native_windows_app()
