# backend/app/models/state.py
from typing import TypedDict, List, Dict, Any, Optional
from .schemas import Evidence, EvidenceRequest, Action, SAR

class InvestigationState(TypedDict):
    case_id: str
    trigger: Dict[str, Any]
    flagged_transaction: Dict[str, Any]
    customer_context: Dict[str, Any]
    card_context: Dict[str, Any]
    
    # Evidence Gathering
    transaction_evidence: List[Dict[str, Any]]
    device_evidence: List[Dict[str, Any]]
    region_evidence: List[Dict[str, Any]]
    connected_card_evidence: List[Dict[str, Any]]
    prior_cases: List[Dict[str, Any]]
    
    # Synthesis
    pattern_candidates: List[str]
    evidence_packet: Dict[str, Any]
    fraud_probability_initial: float
    fraud_probability_final: float
    uncertainty: float
    
    # Simulation & Routing
    evidence_requests: List[EvidenceRequest]
    evidence_responses: List[Dict[str, Any]]
    initial_actions: List[Action]
    final_actions: List[Action]
    policy_references: List[str]
    
    # Output Requirements
    sar_required: bool
    sar_data: Optional[SAR]
    stop_reason: str
    
    # Telemetry
    tool_calls: int
    tokens: int
    latency_s: float
    graph_case_id: str
    errors: List[str]