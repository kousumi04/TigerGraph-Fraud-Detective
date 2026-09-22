# backend/app/agent/workflow.py
from langgraph.graph import StateGraph, END
from ..models.state import InvestigationState
from .nodes_gather import load_case, gather_context, retrieve_memory
from .nodes_analyze import evaluate_evidence, check_policy
from .nodes_finalize import request_and_simulate_evidence, finalize_case

def enough_evidence_condition(state: InvestigationState) -> str:
    """Conditional router: decides whether to simulate missing evidence or proceed to finalize."""
    uncertainty = state.get("uncertainty", False)
    has_requested = len(state.get("evidence_requests", [])) > 0
    
    if uncertainty and not has_requested:
        return "request_evidence"
    return "finalize"

def build_investigation_graph():
    """Constructs the LangGraph multi-step state machine."""
    workflow = StateGraph(InvestigationState)
    
    # Add Nodes
    workflow.add_node("load_case", load_case)
    workflow.add_node("gather_context", gather_context)
    workflow.add_node("retrieve_memory", retrieve_memory)
    workflow.add_node("evaluate_evidence", evaluate_evidence)
    workflow.add_node("check_policy", check_policy)
    workflow.add_node("request_and_simulate_evidence", request_and_simulate_evidence)
    workflow.add_node("check_policy_reassess", check_policy)
    workflow.add_node("finalize_case", finalize_case)
    
    # Define primary linear flow
    workflow.set_entry_point("load_case")
    workflow.add_edge("load_case", "gather_context")
    workflow.add_edge("gather_context", "retrieve_memory")
    workflow.add_edge("retrieve_memory", "evaluate_evidence")
    workflow.add_edge("evaluate_evidence", "check_policy")
    
    # Define conditional branching
    workflow.add_conditional_edges(
        "check_policy",
        enough_evidence_condition,
        {
            "request_evidence": "request_and_simulate_evidence",
            "finalize": "finalize_case"
        }
    )
    
    # Secondary linear flow for simulated evidence feedback loop
    workflow.add_edge("request_and_simulate_evidence", "check_policy_reassess")
    workflow.add_edge("check_policy_reassess", "finalize_case")
    
    workflow.add_edge("finalize_case", END)
    
    return workflow.compile()