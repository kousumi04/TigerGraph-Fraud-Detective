// frontend/app/page.tsx
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchCases, fetchCaseDetails } from "../lib/api";
import { BenchmarkCaseOutput } from "../types";

export default function DashboardPage() {
  const [cases, setCases] = useState<BenchmarkCaseOutput[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAll() {
      try {
        const ids = await fetchCases();
        const details = await Promise.all(
          ids.slice(0, 20).map((id) => fetchCaseDetails(id).catch(() => null))
        );
        setCases(details.filter((c): c is BenchmarkCaseOutput => c !== null));
      } catch (err) {
        console.error("Failed to load dashboard cases", err);
      } finally {
        setLoading(false);
      }
    }
    loadAll();
  }, []);

  const total = cases.length;
  const fraudCount = cases.filter((c) => c.case.verdict === "fraud").length;
  const legCount = cases.filter((c) => c.case.verdict === "legitimate").length;
  const sarCount = cases.filter((c) => c.sar.file).length;
  const totalExposure = cases.reduce((acc, c) => acc + (c.case.exposure_usd || 0), 0);

  return (
    <div className="space-y-6">
      {/* Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-surface border border-surface-border p-4 rounded">
          <div className="text-xs font-mono text-muted uppercase">Cases Processed</div>
          <div className="text-2xl font-bold text-heading mt-1 font-mono">{total} / 20</div>
        </div>
        <div className="bg-surface border border-surface-border p-4 rounded">
          <div className="text-xs font-mono text-muted uppercase">Fraud Confirmed</div>
          <div className="text-2xl font-bold text-danger mt-1 font-mono">{fraudCount}</div>
        </div>
        <div className="bg-surface border border-surface-border p-4 rounded">
          <div className="text-xs font-mono text-muted uppercase">Cleared Legitimate</div>
          <div className="text-2xl font-bold text-success mt-1 font-mono">{legCount}</div>
        </div>
        <div className="bg-surface border border-surface-border p-4 rounded">
          <div className="text-xs font-mono text-muted uppercase">SAR Filings</div>
          <div className="text-2xl font-bold text-warning mt-1 font-mono">{sarCount}</div>
        </div>
        <div className="bg-surface border border-surface-border p-4 rounded">
          <div className="text-xs font-mono text-muted uppercase">Total Exposure</div>
          <div className="text-2xl font-bold text-heading mt-1 font-mono">
            ${totalExposure.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
        </div>
      </div>

      {/* Case Queue Table */}
      <div className="bg-surface border border-surface-border rounded overflow-hidden">
        <div className="px-4 py-3 border-b border-surface-border flex justify-between items-center">
          <span className="text-xs font-mono text-heading font-semibold uppercase tracking-wider">
            Benchmark Case Feed
          </span>
          <span className="text-xs font-mono text-muted">{cases.length} items logged</span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs font-mono text-muted">Loading investigations...</div>
        ) : cases.length === 0 ? (
          <div className="p-8 text-center text-xs font-mono text-muted">
            No completed cases found. Run the benchmark script to populate cases/.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono border-collapse">
              <thead>
                <tr className="border-b border-surface-border text-muted bg-[#12161c]">
                  <th className="p-3">CASE ID</th>
                  <th className="p-3">VERDICT</th>
                  <th className="p-3">PROBABILITY</th>
                  <th className="p-3">PATTERN</th>
                  <th className="p-3">EXPOSURE</th>
                  <th className="p-3">SAR</th>
                  <th className="p-3">ROUTE</th>
                  <th className="p-3">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-border">
                {cases.map((c) => {
                  const verdictColor =
                    c.case.verdict === "fraud"
                      ? "text-danger bg-danger/10 border-danger/30"
                      : c.case.verdict === "legitimate"
                      ? "text-success bg-success/10 border-success/30"
                      : "text-warning bg-warning/10 border-warning/30";

                  const route = c.next_best_actions.final[0]?.route || "auto";

                  return (
                    <tr key={c.case_id} className="hover:bg-[#1c2128]">
                      <td className="p-3 font-bold text-heading">
                        <Link href={`/cases/${c.case_id}`} className="hover:underline text-accent">
                          {c.case_id}
                        </Link>
                      </td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded border text-[10px] uppercase font-bold ${verdictColor}`}>
                          {c.case.verdict}
                        </span>
                      </td>
                      <td className="p-3">{(c.case.fraud_probability * 100).toFixed(1)}%</td>
                      <td className="p-3 text-muted">{c.case.pattern}</td>
                      <td className="p-3 font-semibold text-heading">${c.case.exposure_usd.toFixed(2)}</td>
                      <td className="p-3">
                        {c.sar.file ? (
                          <span className="text-warning font-bold">REQUIRED</span>
                        ) : (
                          <span className="text-muted">NONE</span>
                        )}
                      </td>
                      <td className="p-3 uppercase text-muted">{route}</td>
                      <td className="p-3">
                        <Link
                          href={`/cases/${c.case_id}`}
                          className="text-xs bg-surface-border hover:bg-[#3d444d] text-heading px-2 py-1 rounded"
                        >
                          Inspect
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}