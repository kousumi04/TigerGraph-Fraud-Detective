# backend/app/fraud/new_device.py
from typing import Dict, Any, Tuple

def detect_new_device(
    flagged_txn: Dict[str, Any],
    device_profile: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    """
    Identifies if transaction originated from an unrecognized device profile,
    new hardware footprint, or proxy/emulator.
    """
    if not device_profile:
        return False, {"matched": False, "reason": "no_device_profile"}

    is_new = bool(device_profile.get("is_new", False))
    device_type = str(device_profile.get("device_type", "")).lower()
    has_proxy = bool(device_profile.get("proxy_detected", False))
    
    channel = str(flagged_txn.get("channel", "")).lower()
    is_remote = any(k in channel for k in ["w", "online", "mobile", "app"])

    matched = is_new and is_remote

    return matched, {
        "matched": matched,
        "is_new": is_new,
        "device_type": device_type,
        "proxy_detected": has_proxy,
        "channel": channel
    }