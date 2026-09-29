# Active Lessons Learned (Tier 1 Invariants)

1. **Deterministic Logic Over LLM Agent Chaining**: In enterprise claims triage, deterministic lookups (SQL/REST to ClaimCenter) must never be wrapped in LLM conversational agents. Chaining 4 serial LLM calls introduces compounding latency (15-20s), error cascades, and token cost.
2. **LangGraph State Graph with Human-in-the-Loop (HITL)**: Route ambiguous, high-risk, or excluded claims to human adjusters via LangGraph checkpoints (`interrupt_before`) rather than allowing LLMs to guess autonomous claim settlement.
3. **PII Redaction Before LLM Context Ingestion**: Insured party SSNs, policy IDs, VINs, and medical records must be masked/tokenized before hitting LLM inference endpoints to comply with GLBA/HIPAA regulations.
