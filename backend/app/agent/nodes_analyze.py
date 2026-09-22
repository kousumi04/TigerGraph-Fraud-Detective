# backend/app/agent/nodes_analyze.py
from typing import Dict, Any
from ..models.state import InvestigationState
from ..rag.evidence_builder import build_evidence_packet, format_evidence_for_prompt
from .llm_client import assess_evidence_with_llm
from ..policy.evaluator import PolicyEngine
from ..fraud.scoring import FraudScorer

def evaluate_evidence(state: InvestigationState) -> Dict[str, Any]:
    packet = build_evidence_packet(state)
    packet_str = format_evidence_for_prompt(packet)
    
    try:
        assessment, tokens = assess_evidence_with_llm(packet_str)
        pattern_name = assessment.pattern if assessment.pattern else "none"
        
        base_prob, _ = FraudScorer.calculate_probability(
            detector_results={pattern_name: True},
            graph_signals={"shares_device_with_fraud": len(state.get("prior_cases", [])) > 0}
        )
        
        final_prob = round((base_prob + assessment.fraud_probability) / 2, 4)
        
        return {
            "evidence_packet": packet,
            "pattern_candidates": [pattern_name],
            "fraud_probability_initial": final_prob,
            "fraud_probability_final": final_prob,
            "uncertainty": assessment.requires_more_evidence,
            "tool_calls": state.get("tool_calls", 0) + 1,
            "tokens": state.get("tokens", 0) + tokens
        }
    except Exception as e:
        return {"errors": state.get("errors", []) + [str(e)]}

def reassess_probability(state: InvestigationState) -> Dict[str, Any]:
    """Recomputes final probability incorporating the simulated response."""
    last_response = state.get("evidence_responses", [{}])[-1]
    pattern_name = state.get("pattern_candidates", ["none"])[0]
    
    recalc_prob, _ = FraudScorer.calculate_probability(
        detector_results={pattern_name: True},
        graph_signals={"shares_device_with_fraud": len(state.get("prior_cases", [])) > 0},
        simulation_signal=last_response
    )
    
    return {
        "fraud_probability_final": recalc_prob,
        "uncertainty": False,
        "tool_calls": state.get("tool_calls", 0) + 1
    }

def check_policy(state: InvestigationState) -> Dict[str, Any]:
    engine = PolicyEngine()
    exposure = sum(t.get("amount", 0) for t in state.get("transaction_evidence", []))
    last_response = state.get("evidence_responses", [{}])[-1] if state.get("evidence_responses") else None
    
    context = {
        "fraud_probability": state.get("fraud_probability_final", 0.0),
        "pattern": state.get("pattern_candidates", ["none"])[0],
        "exposure_usd": exposure,
        "connected_card_ids": state.get("connected_card_evidence", []),
        "customer_response": last_response.get("status") if last_response else None
    }
    
    actions = engine.evaluate_policy(context)
    return {
        "initial_actions": state.get("initial_actions") or actions,
        "final_actions": actions,
        "sar_required": any(a.action == "FILE_REPORT" for a in actions)
    }