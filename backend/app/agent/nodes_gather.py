# backend/app/agent/nodes_gather.py
from typing import Dict, Any
from ..models.state import InvestigationState
from ..graph.mcp_tools import get_all_mcp_tools
from ..memory.case_memory import retrieve_prior_cases

def load_case(state: InvestigationState) -> Dict[str, Any]:
    """Initializes the case parameters from the trigger."""
    return {"status": "open", "tool_calls": state.get("tool_calls", 0) + 1}

def gather_context(state: InvestigationState) -> Dict[str, Any]:
    """
    Batches deterministic MCP tool calls to expand transaction context,
    investigate devices, regions, and connected cards.
    """
    trigger = state.get("trigger", {})
    txn_id = trigger.get("transaction_id", "")
    tools = {t.name: t for t in get_all_mcp_tools()}
    flagged = tools["get_transaction"].invoke({"transaction_id": txn_id})
    customer_id = trigger.get("customer_id") or flagged.get("customer_id", "")
    history = tools["get_customer_history"].invoke({"customer_id": customer_id})
    devices = tools["get_device_neighbors"].invoke({"device_id": txn_id})
    device_ids = []
    for tx in devices:
        device_id = f"{tx.get('channel', 'unknown')}|{tx.get('email_domain', 'unknown')}"
        if device_id not in device_ids:
            device_ids.append(device_id)

    flagged["status"] = "flagged"
    customer_context = {"customer_id": customer_id, "account_age": None, "identity_status": "unknown"}
    for tx in history:
        tx["status"] = "flagged" if tx.get("id") == txn_id else "context"

    return {
        "flagged_transaction": flagged,
        "card_context": {"card_id": trigger.get("card_id")},
        "transaction_evidence": [flagged],
        "customer_context": {**customer_context, "history": history},
        "device_evidence": [{"id": device_id} for device_id in device_ids],
        "region_evidence": [{"region": flagged.get("billing_region")}],
        "connected_card_evidence": [],
        "tool_calls": state.get("tool_calls", 0) + 4
    }

def retrieve_memory(state: InvestigationState) -> Dict[str, Any]:
    """Retrieves similar prior cases from graph memory."""
    tools = {t.name: t for t in get_all_mcp_tools()}
    txn_id = state.get("trigger", {}).get("transaction_id", "")
    
    cases = retrieve_prior_cases(txn_id, "", state.get("trigger", {}).get("card_id", ""), tools)
    return {"prior_cases": cases, "tool_calls": state.get("tool_calls", 0) + 1}
