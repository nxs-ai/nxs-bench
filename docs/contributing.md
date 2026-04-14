# Contributing

## Scope

Contributions are welcome for:

- New benchmark scenarios
- Scenario fixes and clarifications
- Additional mock tool handlers
- Runner and scoring improvements
- Documentation improvements

## Advisory Board Formation Threshold

NXS-Bench forms its Advisory Board after **10 external contributions**. The
tracked contribution ledger lives in [`../CONTRIBUTIONS.md`](../CONTRIBUTIONS.md).

Counted contribution types are:

- `new scenario`
- `bug fix`
- `methodology feedback`

The tracker is updated automatically after merged pull requests from external
contributors.

## Scenario Pull Requests

Every new scenario PR should include:

1. A YAML scenario under the correct `suites/<suite_name>/scenarios/` directory.
2. A matching update to the suite task count when a new scenario is added.
3. Initial backend state, expected state changes, expected tool calls, forbidden behaviors, required behaviors, and at least one supported persona.
4. An `author` field for attribution if you want public credit.

## Quality Criteria

Accepted scenarios should be:

- Reproducible with no proprietary dependencies
- Specific enough to fail deterministically when the agent is wrong
- Distinct from existing scenarios in user goal, constraints, or failure mode
- Calibrated to an explicit difficulty level
- Expressed with generic tool names and generic endpoint assumptions

## Deduplication Checklist

Before opening a PR:

1. Search the target suite for the same user goal or same failure mode.
2. Check whether your scenario differs in constraints, hidden information, or expected backend/tool outcomes.
3. Prefer extending coverage over creating superficial variants.

## Difficulty Calibration Process

Maintain the intended distribution across `easy`, `medium`, `hard`, and `adversarial`:

1. Propose the initial label in the scenario YAML.
2. Review observed pass rates after benchmark runs.
3. Re-label or revise the scenario when the observed difficulty drifts.

## Local Validation

```bash
nxs-bench validate
pytest tests/ -x -q
```

## Licensing

All contributions are submitted under the MIT license in this repository.
