# tests/test_patterns.py
from backend.app.fraud.card_testing import detect_card_testing

def test_detect_card_testing_velocity():
    flagged_txn = {"id": "T4", "amount": 200.0, "ts": 3605}
    # 3 small authorizations within 3600 seconds
    recent_txns = [
        {"id": "T1", "amount": 1.0, "ts": 10},
        {"id": "T2", "amount": 2.5, "ts": 600},
        {"id": "T3", "amount": 0.5, "ts": 1200}
    ]
    
    matched, details = detect_card_testing(flagged_txn, recent_txns)
    
    assert matched is True
    assert details["small_txn_count"] >= 3
    assert details["trigger_amount"] == 200.0