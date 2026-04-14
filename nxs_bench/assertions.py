from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .types import AssertionResult


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def _lookup_field(entity: dict[str, Any] | None, field: str | None) -> Any:
    if entity is None or not field:
        return None
    current: Any = entity
    for part in field.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def normalize_tool_call(tool_call: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(tool_call)
    name = normalized.get("name") or normalized.get("tool_name")
    if name and "." in name:
        tool_name, operation = name.split(".", 1)
        normalized.setdefault("tool", tool_name)
        normalized.setdefault("operation", operation)
    normalized.setdefault("tool", "")
    normalized.setdefault("operation", "")
    normalized.setdefault("arguments", normalized.get("params", {}))
    return normalized


@dataclass
class StateAssertion:
    entity_type: str
    entity_id: str | None
    operation: str
    field: str | None
    expected_value: Any

    def check(self, backend: Any) -> AssertionResult:
        snapshot = backend.snapshot() if hasattr(backend, "snapshot") else backend
        entities = snapshot.get(self.entity_type, {}) if isinstance(snapshot, dict) else {}
        if self.entity_id is None:
            entity = next(iter(entities.values()), None) if isinstance(entities, dict) else None
            matching_entities = list(entities.values()) if isinstance(entities, dict) else []
        else:
            entity = entities.get(self.entity_id) if isinstance(entities, dict) else None
            matching_entities = [entity] if entity else []

        if self.operation == "exists":
            return AssertionResult(passed=entity is not None, detail=f"{self.entity_type} exists")
        if self.operation == "not_exists":
            return AssertionResult(passed=entity is None, detail=f"{self.entity_type} does not exist")
        if self.operation == "field_equals":
            passed = any(_lookup_field(candidate, self.field) == self.expected_value for candidate in matching_entities)
            detail = f"{self.entity_type}.{self.field} == {self.expected_value!r}"
            return AssertionResult(passed=passed, detail=detail)
        if self.operation == "field_gt":
            passed = any((_lookup_field(candidate, self.field) or 0) > self.expected_value for candidate in matching_entities)
            detail = f"{self.entity_type}.{self.field} > {self.expected_value!r}"
            return AssertionResult(passed=passed, detail=detail)
        if self.operation == "field_lt":
            passed = any((_lookup_field(candidate, self.field) or 0) < self.expected_value for candidate in matching_entities)
            detail = f"{self.entity_type}.{self.field} < {self.expected_value!r}"
            return AssertionResult(passed=passed, detail=detail)
        if self.operation == "field_contains":
            passed = any(
                self.expected_value in (_lookup_field(candidate, self.field) or [])
                for candidate in matching_entities
            )
            detail = f"{self.entity_type}.{self.field} contains {self.expected_value!r}"
            return AssertionResult(passed=passed, detail=detail)
        return AssertionResult(passed=False, detail=f"Unsupported state assertion operation: {self.operation}")


@dataclass
class ToolAssertion:
    tool: str
    operation: str
    should_be_called: bool = True
    min_calls: int = 1
    max_calls: int | None = None
    param_assertions: dict[str, Any] | None = None

    def check(self, recorded_calls: list[dict[str, Any]]) -> AssertionResult:
        normalized_calls = [normalize_tool_call(call) for call in recorded_calls]
        matches = [
            call
            for call in normalized_calls
            if call.get("tool") == self.tool and call.get("operation") == self.operation
        ]
        if self.param_assertions:
            matches = [
                call
                for call in matches
                if all(call.get("arguments", {}).get(key) == value for key, value in self.param_assertions.items())
            ]

        count = len(matches)
        if not self.should_be_called:
            passed = count == 0
        else:
            within_max = self.max_calls is None or count <= self.max_calls
            passed = count >= self.min_calls and within_max
        detail = f"{self.tool}.{self.operation} called {count} time(s)"
        return AssertionResult(passed=passed, detail=detail)


@dataclass
class BehaviorAssertion:
    behavior: str
    is_forbidden: bool

    def check(self, transcript: str) -> tuple[str, bool]:
        transcript_tokens = set(_normalize_text(transcript).split())
        behavior_tokens = {
            token
            for token in re.findall(r"[a-z0-9]+", self.behavior.lower())
            if len(token) > 2 and token not in {"the", "and", "for", "with", "that"}
        }
        if not behavior_tokens:
            verdict = "AMBIGUOUS"
        else:
            overlap = len(transcript_tokens & behavior_tokens) / len(behavior_tokens)
            if overlap >= 0.75:
                verdict = "CLEARLY_YES"
            elif overlap >= 0.35:
                verdict = "AMBIGUOUS"
            else:
                verdict = "CLEARLY_NO"

        if self.is_forbidden:
            passed = verdict != "CLEARLY_YES"
        else:
            passed = verdict != "CLEARLY_NO"
        return verdict, passed
