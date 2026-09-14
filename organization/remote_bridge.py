"""Remote Device Bridge for Outbound Mobile Connections.

Handles telemetry and task queueing for devices operating outside the local Wi-Fi,
such as phones connected over 4G/5G mobile data, remote subnets, or cloud-hosted hubs.
"""

import time
from typing import Dict, Any, List, Optional

class RemoteDeviceRegistry:
    _devices: Dict[str, Dict[str, Any]] = {}
    _task_queues: Dict[str, List[Dict[str, Any]]] = {}

    @classmethod
    def register_or_update(cls, device_id: str, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        telemetry["last_seen"] = time.time()
        cls._devices[device_id] = telemetry
        if device_id not in cls._task_queues:
            cls._task_queues[device_id] = []
        return {"status": "ok", "device_id": device_id}

    @classmethod
    def queue_task(cls, device_id: str, action: Dict[str, Any]) -> str:
        if device_id not in cls._task_queues:
            cls._task_queues[device_id] = []
        task_id = f"task_{int(time.time()*1000)}"
        action["task_id"] = task_id
        action["queued_at"] = time.time()
        cls._task_queues[device_id].append(action)
        return task_id

    @classmethod
    def poll_tasks(cls, device_id: str) -> List[Dict[str, Any]]:
        if device_id not in cls._task_queues:
            return []
        pending = cls._task_queues[device_id]
        cls._task_queues[device_id] = []
        return pending

    @classmethod
    def get_active_devices(cls, timeout_sec: int = 60) -> List[Dict[str, Any]]:
        now = time.time()
        active = []
        for dev_id, data in cls._devices.items():
            if now - data.get("last_seen", 0) <= timeout_sec:
                dev_copy = dict(data)
                dev_copy["device_id"] = dev_id
                dev_copy["online"] = True
                active.append(dev_copy)
        return active
