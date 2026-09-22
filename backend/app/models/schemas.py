# backend/app/models/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# ---------------------------------------------------------
# Final JSON Output Schemas (Strictly matching README spec)
# ---------------------------------------------------------

class Evidence(BaseModel):
    claim: str
    source: Literal["graph", "document", "customer", "external"]
    ref: str
    entity_ids: List[str]

class EvidenceRequest(BaseModel):
    type: Literal["customer_validation", "step_up_auth", "analyst_info"]
    asked_after_step: int
    assumed_response: str

class Action(BaseModel):
    action: str
    route: Literal["auto", "L1", "L2"]
    reason: str

class SAR(BaseModel):
    file: bool
    reason: Optional[str] = None
    narrative: Optional[str] = None
    subjects: Optional[List[str]] = None
    total_amount_usd: Optional[float] = None
    activity_dates: Optional[List[str]] = None

class CaseDetails(BaseModel):
    status: Literal["open", "closed_fraud", "closed_legitimate", "escalated"]
    verdict: Literal["fraud", "legitimate", "uncertain"]
    fraud_probability: float
    pattern: str
    pattern_description: str
    affected_txn_ids: List[str]
    first_suspicious_txn_id: str
    connected_card_ids: List[str]
    connected_device_profiles: List[str]
    exposure_usd: float
    evidence: List[Evidence]
    similar_prior_cases: List[str]
    summary: str
    written_to_graph: bool
    graph_case_id: str

class NextBestActions(BaseModel):
    initial: List[Action]
    final: List[Action]
    what_changed: str

class BenchmarkCaseOutput(BaseModel):
    case_id: str
    case: CaseDetails
    evidence_requests: List[EvidenceRequest]
    next_best_actions: NextBestActions
    sar: SAR
    stop_reason: str
    tool_calls: int = 0
    tokens: int = 0
    latency_s: float = 0.0

# ---------------------------------------------------------
# LLM Structured Output Schemas (For tool calling)
# ---------------------------------------------------------

class LLMInvestigationAssessment(BaseModel):
    fraud_probability: float = Field(..., description="Estimated probability of fraud (0.0 to 1.0)")
    pattern: str = Field(..., description="Identified fraud pattern or 'none'")
    reasoning: str = Field(..., description="Step-by-step reasoning based strictly on evidence")
    requires_more_evidence: bool = Field(..., description="True if uncertainty is high and verifiable data is missing")
    suggested_evidence_request: Optional[str] = Field(None, description="Type of evidence needed if required")

class LLMActionRecommendation(BaseModel):
    recommended_actions: List[str] = Field(..., description="List of actions to take based on policy")
    route: Literal["auto", "L1", "L2"] = Field(..., description="Required approval route")
    explanation: str = Field(..., description="Why these actions were chosen")