# backend/app/fraud/out_of_region.py
from typing import List, Dict, Any, Tuple

def detect_out_of_region(
    flagged_txn: Dict[str, Any],
    historical_regions: List[str]
) -> Tuple[bool, Dict[str, Any]]:
    """
    Compares billing region against historical regions to spot non-local usage.
    """
    current_region = str(flagged_txn.get("billing_region", "")).strip()
    if not current_region or not historical_regions:
        return False, {"matched": False, "reason": "missing_region_data"}

    norm_historical = [str(r).strip().lower() for r in historical_regions if r]
    norm_current = current_region.lower()

    is_new_region = norm_current not in norm_historical

    return is_new_region, {
        "matched": is_new_region,
        "current_region": current_region,
        "known_regions": list(set(historical_regions))
    }