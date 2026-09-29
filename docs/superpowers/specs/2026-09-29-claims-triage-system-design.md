# Design Specification: Claims Triage Multi-Agent System

**Date**: 2026-09-29  
**Status**: Approved  
**Author**: Antigravity & Pair Programming Partner  
**Target Repository**: `D:\Downloads\triage_project`

---

## 1. Overview & Business Objective

This project implements an enterprise-grade automated insurance claims triage system. It demonstrates how a modern property & casualty (P&C) insurer automates First Notice of Loss (FNOL) triage, policy verification, document validation, fraud risk screening, and human-in-the-loop (HITL) adjuster routing using **LangGraph**, **Pydantic**, and **OpenAI**.

The system replaces manual, error-prone 48-hour intake reviews with a deterministic, low-latency (<5s) state graph, reducing operational triage costs while guaranteeing zero autonomous payouts for high-risk, ambiguous, or excluded claims.

---

## 2. Architectural Decisions & Skeptical Analysis

### 2.1 Deterministic State Graph vs. Conversational Multi-Agent Swarm
* **Flawed Proposal**: Chaining 4 autonomous LLM agents sequentially (`Policy Agent → History Agent → Document Agent → Triage Agent`).
* **Why Rejected**: Linear latency compounding (15–20s total), 4x token costs, non-deterministic loops, and catastrophic error cascade where upstream hallucinations corrupt downstream decisions.
* **Adopted Architecture**: A **LangGraph StateGraph**:
  - Deterministic data fetching (ClaimCenter API) and document parsing (Document AI) execute in parallel.
  - Hybrid policy retrieval (Vector + BM25) surfaces relevant contract clauses.
  - A single synthesis LLM call generates structured triage recommendations with citations.
  - Deterministic safety guardrail edges enforce mandatory human escalation for high damage (> $10k), bodily injury, low confidence (< 0.85), or policy exclusions.

### 2.2 LLM Engine & Graceful Fallback
* Supports live calls to OpenAI (`gpt-4o` for triage reasoning, `gpt-4o-mini` for extraction) via `OPENAI_API_KEY`.
* Includes an integrated deterministic fallback engine so the entire test suite and evaluation runner execute reliably with zero network dependencies or when an API key is not supplied.

---

## 3. Subsystem Breakdown & Repository Cartography

In accordance with repository cartography standards, the system is decomposed into decoupled subsystems, each accompanied by its own scoped `AGENTS.md`:

```
triage_project/
├── .gemini/
│   └── memory/
│       ├── active_lessons.md
│       ├── catalog.jsonl
│       └── inbox.md
├── GEMINI.md                    # Root cartography guide (<400 words)
├── requirements.txt             # Project dependencies
├── core/                        # LangGraph State Graph & Orchestration
│   ├── AGENTS.md                # Scoped subsystem contract
│   ├── state.py                 # TriageState TypedDict & Pydantic output schemas
│   ├── nodes.py                 # Ingestion, parallel fetch, RAG, reasoning, guardrail nodes
│   └── graph.py                 # StateGraph definition and compilation with checkpoints
├── retrieval/                   # Policy Document RAG Subsystem
│   ├── AGENTS.md                # Scoped subsystem contract
│   ├── policies.py              # Gold standard auto insurance policies & exclusions
│   └── store.py                 # In-memory hybrid vector store (dense cosine + BM25)
├── integrations/                # Enterprise System Integrations
│   ├── AGENTS.md                # Scoped subsystem contract
│   ├── guidewire.py             # Mock Guidewire ClaimCenter REST API
│   └── document_ai.py           # Mock Azure Document Intelligence OCR parser
├── guardrails/                  # Safety, Privacy & Compliance
│   ├── AGENTS.md                # Scoped subsystem contract
│   ├── pii.py                   # PII scrubbing (SSN, VIN, names, phones)
│   └── injection.py             # Prompt injection defense and delimiter fencing
├── eval/                        # Evaluation Benchmark Suite
│   ├── AGENTS.md                # Scoped subsystem contract
│   ├── scenarios.py             # Curated gold scenarios + 200+ scenario generator
│   └── runner.py                # Benchmark evaluator (accuracy, recall, cost, latency)
└── tests/                       # Automated Pytest Suite
    └── test_workflow.py         # Full end-to-end integration and unit tests
```

---

## 4. State Schema & Data Models

### 4.1 Output Schema (`TriageDecision`)
```python
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class TriageDecision(BaseModel):
    recommendation: Literal["FAST_TRACK", "MANUAL_REVIEW", "SIU_FRAUD_INVESTIGATION", "REQUEST_INFO"]
    confidence_score: float = Field(ge=0.0, le=1.0)
    fraud_risk_score: float = Field(ge=0.0, le=1.0)
    is_covered: bool
    policy_exclusions_identified: List[str]
    missing_documents: List[str]
    citations: List[str]
    reasoning: str
```

### 4.2 Graph State (`TriageState`)
```python
from typing import TypedDict, List, Dict, Any, Optional

class TriageState(TypedDict):
    claim_id: str
    policy_number: str
    incident_date: str
    claimant_statement: str
    raw_documents: List[Dict[str, Any]]
    sanitized_documents: List[Dict[str, Any]]
    pii_entities_scrubbed: List[str]
    claims_history: Dict[str, Any]
    retrieved_policy_clauses: List[Dict[str, Any]]
    decision: Optional[TriageDecision]
    requires_human_review: bool
    escalation_reason: Optional[str]
    errors: List[str]
```

---

## 5. Execution Flow

```
                     [Start: Submit Claim]
                               │
                               ▼
                    [1. Ingest & Scrub PII]
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
     [2a. Fetch Guidewire DB]     [2b. OCR Document AI]
                └──────────────┬──────────────┘
                               │
                               ▼
                   [3. Retrieve Policy RAG]
                               │
                               ▼
                   [4. LLM Triage Reasoning]
                               │
                               ▼
                   [5. Deterministic Guardrail]
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
       (All rules passed?)              (Risk/Exclusion/Low Conf?)
         [FAST_TRACK]                   [HUMAN_ADJUSTER_QUEUE]
```

---

## 6. Evaluation Framework

The system includes an automated evaluation harness in `eval/` running both the 6 golden test scenarios and a synthetic 200+ scenario generator:
1. **Simple Auto Claim**: Clean rear-end collision, full documents, zero past claims -> `FAST_TRACK`.
2. **Policy Exclusion**: Track racing or intentional damage -> `MANUAL_REVIEW` / Denied with exact policy citation.
3. **Missing Documents**: Claim filed without police report or repair estimate -> `REQUEST_INFO`.
4. **High-Risk / Fraud (SIU)**: Inconsistent dates, multiple claims in 90 days, staged accident flags -> `SIU_FRAUD_INVESTIGATION`.
5. **Coverage Query**: Clarifying deductible and rental car limits -> Grounded answer from policy.
6. **Ambiguous Conflict**: Conflicting statements between driver and witness -> `MANUAL_REVIEW` (no hallucinated assumptions).

### Target Metrics:
- **Routing Accuracy**: > 95% across evaluation scenarios.
- **False Fast-Track Rate (Critical Safety)**: 0.0% (Zero ineligible claims auto-approved).
- **Execution Latency**: < 2.5s in mock mode; < 5.0s in live API mode.

---

## 7. Verification Plan
- Unit tests for PII scrubbing and prompt injection guards.
- Unit tests for Guidewire API and Document AI mockers.
- Unit tests for Policy hybrid search (vector + BM25).
- End-to-end integration tests in `tests/test_workflow.py` executing all 6 scenarios via LangGraph.
- Evaluation benchmark runner (`python -m eval.runner`) producing a full performance report.
