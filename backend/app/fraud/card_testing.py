# backend/app/fraud/card_testing.py
from typing import List, Dict, Any, Tuple
from datetime import datetime

def detect_card_testing(
    flagged_txn: Dict[str, Any],
    recent_txns: List[Dict[str, Any]],
    small_amount_threshold: float = 15.0,
    window_seconds: int = 3600
) -> Tuple[bool, Dict[str, Any]]:
    """
    Detects card testing behavior:
    3+ small authorizations within ~1 hour followed by a larger transaction.
    """
    if not recent_txns:
        return False, {"reason": "insufficient_transactions"}

    all_txns = sorted(
        recent_txns + ([flagged_txn] if flagged_txn not in recent_txns else []),
        key=lambda x: x.get("ts", 0)
    )

    small_txns = []
    for txn in all_txns:
        amount = float(txn.get("amount", 0.0))
        if amount <= small_amount_threshold:
            small_txns.append(txn)

    # Check for clusters within window_seconds
    for i in range(len(small_txns)):
        window = [small_txns[i]]
        t_start = small_txns[i].get("ts", 0)
        
        for j in range(i + 1, len(small_txns)):
            t_curr = small_txns[j].get("ts", 0)
            if isinstance(t_start, (int, float)) and isinstance(t_curr, (int, float)):
                if (t_curr - t_start) <= window_seconds:
                    window.append(small_txns[j])
            elif isinstance(t_start, str) and isinstance(t_curr, str):
                try:
                    dt_start = datetime.fromisoformat(t_start)
                    dt_curr = datetime.fromisoformat(t_curr)
                    if (dt_curr - dt_start).total_seconds() <= window_seconds:
                        window.append(small_txns[j])
                except ValueError:
                    pass

        if len(window) >= 3:
            flagged_amount = float(flagged_txn.get("amount", 0.0))
            if flagged_amount > small_amount_threshold:
                return True, {
                    "matched": True,
                    "small_txn_count": len(window),
                    "trigger_amount": flagged_amount,
                    "window_sample_ids": [t.get("id") or t.get("TransactionID") for t in window]
                }

    return False, {"matched": False}