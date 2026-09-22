# scripts/run_case.py
import sys
from pathlib import Path

# Add project root to sys.path so 'backend' can be resolved
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import asyncio
import argparse
import json
import logging
from backend.app.services.runner import run_investigation

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def main():
    parser = argparse.ArgumentParser(description="Run Agentic Fraud Investigation for a single case.")
    parser.add_argument("--case-id", required=True, help="Case ID (e.g., HHG-001)")
    parser.add_argument("--txn-id", default="TXN-DEFAULT", help="Trigger Transaction ID")
    parser.add_argument("--risk-score", type=float, default=0.85, help="Initial Trigger Risk Score")
    parser.add_argument("--demo", action="store_true", help="Enable verbose demo mode output")
    
    args = parser.parse_args()
    
    trigger_data = {
        "transaction_id": args.txn_id,
        "risk_score": args.risk_score,
        "source": "demo_trigger" if args.demo else "benchmark_trigger"
    }
    
    logging.info(f"Starting investigation for {args.case_id}...")
    try:
        output = await run_investigation(args.case_id, trigger_data)
        if args.demo:
            print("\n" + "="*50)
            print("DEMO MODE: INVESTIGATION COMPLETE")
            print("="*50)
            print(json.dumps(output.model_dump(), indent=2))
        else:
            logging.info(f"Successfully generated cases/{args.case_id}.json")
    except Exception as e:
        logging.error(f"Investigation failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())