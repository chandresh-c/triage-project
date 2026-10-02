# Claims Triage Multi-Agent System

Enterprise insurance claims triage automation orchestrating policy verification, document validation, fraud detection, and adjuster routing via LangGraph.

## Quick Start & Verification
```bash
# Setup virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Run full evaluation benchmark across all test scenarios
python -m pytest tests/ -v
python -m eval.runner
```

## Active Lessons & Invariants
Review Tier 1 invariants in [.gemini/memory/active_lessons.md](file:///D:/Downloads/triage_project/.gemini/memory/active_lessons.md).
For candidate interview Q&A and technical rationale, see [docs/INTERVIEW_QNA_GUIDE.md](file:///D:/Downloads/triage_project/docs/INTERVIEW_QNA_GUIDE.md).
For cloud architecture, deployment & telemetry, see [docs/AZURE_DEPLOYMENT_OBSERVABILITY_GUIDE.md](file:///D:/Downloads/triage_project/docs/AZURE_DEPLOYMENT_OBSERVABILITY_GUIDE.md).


## Subsystems Map
| Subsystem | Scoped Guide | Responsibility |
| :--- | :--- | :--- |
| **Orchestration Core** | [core/AGENTS.md](file:///D:/Downloads/triage_project/core/AGENTS.md) | LangGraph state graph, node routers, HITL checkpoints |
| **Policy Retrieval** | [retrieval/AGENTS.md](file:///D:/Downloads/triage_project/retrieval/AGENTS.md) | RAG over policy documents, chunking, vector similarity |
| **Enterprise Integrations**| [integrations/AGENTS.md](file:///D:/Downloads/triage_project/integrations/AGENTS.md) | Mock Guidewire ClaimCenter API, Document AI parser |
| **Guardrails & Safety** | [guardrails/AGENTS.md](file:///D:/Downloads/triage_project/guardrails/AGENTS.md) | PII masking (Presidio pattern), hallucination guards |
| **Evaluation Benchmark** | [eval/AGENTS.md](file:///D:/Downloads/triage_project/eval/AGENTS.md) | 200+ curated claim scenarios, accuracy & routing metrics |
