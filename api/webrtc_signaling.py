"""WebRTC Signaling Relay for Pentactopus Mesh.

Provides an HTTP-based signaling exchange to establish P2P WebRTC data channels
between Windows Host Agents and Android/Web Remote Clients.
Works within Vercel Serverless constraints by using a polling queue.
"""

import time
from typing import Dict, List, Any

class SignalingHub:
    # In-memory store for signaling messages.
    # Format: { "device_id_or_session_id": [ {type, sender, payload, timestamp}, ... ] }
    _messages: Dict[str, List[Dict[str, Any]]] = {}

    @classmethod
    def push_signal(cls, target_id: str, sender_id: str, signal_type: str, payload: Any) -> None:
        """Push a signaling message (offer, answer, or ice) to the target's queue."""
        if target_id not in cls._messages:
            cls._messages[target_id] = []
        
        cls._messages[target_id].append({
            "type": signal_type,
            "sender": sender_id,
            "payload": payload,
            "timestamp": time.time()
        })
        
        # Cleanup old messages to prevent memory leaks in serverless warm instances
        cls._cleanup_stale()

    @classmethod
    def poll_signals(cls, target_id: str) -> List[Dict[str, Any]]:
        """Retrieve and clear pending signals for a target."""
        if target_id not in cls._messages:
            return []
        
        msgs = cls._messages[target_id]
        cls._messages[target_id] = []
        return msgs

    @classmethod
    def _cleanup_stale(cls) -> None:
        """Remove signals older than 5 minutes."""
        now = time.time()
        for target, msgs in list(cls._messages.items()):
            valid_msgs = [m for m in msgs if now - m["timestamp"] < 300]
            if valid_msgs:
                cls._messages[target] = valid_msgs
            else:
                del cls._messages[target]
