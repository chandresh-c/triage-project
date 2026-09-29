# Claims Triage Multi-Agent System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fully functional, self-contained, enterprise-grade Claims Triage System using LangGraph, Pydantic, hybrid policy RAG, enterprise API mocks (Guidewire ClaimCenter, Document AI), PII/security guardrails, and an automated 6-scenario (and 200+ batch) evaluation runner.

**Architecture:** A deterministic LangGraph StateGraph where data gathering (claims history, document parsing) runs in parallel, policy terms are retrieved via hybrid vector search, and a structured LLM triage node synthesizes coverage, fraud risk, and citations, followed by deterministic guardrail routing (fast-track vs. human-in-the-loop escalation).

**Tech Stack:** Python 3.11+, LangGraph, LangChain Core, Pydantic v2, OpenAI API (with integrated deterministic fallback), Pytest.

## Global Constraints
- Python 3.11+ compatibility.
- Zero mandatory external network dependencies: LLM node uses `OPENAI_API_KEY` if present, but seamlessly falls back to a deterministic rule-based LLM engine so tests and benchmarks always pass in offline or sandbox environments.
- Windows PowerShell compatibility (use `;` instead of `&&`).
- Adhere strictly to the repository cartography standards: each subsystem must have its own scoped `AGENTS.md` and tests.

---

### Task 1: Environment & Project Scaffolding
**Files:**
- Create: `requirements.txt`
- Create: `core/AGENTS.md`
- Create: `retrieval/AGENTS.md`
- Create: `integrations/AGENTS.md`
- Create: `guardrails/AGENTS.md`
- Create: `eval/AGENTS.md`

**Interfaces:**
- Produces: Project dependencies and subsystem scoped boundary documentation.

- [ ] **Step 1: Create requirements.txt**
Define dependencies: `langgraph>=0.2.0`, `langchain-core>=0.3.0`, `pydantic>=2.0.0`, `openai>=1.0.0`, `pytest>=7.0.0`.
- [ ] **Step 2: Create subsystem AGENTS.md files**
Create scoped `AGENTS.md` for `core/`, `retrieval/`, `integrations/`, `guardrails/`, and `eval/`.
- [ ] **Step 3: Verify environment**
Run: `python -m pip install -r requirements.txt`
- [ ] **Step 4: Commit**
`git add requirements.txt core/AGENTS.md retrieval/AGENTS.md integrations/AGENTS.md guardrails/AGENTS.md eval/AGENTS.md; git commit -m "chore: scaffold project requirements and subsystem AGENTS.md"`

---

### Task 2: Guardrails & Security Subsystem
**Files:**
- Create: `guardrails/pii.py`
- Create: `guardrails/injection.py`
- Create: `tests/test_guardrails.py`

**Interfaces:**
- Produces:
  - `guardrails.pii.scrub_pii(text: str) -> tuple[str, list[str]]`
  - `guardrails.injection.detect_prompt_injection(text: str) -> bool`
  - `guardrails.injection.fence_untrusted_input(text: str) -> str`

- [ ] **Step 1: Write failing test in tests/test_guardrails.py**
Test SSN, VIN, phone number redaction, and prompt injection detection (e.g., "ignore all previous instructions").
- [ ] **Step 2: Run test to verify it fails**
Run: `python -m pytest tests/test_guardrails.py -v` (fails with ModuleNotFoundError)
- [ ] **Step 3: Implement guardrails/pii.py and guardrails/injection.py**
Implement regex and pattern-based PII scrubber (matching SSNs `\d{3}-\d{2}-\d{4}`, standard 17-char VINs, phone numbers, and email addresses) and injection sanitizer.
- [ ] **Step 4: Run test to verify it passes**
Run: `python -m pytest tests/test_guardrails.py -v` (passes)
- [ ] **Step 5: Commit**
`git add guardrails/ tests/test_guardrails.py; git commit -m "feat: implement PII scrubbing and prompt injection guardrails"`

---

### Task 3: Enterprise Integrations Subsystem
**Files:**
- Create: `integrations/guidewire.py`
- Create: `integrations/document_ai.py`
- Create: `tests/test_integrations.py`

**Interfaces:**
- Produces:
  - `integrations.guidewire.get_policy_details(policy_number: str) -> dict`
  - `integrations.guidewire.get_claims_history(policy_number: str) -> dict`
  - `integrations.document_ai.parse_claim_document(doc_type: str, content: str) -> dict`

- [ ] **Step 1: Write failing test in tests/test_integrations.py**
Test policy retrieval, claims history retrieval (with fraud indicator checks), and document parsing.
- [ ] **Step 2: Run test to verify it fails**
Run: `python -m pytest tests/test_integrations.py -v` (fails)
- [ ] **Step 3: Implement integrations/guidewire.py and integrations/document_ai.py**
Provide realistic simulated Guidewire ClaimCenter responses (active coverages, collision deductible, tenure, past claims, SIU flags) and Document AI key-value extraction for police reports and repair estimates.
- [ ] **Step 4: Run test to verify it passes**
Run: `python -m pytest tests/test_integrations.py -v` (passes)
- [ ] **Step 5: Commit**
`git add integrations/ tests/test_integrations.py; git commit -m "feat: implement Guidewire and Document AI integration mocks"`

---

### Task 4: Policy Retrieval RAG Subsystem
**Files:**
- Create: `retrieval/policies.py`
- Create: `retrieval/store.py`
- Create: `tests/test_retrieval.py`

**Interfaces:**
- Produces:
  - `retrieval.store.PolicyVectorStore`
  - `store.search(query: str, top_k: int = 3) -> list[dict]` (hybrid dense + token overlap search)

- [ ] **Step 1: Write failing test in tests/test_retrieval.py**
Test searching for collision deductible, track racing exclusion, ride-share exclusion, and rental car reimbursement.
- [ ] **Step 2: Run test to verify it fails**
Run: `python -m pytest tests/test_retrieval.py -v` (fails)
- [ ] **Step 3: Implement retrieval/policies.py and retrieval/store.py**
Standard auto insurance policy clauses (Section I: Collision, Section II: Comprehensive, Section III: Exclusions, Section IV: Conditions) and hybrid similarity search.
- [ ] **Step 4: Run test to verify it passes**
Run: `python -m pytest tests/test_retrieval.py -v` (passes)
- [ ] **Step 5: Commit**
`git add retrieval/ tests/test_retrieval.py; git commit -m "feat: implement policy retrieval RAG subsystem"`

---

### Task 5: Core LangGraph State & Reasoning Subsystem
**Files:**
- Create: `core/state.py`
- Create: `core/nodes.py`
- Create: `core/graph.py`
- Create: `tests/test_core.py`

**Interfaces:**
- Consumes: `guardrails`, `integrations`, `retrieval`
- Produces:
  - `core.state.TriageDecision`, `core.state.TriageState`
  - `core.graph.build_claims_graph(checkpointer=None)`
  - `core.graph.process_claim(claim_input: dict) -> dict`

- [ ] **Step 1: Write failing test in tests/test_core.py**
Test state transitions, structured triage decision schema validation, and guardrail routing logic.
- [ ] **Step 2: Run test to verify it fails**
Run: `python -m pytest tests/test_core.py -v` (fails)
- [ ] **Step 3: Implement core/state.py, core/nodes.py, and core/graph.py**
Implement Pydantic models, parallel gathering nodes (`fetch_guidewire_data`, `parse_documents`), policy RAG node, LLM reasoning node with OpenAI API call and deterministic fallback, and deterministic router edge.
- [ ] **Step 4: Run test to verify it passes**
Run: `python -m pytest tests/test_core.py -v` (passes)
- [ ] **Step 5: Commit**
`git add core/ tests/test_core.py; git commit -m "feat: implement LangGraph state graph and triage synthesis"`

---

### Task 6: Evaluation Benchmark Suite
**Files:**
- Create: `eval/scenarios.py`
- Create: `eval/runner.py`
- Create: `tests/test_eval.py`

**Interfaces:**
- Consumes: `core.graph.process_claim`
- Produces:
  - `eval.scenarios.GOLD_SCENARIOS`: 6 core test scenarios
  - `eval.scenarios.generate_scenario_batch(n=200)`: 200+ scenario generator
  - `eval.runner.run_benchmark()`: Full metrics evaluator (accuracy, precision, recall, false fast-track rate)

- [ ] **Step 1: Write failing test in tests/test_eval.py**
Test running the evaluation runner across the 6 gold scenarios and asserting accuracy > 90% and false fast-track rate == 0.0%.
- [ ] **Step 2: Run test to verify it fails**
Run: `python -m pytest tests/test_eval.py -v` (fails)
- [ ] **Step 3: Implement eval/scenarios.py and eval/runner.py**
Implement 6 detailed scenarios (Simple Claim, Exclusion, Missing Docs, SIU Fraud, Coverage Q&A, Ambiguous Conflict), batch generator, and benchmark metric runner.
- [ ] **Step 4: Run test to verify it passes**
Run: `python -m pytest tests/test_eval.py -v` (passes)
- [ ] **Step 5: Commit**
`git add eval/ tests/test_eval.py; git commit -m "feat: implement evaluation benchmark runner and scenarios"`

---

### Task 7: End-to-End Verification & Documentation
**Files:**
- Create: `tests/test_workflow.py`
- Modify: `README.md`

- [ ] **Step 1: Run complete pytest suite**
Run: `python -m pytest tests/ -v` (all tests pass)
- [ ] **Step 2: Run CLI benchmark tool**
Run: `python -m eval.runner` (prints full metrics table to console)
- [ ] **Step 3: Write comprehensive README.md**
Document architecture, setup guide, interview talking points, cost calculation, and running instructions.
- [ ] **Step 4: Commit**
`git add tests/test_workflow.py README.md; git commit -m "docs: add comprehensive README and end-to-end verification"`
