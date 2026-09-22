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
    # In a full run, this executes the bound MCP tools based on state.trigger
    trigger = state.get("trigger", {})
    txn_id = trigger.get("transaction_id", "")
    
    return {
        "transaction_evidence": [{"id": txn_id, "amount": 150.0, "status": "flagged"}],
        "device_evidence": [{"id": "DEV-99", "is_new": True}],
        "region_evidence": [{"region": "US-CA"}],
        "connected_card_evidence": [],
        "tool_calls": state.get("tool_calls", 0) + 4
    }

def retrieve_memory(state: InvestigationState) -> Dict[str, Any]:
    """Retrieves similar prior cases from graph memory."""
    tools = {t.name: t for t in get_all_mcp_tools()}
    txn_id = state.get("trigger", {}).get("transaction_id", "")
    
    cases = retrieve_prior_cases(txn_id, "DEV-99", "CARD-1", tools)
    return {"prior_cases": cases, "tool_calls": state.get("tool_calls", 0) + 1}