# backend/app/fraud/account_takeover.py
from typing import Dict, Any, Tuple

def detect_account_takeover(
    device_meta: Dict[str, Any],
    email_meta: Dict[str, Any],
    customer_context: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    """
    Detects signals indicating account takeover:
    Sudden credential/device shifts combined with rapid transaction triggers.
    """
    device_new = device_meta.get("is_new", False)
    email_domain_mismatch = email_meta.get("is_disposable_or_unrecognized", False)
    account_age_days = customer_context.get("account_age", 365)

    ato_score = 0
    if device_new:
        ato_score += 1
    if email_domain_mismatch:
        ato_score += 1
    if account_age_days > 180 and (device_new and email_domain_mismatch):
        ato_score += 2

    matched = ato_score >= 2

    return matched, {
        "matched": matched,
        "ato_indicator_score": ato_score,
        "device_new": device_new,
        "email_mismatch": email_domain_mismatch
    }