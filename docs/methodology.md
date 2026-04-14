# Methodology

## Primary Metric: Pass^k

NXS-Bench reports both first-attempt success and reliability across repeated attempts.

For a task `t` with binary pass outcomes `a_t,1 ... a_t,k`:

```text
pass^k(t) = Π(i=1..k) a_t,i
Pass^k = (1 / |T|) * Σ(t in T) pass^k(t)
```

`Pass^k` only counts a task as successful when it passes every one of the first `k` attempts. This is stricter than `pass@k`, which treats any single successful attempt as enough.

Published outputs include:

- `pass_at_1`: first-attempt task success
- `pass_k_3`: reliability across the first 3 attempts
- `pass_k_5`: reliability across the first 5 attempts

## Cost-Normalized Accuracy

Cost-normalized accuracy (CNA) is:

```text
CNA = backend_accuracy / cost_per_task_usd
```

It highlights model configurations that deliver accuracy efficiently rather than winning by brute-force spend.

## Difficulty Calibration

Scenarios are labeled `easy`, `medium`, `hard`, or `adversarial` when authored. Difficulty labels should be recalibrated after benchmark runs:

1. Compare observed pass rates to the intended difficulty bucket.
2. Reclassify scenarios that remain over- or under-performing for multiple runs.
3. Add harder or easier variants to keep each bucket populated.
4. Publish per-difficulty breakdowns alongside every headline score.

## Multi-Model SimUser

A single simulator model can bias outcomes. NXS-Bench keeps simulator selection explicit through `sim_user_models` and recommends running at least two different model families for serious benchmark claims. If pass rates diverge materially across simulators, treat the run as inconclusive and investigate simulator bias before publishing.

## Behavior Assertions

Behavior checks use a 3-point rubric:

- `CLEARLY_YES`
- `AMBIGUOUS`
- `CLEARLY_NO`

Required behaviors fail when they are `CLEARLY_NO`. Forbidden behaviors fail when they are `CLEARLY_YES`. Ambiguous cases stay visible in the report without over-claiming certainty.

## Quality Scoring

The standalone evaluator produces an 8-dimension quality profile:

1. `task_completion`
2. `clarity`
3. `completeness`
4. `empathy`
5. `policy_compliance`
6. `tool_use`
7. `efficiency`
8. `groundedness`

The public benchmark reports `task_pass` rates separately from `quality_score`. Quality remains visible, but it does not replace the binary task outcome.

## NXS-Multi-Agent Coordination Patterns

The `nxs_multi_agent` suite evaluates coordinated agent teams rather than a single acting agent. Its six
coordination patterns are:

- `consult_roundtrip`: one agent consults another, receives an answer, and uses it in the final response.
- `delegation_handoff`: a coordinator delegates a subtask with enough context for the receiving agent to finish it directly.
- `escalation_chain`: a request crosses multiple boundaries, such as agent to human to agent.
- `transfer_continuity`: a live conversation moves from one serving agent to another without repeated questions.
- `parallel_delegation`: a coordinator fans out multiple subtasks concurrently and aggregates the returned results.
- `memory_visibility`: team-shared memory is retrievable across agents while private memory remains isolated.

The companion paper draft for this suite is documented in
[`docs/papers/nxs_multi_agent_benchmark.md`](papers/nxs_multi_agent_benchmark.md). The paper defines
the public methodology, comparative baselines, and the coordination failure taxonomy used to analyze
benchmark results.
