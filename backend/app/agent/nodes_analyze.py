# backend/app/agent/nodes_analyze.py
from typing import Dict, Any
from ..models.state import InvestigationState
from ..rag.evidence_builder import build_evidence_packet, format_evidence_for_prompt
from .llm_client import assess_evidence_with_llm
from ..policy.evaluator import PolicyEngine
from ..fraud.scoring import FraudScorer

def evaluate_evidence(state: InvestigationState) -> Dict[str, Any]:
    """Builds the evidence packet and invokes the LLM for structured reasoning."""
    packet = build_evidence_packet(state)
    packet_str = format_evidence_for_prompt(packet)
    
    try:
        assessment = assess_evidence_with_llm(packet_str)
        # Combine deterministic scoring with LLM interpretation
        base_prob, _ = FraudScorer.calculate_probability(
            detector_results={"card_not_present": True}, # Mocked deterministic output for state flow
            graph_signals={"shares_device_with_fraud": len(state.get("prior_cases", [])) > 0}
        )
        
        final_prob = (base_prob + assessment.fraud_probability) / 2
        
        return {
            "evidence_packet": packet,
            "pattern_candidates": [assessment.pattern],
            "fraud_probability_initial": final_prob,
            "fraud_probability_final": final_prob, # Can be updated if evidence is requested
            "uncertainty": assessment.requires_more_evidence,
            "tool_calls": state.get("tool_calls", 0) + 1
        }
    except Exception as e:
        return {"errors": state.get("errors", []) + [str(e)]}

def check_policy(state: InvestigationState) -> Dict[str, Any]:
    """Runs deterministic policy evaluation over the current state probabilities."""
    engine = PolicyEngine()
    context = {
        "fraud_probability": state.get("fraud_probability_final", 0.0),
        "pattern": state.get("pattern_candidates", ["none"])[0],
        "exposure_usd": sum(t.get("amount", 0) for t in state.get("transaction_evidence", [])),
        "customer_response": state.get("evidence_responses", [{}])[-1].get("status") if state.get("evidence_responses") else None
    }
    
    actions = engine.evaluate_policy(context)
    return {
        "initial_actions": state.get("initial_actions") or actions,
        "final_actions": actions,
        "sar_required": any(a.action == "FILE_REPORT" for a in actions)
    }