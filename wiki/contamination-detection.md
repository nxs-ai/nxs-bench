# Contamination Detection

Data contamination occurs when an agent's underlying model has been trained on benchmark scenarios, allowing it to pass tasks through memorization rather than capability. NXS-Bench uses four mechanisms to detect contamination.

## Canary Scenarios

NXS-Bench maintains 10 canary scenarios per suite. These are never published in the open-source repository. They are structurally identical to public scenarios: same YAML format, same difficulty distribution, same persona types, same tool and state assertion patterns. The only difference is the surface details (customer names, order IDs, product descriptions, policy specifics).

Canary scenarios are stored in a private repository accessible only to the NXS-Bench maintainers. They are included in official benchmark runs but excluded from the public results JSON.

### Canary Gap

The canary gap is the absolute difference in task pass rate between public and canary scenarios within the same suite and difficulty level.

- **Canary gap <= 2%**: No contamination signal. The agent performs equivalently on seen and unseen scenarios.
- **Canary gap > 2%**: Contamination signal. The agent performs materially better on public scenarios than on structurally identical private ones. This suggests the model has been exposed to benchmark data during training.

When a canary gap exceeds 2%, the affected suite's results are flagged with `contamination_signal: true` in the results JSON. The specific canary scenarios are not revealed (doing so would compromise future detection).

## Version Rotation

Every 6 months, 20% of scenarios in each suite are retired and replaced with new scenarios. Retired scenarios are moved to an archive (`suites/<suite>/archive/`) and are no longer included in active benchmark runs.

The replacement scenarios cover the same task categories, difficulty levels, and behavior assertions as the retired ones. They test the same capabilities with different surface details.

### Rotation Gap

After a rotation, compare the agent's task pass rate on:

- **Retained scenarios**: scenarios that existed before and after the rotation
- **New scenarios**: scenarios introduced in the rotation

A rotation gap greater than 5 percentage points (higher task pass rate on retained vs. new) is a contamination signal. The agent has likely been trained on — or heavily optimized against — the specific details of retained scenarios.

Rotation gap analysis requires at least one pre-rotation and one post-rotation run from the same agent platform.

## Benchmark Versioning

NXS-Bench uses semantic versioning: v1.0, v1.1, v1.2, and so on. Minor versions include scenario additions, difficulty recalibrations, and rotations. Major versions include methodology changes.

Track each agent platform's scores across versions:

| Version | Platform A | Platform B |
|---|---|---|
| v1.0 | 82% | 78% |
| v1.1 | 84% | 79% |
| v1.2 | 91% | 80% |

If a platform's score increases substantially across versions without corresponding agent improvements (no new model, no architectural changes, no policy updates), the increase is likely driven by optimization against published scenarios rather than genuine capability improvement.

Score inflation is assessed per-platform. A 2-point increase across versions is normal noise. A 7+ point increase with no disclosed agent changes warrants investigation.

## Paraphrase Detection

This mechanism tests whether a model has memorized specific scenario text.

### Procedure

1. Select a scenario. Extract the first 50% of the scenario description (the `user_goal`, `user_context`, and `user_known_info` fields concatenated).
2. Feed the partial text to the model as a prompt: "Continue the following benchmark scenario description."
3. Compare the model's generated continuation against the actual remaining 50% of the scenario.
4. Compute token-level overlap between the generated and actual text.

### Interpretation

- **Token overlap <= 40%**: No contamination signal. The model is generating plausible but distinct continuations.
- **Token overlap 40-80%**: Ambiguous. The model may have seen similar content. Flag for further investigation.
- **Token overlap > 80%**: Likely contaminated. The model is reproducing scenario text from memory rather than generating novel continuations.

Paraphrase detection is run on a sample of 20 public scenarios per suite, not on the full set. It is a spot check, not a comprehensive scan.

### Limitations

Paraphrase detection has a high false-negative rate. A model can benefit from contamination without reproducing exact text (e.g., if it learned the solution strategy rather than the surface wording). This mechanism catches only the most obvious cases and should be used alongside, not instead of, canary and rotation methods.

## Reporting

When publishing benchmark results, include:

- Benchmark version (e.g., v1.2)
- Whether canary scenarios were included in the run
- Canary gap (if canary scenarios were run)
- Rotation gap (if applicable, comparing pre- and post-rotation runs)
- Any contamination flags raised by any detection mechanism

Results with active contamination signals are still published but are annotated. The community can assess the severity and decide how to weight the results.
