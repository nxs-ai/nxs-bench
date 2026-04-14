from __future__ import annotations

from statistics import mean

from .assertions import BehaviorAssertion
from .types import BehaviorAssertionResult, ConversationEvaluation, ConversationTurn


class ConversationEvaluator:
    """Standalone eight-dimension evaluator with heuristic fallbacks."""

    DIMENSIONS = (
        "task_completion",
        "clarity",
        "completeness",
        "empathy",
        "policy_compliance",
        "tool_use",
        "efficiency",
        "groundedness",
    )

    def __init__(self, *, evaluator_model: str = "heuristic") -> None:
        self.evaluator_model = evaluator_model

    def evaluate(
        self,
        conversation: list[ConversationTurn],
        *,
        required_behaviors: list[str],
        forbidden_behaviors: list[str],
        expected_resolution: bool,
        tool_assertion_pass_rate: float,
        backend_accuracy: float,
    ) -> ConversationEvaluation:
        transcript = "\n".join(f"{turn.role}: {turn.content}" for turn in conversation)
        lower_transcript = transcript.lower()
        behavior_results: list[BehaviorAssertionResult] = []

        for behavior in forbidden_behaviors:
            verdict, passed = BehaviorAssertion(behavior=behavior, is_forbidden=True).check(transcript)
            behavior_results.append(
                BehaviorAssertionResult(
                    behavior=behavior,
                    is_forbidden=True,
                    verdict=verdict,
                    passed=passed,
                    detail=f"Forbidden behavior evaluation: {verdict}",
                )
            )

        for behavior in required_behaviors:
            verdict, passed = BehaviorAssertion(behavior=behavior, is_forbidden=False).check(transcript)
            behavior_results.append(
                BehaviorAssertionResult(
                    behavior=behavior,
                    is_forbidden=False,
                    verdict=verdict,
                    passed=passed,
                    detail=f"Required behavior evaluation: {verdict}",
                )
            )

        response_text = next((turn.content for turn in reversed(conversation) if turn.role == "agent"), "")
        resolution_pass = bool(response_text) and (
            not expected_resolution or any(word in response_text.lower() for word in ("refund", "resolved", "completed", "confirmed"))
        )
        required_pass_rate = self._pass_rate([result.passed for result in behavior_results if not result.is_forbidden], default=1.0)
        forbidden_pass_rate = self._pass_rate([result.passed for result in behavior_results if result.is_forbidden], default=1.0)

        dimensions = {
            "task_completion": 1.0 if resolution_pass else 0.0,
            "clarity": 1.0 if 20 <= len(response_text) <= 800 else 0.6 if response_text else 0.0,
            "completeness": min(1.0, (required_pass_rate + backend_accuracy) / 2),
            "empathy": 1.0 if any(token in lower_transcript for token in ("sorry", "understand", "happy to help")) else 0.5,
            "policy_compliance": forbidden_pass_rate,
            "tool_use": tool_assertion_pass_rate,
            "efficiency": 1.0 if len(conversation) <= 6 else 0.6,
            "groundedness": 1.0 if any(token in lower_transcript for token in ("policy", "refund", "article", "documented")) else 0.7,
        }
        quality_score = mean(dimensions.values()) if dimensions else 0.0
        critique = (
            f"Evaluator model: {self.evaluator_model}. "
            f"Resolution={'yes' if resolution_pass else 'no'}, "
            f"required_behaviors={required_pass_rate:.2f}, forbidden_behaviors={forbidden_pass_rate:.2f}."
        )
        return ConversationEvaluation(
            quality_score=round(quality_score, 4),
            quality_dimensions={key: round(value, 4) for key, value in dimensions.items()},
            critique=critique,
            behavior_results=behavior_results,
            resolution_pass=resolution_pass,
        )

    @staticmethod
    def _pass_rate(values: list[bool], *, default: float) -> float:
        if not values:
            return default
        return sum(1 for value in values if value) / len(values)
