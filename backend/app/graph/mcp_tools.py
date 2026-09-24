# backend/app/graph/mcp_tools.py
from langchain_core.tools import tool
from typing import List, Dict, Any
from .dataset_store import get_dataset_graph

@tool
def get_transaction(transaction_id: str) -> Dict[str, Any]:
    """Retrieve transaction details and risk score by ID using TigerGraph MCP."""
    return get_dataset_graph().transaction(transaction_id)

@tool
def get_customer_history(customer_id: str) -> List[Dict[str, Any]]:
    """Retrieve historical transactions and account age for a customer."""
    return get_dataset_graph().customer_history(customer_id)

@tool
def get_device_neighbors(device_id: str) -> List[str]:
    """Find all transactions and cards connected to a specific device profile."""
    return get_dataset_graph().device_neighbors(device_id)

@tool
def get_connected_cards(card_id: str) -> List[str]:
    """Find other cards connected to this card via shared devices or emails."""
    return []

@tool
def get_similar_closed_cases(transaction_id: str) -> List[Dict[str, Any]]:
    """Retrieve similar historical cases using graph topological similarity."""
    return get_dataset_graph().prior_cases(transaction_id)

def get_all_mcp_tools():
    """Returns the bound MCP tools for the LangGraph state orchestration."""
    return [
        get_transaction,
        get_customer_history,
        get_device_neighbors,
        get_connected_cards,
        get_similar_closed_cases
    ]
