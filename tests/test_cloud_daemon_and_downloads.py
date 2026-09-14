"""Automated tests for Cloud-to-Device Daemon Relay, Task Dispatching, and Download Assets."""

import os
import json
import zipfile
import pytest
from io import BytesIO
from unittest.mock import MagicMock, patch

from hub.device_hub import DeviceHub
from penta.penta_daemon import PentaDaemon
from api.index import handler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class MockHandler(handler):
    def __init__(self, method, path, body=b"", headers=None):
        self.command = method
        self.path = path
        self.rfile = BytesIO(body)
        self.wfile = BytesIO()
        self.headers = headers or {"Content-Length": str(len(body))}
        self.client_address = ("127.0.0.1", 12345)
        self.status_code = 200

    def send_response(self, code, message=None):
        self.status_code = code

    def send_header(self, keyword, value):
        pass

    def end_headers(self):
        pass


def test_android_apk_asset_validity():
    """Verify that PentaAssistant.apk exists in dist and public/download, with valid manifest."""
    apk_paths = [
        os.path.join(BASE_DIR, "dist", "PentaAssistant.apk"),
        os.path.join(BASE_DIR, "public", "download", "PentaAssistant.apk")
    ]
    for p in apk_paths:
        assert os.path.isfile(p), f"Missing APK package at {p}"
        assert os.path.getsize(p) > 500, f"APK size too small: {p}"
        
        # Verify valid ZIP/APK structure
        with zipfile.ZipFile(p, "r") as zf:
            namelist = zf.namelist()
            assert "AndroidManifest.xml" in namelist, f"AndroidManifest.xml missing in {p}"
            assert "classes.dex" in namelist, f"classes.dex missing in {p}"


def test_windows_setup_exe_in_public_downloads():
    """Verify that PentaAssistant-Setup.exe exists in public/download for direct web downloads."""
    exe_path = os.path.join(BASE_DIR, "public", "download", "PentaAssistant-Setup.exe")
    assert os.path.isfile(exe_path), f"Expected setup executable at {exe_path}"
    with open(exe_path, "rb") as f:
        magic = f.read(2)
        assert magic == b"MZ", "Not a valid Windows PE binary"


def test_penta_daemon_task_execution_and_reporting():
    """Verify PentaDaemon executes local PC tasks and parses actions properly."""
    daemon = PentaDaemon(cloud_url="http://mock-cloud.pentactopus.com")
    
    # Test PC task execution
    with patch.object(daemon.win_controller, "click") as mock_click:
        success, msg = daemon._execute_pc_task({"type": "click", "norm_x": 0.5, "norm_y": 0.5, "button": "left"})
        assert success is True
        mock_click.assert_called_once_with(0.5, 0.5, button="left")

    with patch.object(daemon.win_controller, "type_text") as mock_type:
        success, msg = daemon._execute_pc_task({"type": "type", "text": "Hello Pentactopus"})
        assert success is True
        mock_type.assert_called_once_with("Hello Pentactopus")

    with patch.object(daemon.win_controller, "send_hotkey", return_value=True) as mock_hk:
        success, msg = daemon._execute_pc_task({"type": "hotkey", "hotkey": "win_d"})
        assert success is True
        mock_hk.assert_called_once_with("win_d")

    # Test Android task execution
    with patch.object(daemon.adb, "run_command", return_value=(0, "", "")) as mock_adb:
        success, msg = daemon._execute_android_task({"type": "tap", "norm_x": 0.5, "norm_y": 0.5})
        assert success is True
        mock_adb.assert_called_once()


def test_api_device_action_and_task_polling():
    """Verify /api/device/:id/action and /api/device/:id/tasks end-to-end routing."""
    dev_id = "test_device_unit_001"
    DeviceHub.register_device(dev_id, "Test Unit", "windows")

    # 1. Dispatch action
    post_payload = json.dumps({"type": "hotkey", "hotkey": "vol_up"}).encode("utf-8")
    req_post = MockHandler("POST", f"/api/device/{dev_id}/action", body=post_payload)
    req_post.do_POST()
    
    post_response = req_post.wfile.getvalue().decode("utf-8")
    post_json = json.loads(post_response)
    assert post_json.get("success") is True
    assert "task_id" in post_json
    task_id = post_json["task_id"]

    # 2. Poll tasks via GET /api/device/:id/tasks
    req_get = MockHandler("GET", f"/api/device/{dev_id}/tasks")
    req_get.do_GET()
    
    get_response = req_get.wfile.getvalue().decode("utf-8")
    get_json = json.loads(get_response)
    assert "tasks" in get_json
    assert len(get_json["tasks"]) == 1
    assert get_json["tasks"][0]["hotkey"] == "vol_up"

    # 3. Report task result via POST /api/device/:id/task/:task_id/result
    res_payload = json.dumps({"success": True, "message": "Volume increased"}).encode("utf-8")
    req_res = MockHandler("POST", f"/api/device/{dev_id}/task/{task_id}/result", body=res_payload)
    req_res.do_POST()
    
    res_response = req_res.wfile.getvalue().decode("utf-8")
    res_json = json.loads(res_response)
    assert res_json.get("success") is True
    assert res_json.get("acknowledged") is True


def test_api_agent_mission_dispatch():
    """Verify /api/agent/dispatch queues autonomous missions into DeviceHub."""
    dev_id = "test_mission_pc"
    DeviceHub.register_device(dev_id, "Mission PC", "windows")

    payload = json.dumps({"objective": "Open Calculator and calculate 42", "device_id": dev_id}).encode("utf-8")
    req = MockHandler("POST", "/api/agent/dispatch", body=payload)
    req.do_POST()

    output = req.wfile.getvalue().decode("utf-8")
    data = json.loads(output)
    assert data.get("success") is True
    assert "task_id" in data

    tasks = DeviceHub.poll_actions(dev_id)
    assert len(tasks) == 1
    assert tasks[0]["type"] == "goal"
    assert "Calculator" in tasks[0]["goal"]
