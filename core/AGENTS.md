# Orchestration Core Subsystem

## Responsibilities & Boundaries
- Manages the LangGraph `StateGraph` orchestrating end-to-end claim triage workflows.
- Coordinates parallel data gathering (policy lookup, document extraction) and retrieval before LLM synthesis.
- Enforces deterministic human-in-the-loop (HITL) checkpoints (`interrupt_before`) for high-risk, ambiguous, or excluded claims.

## Key Interfaces
- `core.state.TriageDecision`: Pydantic schema for structured triage outputs (routing action, coverage assessment, fraud score, citations).
- `core.state.TriageState`: Typed state container for claim data, retrieved policies, extracted evidence, and audit logs.
- `core.graph.build_claims_graph(checkpointer=None)`: Constructs compiled LangGraph instance.
- `core.graph.process_claim(claim_input: dict) -> dict`: Convenience entry point for triage execution.

## Invariants & Rules
- Do not chain serial conversational LLM agents; parallelize deterministic fetches and synthesize once.
- Deterministic routing overrides: fraud flags or explicit policy exclusions must route to adjuster escalation.

## Testing Pattern
```bash
python -m pytest tests/test_core.py -v
```
