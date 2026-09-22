# tests/test_policy.py
import pytest
from backend.app.policy.evaluator import PolicyEngine

def test_r7_mandatory_sar_high_exposure():
    engine = PolicyEngine()
    # Context triggering R7 (Exposure >= $5000)
    context = {
        "exposure_usd": 5500.0,
        "fraud_probability": 0.60,
        "pattern": "card_not_present",
        "customer_response": None
    }
    
    actions = engine.evaluate_policy(context)
    action_types = [a.action for a in actions]
    
    assert "FILE_REPORT" in action_types, "R7 failed: High exposure did not trigger mandatory SAR."
    sar_action = next(a for a in actions if a.action == "FILE_REPORT")
    assert sar_action.route == "L2", "R7 failed: SAR must route to L2."

def test_r9_customer_denial_blocks_cards():
    engine = PolicyEngine()
    # Context triggering R9 (Customer denied)
    context = {
        "exposure_usd": 150.0,
        "fraud_probability": 0.50,
        "customer_response": "denied"
    }
    
    actions = engine.evaluate_policy(context)
    action_types = [a.action for a in actions]
    
    assert "BLOCK_ALL_CARDS" in action_types, "R9 failed: Customer denial did not block cards."

def test_r1_low_risk_closure():
    engine = PolicyEngine()
    # Context triggering R1 (Low risk, no anomalies)
    context = {
        "exposure_usd": 50.0,
        "fraud_probability": 0.10,
        "anomalies_present": False
    }
    
    actions = engine.evaluate_policy(context)
    assert any(a.action == "CLOSE_NO_FRAUD" for a in actions), "R1 failed: Low risk was not closed."