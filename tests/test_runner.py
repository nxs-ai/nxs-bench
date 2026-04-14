import json
from pathlib import Path

import httpx
from click.testing import CliRunner

from nxs_bench import BenchmarkRunner, SimulationScenario
from nxs_bench.runner import cli, load_scenario_file
from nxs_bench.types import BenchmarkResults


def _mock_handler(request: httpx.Request) -> httpx.Response:
    payload = json.loads(request.content.decode("utf-8"))
    assert payload["message"]
    assert payload["conversation_id"]
    assert "tools" in payload
    assert payload["context"]["role_template"] == "l1-support"
    return httpx.Response(
        200,
        json={
            "response": "I verified the order, processed the refund, and the refund timeline is 5-7 business days.",
            "tool_calls": [
                {
                    "tool": "payments",
                    "operation": "process_refund",
                    "arguments": {"order_id": "ORD-1", "customer_id": "cust-1", "amount": 42.5},
                }
            ],
            "metadata": {"cost_usd": 0.25},
        },
    )


def test_load_scenario_file_returns_simulation_scenario(sample_suite_root: Path) -> None:
    scenario = load_scenario_file(sample_suite_root / "nxs_support" / "scenarios" / "refund_001.yaml")
    assert isinstance(scenario, SimulationScenario)
    assert scenario.id == "support-refund-001"


def test_benchmark_runner_executes_suite_and_aggregates_results(sample_suite_root: Path) -> None:
    runner = BenchmarkRunner(
        agent_endpoint="http://agent.test/chat",
        data_root=sample_suite_root,
        transport=httpx.MockTransport(_mock_handler),
        pass_k_repetitions=3,
        timeout_seconds=5,
        sim_user_models=["scripted-user"],
        evaluator_model="heuristic",
    )

    results = runner.run(suite_name="nxs-support", platform="Acme Agents", version="0.1.0", model="demo-model")

    assert isinstance(results, BenchmarkResults)
    assert results.platform == "Acme Agents"
    assert results.model == "demo-model"
    assert results.environment.pass_k_repetitions == 3
    suite_metrics = results.suites["nxs_support"]
    assert suite_metrics.total_tasks == 1
    assert suite_metrics.pass_at_1 == 1.0
    assert suite_metrics.pass_k_3 == 1.0
    assert suite_metrics.backend_accuracy == 1.0
    assert suite_metrics.cost_per_task_usd == 0.25


def test_cli_run_list_validate_and_compare(sample_suite_root: Path, monkeypatch, tmp_path: Path) -> None:
    original_client = httpx.Client

    def patched_client(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(_mock_handler)
        return original_client(*args, **kwargs)

    monkeypatch.setattr("nxs_bench.runner.httpx.Client", patched_client)

    cli_runner = CliRunner()
    output_path = tmp_path / "results.json"

    run_result = cli_runner.invoke(
        cli,
        [
            "run",
            "--suite",
            "nxs-support",
            "--agent-endpoint",
            "http://agent.test/chat",
            "--data-root",
            str(sample_suite_root),
            "--output",
            str(output_path),
            "--platform",
            "Acme Agents",
            "--version",
            "0.1.0",
            "--model",
            "demo-model",
            "--pass-k-repetitions",
            "3",
        ],
    )
    assert run_result.exit_code == 0, run_result.output
    assert output_path.exists()

    list_result = cli_runner.invoke(cli, ["list", "--data-root", str(sample_suite_root)])
    assert list_result.exit_code == 0
    assert "nxs-support" in list_result.output
    assert "1 task" in list_result.output

    validate_result = cli_runner.invoke(cli, ["validate", "--data-root", str(sample_suite_root)])
    assert validate_result.exit_code == 0
    assert "Validated 1 suite" in validate_result.output

    candidate_path = tmp_path / "candidate.json"
    candidate_payload = json.loads(output_path.read_text(encoding="utf-8"))
    candidate_payload["suites"]["nxs_support"]["quality_score"] = 0.9
    candidate_path.write_text(json.dumps(candidate_payload), encoding="utf-8")

    compare_result = cli_runner.invoke(
        cli,
        ["compare", "--baseline", str(output_path), "--candidate", str(candidate_path)],
    )
    assert compare_result.exit_code == 0
    assert "nxs_support" in compare_result.output
    assert "quality_score" in compare_result.output
