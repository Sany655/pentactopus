"""Playwright End-to-End Headless Browser UI Test Suite for Pentactopus.

Tests live rendering, DOM manipulation, form inputs, dynamic calculators,
authentication workflows, admin console governance, and branding integrity
across both the Cloud Web Platform (port 5051) and Desktop Command Center (port 5050).
"""

import os
import re
import pytest
from playwright.sync_api import sync_playwright

WEB_URL = "http://localhost:5051"
DESKTOP_URL = "http://localhost:5050"
SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "ui_screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

FORBIDDEN_BRANDS = ["anydesk", "antigravity"]


@pytest.fixture(scope="module")
def browser_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        yield context
        browser.close()


def test_web_landing_page_rendering(browser_context):
    """Verify landing page typography, branding, navigation, and visual hierarchy."""
    page = browser_context.new_page()
    page.goto(WEB_URL, wait_until="networkidle")

    # Verify Title & Meta
    assert "Pentactopus" in page.title()
    assert "Autonomous Cross-Platform" in page.title()

    # Verify Navbar Brand
    brand_text = page.locator(".nav-brand").inner_text()
    assert "Pentactopus" in brand_text

    # Verify Navigation Links
    nav_links = page.locator(".nav-links a").all_inner_texts()
    expected_links = ["Platform", "Architecture", "Economics", "Downloads", "Pricing"]
    for expected in expected_links:
        assert any(expected.lower() in link.lower() for link in nav_links), f"Missing nav link: {expected}"

    # Verify Hero Title & Subtitle
    hero_title = page.locator(".hero-title").inner_text()
    assert "YOUR COMPUTER" in hero_title

    # Verify Downloads Section presence
    downloads_section = page.locator("#downloads")
    assert downloads_section.is_visible()

    # Check Download Links
    exe_link = page.locator('a[href="/download/PentaAssistant-Setup.exe"]')
    apk_link = page.locator('a[href="/download/PentaAssistant.apk"]')
    assert exe_link.count() > 0
    assert apk_link.count() > 0

    # Capture Screenshot
    screenshot_path = os.path.join(SCREENSHOT_DIR, "web_landing.png")
    page.screenshot(path=screenshot_path, full_page=False)
    assert os.path.exists(screenshot_path)
    page.close()


def test_web_economics_calculator_interaction(browser_context):
    """Test interactive sliders and dynamic formula calculations on the web landing page."""
    page = browser_context.new_page()
    page.goto(WEB_URL, wait_until="networkidle")

    # Initial values check
    disp_devices = page.locator("#disp-devices").inner_text()
    assert disp_devices == "2"

    init_total = page.locator("#cost-grand").inner_text()
    assert "$" in init_total

    # Change paired devices to 6
    page.fill("#input-devices", "6")
    page.evaluate("calculateEconomics()")
    new_disp_devices = page.locator("#disp-devices").inner_text()
    assert new_disp_devices == "6"

    # Change autonomous tasks per day to 50
    page.fill("#input-tasks", "50")
    page.evaluate("calculateEconomics()")
    new_disp_tasks = page.locator("#disp-tasks").inner_text()
    assert new_disp_tasks == "50"

    # Change stream hours to 25
    page.fill("#input-hours", "25")
    page.evaluate("calculateEconomics()")

    # Recalculated total should have increased
    updated_total = page.locator("#cost-grand").inner_text()
    assert updated_total != init_total
    assert "$" in updated_total

    page.close()


def test_web_auth_modal_interaction(browser_context):
    """Test modal opening, tab switching, and closing."""
    page = browser_context.new_page()
    page.goto(WEB_URL, wait_until="networkidle")

    overlay = page.locator("#auth-overlay")
    assert not overlay.is_visible()

    # Open Sign In modal
    page.click('button:has-text("Sign In")')
    assert overlay.is_visible()

    # Switch to Register tab using toggle link
    page.click("#auth-toggle-link")
    assert page.locator("#auth-modal-title").inner_text() == "Create Pentactopus Account"
    assert page.locator("#group-name").is_visible()

    # Switch back to Login tab
    page.click("#auth-toggle-link")
    assert page.locator("#auth-modal-title").inner_text() == "Sign In to Pentactopus"

    # Close modal
    page.click('button:has-text("✕")')
    assert not overlay.is_visible()

    page.close()


def test_web_user_login_and_dashboard(browser_context):
    """Test user authentication flow, session initialization, and task dispatch."""
    page = browser_context.new_page()
    page.goto(WEB_URL, wait_until="networkidle")

    # Open Login Modal
    page.click('button:has-text("Sign In")')

    # Fill Credentials (using pre-seeded user)
    page.fill("#auth-email", "alex@pentactopus.com")
    page.fill("#auth-password", "PentaPro2026!")
    page.click("#auth-submit-btn")

    # Wait for dashboard view to become visible
    dash_view = page.locator("#dashboard-view")
    dash_view.wait_for(state="visible", timeout=15000)

    # Verify Dashboard displays correct user info
    email_display = page.locator("#dash-user-email").inner_text()
    assert "alex@pentactopus.com" in email_display

    role_badge = page.locator("#dash-role-badge").inner_text()
    assert len(role_badge) > 0

    # Test Autonomous Task Dispatch
    page.fill("#ai-task-input", "Export monthly sales analytics to PDF")
    page.click('button:has-text("Dispatch")')

    # Verify terminal log updates
    terminal = page.locator("#ai-log-terminal")
    page.wait_for_function("document.getElementById('ai-log-terminal').innerText.includes('Export monthly sales analytics') || document.getElementById('ai-log-terminal').innerText.includes('QUEUED') || document.getElementById('ai-log-terminal').innerText.includes('Dispatched')")
    log_text = terminal.inner_text()
    assert "Export monthly sales analytics" in log_text or "Dispatched" in log_text or "QUEUED" in log_text

    # Take Screenshot of authenticated dashboard
    screenshot_path = os.path.join(SCREENSHOT_DIR, "web_user_dashboard.png")
    page.screenshot(path=screenshot_path, full_page=False)
    assert os.path.exists(screenshot_path)

    page.close()


def test_web_admin_dashboard_rendering(browser_context):
    """Test the administrative console with overview metrics, user management, and coupons."""
    page = browser_context.new_page()

    # Pre-seed admin secret in localStorage to authenticate to /admin (clearing any prior subscriber session)
    page.goto(WEB_URL)
    page.evaluate("""
        localStorage.removeItem('penta_auth_token');
        localStorage.setItem('penta_admin_secret', 'penta_admin_secret_2026');
    """)

    # Navigate to /admin
    page.goto(f"{WEB_URL}/admin", wait_until="networkidle")

    # Wait for the authenticated admin dashboard to render
    page.wait_for_selector("table, .stat-card, .metric-card", timeout=15000)
    body_text = page.locator("body").inner_text()
    assert "Pentactopus" in body_text

    # Verify User Accounts Table contains seeded users
    assert "admin@pentactopus.com" in body_text
    assert "alex@pentactopus.com" in body_text
    assert "guest@pentactopus.com" in body_text

    # Verify Promo Codes / Coupon Section exists
    assert "PENTAFREE" in body_text or "Coupons" in body_text or "Promo" in body_text

    # Capture Screenshot of Admin Dashboard
    screenshot_path = os.path.join(SCREENSHOT_DIR, "admin_dashboard.png")
    page.screenshot(path=screenshot_path, full_page=False)
    assert os.path.exists(screenshot_path)

    page.close()


def test_desktop_agent_ui_rendering_and_task_execution(browser_context):
    """Test Desktop Command Center UI (port 5050): status, daemon indicators, and local task runner."""
    page = browser_context.new_page()
    page.goto(DESKTOP_URL, wait_until="networkidle")

    # Verify Title
    assert "Pentactopus PC Agent" in page.title()

    # Verify Header Branding
    header_text = page.locator(".header").inner_text()
    assert "Pentactopus PC Agent" in header_text
    assert "Daemon Active" in header_text

    # Verify Local Agent Card
    assert page.locator("#ai-prompt").is_visible()
    assert page.locator("#run-btn").is_visible()

    # Test Task Submission
    page.fill("#ai-prompt", "Verify desktop display resolution")
    page.click("#run-btn")

    # Verify Event Log in Terminal
    terminal = page.locator("#terminal")
    page.wait_for_function("document.getElementById('terminal').innerText.includes('Verify desktop display resolution') || document.getElementById('terminal').innerText.includes('AGENT')")
    term_text = terminal.inner_text()
    assert "Verify desktop display resolution" in term_text or "AGENT" in term_text

    # Capture Screenshot of Desktop Agent UI
    screenshot_path = os.path.join(SCREENSHOT_DIR, "desktop_agent_ui.png")
    page.screenshot(path=screenshot_path, full_page=False)
    assert os.path.exists(screenshot_path)

    page.close()


def test_zero_brand_infringement_in_dom(browser_context):
    """Strictly verify that rendered DOMs contain zero typos and zero unauthorized third-party marks."""
    page = browser_context.new_page()

    for url in [WEB_URL, DESKTOP_URL]:
        page.goto(url, wait_until="networkidle")
        body_content = page.locator("body").inner_text().lower()

        # Zero typo occurrences
        assert "pentatopus" not in body_content, f"Found typo 'pentatopus' on {url}"

        # Zero competitor brand occurrences
        for forbidden in FORBIDDEN_BRANDS:
            assert forbidden not in body_content, f"Found forbidden mark '{forbidden}' on {url}"

    page.close()
