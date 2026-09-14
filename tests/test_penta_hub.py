"""Unit tests for Penta-Assistant DeviceHub and Cross-Platform routing."""

import pytest
from hub.device_hub import DeviceHub

def test_device_registration():
    dev = DeviceHub.register_device(
        device_id="test_pc_1",
        name="Test PC",
        platform="windows",
        resolution=(1366, 768),
        capabilities=["screen_capture", "mouse_click"]
    )
    assert dev["device_id"] == "test_pc_1"
    assert dev["platform"] == "windows"
    assert dev["resolution"] == [1366, 768]
    assert dev["status"] == "online"

def test_device_active_list():
    DeviceHub.register_device(
        device_id="test_phone_1",
        name="Test Phone",
        platform="android",
        resolution=(1080, 2400)
    )
    devices = DeviceHub.get_active_devices(timeout_sec=10)
    ids = [d["device_id"] for d in devices]
    assert "test_phone_1" in ids

def test_action_queueing_and_polling():
    dev_id = "test_queue_device"
    DeviceHub.register_device(dev_id, "Queue Dev", "android")
    
    task_id = DeviceHub.queue_action(dev_id, {"type": "tap", "x": 100, "y": 200})
    assert task_id.startswith("penta_")
    
    tasks = DeviceHub.poll_actions(dev_id)
    assert len(tasks) == 1
    assert tasks[0]["type"] == "tap"
    assert tasks[0]["x"] == 100
    
    # Polling again should be empty
    assert DeviceHub.poll_actions(dev_id) == []

def test_coordinate_normalization():
    # Test Windows scaling: normalized (0.5, 0.5) -> (682 or 683, 384)
    px, py = DeviceHub.normalize_coordinates("windows", 0.5, 0.5, (1366, 768))
    assert px in (682, 683)
    assert py in (383, 384)

    # Test Android scaling: normalized (0.0, 1.0) -> (0, 2399)
    px, py = DeviceHub.normalize_coordinates("android", 0.0, 1.0, (1080, 2400))
    assert px == 0
    assert py == 2399

def test_frame_buffer_cache():
    dev_id = "test_frame_dev"
    sample_frame = b"FAKE_JPEG_FRAME_DATA"
    DeviceHub.set_frame(dev_id, sample_frame)
    retrieved = DeviceHub.get_frame(dev_id)
    assert retrieved == sample_frame

def test_android_package_map():
    assert "settings" in DeviceHub.ANDROID_APP_PACKAGES
    assert "chrome" in DeviceHub.ANDROID_APP_PACKAGES
    assert DeviceHub.ANDROID_APP_PACKAGES["settings"] == "com.android.settings"
