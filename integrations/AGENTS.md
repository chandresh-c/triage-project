# Enterprise Integrations Subsystem

## Responsibilities & Boundaries
- Simulates Guidewire ClaimCenter core system REST/SQL integration (policy status, deductible, claims history, SIU flags).
- Simulates Document AI extraction for claims documents (police reports, repair estimates).
- Formats structured payloads consumable by core orchestration nodes.

## Key Interfaces
- `integrations.guidewire.get_policy_details(policy_number: str) -> dict`: Returns active coverages, limits, deductibles.
- `integrations.guidewire.get_claims_history(policy_number: str) -> dict`: Returns past claims and SIU fraud markers.
- `integrations.document_ai.parse_claim_document(doc_type: str, content: str) -> dict`: Key-value extraction from documents.

## Invariants & Rules
- Deterministic API simulation; never route simple system-of-record queries through LLMs.
- Document parsing must handle malformed/missing fields gracefully without unhandled exceptions.

## Testing Pattern
```bash
python -m pytest tests/test_integrations.py -v
```
