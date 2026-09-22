# backend/app/rag/evidence_builder.py
from typing import Dict, Any
from ..models.state import InvestigationState

def build_evidence_packet(state: InvestigationState) -> Dict[str, Any]:
    """
    Compresses investigation state into a dense, token-optimized packet for the LLM.
    Never dumps the entire graph or unformatted CSVs.
    """
    
    # 1. Summarize base entities
    packet = {
        "case_id": state.get("case_id"),
        "trigger": state.get("trigger"),
        "flagged_transaction": state.get("flagged_transaction"),
    }
    
    # 2. Extract key signals from graph evidence
    packet["customer_summary"] = {
        "account_age": state.get("customer_context", {}).get("account_age"),
        "identity_status": state.get("customer_context", {}).get("identity_status", "verified")
    }
    
    packet["device_relationships"] = len(state.get("device_evidence", []))
    packet["connected_cards"] = len(state.get("connected_card_evidence", []))
    
    # 3. Format prior closed cases
    packet["prior_closed_cases"] = [
        {
            "id": c.get("case_id"),
            "verdict": c.get("verdict"),
            "pattern": c.get("pattern"),
            "relevance": c.get("relevance")
        }
        for c in state.get("prior_cases", [])[:state.get("max_prior_cases", 3)]
    ]
    
    # 4. Inject deterministic pattern evidence
    packet["pattern_evidence"] = state.get("pattern_candidates", [])
    
    # 5. Inject policy rules retrieved via Document RAG
    packet["policy_rules"] = state.get("policy_references", [])
    
    # 6. Include Simulated Responses (if requested in prior iterations)
    if state.get("evidence_responses"):
        packet["new_evidence_received"] = state.get("evidence_responses")
        
    return packet

def format_evidence_for_prompt(evidence_packet: Dict[str, Any]) -> str:
    """
    Converts the structured packet into the exact Markdown string format
    specified in the requirements for the LLM prompt.
    """
    lines = ["EVIDENCE PACKET\n"]
    
    lines.append(f"Case:\n{evidence_packet.get('case_id', 'Unknown')}\n")
    lines.append(f"Trigger:\n{evidence_packet.get('trigger', {})}\n")
    lines.append(f"Flagged transaction:\n{evidence_packet.get('flagged_transaction', {})}\n")
    
    lines.append(f"Customer:\n{evidence_packet.get('customer_summary', {})}\n")
    lines.append(f"Device relationships:\n{evidence_packet.get('device_relationships', 0)} connections found.\n")
    lines.append(f"Connected cards:\n{evidence_packet.get('connected_cards', 0)} connected cards identified.\n")
    
    cases = evidence_packet.get('prior_closed_cases', [])
    lines.append(f"Prior closed cases:\n{cases if cases else 'None'}\n")
    
    rules = evidence_packet.get('policy_rules', [])
    lines.append(f"Policy rules:\n{rules if rules else 'None'}\n")
    
    patterns = evidence_packet.get('pattern_evidence', [])
    lines.append(f"Pattern evidence:\n{patterns if patterns else 'None'}\n")
    
    responses = evidence_packet.get('new_evidence_received', [])
    if responses:
        lines.append(f"New Evidence Received:\n{responses}\n")
        
    return "\n".join(lines)