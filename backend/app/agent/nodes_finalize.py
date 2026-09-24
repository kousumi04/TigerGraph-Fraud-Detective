# backend/app/agent/nodes_finalize.py
from typing import Dict, Any
from ..models.state import InvestigationState

def request_and_simulate_evidence(state: InvestigationState) -> Dict[str, Any]:
    trigger_type = state.get("trigger", {}).get("trigger_type")
    status = "denied" if trigger_type == "customer_report" else "timeout"
    req = {
        "type": "customer_validation",
        "asked_after_step": state.get("tool_calls", 0),
        "assumed_response": f"Simulation: {status}"
    }
    response = {"status": status, "source": "simulated_customer"}
    
    return {
        "evidence_requests": state.get("evidence_requests", []) + [req],
        "evidence_responses": state.get("evidence_responses", []) + [response]
    }

def finalize_case(state: InvestigationState) -> Dict[str, Any]:
    prob = state.get("fraud_probability_final", 0.0)
    
    if prob >= 0.85:
        verdict = "fraud"
        status = "closed_fraud"
    elif prob <= 0.15:
        verdict = "legitimate"
        status = "closed_legitimate"
    else:
        verdict = "uncertain"
        status = "escalated"
        
    return {
        "stop_reason": "Policy thresholds met or maximum evidence gathered.",
        "graph_case_id": f"TG-{state.get('case_id')}",
        "verdict": verdict,
        "status": status,
    }
