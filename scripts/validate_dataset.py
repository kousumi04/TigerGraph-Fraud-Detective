# scripts/validate_dataset.py
import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

DATA_DIR = Path("data")
TRANSACTIONS_FILE = DATA_DIR / "transactions.csv"
IDENTITY_FILE = DATA_DIR / "identity.csv"
CASES_FILE = DATA_DIR / "case_pack.csv"

def validate_transactions(chunk_size: int = 50000):
    logging.info(f"Validating transactions in chunks of {chunk_size}...")
    if not TRANSACTIONS_FILE.exists():
        logging.error(f"Missing {TRANSACTIONS_FILE}")
        return False

    total_rows = 0
    missing_ids = 0
    
    for chunk in pd.read_csv(TRANSACTIONS_FILE, chunksize=chunk_size):
        total_rows += len(chunk)
        if 'TransactionID' not in chunk.columns:
            logging.error("TransactionID column missing.")
            return False
        missing_ids += chunk['TransactionID'].isna().sum()

    logging.info(f"Processed {total_rows} transactions. Missing IDs: {missing_ids}")
    return missing_ids == 0

def validate_case_pack():
    logging.info("Validating 20 benchmark cases...")
    if not CASES_FILE.exists():
        logging.error(f"Missing {CASES_FILE}")
        return False
        
    df = pd.read_csv(CASES_FILE)
    if len(df) != 20:
        logging.warning(f"Expected 20 cases, found {len(df)}")
    
    invalid_ids = df[~df['case_id'].str.startswith('HHG-')]
    if not invalid_ids.empty:
        logging.error(f"Found invalid case IDs: {invalid_ids['case_id'].tolist()}")
        return False
        
    logging.info("Case pack validation passed.")
    return True

if __name__ == "__main__":
    logging.info("Starting Dataset Validation")
    tx_valid = validate_transactions()
    cases_valid = validate_case_pack()
    
    if tx_valid and cases_valid:
        logging.info("Dataset validation complete. Ready for graph ingestion.")
    else:
        logging.error("Dataset validation failed. Check required files.")