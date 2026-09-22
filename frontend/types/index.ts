// frontend/types/index.ts

export type Verdict = "fraud" | "legitimate" | "uncertain";
export type CaseStatus = "open" | "closed_fraud" | "closed_legitimate" | "escalated";
export type ApprovalRoute = "auto" | "L1" | "L2";

export interface Action {
  action: string;
  route: ApprovalRoute;
  reason: string;
}

export interface EvidenceRequest {
  type: "customer_validation" | "step_up_auth" | "analyst_info";
  asked_after_step: number;
  assumed_response: string;
}

export interface SAR {
  file: boolean;
  reason?: string;
  narrative?: string;
  subjects?: string[];
  total_amount_usd?: number;
  activity_dates?: string[];
}

export interface CaseDetails {
  status: CaseStatus;
  verdict: Verdict;
  fraud_probability: number;
  pattern: string;
  pattern_description: string;
  affected_txn_ids: string[];
  first_suspicious_txn_id: string;
  connected_card_ids: string[];
  connected_device_profiles: string[];
  exposure_usd: number;
  evidence: Array<{ claim: string; source: string; ref: string; entity_ids: string[] }>;
  similar_prior_cases: string[];
  summary: string;
  written_to_graph: boolean;
  graph_case_id: string;
}

export interface BenchmarkCaseOutput {
  case_id: string;
  case: CaseDetails;
  evidence_requests: EvidenceRequest[];
  next_best_actions: {
    initial: Action[];
    final: Action[];
    what_changed: string;
  };
  sar: SAR;
  stop_reason: string;
  tool_calls: number;
  tokens: number;
  latency_s: number;
}

export interface SystemStatus {
  mcp_connected: boolean;
  llm_provider_active: boolean;
  vector_store_loaded: boolean;
}