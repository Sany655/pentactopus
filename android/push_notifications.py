"""Firebase Cloud Messaging push notification sender."""
import os
import json
import urllib.request
from typing import Optional, Dict, Any

FCM_URL = "https://fcm.googleapis.com/fcm/send"

def send_push(device_token: str, title: str, body: str, data: Optional[Dict[str, Any]] = None) -> dict:
    """Send a push notification to an Android device via FCM."""
    server_key = os.environ.get("FCM_SERVER_KEY", "")
    if not server_key:
        return {"success": False, "error": "FCM_SERVER_KEY not configured"}

    payload = json.dumps({
        "to": device_token,
        "notification": {"title": title, "body": body},
        "data": data or {}
    }).encode("utf-8")

    req = urllib.request.Request(
        FCM_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"key={server_key}"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"success": False, "error": str(e)}
