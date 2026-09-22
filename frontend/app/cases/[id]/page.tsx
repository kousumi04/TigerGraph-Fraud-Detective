// frontend/app/cases/[id]/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { fetchCaseDetails } from "../../../lib/api";
import { BenchmarkCaseOutput } from "../../../types";
import GraphViewer from "../../../components/GraphViewer";

export default function CaseDetailsPage() {
  const { id } = useParams() as { id: string };
  const [data, setData] = useState<BenchmarkCaseOutput | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetchCaseDetails(id);
        setData(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) {
    return <div className="p-8 text-center text-xs font-mono text-muted">Inspecting case {id}...</div>;
  }

  if (!data) {
    return (
      <div className="p-8 text-center text-xs font-mono text-muted space-y-2">
        <div>Case {id} not found on disk.</div>
        <Link href="/" className="text-accent underline">
          Return to Queue
        </Link>
      </div>
    );
  }

  const { case: c, sar, next_best_actions: actions } = data;
  const isFraud = c.verdict === "fraud";
  const isLegit = c.verdict === "legitimate";

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <div className="bg-surface border border-surface-border p-4 rounded flex flex-wrap justify-between items-center gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h2 className="text-lg font-bold font-mono text-heading">{data.case_id}</h2>
            <span
              className={`px-2 py-0.5 rounded border text-xs font-mono font-bold uppercase ${
                isFraud
                  ? "text-danger bg-danger/10 border-danger/30"
                  : isLegit
                  ? "text-success bg-success/10 border-success/30"
                  : "text-warning bg-warning/10 border-warning/30"
              }`}
            >
              {c.verdict}
            </span>
            <span className="text-xs font-mono text-muted uppercase">Status: {c.status}</span>
          </div>
          <p className="text-xs font-mono text-muted mt-1">
            Pattern: <span className="text-heading font-semibold">{c.pattern}</span>
          </p>
        </div>

        <div className="flex items-center space-x-6 text-xs font-mono">
          <div>
            <div className="text-muted uppercase text-[10px]">Probability</div>
            <div className="text-sm font-bold text-heading">{(c.fraud_probability * 100).toFixed(1)}%</div>
          </div>
          <div>
            <div className="text-muted uppercase text-[10px]">Exposure</div>
            <div className="text-sm font-bold text-heading">${c.exposure_usd.toFixed(2)}</div>
          </div>
          <div>
            <div className="text-muted uppercase text-[10px]">Latency</div>
            <div className="text-sm font-bold text-heading">{data.latency_s.toFixed(2)}s</div>
          </div>
        </div>
      </div>

      {/* Graph Relationship Explorer */}
      <GraphViewer
        caseId={data.case_id}
        affectedTxns={c.affected_txn_ids}
        connectedCards={c.connected_card_ids}
        devices={c.connected_device_profiles}
      />

      {/* Evidence & Policy Actions Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Next Best Actions Panel */}
        <div className="bg-surface border border-surface-border rounded p-4 space-y-3">
          <div className="text-xs font-mono font-semibold uppercase text-heading border-b border-surface-border pb-2">
            Deterministic Policy Actions
          </div>
          <div className="space-y-2 text-xs font-mono">
            {actions.final.map((a, idx) => (
              <div key={idx} className="bg-[#090d12] border border-surface-border p-2.5 rounded">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-accent">{a.action}</span>
                  <span className="px-1.5 py-0.5 rounded bg-surface-border text-[10px] uppercase font-bold text-muted">
                    Route: {a.route}
                  </span>
                </div>
                <p className="text-[11px] text-muted mt-1">{a.reason}</p>
              </div>
            ))}
          </div>

          <div className="pt-2 text-[11px] font-mono text-muted border-t border-surface-border">
            <span className="text-heading font-semibold">State Shift:</span> {actions.what_changed}
          </div>
        </div>

        {/* Evidence Simulation Log */}
        <div className="bg-surface border border-surface-border rounded p-4 space-y-3">
          <div className="text-xs font-mono font-semibold uppercase text-heading border-b border-surface-border pb-2">
            Evidence Requests & Simulation Log
          </div>
          {data.evidence_requests.length === 0 ? (
            <div className="text-xs font-mono text-muted pt-2">
              Investigation reached confidence threshold without requesting external validation.
            </div>
          ) : (
            <div className="space-y-2 text-xs font-mono">
              {data.evidence_requests.map((req, idx) => (
                <div key={idx} className="bg-[#090d12] border border-surface-border p-2.5 rounded">
                  <div className="flex justify-between items-center text-[11px]">
                    <span className="text-warning font-semibold uppercase">{req.type}</span>
                    <span className="text-muted text-[10px]">Step {req.asked_after_step}</span>
                  </div>
                  <p className="text-[11px] text-text mt-1 font-mono">{req.assumed_response}</p>
                </div>
              ))}
            </div>
          )}

          <div className="pt-2 text-[11px] font-mono text-muted border-t border-surface-border">
            <span className="text-heading font-semibold">Stop Condition:</span> {data.stop_reason}
          </div>
        </div>
      </div>

      {/* SAR Filing Details (If Required) */}
      {sar.file && (
        <div className="bg-surface border border-warning/40 rounded p-4 space-y-2">
          <div className="flex justify-between items-center border-b border-surface-border pb-2">
            <span className="text-xs font-mono font-semibold uppercase text-warning">
              Regulatory Filing Required (Suspicious Activity Report)
            </span>
            <span className="text-[10px] font-mono bg-warning/10 text-warning px-2 py-0.5 rounded border border-warning/30">
              MANDATORY SAR
            </span>
          </div>
          <div className="text-xs font-mono space-y-2 pt-1">
            <div className="text-muted">
              <span className="text-heading font-semibold">Filing Reason:</span> {sar.reason}
            </div>
            <div className="bg-[#090d12] border border-surface-border p-3 rounded text-[11px] leading-relaxed text-heading whitespace-pre-wrap">
              {sar.narrative}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}