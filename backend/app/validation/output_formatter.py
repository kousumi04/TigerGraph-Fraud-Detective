# backend/app/validation/output_formatter.py
from typing import Dict, Any
from ..models.schemas import BenchmarkCaseOutput, CaseDetails, NextBestActions, Action
from ..models.state import InvestigationState
from .sar_generator import generate_sar

def format_benchmark_output(state: InvestigationState) -> BenchmarkCaseOutput:
    """
    Converts the final LangGraph state into the strict JSON schema required for the benchmark cases.
    """
    txns = state.get("transaction_evidence", [])
    exposure = sum(float(t.get("amount", 0.0)) for t in txns)
    affected_ids = [str(t.get("id", "")) for t in txns if t.get("status") == "flagged"]
    
    first_suspicious = affected_ids[0] if affected_ids else ""
    
    # Map actions
    initial_acts = [Action(**a) if isinstance(a, dict) else a for a in state.get("initial_actions", [])]
    final_acts = [Action(**a) if isinstance(a, dict) else a for a in state.get("final_actions", [])]
    
    case_details = CaseDetails(
        status=state.get("status", "closed_legitimate"),
        verdict="fraud" if state.get("fraud_probability_final", 0.0) >= 0.85 else "legitimate" if state.get("fraud_probability_final", 1.0) <= 0.15 else "uncertain",
        fraud_probability=state.get("fraud_probability_final", 0.0),
        pattern=state.get("pattern_candidates", ["none"])[0] if state.get("pattern_candidates") else "none",
        pattern_description="Determined by deterministic signatures and LLM verification.",
        affected_txn_ids=affected_ids,
        first_suspicious_txn_id=first_suspicious,
        connected_card_ids=[str(c.get("id", "")) for c in state.get("connected_card_evidence", [])],
        connected_device_profiles=[str(d.get("id", "")) for d in state.get("device_evidence", [])],
        exposure_usd=exposure,
        evidence=[], # In a full run, map `state["evidence_packet"]` back to `Evidence` objects here
        similar_prior_cases=[str(c.get("case_id", "")) for c in state.get("prior_cases", [])],
        summary="Automated agentic investigation complete.",
        written_to_graph=bool(state.get("graph_case_id")),
        graph_case_id=state.get("graph_case_id", "")
    )
    
    actions = NextBestActions(
        initial=initial_acts,
        final=final_acts,
        what_changed="Evidence simulation shifted probability." if state.get("evidence_responses") else "No changes from initial assessment."
    )
    
    sar_data = state.get("sar_data") or generate_sar(state)
    
    return BenchmarkCaseOutput(
        case_id=state.get("case_id", "UNKNOWN"),
        case=case_details,
        evidence_requests=state.get("evidence_requests", []),
        next_best_actions=actions,
        sar=sar_data,
        stop_reason=state.get("stop_reason", "Max steps reached."),
        tool_calls=state.get("tool_calls", 0),
        tokens=state.get("tokens", 0),
        latency_s=state.get("latency_s", 0.0)
    )