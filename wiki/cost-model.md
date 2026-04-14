# Cost Model

## Cost Components

Every NXS-Bench run incurs three categories of LLM cost:

1. **SimUser model calls.** The simulated user generates messages in the conversation. With the multi-model SimUser protocol, each scenario is run with at least 2 SimUser models, doubling the SimUser cost.

2. **Agent model calls.** The agent under test processes each conversation turn. This cost depends entirely on the agent's architecture and model choice. NXS-Bench does not control it.

3. **Evaluator judge calls.** Behavior assertions use a dual-judge protocol (2 independent LLM calls per assertion). Quality scoring uses 1 LLM call per scenario. A scenario with 3 behavior assertions requires 7 evaluator calls (3 assertions x 2 judges + 1 quality evaluation).

## Per-Suite Estimates

Estimates below assume:

- Average 4 conversation turns per scenario
- Average 500 tokens per turn (SimUser + agent combined)
- 2 SimUser models (the minimum for the multi-model protocol)
- Mid-tier cloud model pricing (~$0.50/M input tokens, ~$1.50/M output tokens)
- 2-3 behavior assertions per scenario

These are rough order-of-magnitude numbers. Actual costs vary with model pricing, conversation length, and scenario complexity.

| Suite | Tasks | Estimated Cost |
|---|---|---|
| NXS-Support | 100 | $8 - $12 |
| NXS-Sales | 50 | $5 - $7 |
| NXS-Knowledge | 50 | $4 - $6 |
| NXS-Trust | 40 | $2 - $4 |
| NXS-Multi-Agent | 30 | $3 - $5 |
| NXS-Voice | 30 | $2 - $4 |
| NXS-Safety | 260 | $10 - $15 |
| NXS-MCP | 30 | $2 - $4 |
| NXS-Groundedness | 30 | $3 - $5 |
| NXS-Hardened | 25 | $2 - $3 |
| **Full 645-task run** | **645** | **$40 - $60** |

NXS-Safety is the cheapest per-task despite the high task count because all 260 scenarios use `adversarial_user` personas with short conversation lengths (the agent should refuse quickly). NXS-Knowledge and NXS-Groundedness are more expensive per-task because they involve long-context retrieval.

## Cost Reduction Strategies

### Subset runs for CI/CD

Running all 645 tasks on every code change is unnecessary. Use targeted subsets:

- **Regression gate:** Run NXS-Trust (40 tasks, ~$2-4) on every PR. Trust governance is the most sensitive to policy changes.
- **Safety gate:** Run NXS-Safety (260 tasks, ~$10-15) on releases. Safety regressions are the highest-risk failure mode.
- **Full suite:** Run all 645 tasks on major releases or quarterly evaluations.

Configure subsets via `nxs-bench run --suite <suite_name>`.

### Single SimUser model for development

During iterative development, running with 1 SimUser model instead of 2 cuts SimUser costs in half. Results from single-model runs are valid for internal use but should not be published as official benchmark results (the multi-model protocol is required for publication).

### Cheaper evaluator models

The dual-judge evaluator calls are the second-largest cost component. For development runs, using smaller models (e.g., Qwen3-8B) as judges reduces evaluator cost. For published results, use the same judge model tier as the standard configuration to ensure comparability.

### Reduce k in Pass^k

Pass^5 requires 5 complete runs per scenario (5x the base cost). For CI/CD, Pass^1 (single attempt) is sufficient. Reserve Pass^3 or Pass^5 for release evaluations.

## Cost-Normalized Accuracy (CNA)

NXS-Bench reports CNA alongside task pass rates:

```
CNA = task_pass_rate / cost_per_task_usd
```

CNA answers the question: "How much accuracy do I get per dollar spent?" A 90% agent at $0.05/task (CNA = 18.0) is more cost-effective than a 92% agent at $0.50/task (CNA = 1.84) for most enterprise deployments.

CNA is computed from the agent's model costs only (not SimUser or evaluator costs, which are benchmark infrastructure). The agent reports `cost_usd` in each response's `metadata` field.

## Reporting

Always report cost alongside task pass rates. A result without cost context is incomplete.

Required cost fields in results JSON:

| Field | Description |
|---|---|
| `cost_per_task` | Average agent cost per task (from agent metadata) |
| `total_agent_cost` | Sum of all agent costs across the run |
| `total_benchmark_cost` | Total cost including SimUser and evaluator calls |
| `sim_user_models` | Which SimUser models were used and their pricing tier |

A published result that reports 95% task pass rate without disclosing cost is not comparable to other results. Two agents at the same task pass rate can differ by 10x in cost.
