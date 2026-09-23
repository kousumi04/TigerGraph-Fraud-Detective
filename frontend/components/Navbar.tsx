// frontend/components/Navbar.tsx
import Link from "next/link";

export default function Navbar() {
  return (
    <header className="border-b border-surface-border bg-surface px-6 py-3 flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <h1 className="text-sm font-semibold text-heading tracking-wide">
          Agentic Fraud
        </h1>
      </div>
      <nav className="flex items-center space-x-6 text-xs font-mono uppercase tracking-wide">
        <Link href="/" className="text-text hover:text-heading transition-colors">
          Dashboard Queue
        </Link>
        <Link href="/health" className="text-text hover:text-heading transition-colors">
          System Status
        </Link>
      </nav>
    </header>
  );
}