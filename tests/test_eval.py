"""Unit tests for the evaluation benchmark suite."""

import pytest
from eval.scenarios import GOLD_SCENARIOS, generate_scenario_batch
from eval.runner import run_benchmark


class TestEvaluationSuite:
    def test_gold_scenarios_count(self):
        assert len(GOLD_SCENARIOS) == 6

    def test_batch_generator_distribution(self):
        batch = generate_scenario_batch(100)
        assert len(batch) == 100
        # Check distribution
        simple = [s for s in batch if s["expected_recommendation"] == "FAST_TRACK"]
        missing = [s for s in batch if s["expected_recommendation"] == "REQUEST_INFO"]
        assert len(simple) == 40
        assert len(missing) == 20

    def test_run_gold_benchmark_accuracy_and_safety(self):
        report = run_benchmark(GOLD_SCENARIOS)
        assert report.total_scenarios == 6
        assert report.accuracy == 100.0
        assert report.routing_accuracy == 100.0
        # Invariant: 0.0% false fast-track rate
        assert report.false_fast_track_rate == 0.0
        assert report.avg_latency_ms < 500.0  # Fast local execution
