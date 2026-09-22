// frontend/lib/api.ts
import { BenchmarkCaseOutput, SystemStatus } from "../types";

const API_BASE = "/api";

export async function fetchSystemStatus(): Promise<SystemStatus> {
  const res = await fetch(`${API_BASE}/system/status`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch system status");
  return res.json();
}

export async function fetchCases(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/cases`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch case list");
  return res.json();
}

export async function fetchCaseDetails(caseId: string): Promise<BenchmarkCaseOutput> {
  const res = await fetch(`${API_BASE}/cases/${caseId}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Case ${caseId} not found`);
  return res.json();
}

export async function triggerInvestigation(caseId: string, txnId: string, riskScore: number): Promise<BenchmarkCaseOutput> {
  const res = await fetch(`${API_BASE}/cases/${caseId}/investigate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ transaction_id: txnId, risk_score: riskScore }),
  });
  if (!res.ok) throw new Error(`Investigation failed for ${caseId}`);
  return res.json();
}