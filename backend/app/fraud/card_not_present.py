# backend/app/fraud/card_not_present.py
from typing import List, Dict, Any, Tuple

def detect_card_not_present(
    flagged_txn: Dict[str, Any],
    historical_txns: List[Dict[str, Any]],
    amount_multiplier: float = 3.0
) -> Tuple[bool, Dict[str, Any]]:
    """
    Detects suspicious Card-Not-Present (CNP) fraud:
    Online/digital channel combined with anomalous transaction volume or amount spikes.
    """
    channel = str(flagged_txn.get("channel", "")).lower()
    is_digital = any(k in channel for k in ["w", "online", "web", "ecommerce", "cnp"])
    
    if not is_digital:
        return False, {"matched": False, "reason": "not_digital_channel"}

    flagged_amount = float(flagged_txn.get("amount", 0.0))
    if not historical_txns:
        return flagged_amount > 200.0, {
            "matched": flagged_amount > 200.0,
            "reason": "new_channel_no_history"
        }

    historical_amounts = [float(t.get("amount", 0.0)) for t in historical_txns if float(t.get("amount", 0.0)) > 0]
    if not historical_amounts:
        avg_amount = 50.0
    else:
        avg_amount = sum(historical_amounts) / len(historical_amounts)

    is_spike = flagged_amount >= (avg_amount * amount_multiplier)
    
    return is_spike, {
        "matched": is_spike,
        "historical_avg": round(avg_amount, 2),
        "flagged_amount": flagged_amount,
        "spike_factor": round(flagged_amount / avg_amount, 2) if avg_amount > 0 else 0
    }