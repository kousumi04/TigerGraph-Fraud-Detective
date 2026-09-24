"""Small, cached graph-shaped view of the benchmark data.

The benchmark files are the source of truth when TigerGraph/MCP is not
available locally.  The same entity and relationship shape is returned by
the MCP tool facade, so the investigation code does not need fake evidence.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import threading

import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[3] / "data"
TX_COLUMNS = [
    "TransactionID", "TransactionAmt", "addr1", "P_emaildomain",
    "R_emaildomain", "customer_id", "ts", "channel", "risk_score",
]
IDENTITY_COLUMNS = ["TransactionID", "DeviceType", "DeviceInfo", "id_15", "id_27"]


def _clean(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


class DatasetGraph:
    """Cached graph view used by the local MCP-compatible tools."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._loaded = False
        self._transactions: dict[str, dict[str, Any]] = {}
        self._by_customer: dict[str, list[dict[str, Any]]] = {}
        self._by_device: dict[str, list[str]] = {}
        self._closed_cases: list[dict[str, Any]] = []

    def _load(self) -> None:
        if self._loaded:
            return
        with self._lock:
            if self._loaded:
                return

            case_pack = pd.read_csv(DATA_DIR / "case_pack.csv", dtype={"flagged_txn_id": str})
            target_customers = set(case_pack["customer_id"].astype(str))
            target_transactions = set(case_pack["flagged_txn_id"].astype(str))

            # Keep only benchmark customers. This scans the large file once
            # and avoids loading all 590k rows into the application process.
            for chunk in pd.read_csv(DATA_DIR / "transactions.csv", usecols=TX_COLUMNS, chunksize=100_000):
                chunk["TransactionID"] = chunk["TransactionID"].astype(str)
                selected = chunk[chunk["customer_id"].astype(str).isin(target_customers)]
                for row in selected.to_dict(orient="records"):
                    tx = self._normalise_transaction(row)
                    self._transactions[tx["id"]] = tx
                    self._by_customer.setdefault(str(tx["customer_id"]), []).append(tx)

            # Identity rows are the graph's device vertices. A stable device
            # fingerprint lets us find activity on other customers' cards.
            target_devices: set[str] = set()
            for chunk in pd.read_csv(DATA_DIR / "identity.csv", usecols=IDENTITY_COLUMNS, chunksize=100_000):
                chunk["TransactionID"] = chunk["TransactionID"].astype(str)
                for row in chunk.to_dict(orient="records"):
                    tx_id = str(row["TransactionID"])
                    fingerprint = self._device_fingerprint(row)
                    if tx_id in target_transactions or tx_id in self._transactions:
                        target_devices.add(fingerprint)
            neighbor_ids: set[str] = set()
            for chunk in pd.read_csv(DATA_DIR / "identity.csv", usecols=IDENTITY_COLUMNS, chunksize=100_000):
                chunk["TransactionID"] = chunk["TransactionID"].astype(str)
                for row in chunk.to_dict(orient="records"):
                    if self._device_fingerprint(row) in target_devices:
                        neighbor_ids.add(str(row["TransactionID"]))
            if neighbor_ids - self._transactions.keys():
                for chunk in pd.read_csv(DATA_DIR / "transactions.csv", usecols=TX_COLUMNS, chunksize=100_000):
                    chunk["TransactionID"] = chunk["TransactionID"].astype(str)
                    for row in chunk[chunk["TransactionID"].isin(neighbor_ids)].to_dict(orient="records"):
                        tx = self._normalise_transaction(row)
                        self._transactions[tx["id"]] = tx

            for chunk in pd.read_csv(DATA_DIR / "identity.csv", usecols=IDENTITY_COLUMNS, chunksize=100_000):
                chunk["TransactionID"] = chunk["TransactionID"].astype(str)
                for row in chunk.to_dict(orient="records"):
                    fingerprint = self._device_fingerprint(row)
                    if fingerprint in target_devices:
                        self._by_device.setdefault(fingerprint, []).append(str(row["TransactionID"]))

            self._closed_cases = pd.read_csv(
                DATA_DIR / "closed_cases_history.csv", dtype=str
            ).fillna("").to_dict(orient="records")
            self._loaded = True

    @staticmethod
    def _device_fingerprint(row: dict[str, Any]) -> str:
        device_type = str(_clean(row.get("DeviceType")) or "unknown").strip().lower()
        device_info = str(_clean(row.get("DeviceInfo")) or "unknown").strip().lower()
        return f"{device_type}|{device_info}"

    @staticmethod
    def _normalise_transaction(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(row["TransactionID"]),
            "transaction_id": str(row["TransactionID"]),
            "amount": float(_clean(row.get("TransactionAmt")) or 0.0),
            "billing_region": str(_clean(row.get("addr1")) or ""),
            "email_domain": _clean(row.get("P_emaildomain")) or _clean(row.get("R_emaildomain")),
            "customer_id": str(_clean(row.get("customer_id")) or ""),
            "ts": _clean(row.get("ts")),
            "channel": str(_clean(row.get("channel")) or ""),
            "risk_score": float(_clean(row.get("risk_score")) or 0.0),
        }

    def transaction(self, transaction_id: str) -> dict[str, Any]:
        self._load()
        return dict(self._transactions.get(str(transaction_id), {"id": str(transaction_id)}))

    def customer_history(self, customer_id: str) -> list[dict[str, Any]]:
        self._load()
        return sorted(self._by_customer.get(str(customer_id), []), key=lambda x: str(x.get("ts", "")))

    def device_neighbors(self, transaction_id: str) -> list[dict[str, Any]]:
        self._load()
        identity = self._identity_for(transaction_id)
        if not identity:
            return []
        return [self._transactions[tx_id] for tx_id in self._by_device.get(identity, []) if tx_id in self._transactions]

    def _identity_for(self, transaction_id: str) -> str | None:
        # Identity is loaded into the device index; find the index containing
        # the transaction without exposing the raw identity table to callers.
        for fingerprint, tx_ids in self._by_device.items():
            if str(transaction_id) in tx_ids:
                return fingerprint
        return None

    def prior_cases(self, transaction_id: str) -> list[dict[str, Any]]:
        tx = self.transaction(transaction_id)
        customer_id = tx.get("customer_id", "")
        matches = []
        for case in self._closed_cases:
            if case.get("customer_id") == customer_id or str(transaction_id) in str(case.get("txn_ids", "")).split("|"):
                matches.append({
                    "case_id": case.get("case_id"),
                    "verdict": "fraud" if case.get("outcome") == "confirmed_fraud" else "legitimate",
                    "pattern": case.get("pattern") or "none",
                    "relevance": case.get("analyst_notes", ""),
                    "summary": case.get("analyst_notes", ""),
                })
        return matches[:8]


_DATASET_GRAPH = DatasetGraph()


def get_dataset_graph() -> DatasetGraph:
    return _DATASET_GRAPH
