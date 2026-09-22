// frontend/components/GraphViewer.tsx
"use client";

import { useState } from "react";

interface GraphNode {
  id: string;
  type: "Customer" | "Card" | "Transaction" | "DeviceProfile" | "BillingRegion" | "FraudCase";
  x: number;
  y: number;
  meta: Record<string, string | number>;
}

interface GraphEdge {
  from: string;
  to: string;
  label: string;
}

export default function GraphViewer({
  caseId,
  affectedTxns,
  connectedCards,
  devices,
}: {
  caseId: string;
  affectedTxns: string[];
  connectedCards: string[];
  devices: string[];
}) {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  // Derive topological graph representation from evidence
  const nodes: GraphNode[] = [
    { id: `CASE:${caseId}`, type: "FraudCase", x: 260, y: 150, meta: { caseId, status: "Evaluated" } },
    ...affectedTxns.map((id, idx) => ({
      id: `TXN:${id}`,
      type: "Transaction" as const,
      x: 100 + idx * 80,
      y: 60,
      meta: { TransactionID: id, Role: "Flagged/Suspicious" },
    })),
    ...connectedCards.map((id, idx) => ({
      id: `CARD:${id}`,
      type: "Card" as const,
      x: 420,
      y: 80 + idx * 60,
      meta: { CardID: id, Link: "Connected entity" },
    })),
    ...devices.map((id, idx) => ({
      id: `DEV:${id}`,
      type: "DeviceProfile" as const,
      x: 260,
      y: 250 + idx * 40,
      meta: { DeviceID: id, Footprint: "Hardware Fingerprint" },
    })),
  ];

  const edges: GraphEdge[] = [
    ...affectedTxns.map((id) => ({ from: `CASE:${caseId}`, to: `TXN:${id}`, label: "INVOLVES" })),
    ...connectedCards.map((id) => ({ from: `CASE:${caseId}`, to: `CARD:${id}`, label: "ON_CARD" })),
    ...devices.map((id) => ({ from: `CASE:${caseId}`, to: `DEV:${id}`, label: "RELATED_TO" })),
  ];

  const nodeColor = (type: GraphNode["type"]) => {
    switch (type) {
      case "FraudCase": return "#d29922";
      case "Transaction": return "#f85149";
      case "Card": return "#1f6feb";
      case "DeviceProfile": return "#a371f7";
      default: return "#8b949e";
    }
  };

  return (
    <div className="bg-surface border border-surface-border rounded p-4 space-y-3">
      <div className="flex justify-between items-center border-b border-surface-border pb-2">
        <span className="text-xs font-mono font-semibold uppercase text-heading">
          TigerGraph Subgraph Topology
        </span>
        <span className="text-[11px] font-mono text-muted">Click node for inspection metadata</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* SVG Visualization Canvas */}
        <div className="lg:col-span-2 bg-[#090d12] border border-surface-border rounded h-72 relative overflow-hidden flex items-center justify-center">
          <svg className="w-full h-full" viewBox="0 0 520 320">
            {/* Draw Edges */}
            {edges.map((e, idx) => {
              const src = nodes.find((n) => n.id === e.from);
              const dst = nodes.find((n) => n.id === e.to);
              if (!src || !dst) return null;
              return (
                <g key={idx}>
                  <line
                    x1={src.x}
                    y1={src.y}
                    x2={dst.x}
                    y2={dst.y}
                    stroke="#30363d"
                    strokeWidth="1.5"
                    strokeDasharray="3 3"
                  />
                </g>
              );
            })}

            {/* Draw Nodes */}
            {nodes.map((n) => (
              <g
                key={n.id}
                onClick={() => setSelectedNode(n)}
                className="cursor-pointer transition-transform hover:scale-110"
              >
                <circle
                  cx={n.x}
                  cy={n.y}
                  r="14"
                  fill={nodeColor(n.type)}
                  stroke="#ffffff"
                  strokeWidth={selectedNode?.id === n.id ? "2.5" : "0.5"}
                />
                <text
                  x={n.x}
                  y={n.y + 24}
                  textAnchor="middle"
                  fill="#c9d1d9"
                  fontSize="9"
                  fontFamily="monospace"
                >
                  {n.id}
                </text>
              </g>
            ))}
          </svg>
        </div>

        {/* Node Inspection Metadata Panel */}
        <div className="bg-[#090d12] border border-surface-border rounded p-3 text-xs font-mono space-y-2">
          <div className="text-muted uppercase text-[10px] tracking-wider border-b border-surface-border pb-1">
            Vertex Inspector
          </div>
          {selectedNode ? (
            <div className="space-y-1.5">
              <div className="text-heading font-bold">{selectedNode.id}</div>
              <div className="text-[11px] text-accent">Type: {selectedNode.type}</div>
              <div className="mt-2 space-y-1 bg-surface p-2 rounded border border-surface-border">
                {Object.entries(selectedNode.meta).map(([k, v]) => (
                  <div key={k} className="flex justify-between text-[10px]">
                    <span className="text-muted">{k}:</span>
                    <span className="text-heading font-semibold">{v}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-muted text-[11px] pt-4">
              Select any graph vertex on the left to inspect relationship attributes.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}