# Evaluation Benchmark Subsystem

## Responsibilities & Boundaries
- Defines standard benchmark scenarios representing realistic insurance claim archetypes.
- Generates synthetic evaluation batches (up to 200+ scenarios) testing edge cases and load.
- Executes automated regression evaluations reporting accuracy, precision, recall, and false fast-track rates.

## Key Interfaces
- `eval.scenarios.GOLD_SCENARIOS`: 6 core curated scenarios (clean claim, excluded loss, missing docs, SIU fraud, coverage Q&A, ambiguous liability).
- `eval.scenarios.generate_scenario_batch(n=200) -> list[dict]`: Synthetic benchmark batch generator.
- `eval.runner.run_benchmark()`: Executes evaluation against `core.graph.process_claim` and computes metrics.

## Invariants & Rules
- False Fast-Track Rate must strictly be 0.0% (fraudulent or clearly excluded claims must never be auto-approved).
- Benchmark must run deterministically in CI/CD without requiring live external API keys.

## Testing Pattern
```bash
python -m pytest tests/test_eval.py -v
python -m eval.runner
```
