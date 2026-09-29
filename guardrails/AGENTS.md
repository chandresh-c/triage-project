# Guardrails & Safety Subsystem

## Responsibilities & Boundaries
- Sanitizes unstructured claim descriptions, notes, and uploaded text before LLM context ingestion.
- Redacts PII entities (SSN, 17-character VIN, telephone numbers, emails) complying with GLBA/HIPAA.
- Detects prompt injection and adversarial manipulation attempts, fencing untrusted user inputs.

## Key Interfaces
- `guardrails.pii.scrub_pii(text: str) -> tuple[str, list[str]]`: Returns sanitized text and list of redacted entity types.
- `guardrails.injection.detect_prompt_injection(text: str) -> bool`: Flags adversarial jailbreak attempts.
- `guardrails.injection.fence_untrusted_input(text: str) -> str`: Encloses untrusted inputs in XML boundary tags.

## Invariants & Rules
- PII redaction must occur upstream before passing any text to LLM inference or prompt builders.
- Fail-closed security: detected injections must halt autonomous fast-track and flag claim for human adjuster review.

## Testing Pattern
```bash
python -m pytest tests/test_guardrails.py -v
```
