# backend/app/agent/nodes_analyze.py
from typing import Dict, Any
from ..models.state import InvestigationState
from ..rag.evidence_builder import build_evidence_packet, format_evidence_for_prompt
from .llm_client import assess_evidence_with_llm
from ..policy.evaluator import PolicyEngine
from ..fraud.scoring import FraudScorer
from ..fraud.card_testing import detect_card_testing
from ..fraud.card_not_present import detect_card_not_present
from ..fraud.out_of_region import detect_out_of_region


def _deterministic_patterns(state: InvestigationState) -> dict[str, bool]:
    flagged = state.get("flagged_transaction", {})
    history = state.get("customer_context", {}).get("history", [])
    previous = [tx for tx in history if tx.get("id") != flagged.get("id")]

    card_testing, _ = detect_card_testing(flagged, previous)
    cnp, _ = detect_card_not_present(flagged, previous)
    regions = [tx.get("billing_region") for tx in previous if tx.get("billing_region")]
    out_of_region, _ = detect_out_of_region(flagged, regions)

    channel = str(flagged.get("channel", "")).lower()
    trigger_type = str(state.get("trigger", {}).get("trigger_type", ""))
    patterns = {
        "card_testing": card_testing,
        "card_not_present_new_device": False,
        "card_not_present": cnp,
        "out_of_region_use": out_of_region and "online" not in channel,
        "account_takeover": trigger_type == "customer_report" and len(previous) >= 2 and cnp,
    }
    return patterns

def evaluate_evidence(state: InvestigationState) -> Dict[str, Any]:
    packet = build_evidence_packet(state)
    packet_str = format_evidence_for_prompt(packet)
    
    patterns = _deterministic_patterns(state)
    matched = [name for name, value in patterns.items() if value]
    pattern_name = matched[0] if matched else "none"
    prior_fraud = any(c.get("verdict") == "fraud" for c in state.get("prior_cases", []))
    risk_score = state.get("flagged_transaction", {}).get("risk_score")
    graph_signals = {"shares_device_with_fraud": prior_fraud}
    if risk_score is not None:
        graph_signals["risk_score"] = float(risk_score)

    final_prob, _ = FraudScorer.calculate_probability(
        detector_results=patterns,
        graph_signals=graph_signals,
    )

    # The model is advisory. It may explain the packet, but it must not turn
    # missing/default graph data into a fraud verdict or overwrite signals
    # computed from the actual dataset.
    tokens = 0
    try:
        assessment, tokens = assess_evidence_with_llm(packet_str)
    except Exception:
        pass

    return {
            "evidence_packet": packet,
            "pattern_candidates": [pattern_name],
            "fraud_probability_initial": final_prob,
            "fraud_probability_final": final_prob,
            "uncertainty": not matched and final_prob < 0.70,
            "tool_calls": state.get("tool_calls", 0) + 1,
            "tokens": state.get("tokens", 0) + tokens
        }

def reassess_probability(state: InvestigationState) -> Dict[str, Any]:
    """Recomputes final probability incorporating the simulated response."""
    last_response = state.get("evidence_responses", [{}])[-1]
    pattern_name = state.get("pattern_candidates", ["none"])[0]
    
    recalc_prob, _ = FraudScorer.calculate_probability(
        detector_results={pattern_name: pattern_name != "none"},
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
