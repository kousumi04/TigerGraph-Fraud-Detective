// frontend/app/health/page.tsx
"use client";

import { useEffect, useState } from "react";
import { fetchSystemStatus } from "../../lib/api";
import { SystemStatus } from "../../types";

export default function HealthPage() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSystemStatus()
      .then(setStatus)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <h2 className="text-sm font-mono font-bold uppercase text-heading tracking-wider">
        System Health & Subsystem Connectivity
      </h2>

      <div className="bg-surface border border-surface-border rounded p-4 space-y-3 font-mono text-xs">
        {error ? (
          <div className="text-danger">Backend unreachable: {error}</div>
        ) : !status ? (
          <div className="text-muted">Pinging backend services...</div>
        ) : (
          <div className="space-y-3">
            <div className="flex justify-between items-center py-1 border-b border-surface-border">
              <span>TigerGraph MCP Server</span>
              <span className={status.mcp_connected ? "text-success font-bold" : "text-danger font-bold"}>
                {status.mcp_connected ? "CONNECTED" : "DISCONNECTED"}
              </span>
            </div>
            <div className="flex justify-between items-center py-1 border-b border-surface-border">
              <span>LLM Inference Endpoint</span>
              <span className={status.llm_provider_active ? "text-success font-bold" : "text-danger font-bold"}>
                {status.llm_provider_active ? "READY" : "OFFLINE"}
              </span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span>Policy & Regulatory Vector Store</span>
              <span className={status.vector_store_loaded ? "text-success font-bold" : "text-danger font-bold"}>
                {status.vector_store_loaded ? "LOADED" : "UNINITIALIZED"}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}