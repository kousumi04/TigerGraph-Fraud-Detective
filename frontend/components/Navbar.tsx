// frontend/components/Navbar.tsx
import Link from "next/link";

export default function Navbar() {
  return (
    <header className="border-b border-surface-border bg-surface px-6 py-3 flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <span className="text-xs font-mono font-bold tracking-widest uppercase bg-surface-border text-heading px-2 py-1 rounded">
          TG × HHGOA 2026
        </span>
        <h1 className="text-sm font-semibold text-heading tracking-wide">
          Agentic Fraud Detective
        </h1>
      </div>
      <nav className="flex items-center space-x-6 text-xs font-mono">
        <Link href="/" className="text-text hover:text-heading transition-colors">
          /dashboard_queue
        </Link>
        <Link href="/health" className="text-text hover:text-heading transition-colors">
          /system_status
        </Link>
      </nav>
    </header>
  );
}