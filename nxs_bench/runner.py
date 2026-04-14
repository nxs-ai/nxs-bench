from __future__ import annotations

import json
import time
from pathlib import Path
from uuid import uuid4

import click
import httpx
import yaml

from .assertions import StateAssertion, ToolAssertion
from .evaluator import ConversationEvaluator
from .mock_backend import MockBackend
from .mock_mcp import MockMCPGateway
from .scorer import aggregate_suite_metrics, compare_results
from .sim_user import build_sim_user
from .types import AgentRequest, AgentResponse, AttemptRecord, BenchmarkResults, ConversationTurn, EnvironmentMetadata, SimulationScenario, SuiteMetadata


BENCHMARK_VERSION = "1.0"


def normalize_suite_name(value: str) -> str:
    return value.replace("-", "_")


def display_suite_name(value: str) -> str:
    return value.replace("_", "-")


def default_suites_root() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    top_level = repo_root / "suites"
    if top_level.exists():
        return top_level
    return Path(__file__).resolve().parent / "resources" / "suites"


def default_results_schema_path() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    top_level = repo_root / "benchmarks" / "results_template.json"
    if top_level.exists():
        return top_level
    return Path(__file__).resolve().parent / "resources" / "benchmarks" / "results_template.json"


def discover_suite_dirs(data_root: Path) -> list[Path]:
    return sorted(path for path in data_root.iterdir() if path.is_dir() and (path / "suite.yaml").exists())


def load_suite_file(path: Path) -> SuiteMetadata:
    return SuiteMetadata.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def load_scenario_file(path: Path) -> SimulationScenario:
    return SimulationScenario.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def load_suite_scenarios(suite_dir: Path) -> list[SimulationScenario]:
    scenario_dir = suite_dir / "scenarios"
    return [load_scenario_file(path) for path in sorted(scenario_dir.glob("*.yaml"))]


def validate_suites(data_root: Path) -> tuple[int, int]:
    suite_count = 0
    scenario_count = 0
    errors: list[str] = []
    for suite_dir in discover_suite_dirs(data_root):
        suite_count += 1
        metadata = load_suite_file(suite_dir / "suite.yaml")
        scenarios = load_suite_scenarios(suite_dir)
        scenario_count += len(scenarios)
        if metadata.task_count != len(scenarios):
            errors.append(
                f"{suite_dir.name}: suite.yaml declares {metadata.task_count} tasks but {len(scenarios)} scenarios were found"
            )
        for scenario in scenarios:
            for payload in scenario.expected_state_changes:
                StateAssertion(**payload)
            for payload in scenario.expected_tool_calls:
                ToolAssertion(**payload)
    if errors:
        raise click.ClickException("\n".join(errors))
    return suite_count, scenario_count


class BenchmarkRunner:
    def __init__(
        self,
        *,
        agent_endpoint: str = "http://localhost:8000/chat",
        data_root: str | Path | None = None,
        timeout_seconds: int = 120,
        pass_k_repetitions: int = 5,
        sim_user_models: list[str] | None = None,
        evaluator_model: str = "heuristic",
        transport: httpx.BaseTransport | None = None,
        retry_backoff_seconds: float = 0.25,
        progress_callback=None,
    ) -> None:
        self.agent_endpoint = agent_endpoint
        self.data_root = Path(data_root) if data_root else default_suites_root()
        self.timeout_seconds = timeout_seconds
        self.pass_k_repetitions = pass_k_repetitions
        self.sim_user_models = sim_user_models or ["scripted-user"]
        self.evaluator_model = evaluator_model
        self.transport = transport
        self.retry_backoff_seconds = retry_backoff_seconds
        self.progress_callback = progress_callback or (lambda message: None)
        self.evaluator = ConversationEvaluator(evaluator_model=evaluator_model)

    def run(
        self,
        *,
        suite_name: str,
        platform: str = "custom-agent-platform",
        version: str = "0.1.0",
        model: str = "unspecified",
    ) -> BenchmarkResults:
        suite_dirs = self._resolve_suites(suite_name)
        suites: dict[str, object] = {}
        with httpx.Client(timeout=self.timeout_seconds, transport=self.transport) as client:
            for suite_dir in suite_dirs:
                suite_key = suite_dir.name
                metadata = load_suite_file(suite_dir / "suite.yaml")
                scenarios = load_suite_scenarios(suite_dir)
                suite_attempts: list[AttemptRecord] = []
                for index, scenario in enumerate(scenarios, start=1):
                    task_started = time.perf_counter()
                    self.progress_callback(
                        f"{display_suite_name(suite_key)} task {index} of {len(scenarios)}"
                    )
                    for attempt_index in range(1, self.pass_k_repetitions + 1):
                        suite_attempts.append(
                            self._run_attempt(
                                client=client,
                                suite_name=suite_key,
                                scenario=scenario,
                                attempt_index=attempt_index,
                            )
                        )
                    elapsed = time.perf_counter() - task_started
                    self.progress_callback(
                        f"{display_suite_name(suite_key)} task {index} of {len(scenarios)} completed in {elapsed:.2f}s"
                    )
                suites[suite_key] = aggregate_suite_metrics(suite_attempts, self.pass_k_repetitions)
                if metadata.task_count != len(scenarios):
                    raise click.ClickException(
                        f"{suite_dir.name}: suite.yaml declares {metadata.task_count} tasks but {len(scenarios)} scenarios were found"
                    )
        return BenchmarkResults(
            platform=platform,
            version=version,
            model=model,
            date=time.strftime("%Y-%m-%d"),
            benchmark_version=BENCHMARK_VERSION,
            suites=suites,
            environment=EnvironmentMetadata(
                infrastructure="custom HTTP endpoint",
                sim_user_models=self.sim_user_models,
                evaluator_model=self.evaluator_model,
                pass_k_repetitions=self.pass_k_repetitions,
            ),
        )

    def _resolve_suites(self, suite_name: str) -> list[Path]:
        suite_key = normalize_suite_name(suite_name)
        all_suites = discover_suite_dirs(self.data_root)
        if suite_key == "all":
            return all_suites
        selected = [suite for suite in all_suites if suite.name == suite_key]
        if not selected:
            raise click.ClickException(f"Unknown suite: {suite_name}")
        return selected

    def _run_attempt(
        self,
        *,
        client: httpx.Client,
        suite_name: str,
        scenario: SimulationScenario,
        attempt_index: int,
    ) -> AttemptRecord:
        backend = MockBackend(scenario.initial_state)
        gateway = MockMCPGateway(backend=backend)
        sim_user = build_sim_user(scenario, model=self.sim_user_models[0])
        conversation: list[ConversationTurn] = []
        conversation_id = f"{suite_name}-{scenario.id}-{attempt_index}-{uuid4().hex[:8]}"
        next_message = sim_user.start()
        total_latency_ms = 0
        total_cost_usd = 0.0
        last_response = ""

        try:
            for _turn in range(scenario.max_user_turns):
                if next_message in {"[DONE]", "[GAVE_UP]"}:
                    break
                conversation.append(ConversationTurn(role="user", content=next_message))
                request_body = AgentRequest(
                    message=next_message,
                    conversation_id=conversation_id,
                    tools=gateway.tool_definitions(scenario.available_tools),
                    context={
                        "role_template": scenario.role_template,
                        "constraints": scenario.agent_constraints,
                        "domain": scenario.domain,
                        "knowledge_articles": scenario.knowledge_articles,
                    },
                )
                started = time.perf_counter()
                payload = self._post_with_retry(client, request_body)
                total_latency_ms += int((time.perf_counter() - started) * 1000)
                total_cost_usd += float(payload.metadata.get("cost_usd", 0.0))
                last_response = payload.response
                conversation.append(ConversationTurn(role="agent", content=payload.response))
                gateway.replay_tool_calls(payload.tool_calls)
                next_message = sim_user.next_message(payload.response)
                if next_message == "[DONE]":
                    break
        except Exception as exc:
            return AttemptRecord(
                scenario_id=scenario.id,
                suite_name=suite_name,
                difficulty=scenario.difficulty,
                attempt_index=attempt_index,
                task_pass=False,
                functional_pass=False,
                safety_pass=False,
                quality_score=0.0,
                backend_accuracy=0.0,
                cost_usd=total_cost_usd,
                latency_ms=total_latency_ms,
                tool_calls=gateway.recorded_calls,
                response=str(exc),
                metadata={"error": str(exc)},
            )

        state_results = [StateAssertion(**payload).check(backend) for payload in scenario.expected_state_changes]
        tool_results = [ToolAssertion(**payload).check(gateway.recorded_calls) for payload in scenario.expected_tool_calls]
        backend_accuracy = self._pass_rate([result.passed for result in state_results], default=1.0)
        tool_pass_rate = self._pass_rate([result.passed for result in tool_results], default=1.0)
        evaluation = self.evaluator.evaluate(
            conversation,
            required_behaviors=scenario.required_behaviors,
            forbidden_behaviors=scenario.forbidden_behaviors,
            expected_resolution=scenario.expected_resolution,
            tool_assertion_pass_rate=tool_pass_rate,
            backend_accuracy=backend_accuracy,
        )
        safety_pass = all(result.passed for result in evaluation.behavior_results)
        functional_pass = backend_accuracy == 1.0 and evaluation.resolution_pass
        return AttemptRecord(
            scenario_id=scenario.id,
            suite_name=suite_name,
            difficulty=scenario.difficulty,
            attempt_index=attempt_index,
            task_pass=functional_pass and safety_pass,
            functional_pass=functional_pass,
            safety_pass=safety_pass,
            quality_score=evaluation.quality_score,
            backend_accuracy=backend_accuracy,
            cost_usd=round(total_cost_usd, 4),
            latency_ms=total_latency_ms,
            tool_calls=gateway.recorded_calls,
            response=last_response,
            metadata={"critique": evaluation.critique},
        )

    def _post_with_retry(self, client: httpx.Client, request_body: AgentRequest) -> AgentResponse:
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = client.post(self.agent_endpoint, json=request_body.model_dump(mode="json"))
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict) or not isinstance(payload.get("response"), str):
                    raise ValueError("malformed response payload")
                return AgentResponse.model_validate(payload)
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteError, httpx.RemoteProtocolError) as exc:
                last_error = exc
                if attempt == 2:
                    break
                time.sleep(self.retry_backoff_seconds * (2**attempt))
            except ValueError as exc:
                raise click.ClickException(str(exc)) from exc
        raise click.ClickException(f"request failed after 3 retries: {last_error}")

    @staticmethod
    def _pass_rate(values: list[bool], *, default: float) -> float:
        if not values:
            return default
        return sum(1 for value in values if value) / len(values)


@click.group()
def cli() -> None:
    """Run, compare, list, and validate NXS-Bench suites."""


@cli.command()
@click.option("--suite", "suite_name", required=True, help="Suite name (e.g. nxs-support or all).")
@click.option(
    "--agent-endpoint",
    default="http://localhost:8000/chat",
    show_default=True,
    help="HTTP endpoint that implements the benchmark /chat contract.",
)
@click.option("--output", type=click.Path(path_type=Path), default=None, help="Write results JSON to this path.")
@click.option("--platform", default="custom-agent-platform", show_default=True)
@click.option("--version", default="0.1.0", show_default=True)
@click.option("--model", default="unspecified", show_default=True)
@click.option("--timeout-seconds", default=120, show_default=True, type=int)
@click.option("--pass-k-repetitions", default=5, show_default=True, type=int)
@click.option("--sim-user-model", "sim_user_models", multiple=True)
@click.option("--evaluator-model", default="heuristic", show_default=True)
@click.option("--data-root", type=click.Path(path_type=Path), default=None)
def run(
    suite_name: str,
    agent_endpoint: str,
    output: Path | None,
    platform: str,
    version: str,
    model: str,
    timeout_seconds: int,
    pass_k_repetitions: int,
    sim_user_models: tuple[str, ...],
    evaluator_model: str,
    data_root: Path | None,
) -> None:
    runner = BenchmarkRunner(
        agent_endpoint=agent_endpoint,
        data_root=data_root,
        timeout_seconds=timeout_seconds,
        pass_k_repetitions=pass_k_repetitions,
        sim_user_models=list(sim_user_models) or ["scripted-user"],
        evaluator_model=evaluator_model,
        progress_callback=click.echo,
    )
    results = runner.run(suite_name=suite_name, platform=platform, version=version, model=model)
    payload = results.model_dump(mode="json")
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        click.echo(f"Wrote results to {output}")
    else:
        click.echo(json.dumps(payload, indent=2))


@cli.command()
@click.option("--baseline", type=click.Path(exists=True, path_type=Path), required=True)
@click.option("--candidate", type=click.Path(exists=True, path_type=Path), required=True)
def compare(baseline: Path, candidate: Path) -> None:
    baseline_payload = json.loads(baseline.read_text(encoding="utf-8"))
    candidate_payload = json.loads(candidate.read_text(encoding="utf-8"))
    deltas = compare_results(baseline_payload, candidate_payload)
    click.echo(json.dumps(deltas, indent=2))


@cli.command("list")
@click.option("--data-root", type=click.Path(path_type=Path), default=None)
def list_command(data_root: Path | None) -> None:
    root = data_root or default_suites_root()
    for suite_dir in discover_suite_dirs(root):
        metadata = load_suite_file(suite_dir / "suite.yaml")
        count_label = "task" if metadata.task_count == 1 else "tasks"
        click.echo(f"{display_suite_name(suite_dir.name)}: {metadata.task_count} {count_label}")


@cli.command()
@click.option("--data-root", type=click.Path(path_type=Path), default=None)
def validate(data_root: Path | None) -> None:
    root = data_root or default_suites_root()
    suite_count, scenario_count = validate_suites(root)
    click.echo(f"Validated {suite_count} suite(s) and {scenario_count} scenario(s).")
