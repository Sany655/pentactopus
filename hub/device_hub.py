"""Central Device Hub for Penta-Assistant.

Coordinates device registration, session pairing, action queueing,
frame buffering, and normalized cross-platform input dispatch across
Windows PC, Android Phone, and Cloud Nodes.

Persistence Strategy:
  - When UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN env vars are set,
    device registrations and action queues are stored in Upstash KV (Redis-over-HTTP).
    This survives across Vercel serverless invocations.
  - Without those env vars, falls back to in-memory class attributes (local dev mode).
  - Frame buffers (JPEG bytes) always use in-memory (too large/transient for KV).
"""

import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Optional Upstash Redis KV backend
# ---------------------------------------------------------------------------

_KV_URL = os.getenv("UPSTASH_REDIS_REST_URL", "")
_KV_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN", "")
_KV_ENABLED = bool(_KV_URL and _KV_TOKEN)

def _kv_get(key: str):
    """GET a key from Upstash KV. Returns Python object or None."""
    if not _KV_ENABLED:
        return None
    try:
        import urllib.request
        req = urllib.request.Request(
            f"{_KV_URL}/get/{key}",
            headers={"Authorization": f"Bearer {_KV_TOKEN}"}
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            body = json.loads(resp.read().decode())
            raw = body.get("result")
            if raw is None:
                return None
            return json.loads(raw)
    except Exception:
        return None


def _kv_set(key: str, value, ex: int = 3600) -> bool:
    """SET a key in Upstash KV with TTL (seconds). Returns True on success."""
    if not _KV_ENABLED:
        return False
    try:
        import urllib.request
        serialized = json.dumps(value)
        # Use SET with EX
        url = f"{_KV_URL}/set/{key}/{urllib.parse.quote(serialized, safe='')}/ex/{ex}"
        import urllib.parse
        url = f"{_KV_URL}/set/{urllib.parse.quote(key, safe='')}"
        data = json.dumps({"value": serialized, "ex": ex}).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {_KV_TOKEN}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            return True
    except Exception:
        return False


def _kv_pipeline_set(key: str, value, ex: int = 3600) -> bool:
    """SET a key via Upstash pipeline REST API."""
    if not _KV_ENABLED:
        return False
    try:
        import urllib.request
        serialized = json.dumps(value)
        commands = [["SET", key, serialized, "EX", str(ex)]]
        data = json.dumps(commands).encode()
        req = urllib.request.Request(
            f"{_KV_URL}/pipeline",
            data=data,
            headers={
                "Authorization": f"Bearer {_KV_TOKEN}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3):
            return True
    except Exception:
        return False


def _kv_del(key: str) -> bool:
    """DEL a key from Upstash KV."""
    if not _KV_ENABLED:
        return False
    try:
        import urllib.request
        req = urllib.request.Request(
            f"{_KV_URL}/del/{key}",
            headers={"Authorization": f"Bearer {_KV_TOKEN}"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3):
            return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# DeviceHub
# ---------------------------------------------------------------------------

class DeviceHub:
    """In-memory + Upstash KV state and action dispatcher for Penta-Assistant nodes."""

    # Fallback in-memory stores (used when KV is not configured)
    _devices: Dict[str, Dict[str, Any]] = {}
    _action_queues: Dict[str, List[Dict[str, Any]]] = {}
    _frame_buffers: Dict[str, bytes] = {}  # Always in-memory (binary, too large for KV)

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

    # KV key prefixes
    _KV_DEVICE_PREFIX = "penta:device:"
    _KV_QUEUE_PREFIX = "penta:queue:"
    _KV_DEVICE_LIST = "penta:device_ids"

    # ---------------------------------------------------------------------------
    # Internal KV helpers
    # ---------------------------------------------------------------------------

    @classmethod
    def _get_device_kv(cls, device_id: str) -> Optional[Dict[str, Any]]:
        return _kv_get(f"{cls._KV_DEVICE_PREFIX}{device_id}")

    @classmethod
    def _set_device_kv(cls, device_id: str, data: Dict[str, Any]) -> None:
        _kv_pipeline_set(f"{cls._KV_DEVICE_PREFIX}{device_id}", data, ex=7200)
        # Update index
        ids = _kv_get(cls._KV_DEVICE_LIST) or []
        if device_id not in ids:
            ids.append(device_id)
            _kv_pipeline_set(cls._KV_DEVICE_LIST, ids, ex=7200)

    @classmethod
    def _get_queue_kv(cls, device_id: str) -> List[Dict[str, Any]]:
        return _kv_get(f"{cls._KV_QUEUE_PREFIX}{device_id}") or []

    @classmethod
    def _set_queue_kv(cls, device_id: str, queue: List[Dict[str, Any]]) -> None:
        _kv_pipeline_set(f"{cls._KV_QUEUE_PREFIX}{device_id}", queue, ex=3600)

    # ---------------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------------

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

        device_data = {
            "device_id": device_id,
            "name": name,
            "platform": platform.lower(),
            "resolution": list(resolution),
            "capabilities": capabilities,
            "connection_type": connection_type,
            "last_seen": time.time(),
            "status": "online"
        }

        if _KV_ENABLED:
            cls._set_device_kv(device_id, device_data)
        else:
            cls._devices[device_id] = device_data
            if device_id not in cls._action_queues:
                cls._action_queues[device_id] = []

        return device_data

    @classmethod
    def update_heartbeat(cls, device_id: str, telemetry: Optional[Dict[str, Any]] = None) -> bool:
        """Update last seen timestamp and optional telemetry."""
        if _KV_ENABLED:
            dev = cls._get_device_kv(device_id)
            if dev is None:
                return False
            dev["last_seen"] = time.time()
            dev["status"] = "online"
            if telemetry:
                dev.update(telemetry)
            cls._set_device_kv(device_id, dev)
            return True
        else:
            if device_id in cls._devices:
                cls._devices[device_id]["last_seen"] = time.time()
                cls._devices[device_id]["status"] = "online"
                if telemetry:
                    cls._devices[device_id].update(telemetry)
                return True
            return False

    @classmethod
    def set_frame(cls, device_id: str, frame_bytes: bytes) -> None:
        """Cache the latest JPEG screen frame for a device (always in-memory)."""
        if frame_bytes:
            cls._frame_buffers[device_id] = frame_bytes
            # Also bump last_seen
            if _KV_ENABLED:
                dev = cls._get_device_kv(device_id)
                if dev:
                    dev["last_seen"] = time.time()
                    cls._set_device_kv(device_id, dev)
            elif device_id in cls._devices:
                cls._devices[device_id]["last_seen"] = time.time()

    @classmethod
    def get_frame(cls, device_id: str) -> Optional[bytes]:
        """Retrieve the latest cached screen frame for a device."""
        return cls._frame_buffers.get(device_id)

    @classmethod
    def queue_action(cls, device_id: str, action: Dict[str, Any]) -> str:
        """Queue an action to be executed on a remote device."""
        task_id = f"penta_{int(time.time() * 1000)}"
        action["task_id"] = task_id
        action["created_at"] = time.time()

        if _KV_ENABLED:
            queue = cls._get_queue_kv(device_id)
            queue.append(action)
            cls._set_queue_kv(device_id, queue)
        else:
            if device_id not in cls._action_queues:
                cls._action_queues[device_id] = []
            cls._action_queues[device_id].append(action)

        return task_id

    @classmethod
    def poll_actions(cls, device_id: str) -> List[Dict[str, Any]]:
        """Retrieve and clear queued actions for a device."""
        if _KV_ENABLED:
            pending = cls._get_queue_kv(device_id)
            if pending:
                cls._set_queue_kv(device_id, [])
            return pending
        else:
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

        if _KV_ENABLED:
            ids = _kv_get(cls._KV_DEVICE_LIST) or []
            for dev_id in ids:
                dev_data = cls._get_device_kv(dev_id)
                if dev_data:
                    is_active = (now - dev_data.get("last_seen", 0)) <= timeout_sec
                    item = dict(dev_data)
                    item["status"] = "online" if is_active else "offline"
                    active.append(item)
        else:
            for dev_id, dev_data in cls._devices.items():
                is_active = (now - dev_data.get("last_seen", 0)) <= timeout_sec
                item = dict(dev_data)
                item["status"] = "online" if is_active else "offline"
                active.append(item)

        return active

    @classmethod
    def get_device(cls, device_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific device."""
        if _KV_ENABLED:
            return cls._get_device_kv(device_id)
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
