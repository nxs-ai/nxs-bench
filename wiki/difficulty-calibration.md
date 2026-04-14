# Difficulty Calibration

## Initial Assignment

Scenario authors assign an initial difficulty label when writing the scenario YAML:

| Label | Intent |
|---|---|
| `easy` | Straightforward task with clear user input, no conflicting constraints, and a single correct action path. |
| `medium` | Requires multi-step reasoning, handling of hidden information, or navigating a moderately ambiguous policy. |
| `hard` | Involves conflicting constraints, edge-case policies, multi-turn information extraction, or complex state changes. |
| `adversarial` | The simulated user actively works against the agent: social engineering, prompt injection, misleading information, or policy exploitation attempts. |

The initial label is an educated guess. It reflects the author's expectation, not empirical evidence. It will be revised.

## Post-Run Recalibration

After benchmark runs accumulate data, difficulty labels are recalibrated based on observed task pass rates across all tested agents:

| Observed Task Pass Rate | Recalibrated Label |
|---|---|
| > 90% | `easy` |
| 60% - 90% | `medium` |
| 30% - 60% | `hard` |
| < 30% | `adversarial` |

These thresholds apply to the aggregate task pass rate across all agents that have run the scenario, not to any single agent's performance. A scenario that one agent passes at 95% but another fails at 20% is evaluated on the aggregate, not cherry-picked.

## Recalibration Cadence

Difficulty labels are reviewed every 3 benchmark runs. A "run" is a complete execution of the suite by any agent platform that submits results. Partial runs (fewer than 80% of scenarios completed) do not count toward the recalibration trigger.

The process:

1. Collect task pass rates for each scenario across all qualifying runs since the last recalibration.
2. Compute the aggregate task pass rate per scenario.
3. Compare each scenario's aggregate rate against the recalibration thresholds.
4. Reclassify scenarios whose aggregate rate falls in a different bucket than their current label.
5. Commit updated labels to the scenario YAML files.
6. Document reclassifications in the benchmark changelog.

## Persistent Misclassification

If a scenario labeled `hard` passes at 95% or higher for 3 consecutive recalibration cycles, it is reclassified as `easy`. This indicates the scenario is not testing what the author intended. When reclassifying:

1. Move the scenario to `easy`.
2. Write a harder variant that addresses the gap. Common approaches: tighten the turn budget, add conflicting constraints, introduce misleading hidden information, or require a less common tool combination.
3. Add the variant as a new scenario in the same suite.

The same applies in reverse. If an `easy` scenario fails below 30% for 3 consecutive cycles, reclassify as `adversarial` and investigate whether the scenario is broken or genuinely harder than expected.

## Per-Difficulty Reporting

All published results must include a per-difficulty breakdown. A headline task pass rate without the breakdown is incomplete and should not be cited.

Example of a complete report:

```
Task pass rate:  85.0%
  Easy (10):           95.0%  (9.5/10)
  Medium (15):         88.0%  (13.2/15)
  Hard (10):           72.0%  (7.2/10)
  Adversarial (5):     48.0%  (2.4/5)
```

Example of an incomplete report:

```
Task pass rate:  85.0%
```

The second report means nothing. An agent that scores 85% by acing easy scenarios and failing hard ones is fundamentally different from an agent that scores 85% uniformly. Per-difficulty breakdowns expose this difference.

## Difficulty Distribution

Each suite maintains a target difficulty distribution in its `suite.yaml`. For example, NXS-Trust targets 8 easy, 16 medium, 12 hard, and 4 adversarial. Recalibration can shift scenarios between buckets, which may leave a bucket under- or over-populated. When this happens:

1. Flag the distribution imbalance in the benchmark changelog.
2. Prioritize new scenario contributions to fill the depleted bucket.
3. Do not artificially reclassify scenarios to maintain distribution targets. Empirical pass rates take precedence over distribution goals.

The distribution is a guideline, not a constraint. Accuracy of labels matters more than uniformity of counts.
