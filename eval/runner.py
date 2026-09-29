"""
Evaluation Benchmark Runner.

Executes claims triage evaluation scenarios, computes precision, recall,
accuracy, false fast-track rate, and token cost economics.
"""

from typing import List, Dict, Any, Optional
import time
from core.graph import process_claim
from eval.scenarios import GOLD_SCENARIOS, generate_scenario_batch


class EvaluationReport:
    """Holds aggregate benchmark performance metrics."""

    def __init__(self):
        self.total_scenarios: int = 0
        self.correct_recommendations: int = 0
        self.correct_routing: int = 0
        self.false_fast_track_count: int = 0  # CRITICAL INVARIANT: Non-fast-track routed as fast-track
        self.latencies_ms: List[float] = []
        self.category_counts: Dict[str, Dict[str, int]] = {
            "FAST_TRACK": {"expected": 0, "predicted": 0, "true_positives": 0},
            "MANUAL_REVIEW": {"expected": 0, "predicted": 0, "true_positives": 0},
            "SIU_FRAUD_INVESTIGATION": {"expected": 0, "predicted": 0, "true_positives": 0},
            "REQUEST_INFO": {"expected": 0, "predicted": 0, "true_positives": 0}
        }

    def record_result(self, scenario: Dict[str, Any], output_state: Dict[str, Any], latency_ms: float):
        self.total_scenarios += 1
        self.latencies_ms.append(latency_ms)

        expected_rec = scenario.get("expected_recommendation")
        expected_review = scenario.get("expected_human_review")
        
        decision = output_state.get("decision")
        pred_rec = decision.recommendation if decision else "UNKNOWN"
        pred_review = output_state.get("requires_human_review", True)

        # Update category counts
        if expected_rec in self.category_counts:
            self.category_counts[expected_rec]["expected"] += 1
        if pred_rec in self.category_counts:
            self.category_counts[pred_rec]["predicted"] += 1

        if expected_rec == pred_rec:
            self.correct_recommendations += 1
            if expected_rec in self.category_counts:
                self.category_counts[expected_rec]["true_positives"] += 1

        if expected_review == pred_review:
            self.correct_routing += 1

        # Check Critical Invariant: False Fast-Track
        if expected_rec != "FAST_TRACK" and pred_rec == "FAST_TRACK":
            self.false_fast_track_count += 1

    @property
    def accuracy(self) -> float:
        return (self.correct_recommendations / self.total_scenarios) * 100.0 if self.total_scenarios > 0 else 0.0

    @property
    def routing_accuracy(self) -> float:
        return (self.correct_routing / self.total_scenarios) * 100.0 if self.total_scenarios > 0 else 0.0

    @property
    def false_fast_track_rate(self) -> float:
        return (self.false_fast_track_count / self.total_scenarios) * 100.0 if self.total_scenarios > 0 else 0.0

    @property
    def avg_latency_ms(self) -> float:
        return sum(self.latencies_ms) / len(self.latencies_ms) if self.latencies_ms else 0.0

    def print_summary(self):
        print("\n" + "=" * 70)
        print(" CLAIMS TRIAGE MULTI-AGENT SYSTEM: EVALUATION BENCHMARK REPORT")
        print("=" * 70)
        print(f"Total Scenarios Evaluated   : {self.total_scenarios}")
        print(f"Overall Decision Accuracy   : {self.accuracy:.2f}%")
        print(f"Routing Decision Accuracy   : {self.routing_accuracy:.2f}%")
        print(f"False Fast-Track Rate (P0)  : {self.false_fast_track_rate:.2f}% (Target: 0.00%)")
        print(f"Average Pipeline Latency    : {self.avg_latency_ms:.1f} ms")
        print("-" * 70)
        print(f"{'Category':<26} | {'Precision':<10} | {'Recall':<10} | {'Count'}")
        print("-" * 70)
        for cat, stats in self.category_counts.items():
            tp = stats["true_positives"]
            pred = stats["predicted"]
            exp = stats["expected"]
            prec = (tp / pred * 100.0) if pred > 0 else 0.0
            rec = (tp / exp * 100.0) if exp > 0 else 0.0
            print(f"{cat:<26} | {prec:>8.1f}% | {rec:>8.1f}% | {exp:>5}")
        print("-" * 70)
        print("Cost Analysis (Simulated 50,000 monthly claims):")
        cost_per_claim = 0.0075  # USD
        monthly_cost = 50000 * cost_per_claim
        print(f"Estimated LLM Cost / Claim  : ${cost_per_claim:.4f}")
        print(f"Total Monthly Compute Spend : ${monthly_cost:,.2f}")
        print("=" * 70 + "\n")


def run_benchmark(scenarios: Optional[List[Dict[str, Any]]] = None) -> EvaluationReport:
    """Run full evaluation suite over scenarios and return report."""
    test_cases = scenarios if scenarios is not None else GOLD_SCENARIOS
    report = EvaluationReport()

    for item in test_cases:
        claim_input = item["input"]
        start_t = time.perf_counter()
        output_state = process_claim(claim_input)
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        report.record_result(item, output_state, elapsed_ms)

    return report


if __name__ == "__main__":
    print("Running Claims Triage Gold Standard Evaluation (6 Scenarios)...")
    gold_report = run_benchmark(GOLD_SCENARIOS)
    gold_report.print_summary()

    print("Running Batch Evaluation (200 Synthetic Scenarios)...")
    batch_scenarios = generate_scenario_batch(200)
    batch_report = run_benchmark(batch_scenarios)
    batch_report.print_summary()
