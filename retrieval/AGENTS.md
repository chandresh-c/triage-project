# Policy Retrieval RAG Subsystem

## Responsibilities & Boundaries
- Manages standardized auto insurance policy forms (Collision, Comprehensive, Exclusions, Conditions).
- Implements deterministic, self-contained hybrid similarity search (dense embeddings + BM25/token overlap).
- Returns referenced policy clauses with section numbers and exact policy language for LLM grounding.

## Key Interfaces
- `retrieval.policies.POLICY_DOCUMENTS`: Structured catalog of policy sections and clauses.
- `retrieval.store.PolicyVectorStore`: In-memory index supporting `search(query: str, top_k: int = 3) -> list[dict]`.
- Output format: List of chunk dictionaries containing `section`, `clause`, `text`, and `relevance_score`.

## Invariants & Rules
- Zero mandatory external vector DB dependencies; must operate fully in-memory with offline determinism.
- Exact clause citations must accompany every retrieved policy fragment.

## Testing Pattern
```bash
python -m pytest tests/test_retrieval.py -v
```
