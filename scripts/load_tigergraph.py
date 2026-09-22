# scripts/load_tigergraph.py
import pandas as pd
import logging
import os
from pathlib import Path
# import pyTigerGraph as tg  # Uncomment when pyTigerGraph is installed in your env

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
DATA_DIR = Path("data")

def load_data_to_tigergraph():
    logging.info("Connecting to TigerGraph...")
    # tg_conn = tg.TigerGraphConnection(
    #     host=os.getenv("TG_HOST"), 
    #     graphname=os.getenv("TG_GRAPH_NAME"),
    #     username=os.getenv("TG_USERNAME"),
    #     password=os.getenv("TG_PASSWORD")
    # )
    # tg_conn.apiToken = tg_conn.getToken(tg_conn.createSecret())
    
    tx_file = DATA_DIR / "transactions.csv"
    if not tx_file.exists():
        logging.error(f"Missing {tx_file}. Ensure data is in the data/ folder.")
        return

    logging.info("Starting memory-safe chunked load for transactions...")
    chunk_size = 50000
    
    # Process large files in chunks to satisfy memory constraints
    for i, chunk in enumerate(pd.read_csv(tx_file, chunksize=chunk_size)):
        logging.info(f"Loading transaction chunk {i+1} ({len(chunk)} rows)...")
        # Upsert mapping logic goes here:
        # tg_conn.upsertVertexDataFrame(chunk, 'Transaction', v_id='TransactionID', attributes={'amount': 'Amount', 'ts': 'Timestamp', 'risk_score': 'RiskScore'})
        
    logging.info("Graph data ingestion simulated successfully.")

if __name__ == "__main__":
    load_data_to_tigergraph()