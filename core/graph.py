"""
LangGraph Workflow Definition for Claims Triage.

Orchestrates data ingestion, parallel Guidewire and Document AI extraction,
hybrid policy RAG retrieval, structured triage reasoning, and conditional
routing to Auto-Settlement or Human Adjuster Queue (HITL).
"""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from core.state import TriageState
from core.nodes import (
    ingest_and_scrub_pii_node,
    fetch_guidewire_data_node,
    parse_documents_node,
    retrieve_policy_rag_node,
    triage_reasoning_node,
    guardrail_router_node,
    adjuster_queue_node,
    auto_settlement_node
)


def _route_decision(state: TriageState) -> str:
    """Evaluate router edge: send to human adjuster or auto-settlement."""
    if state.get("requires_human_review", True):
        return "adjuster_queue"
    return "auto_settlement"


def build_claims_graph(checkpointer: Optional[Any] = None) -> Any:
    """
    Construct and compile the LangGraph claims triage state graph.
    
    Args:
        checkpointer: Optional persistence checkpointer (e.g. MemorySaver)
                     enabling Human-In-The-Loop interrupts.
                     
    Returns:
        Compiled LangGraph runnable.
    """
    workflow = StateGraph(TriageState)

    # Register workflow nodes
    workflow.add_node("ingest_pii", ingest_and_scrub_pii_node)
    workflow.add_node("fetch_guidewire", fetch_guidewire_data_node)
    workflow.add_node("parse_documents", parse_documents_node)
    workflow.add_node("retrieve_policy", retrieve_policy_rag_node)
    workflow.add_node("triage_reasoning", triage_reasoning_node)
    workflow.add_node("guardrail_router", guardrail_router_node)
    workflow.add_node("adjuster_queue", adjuster_queue_node)
    workflow.add_node("auto_settlement", auto_settlement_node)

    # Define DAG flow
    workflow.add_edge(START, "ingest_pii")
    
    # Parallel fan-out after PII scrubbing
    workflow.add_edge("ingest_pii", "fetch_guidewire")
    workflow.add_edge("ingest_pii", "parse_documents")
    
    # Fan-in before policy retrieval
    workflow.add_edge("fetch_guidewire", "retrieve_policy")
    workflow.add_edge("parse_documents", "retrieve_policy")
    
    # Sequential reasoning and guardrailing
    workflow.add_edge("retrieve_policy", "triage_reasoning")
    workflow.add_edge("triage_reasoning", "guardrail_router")

    # Conditional routing edge
    workflow.add_conditional_edges(
        "guardrail_router",
        _route_decision,
        {
            "adjuster_queue": "adjuster_queue",
            "auto_settlement": "auto_settlement"
        }
    )

    workflow.add_edge("adjuster_queue", END)
    workflow.add_edge("auto_settlement", END)

    if checkpointer:
        return workflow.compile(
            checkpointer=checkpointer,
            interrupt_before=["adjuster_queue"]
        )
    return workflow.compile()


def process_claim(claim_input: Dict[str, Any], checkpointer: Optional[Any] = None) -> Dict[str, Any]:
    """
    Execute end-to-end claim triage through the LangGraph workflow.
    
    Args:
        claim_input: Dictionary with claim_id, policy_number, incident_date,
                     claimant_statement, and raw_documents.
                     
    Returns:
        Final state dictionary containing the TriageDecision and routing metadata.
    """
    app = build_claims_graph(checkpointer=checkpointer)
    initial_state: TriageState = {
        "claim_id": claim_input.get("claim_id", "CLM-UNKNOWN"),
        "policy_number": claim_input.get("policy_number", "POL-DEFAULT"),
        "incident_date": claim_input.get("incident_date", "2025-01-01"),
        "claimant_statement": claim_input.get("claimant_statement", ""),
        "raw_documents": claim_input.get("raw_documents", []),
        "errors": []
    }
    
    final_state = app.invoke(initial_state)
    return final_state
