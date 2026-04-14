from __future__ import annotations

from collections import defaultdict
from math import ceil
from statistics import median

from .types import AttemptRecord, DifficultyResult, SuiteMetrics


def calculate_pass_k(grouped_attempts: dict[str, list[bool]], k: int) -> float:
    if k <= 0 or not grouped_attempts:
        return 0.0
    successes = 0
    for attempts in grouped_attempts.values():
        if len(attempts) < k:
            continue
        if all(attempts[index] for index in range(k)):
            successes += 1
    return successes / len(grouped_attempts)


def calculate_cost_normalized_accuracy(backend_accuracy: float, cost_per_task_usd: float) -> float:
    if cost_per_task_usd <= 0:
        return 0.0
    return backend_accuracy / cost_per_task_usd


def aggregate_suite_metrics(attempts: list[AttemptRecord], pass_k_repetitions: int) -> SuiteMetrics:
    if not attempts:
        empty_difficulties = {
            difficulty: DifficultyResult(count=0, pass_rate=0.0)
            for difficulty in ("easy", "medium", "hard", "adversarial")
        }
        return SuiteMetrics(
            total_tasks=0,
            pass_at_1=0.0,
            pass_k_3=0.0,
            pass_k_5=0.0,
            task_pass_rate=0.0,
            quality_score=0.0,
            safety_pass_rate=0.0,
            backend_accuracy=0.0,
            cost_per_task_usd=0.0,
            cost_normalized_accuracy=0.0,
            latency_p50_ms=0,
            latency_p95_ms=0,
            per_difficulty_results=empty_difficulties,
        )

    attempts_by_task: dict[str, list[AttemptRecord]] = defaultdict(list)
    for attempt in attempts:
        attempts_by_task[attempt.scenario_id].append(attempt)
    for task_attempts in attempts_by_task.values():
        task_attempts.sort(key=lambda item: item.attempt_index)

    first_attempts = [task_attempts[0] for task_attempts in attempts_by_task.values()]
    grouped_passes = {
        scenario_id: [attempt.task_pass for attempt in task_attempts]
        for scenario_id, task_attempts in attempts_by_task.items()
    }

    latency_values = sorted(attempt.latency_ms for attempt in attempts)
    cost_values = [attempt.cost_usd for attempt in attempts]
    quality_values = [attempt.quality_score for attempt in attempts]
    backend_values = [attempt.backend_accuracy for attempt in attempts]
    safety_values = [1.0 if attempt.safety_pass else 0.0 for attempt in attempts]
    task_pass_values = [1.0 if attempt.task_pass else 0.0 for attempt in attempts]

    per_difficulty_results: dict[str, DifficultyResult] = {}
    for difficulty in ("easy", "medium", "hard", "adversarial"):
        difficulty_attempts = [attempt for attempt in first_attempts if attempt.difficulty == difficulty]
        per_difficulty_results[difficulty] = DifficultyResult(
            count=len(difficulty_attempts),
            pass_rate=(sum(1 for attempt in difficulty_attempts if attempt.task_pass) / len(difficulty_attempts))
            if difficulty_attempts
            else 0.0,
        )

    backend_accuracy = sum(backend_values) / len(backend_values)
    cost_per_task = sum(cost_values) / len(cost_values)
    return SuiteMetrics(
        total_tasks=len(attempts_by_task),
        pass_at_1=sum(1 for attempt in first_attempts if attempt.task_pass) / len(first_attempts),
        pass_k_3=calculate_pass_k(grouped_passes, 3) if pass_k_repetitions >= 3 else 0.0,
        pass_k_5=calculate_pass_k(grouped_passes, 5) if pass_k_repetitions >= 5 else 0.0,
        task_pass_rate=sum(task_pass_values) / len(task_pass_values),
        quality_score=sum(quality_values) / len(quality_values),
        safety_pass_rate=sum(safety_values) / len(safety_values),
        backend_accuracy=backend_accuracy,
        cost_per_task_usd=cost_per_task,
        cost_normalized_accuracy=calculate_cost_normalized_accuracy(backend_accuracy, cost_per_task),
        latency_p50_ms=int(median(latency_values)),
        latency_p95_ms=_percentile(latency_values, 95),
        per_difficulty_results=per_difficulty_results,
    )


def compare_results(baseline: dict, candidate: dict) -> dict[str, dict[str, float]]:
    metrics = (
        "pass_at_1",
        "pass_k_3",
        "pass_k_5",
        "task_pass_rate",
        "quality_score",
        "safety_pass_rate",
        "backend_accuracy",
        "cost_per_task_usd",
        "cost_normalized_accuracy",
        "latency_p50_ms",
        "latency_p95_ms",
    )
    deltas: dict[str, dict[str, float]] = {}
    baseline_suites = baseline.get("suites", {})
    candidate_suites = candidate.get("suites", {})
    for suite_name in sorted(set(baseline_suites) & set(candidate_suites)):
        deltas[suite_name] = {}
        for metric in metrics:
            deltas[suite_name][metric] = candidate_suites[suite_name].get(metric, 0) - baseline_suites[suite_name].get(metric, 0)
    return deltas


def _percentile(values: list[int], percentile: int) -> int:
    if not values:
        return 0
    rank = ceil((percentile / 100) * len(values)) - 1
    rank = max(0, min(rank, len(values) - 1))
    return int(values[rank])
