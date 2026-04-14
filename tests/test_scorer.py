import pytest

from nxs_bench.scorer import (
    aggregate_suite_metrics,
    calculate_cost_normalized_accuracy,
    calculate_pass_k,
)
from nxs_bench.types import AttemptRecord


def test_calculate_pass_k_requires_every_attempt_to_pass() -> None:
    grouped_attempts = {
        "task-a": [True, True, True],
        "task-b": [True, False, True],
        "task-c": [True, True, True],
    }

    assert calculate_pass_k(grouped_attempts, 3) == pytest.approx(2 / 3)
    assert calculate_pass_k(grouped_attempts, 1) == pytest.approx(1.0)


def test_calculate_cost_normalized_accuracy_handles_zero_cost() -> None:
    assert calculate_cost_normalized_accuracy(backend_accuracy=0.9, cost_per_task_usd=0.3) == pytest.approx(3.0)
    assert calculate_cost_normalized_accuracy(backend_accuracy=0.9, cost_per_task_usd=0.0) == 0.0


def test_aggregate_suite_metrics_builds_difficulty_breakdown() -> None:
    attempts = [
        AttemptRecord(
            scenario_id="a1",
            suite_name="nxs_support",
            difficulty="easy",
            attempt_index=1,
            task_pass=True,
            functional_pass=True,
            safety_pass=True,
            quality_score=0.8,
            backend_accuracy=1.0,
            cost_usd=0.2,
            latency_ms=100,
            tool_calls=[],
            response="resolved",
            metadata={},
        ),
        AttemptRecord(
            scenario_id="a1",
            suite_name="nxs_support",
            difficulty="easy",
            attempt_index=2,
            task_pass=True,
            functional_pass=True,
            safety_pass=True,
            quality_score=0.8,
            backend_accuracy=1.0,
            cost_usd=0.2,
            latency_ms=110,
            tool_calls=[],
            response="resolved",
            metadata={},
        ),
        AttemptRecord(
            scenario_id="b1",
            suite_name="nxs_support",
            difficulty="hard",
            attempt_index=1,
            task_pass=False,
            functional_pass=False,
            safety_pass=True,
            quality_score=0.4,
            backend_accuracy=0.0,
            cost_usd=0.2,
            latency_ms=250,
            tool_calls=[],
            response="failed",
            metadata={},
        ),
        AttemptRecord(
            scenario_id="b1",
            suite_name="nxs_support",
            difficulty="hard",
            attempt_index=2,
            task_pass=False,
            functional_pass=False,
            safety_pass=True,
            quality_score=0.5,
            backend_accuracy=0.0,
            cost_usd=0.2,
            latency_ms=260,
            tool_calls=[],
            response="failed",
            metadata={},
        ),
    ]

    metrics = aggregate_suite_metrics(attempts, pass_k_repetitions=2)

    assert metrics.total_tasks == 2
    assert metrics.pass_at_1 == 0.5
    assert metrics.pass_k_3 == 0.0
    assert metrics.pass_k_5 == 0.0
    assert metrics.per_difficulty_results["easy"].pass_rate == 1.0
    assert metrics.per_difficulty_results["hard"].pass_rate == 0.0
    assert metrics.latency_p50_ms == 180
    assert metrics.latency_p95_ms == 260
