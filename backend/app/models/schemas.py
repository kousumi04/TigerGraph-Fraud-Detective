# backend/app/models/schemas.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Evidence(BaseModel):
    claim: str
    source: str
    ref: str
    entity_ids: List[str]
    
class Action(BaseModel):
    action: str
    route: str
    reason: str

class NextBestActions(BaseModel):
    initial: List[Action]
    final: List[Action]
    what_changed: str
    triggered_rules: List[str] = Field(default_factory=list)

class EvidenceRequest(BaseModel):
    type: str
    asked_after_step: int
    assumed_response: str

class SAR(BaseModel):
    file: bool
    reason: Optional[str] = None
    narrative: Optional[str] = None
    subjects: Optional[List[str]] = None
    total_amount_usd: Optional[float] = None
    activity_dates: Optional[List[str]] = None

class CustomerCommunication(BaseModel):
    channel: str
    message_copy: str

class Playbook(BaseModel):
    case_id: str
    verdict: str
    pattern: str
    primary_action: str
    approval_route: str
    sla_hours: int
    containment_steps: List[str]
    customer_communication: CustomerCommunication
    financial_remediation: List[str]
    compliance_actions: List[str]
    sign_off_checklist: List[str]

class CaseDetails(BaseModel):
    status: str
    verdict: str
    fraud_probability: float
    pattern: str
    pattern_description: str
    customer_id: str
    trigger_type: str
    affected_txn_ids: List[str]
    first_suspicious_txn_id: str
    connected_card_ids: List[str]
    connected_device_profiles: List[str]
    exposure_usd: float
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    similar_prior_cases: List[str]
    summary: str
    written_to_graph: bool
    graph_case_id: str

class BenchmarkCaseOutput(BaseModel):
    case_id: str
    case: CaseDetails
    evidence_requests: List[EvidenceRequest]
    next_best_actions: NextBestActions
    sar: SAR
    playbook: Optional[Playbook] = None
    stop_reason: str
    tool_calls: int
    tokens: int
    latency_s: float

class LLMInvestigationAssessment(BaseModel):
    fraud_probability: float = Field(..., description="Estimated probability of fraud from 0.0 to 1.0")
    pattern: Optional[str] = Field(None, description="Identified fraud pattern name if applicable")
    requires_more_evidence: bool = Field(..., description="True if critical context is missing")
    reasoning: str = Field(..., description="Explanation of the assessment")