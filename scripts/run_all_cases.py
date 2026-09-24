# scripts/run_all_cases.py
import asyncio
import logging
import pandas as pd
from pathlib import Path
from backend.app.services.runner import run_investigation

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def process_all_cases():
    data_dir = Path("data")
    cases_file = data_dir / "case_pack.csv"
    
    if not cases_file.exists():
        logging.error(f"Cannot find {cases_file}. Please ensure data is loaded.")
        return
        
    df = pd.read_csv(cases_file)
    if 'case_id' not in df.columns:
        logging.error("case_pack.csv is missing case_id")
        return

    case_ids = df['case_id'].tolist()
    # Ensure exactly 20 cases are processed as per benchmark rules
    case_ids = case_ids[:20]
    
    logging.info(f"Starting batch run for {len(case_ids)} cases...")
    
    success_count = 0
    failure_count = 0
    
    for case_id in case_ids:
        logging.info(f"--- Processing {case_id} ---")
        
        case = df.loc[df["case_id"] == case_id].iloc[0]
        trigger_data = {
            "transaction_id": str(case["flagged_txn_id"]),
            "customer_id": str(case["customer_id"]),
            "card_id": str(case["card_id"]),
            "trigger_type": str(case["trigger_type"]),
            "trigger_text": str(case["trigger_text"]),
            "risk_score": float(case["risk_score"]) if pd.notna(case["risk_score"]) else None,
        }
        
        try:
            await run_investigation(case_id, trigger_data)
            success_count += 1
        except Exception as e:
            logging.error(f"Failed to process {case_id}: {e}")
            failure_count += 1

        # Correct async way to pace the API calls
        logging.info("Sleeping for 15 seconds to reset Groq TPM rate limits...")
        await asyncio.sleep(15)

    logging.info("="*30)
    logging.info(f"Batch execution complete.")
    logging.info(f"Successful: {success_count}/20")
    logging.info(f"Failed: {failure_count}/20")
    logging.info("Run 'python scripts/validate_all_cases.py' to verify the output schemas.")

if __name__ == "__main__":
    asyncio.run(process_all_cases())
