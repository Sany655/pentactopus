"""Central Device Hub for Penta-Assistant.

Coordinates device registration, session pairing, action queueing,
frame buffering, and normalized cross-platform input dispatch across
Windows PC, Android Phone, and Cloud Nodes.
"""

import time
from typing import Dict, Any, List, Optional, Tuple

class DeviceHub:
    """In-memory state and action dispatcher for Penta-Assistant nodes."""
    
    _devices: Dict[str, Dict[str, Any]] = {}
    _action_queues: Dict[str, List[Dict[str, Any]]] = {}
    _frame_buffers: Dict[str, bytes] = {}
    
    # Common package names for Android quick-launch
    ANDROID_APP_PACKAGES = {
        "settings": "com.android.settings",
        "chrome": "com.android.chrome",
        "camera": "com.android.camera",
        "youtube": "com.google.android.youtube",
        "calculator": "com.android.calculator2",
        "dialer": "com.google.android.dialer",
        "whatsapp": "com.whatsapp",
        "files": "com.google.android.documentsui",
        "messages": "com.google.android.apps.messaging",
    }

    @classmethod
    def register_device(
        cls,
        device_id: str,
        name: str,
        platform: str,
        resolution: Tuple[int, int] = (1080, 2400),
        capabilities: Optional[List[str]] = None,
        connection_type: str = "local"
    ) -> Dict[str, Any]:
        """Register or update a connected device."""
        if capabilities is None:
            capabilities = ["screen_capture", "input_injection", "ai_agent"]
            
        cls._devices[device_id] = {
            "device_id": device_id,
            "name": name,
            "platform": platform.lower(),
            "resolution": list(resolution),
            "capabilities": capabilities,
            "connection_type": connection_type,
            "last_seen": time.time(),
            "status": "online"
        }
        if device_id not in cls._action_queues:
            cls._action_queues[device_id] = []
            
        return cls._devices[device_id]

    @classmethod
    def update_heartbeat(cls, device_id: str, telemetry: Optional[Dict[str, Any]] = None) -> bool:
        """Update last seen timestamp and optional telemetry."""
        if device_id in cls._devices:
            cls._devices[device_id]["last_seen"] = time.time()
            cls._devices[device_id]["status"] = "online"
            if telemetry:
                cls._devices[device_id].update(telemetry)
            return True
        return False

    @classmethod
    def set_frame(cls, device_id: str, frame_bytes: bytes) -> None:
        """Cache the latest JPEG screen frame for a device."""
        if frame_bytes:
            cls._frame_buffers[device_id] = frame_bytes
            if device_id in cls._devices:
                cls._devices[device_id]["last_seen"] = time.time()

    @classmethod
    def get_frame(cls, device_id: str) -> Optional[bytes]:
        """Retrieve the latest cached screen frame for a device."""
        return cls._frame_buffers.get(device_id)

    @classmethod
    def queue_action(cls, device_id: str, action: Dict[str, Any]) -> str:
        """Queue an action to be executed on a remote device."""
        if device_id not in cls._action_queues:
            cls._action_queues[device_id] = []
            
        task_id = f"penta_{int(time.time() * 1000)}"
        action["task_id"] = task_id
        action["created_at"] = time.time()
        cls._action_queues[device_id].append(action)
        return task_id

    @classmethod
    def poll_actions(cls, device_id: str) -> List[Dict[str, Any]]:
        """Retrieve and clear queued actions for a device."""
        if device_id not in cls._action_queues:
            return []
        pending = cls._action_queues[device_id]
        cls._action_queues[device_id] = []
        return pending

    @classmethod
    def get_active_devices(cls, timeout_sec: int = 60) -> List[Dict[str, Any]]:
        """List all active devices seen within the timeout period."""
        now = time.time()
        active = []
        for dev_id, dev_data in cls._devices.items():
            is_active = (now - dev_data.get("last_seen", 0)) <= timeout_sec
            item = dict(dev_data)
            item["status"] = "online" if is_active else "offline"
            active.append(item)
        return active

    @classmethod
    def get_device(cls, device_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific device."""
        return cls._devices.get(device_id)

    @classmethod
    def normalize_coordinates(
        cls,
        platform: str,
        norm_x: float,
        norm_y: float,
        resolution: Optional[Tuple[int, int]] = None
    ) -> Tuple[int, int]:
        """Scale normalized [0.0, 1.0] coordinates to absolute pixel coordinates."""
        norm_x = max(0.0, min(1.0, float(norm_x)))
        norm_y = max(0.0, min(1.0, float(norm_y)))
        
        if resolution:
            w, h = resolution
        elif platform == "windows":
            w, h = 1366, 768
        else:
            w, h = 1080, 2160
            
        px = int(round(norm_x * (w - 1)))
        py = int(round(norm_y * (h - 1)))
        return px, py
