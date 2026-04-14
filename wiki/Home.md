# NXS-Bench Wiki

NXS-Bench is an open-source benchmark suite for enterprise AI agents. It contains 645 tasks across 10 domains, covering customer support, sales, knowledge retrieval, trust governance, multi-agent coordination, voice, safety, MCP connectors, groundedness, and hardened policy compliance. The benchmark is released under the MIT license. All scenario definitions are public YAML files with no proprietary dependencies.

The core differentiator is backend state verification. NXS-Bench does not check whether the agent's response sounds correct. It checks whether the agent's actions produced the correct outcome in a mock backend. A refund scenario passes only if a refund record exists with the correct amount, not because the agent said "I've processed your refund." This methodology extends the approach Sierra introduced with tau-Bench from 2 domains to 10, and adds trust governance, multi-agent coordination, and adversarial safety testing.

NXS-Bench produces three independent verdicts per scenario: a binary functional pass (did the agent complete the task), a binary safety pass (did the agent avoid forbidden behaviors), and a quality score (0.0-1.0 across 8 dimensions). Task pass requires both functional and safety pass. Quality is reported alongside but never folded into the pass rate. The primary reliability metric is Pass^k, which counts a task as passed only if it passes all k consecutive attempts.

## Table of Contents

| Page | Description |
|---|---|
| [Scoring Methodology](scoring-methodology.md) | Pass^k, CNA, quality scoring, per-difficulty breakdowns |
| [Scenario Format](../docs/scenario_format.md) | YAML field reference for scenario definitions |
| [Domain: NXS-Trust](domains/nxs-trust.md) | Trust tier governance benchmark (40 tasks) |
| [Domain: NXS-Multi-Agent](domains/nxs-multi-agent.md) | Coordinated agent team benchmark (30 tasks) |
| [Domain: NXS-Safety](domains/nxs-safety.md) | Adversarial safety benchmark (260 tasks) |
| [Multi-Model SimUser Protocol](multi-model-simuser.md) | Why multiple simulator models are required and how to interpret variance |
| [Behavior Assertion Reliability](behavior-assertions.md) | Dual-judge protocol, 3-point scale, edge cases |
| [Difficulty Calibration](difficulty-calibration.md) | How difficulty labels are assigned and recalibrated |
| [Contamination Detection](contamination-detection.md) | Canary scenarios, version rotation, paraphrase detection |
| [Cost Model](cost-model.md) | Per-suite cost estimates and cost-reduction strategies |
| [Submitting Results](submitting-results.md) | How to run the benchmark and submit your results |
| [Writing Scenarios](../docs/contributing.md) | Contribution guide for new scenario authors |
