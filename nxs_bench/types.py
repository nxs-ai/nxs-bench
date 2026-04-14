from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FlexibleModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class DifficultyResult(FlexibleModel):
    count: int
    pass_rate: float


class SuiteMetadata(FlexibleModel):
    name: str
    version: str
    task_count: int
    description: str
    difficulty_distribution: dict[str, int] = Field(default_factory=dict)
    persona_distribution: dict[str, int] = Field(default_factory=dict)


class SimulationScenario(FlexibleModel):
    id: str
    domain: str
    role_template: str
    category: str
    difficulty: str
    user_goal: str
    user_context: str
    user_known_info: dict[str, Any] = Field(default_factory=dict)
    user_hidden_info: dict[str, Any] = Field(default_factory=dict)
    max_user_turns: int = 8
    available_tools: list[str] = Field(default_factory=list)
    knowledge_articles: list[dict[str, Any]] = Field(default_factory=list)
    agent_constraints: dict[str, Any] = Field(default_factory=dict)
    initial_state: dict[str, Any] = Field(default_factory=dict)
    expected_state_changes: list[dict[str, Any]] = Field(default_factory=list)
    expected_tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    forbidden_behaviors: list[str] = Field(default_factory=list)
    required_behaviors: list[str] = Field(default_factory=list)
    expected_resolution: bool = True
    personas: list[str] = Field(default_factory=list)
    scoring_weights: dict[str, float] | None = None


class ConversationTurn(FlexibleModel):
    role: str
    content: str


class AssertionResult(FlexibleModel):
    passed: bool
    detail: str


class BehaviorAssertionResult(FlexibleModel):
    behavior: str
    is_forbidden: bool
    verdict: str
    passed: bool
    detail: str


class ConversationEvaluation(FlexibleModel):
    quality_score: float
    quality_dimensions: dict[str, float]
    critique: str
    behavior_results: list[BehaviorAssertionResult] = Field(default_factory=list)
    resolution_pass: bool = True


class AttemptRecord(FlexibleModel):
    scenario_id: str
    suite_name: str
    difficulty: str
    attempt_index: int
    task_pass: bool
    functional_pass: bool
    safety_pass: bool
    quality_score: float
    backend_accuracy: float
    cost_usd: float
    latency_ms: int
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    response: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SuiteMetrics(FlexibleModel):
    total_tasks: int
    pass_at_1: float
    pass_k_3: float
    pass_k_5: float
    task_pass_rate: float
    quality_score: float
    safety_pass_rate: float
    backend_accuracy: float
    cost_per_task_usd: float
    cost_normalized_accuracy: float
    latency_p50_ms: int
    latency_p95_ms: int
    per_difficulty_results: dict[str, DifficultyResult]


class EnvironmentMetadata(FlexibleModel):
    infrastructure: str
    sim_user_models: list[str]
    evaluator_model: str
    pass_k_repetitions: int


class BenchmarkResults(FlexibleModel):
    platform: str
    version: str
    model: str
    date: str
    benchmark_version: str = "1.0"
    suites: dict[str, SuiteMetrics]
    environment: EnvironmentMetadata


class AgentRequest(FlexibleModel):
    message: str
    conversation_id: str
    tools: list[dict[str, Any]] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)


class AgentResponse(FlexibleModel):
    response: str
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
