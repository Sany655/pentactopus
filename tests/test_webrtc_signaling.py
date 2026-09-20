"""Test WebRTC Signaling Relay & Session Exchange."""

import pytest
from api.webrtc_signaling import SignalingHub

def test_signaling_push_and_poll():
    target = "test_target_dev_1"
    sender = "test_sender_dev_1"
    payload = {"type": "offer", "sdp": "v=0..."}

    # Ensure queue is clean initially
    SignalingHub.poll_signals(target)

    # Push signal
    SignalingHub.push_signal(target, sender, "offer", payload)

    # Poll signals
    signals = SignalingHub.poll_signals(target)
    assert len(signals) == 1
    assert signals[0]["type"] == "offer"
    assert signals[0]["sender"] == sender
    assert signals[0]["payload"] == payload

    # Subsequent poll should be empty
    subsequent = SignalingHub.poll_signals(target)
    assert len(subsequent) == 0

def test_signaling_isolation_between_targets():
    target_a = "device_alpha"
    target_b = "device_beta"

    SignalingHub.push_signal(target_a, "sender_1", "ice", {"candidate": "cand_a"})
    SignalingHub.push_signal(target_b, "sender_2", "ice", {"candidate": "cand_b"})

    signals_a = SignalingHub.poll_signals(target_a)
    assert len(signals_a) == 1
    assert signals_a[0]["payload"]["candidate"] == "cand_a"

    signals_b = SignalingHub.poll_signals(target_b)
    assert len(signals_b) == 1
    assert signals_b[0]["payload"]["candidate"] == "cand_b"

def test_empty_poll_returns_empty_list():
    assert SignalingHub.poll_signals("non_existent_target") == []
