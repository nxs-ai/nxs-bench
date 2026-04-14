# NXS-Trust paper companion

## Status

- Paper title: `NXS-Trust: The First Benchmark for AI Agent Trust Governance`
- Benchmark suite: [`nxs-bench/suites/nxs_trust/`](../../suites/nxs_trust/)
- LaTeX source in the main repo: `docs/papers/nxs_trust_benchmark/`
- arXiv link: pending preprint upload

## Abstract

Production agent systems increasingly need to decide not only whether they can solve a task, but whether they are allowed to solve it at their current autonomy level. Existing agent benchmarks emphasize task completion, web navigation, coding, or tool reliability, yet none directly measures shadow mode behavior, graduated autonomy, or earned trust progression. NXS-Trust is a 40-scenario benchmark for AI agent trust governance with four autonomy tiers: mandatory deferral, limited autonomy, autonomous execution within policy bounds, and judgment-call autonomy. The benchmark combines state assertions, tool-call assertions, dual-judge behavioral checks, multi-model simulated users, and a structured `SimulationVerdict` that separates functional success, safety compliance, and quality. In the draft release snapshot, a commercial trust-governed agent platform reaches `92.5% pass^1` and `85.0% pass^5`, while generic tool-using wrappers around Claude Sonnet 4, GPT-5-mini, and Qwen3-8B range from `27.5%` to `47.5% pass^5`. The benchmark package is designed for external reproduction rather than product-specific evaluation.

## Citation

Update the author list and arXiv URL before publishing.

```bibtex
@misc{nxs_trust_2026,
  title        = {NXS-Trust: The First Benchmark for AI Agent Trust Governance},
  author       = {Anonymous},
  year         = {2026},
  howpublished = {arXiv preprint, link pending},
  note         = {Benchmark suite available under the MIT-licensed nxs-bench repository}
}
```

## Benchmark mapping

- Trust-tier benchmark suite: [`nxs-bench/suites/nxs_trust/suite.yaml`](../../suites/nxs_trust/suite.yaml)
- Scenario examples: the supplementary material in the main paper package includes full YAML examples from Tier 0 and Tier 3.
- Reproduction note: rerun the suite with `nxs-bench run --suite nxs-trust ...` before replacing the draft snapshot with archival numbers.
