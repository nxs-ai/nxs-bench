# Submitting Results

## Step 1: Run NXS-Bench

Install and run the benchmark against your agent endpoint:

```bash
pip install nxs-bench

# Full suite
nxs-bench run --suite all \
  --agent-endpoint http://your-agent:8000/chat \
  --output results.json

# Single suite
nxs-bench run --suite nxs-trust \
  --agent-endpoint http://your-agent:8000/chat \
  --output results.json
```

Your agent must implement the `POST /chat` endpoint contract described in the README. The runner manages the conversation loop, sending one request per turn.

Use at least 2 SimUser models from different families for results you intend to submit. Configure via `--sim-user-models`:

```bash
nxs-bench run --suite all \
  --agent-endpoint http://your-agent:8000/chat \
  --sim-user-models qwen3-8b,gpt-5-mini \
  --output results.json
```

## Step 2: Collect Results JSON

After the run completes, `results.json` contains the full output. Verify it includes the required fields before submitting.

### Results JSON Schema

The results file must contain:

```json
{
  "platform_name": "Your Platform Name",
  "model": "claude-sonnet-4.6",
  "date": "2026-04-14",
  "benchmark_version": "1.0",
  "environment": {
    "sim_user_models": ["qwen3-8b", "gpt-5-mini"],
    "runner_version": "0.1.0",
    "agent_endpoint": "http://your-agent:8000/chat",
    "notes": "Optional description of agent configuration"
  },
  "aggregate": {
    "task_pass_rate": 0.875,
    "safety_pass_rate": 0.98,
    "quality_score": 0.83,
    "pass_k_3": 0.82,
    "pass_k_5": 0.78,
    "cost_per_task": 0.047,
    "total_agent_cost": 30.35,
    "total_benchmark_cost": 52.10,
    "sim_user_variance": 0.03
  },
  "per_difficulty": {
    "easy": { "task_pass_rate": 0.95, "count": 120 },
    "medium": { "task_pass_rate": 0.88, "count": 250 },
    "hard": { "task_pass_rate": 0.72, "count": 180 },
    "adversarial": { "task_pass_rate": 0.48, "count": 95 }
  },
  "per_suite": {
    "nxs-support": { "task_pass_rate": 0.91, "safety_pass_rate": 1.0, "quality_score": 0.85, "cost_per_task": 0.042 },
    "nxs-sales": { "task_pass_rate": 0.88, "safety_pass_rate": 1.0, "quality_score": 0.81, "cost_per_task": 0.051 },
    "nxs-trust": { "task_pass_rate": 0.925, "safety_pass_rate": 1.0, "quality_score": 0.83, "cost_per_task": 0.047 },
    "nxs-multi-agent": { "task_pass_rate": 0.867, "safety_pass_rate": 1.0, "quality_score": 0.76, "cost_per_task": 0.089 },
    "nxs-safety": { "task_pass_rate": 0.85, "safety_pass_rate": 0.85, "quality_score": 0.79, "cost_per_task": 0.031 }
  },
  "per_scenario": [
    {
      "scenario_id": "support-refund-001",
      "suite": "nxs-support",
      "task_pass": true,
      "safety_pass": true,
      "quality_score": 0.88,
      "turns": 3,
      "cost_usd": 0.038
    }
  ]
}
```

**Required fields:**

- `platform_name`, `model`, `date`, `benchmark_version`
- `environment.sim_user_models` (list of SimUser models used)
- `aggregate.task_pass_rate`, `aggregate.safety_pass_rate`, `aggregate.cost_per_task`
- `per_difficulty` breakdown with counts
- `per_suite` breakdown for every suite that was run

**Optional but recommended:**

- `aggregate.pass_k_3` and `aggregate.pass_k_5` (requires multiple run attempts)
- `per_scenario` array (full scenario-level detail)
- `environment.notes` (agent configuration description)

## Step 3: Submit via Pull Request

1. Fork the `nxs-bench` repository.
2. Add your results file to `benchmarks/community/`:

```
benchmarks/community/<platform-name>-<date>.json
```

Example: `benchmarks/community/acme-agents-2026-04-14.json`

3. Open a pull request against the `main` branch with a title like: `results: Acme Agents (Claude Sonnet 4.6) — April 2026`
4. In the PR description, include:
   - Platform name and version
   - Model backbone
   - Which suites were run
   - SimUser models used
   - Any notable configuration (e.g., "trust governance enabled", "single-agent mode")

## Verification

The NXS-Bench team re-runs a random 10% subset of your submitted scenarios to verify the results are reproducible. Verification runs use the same SimUser models specified in your submission.

Verification criteria:

- Task pass rates on the sampled subset must be within 5 percentage points of the submitted rates.
- Safety pass rates must be within 2 percentage points.
- If verification diverges beyond these thresholds, the submitter is contacted for investigation before publication.

Verification is not adversarial. It exists to catch configuration errors, endpoint changes, or accidental submission of partial results.

## Publishing Policy

All submitted results are published regardless of the scores. NXS-Bench does not curate results to favor any platform, including NXS.

Published results appear in:

- The README's Community Results table
- The benchmark's results archive (`benchmarks/community/`)

Results are attributed to the submitting platform. The NXS-Bench team does not editorialize or rank results beyond presenting the numbers.

## Updating Results

To update previously submitted results (e.g., after an agent improvement or a new benchmark version):

1. Submit a new results file with the updated date: `benchmarks/community/<platform-name>-<new-date>.json`
2. The previous submission remains in the archive. Results are never deleted.
3. The README table shows the most recent submission per platform.

## What Not to Submit

- Results from single SimUser model runs (multi-model protocol is required)
- Results from partial suite runs presented as full suite results (submit per-suite results instead)
- Results with fabricated or manually adjusted numbers
- Results without cost data
