# backend/app/agent/workflow.py
from langgraph.graph import StateGraph, END
from ..models.state import InvestigationState
from .nodes_gather import load_case, gather_context, retrieve_memory
from .nodes_analyze import evaluate_evidence, check_policy, reassess_probability
from .nodes_finalize import request_and_simulate_evidence, finalize_case

def enough_evidence_condition(state: InvestigationState) -> str:
    uncertainty = state.get("uncertainty", False)
    has_requested = len(state.get("evidence_requests", [])) > 0
    if uncertainty and not has_requested:
        return "request_evidence"
    return "finalize"

def build_investigation_graph():
    workflow = StateGraph(InvestigationState)
    
    workflow.add_node("load_case", load_case)
    workflow.add_node("gather_context", gather_context)
    workflow.add_node("retrieve_memory", retrieve_memory)
    workflow.add_node("evaluate_evidence", evaluate_evidence)
    workflow.add_node("check_policy", check_policy)
    workflow.add_node("request_and_simulate_evidence", request_and_simulate_evidence)
    workflow.add_node("reassess_probability", reassess_probability)
    workflow.add_node("check_policy_reassess", check_policy)
    workflow.add_node("finalize_case", finalize_case)
    
    workflow.set_entry_point("load_case")
    workflow.add_edge("load_case", "gather_context")
    workflow.add_edge("gather_context", "retrieve_memory")
    workflow.add_edge("retrieve_memory", "evaluate_evidence")
    workflow.add_edge("evaluate_evidence", "check_policy")
    
    workflow.add_conditional_edges(
        "check_policy",
        enough_evidence_condition,
        {
            "request_evidence": "request_and_simulate_evidence",
            "finalize": "finalize_case"
        }
    )
    
    workflow.add_edge("request_and_simulate_evidence", "reassess_probability")
    workflow.add_edge("reassess_probability", "check_policy_reassess")
    workflow.add_edge("check_policy_reassess", "finalize_case")
    workflow.add_edge("finalize_case", END)
    
    return workflow.compile()