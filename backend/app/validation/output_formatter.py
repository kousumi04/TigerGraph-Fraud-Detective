# backend/app/validation/output_formatter.py
from typing import Dict, Any
from ..models.schemas import BenchmarkCaseOutput, CaseDetails, NextBestActions, Action, Playbook, CustomerCommunication
from ..models.state import InvestigationState
from ..fraud.sar_generator import generate_sar
import re

def extract_rules(actions: list) -> list:
    """Extracts rule prefixes like 'R1', 'R7' from action reasons."""
    rules = []
    for a in actions:
        match = re.search(r'^(R\d+):', a.reason)
        if match:
            rules.append(match.group(1))
    return list(set(rules))

def format_benchmark_output(state: InvestigationState) -> BenchmarkCaseOutput:
    txns = state.get("transaction_evidence", [])
    exposure = sum(float(t.get("amount", 0.0)) for t in txns)
    affected_ids = [str(t.get("id", "")) for t in txns if t.get("status") == "flagged"]
    first_suspicious = affected_ids[0] if affected_ids else ""
    
    initial_acts = [Action(**a) if isinstance(a, dict) else a for a in state.get("initial_actions", [])]
    final_acts = [Action(**a) if isinstance(a, dict) else a for a in state.get("final_actions", [])]
    triggered_rules = extract_rules(final_acts)
    
    prob = state.get("fraud_probability_final", 0.0)
    if prob >= 0.85:
        final_status = "closed_fraud"
        final_verdict = "fraud"
    elif prob <= 0.15:
        final_status = "closed_legitimate"
        final_verdict = "legitimate"
    else:
        final_status = "escalated"
        final_verdict = "uncertain"
        
    pattern = state.get("pattern_candidates", ["none"])[0] if state.get("pattern_candidates") else "none"
    
    case_details = CaseDetails(
        status=final_status,
        verdict=final_verdict,
        fraud_probability=prob,
        pattern=pattern,
        pattern_description="Determined by deterministic signatures and LLM verification.",
        customer_id="Extracted-Customer-ID", # Placeholder for actual graph traversal extraction
        trigger_type="risk_score",
        affected_txn_ids=affected_ids,
        first_suspicious_txn_id=first_suspicious,
        connected_card_ids=[str(c.get("id", "")) for c in state.get("connected_card_evidence", [])],
        connected_device_profiles=[str(d.get("id", "")) for d in state.get("device_evidence", [])],
        exposure_usd=exposure,
        evidence=[], 
        similar_prior_cases=[str(c.get("case_id", "")) for c in state.get("prior_cases", [])],
        summary="Automated agentic investigation complete.",
        written_to_graph=bool(state.get("graph_case_id")),
        graph_case_id=state.get("graph_case_id", "")
    )
    
    actions = NextBestActions(
        initial=initial_acts,
        final=final_acts,
        what_changed="Evidence simulation shifted probability." if state.get("evidence_responses") else "No changes from initial assessment.",
        triggered_rules=triggered_rules
    )
    
    sar_data = state.get("sar_data") or generate_sar(state)
    
    # Generate the Playbook dynamically
    primary_action = final_acts[0].action if final_acts else "NO_ACTION"
    primary_route = final_acts[0].route if final_acts else "auto"
    
    containment = []
    remediation = []
    if final_verdict in ["fraud", "uncertain"]:
        containment.append(f"Place temporary security authorization hold on transaction {first_suspicious}")
        if primary_action == "BLOCK_ALL_CARDS":
            containment.append("Issue immediate network-level block on all linked card PANs")
            remediation.append("Initiate chargeback procedures for identified exposure")
        else:
            containment.append("Dispatch automated SMS two-way verification prompt")
            remediation.append("Hold settlement pending cardholder response")
    else:
        containment.append("Clear holds and allow transaction processing")
        remediation.append("No financial remediation required")

    playbook = Playbook(
        case_id=state.get("case_id", "UNKNOWN"),
        verdict=final_verdict,
        pattern=pattern,
        primary_action=primary_action,
        approval_route=primary_route,
        sla_hours=2 if final_verdict == "uncertain" else 24,
        containment_steps=containment,
        customer_communication=CustomerCommunication(
            channel="SMS / In-App Push" if final_verdict != "legitimate" else "None",
            message_copy=f"Did you attempt a purchase of ${exposure:.2f}? Reply YES if this was you, or NO if you did not make this purchase." if final_verdict != "legitimate" else "No communication necessary."
        ),
        financial_remediation=remediation,
        compliance_actions=[f"Confirm policy rule alignment ({', '.join(triggered_rules)})"] if triggered_rules else ["Standard log archival"],
        sign_off_checklist=[
            f"Verify financial exposure calculation (${exposure:.2f})",
            "Confirm TigerGraph graph resolution payload"
        ]
    )
    
    return BenchmarkCaseOutput(
        case_id=state.get("case_id", "UNKNOWN"),
        case=case_details,
        evidence_requests=state.get("evidence_requests", []),
        next_best_actions=actions,
        sar=sar_data,
        playbook=playbook,
        stop_reason=state.get("stop_reason", "Max steps reached."),
        tool_calls=state.get("tool_calls", 0),
        tokens=state.get("tokens", 0),
        latency_s=state.get("latency_s", 0.0)
    )