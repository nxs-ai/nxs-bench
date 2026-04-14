# NXS-Multi-Agent: Benchmarking Coordinated Agent Teams

Status: arXiv preprint draft, pending submission

ArXiv link: pending submission; replace this line with the canonical `https://arxiv.org/abs/...` URL once the preprint is live.

## Abstract

`NXS-Multi-Agent` is a 30-scenario benchmark for coordinated agent teams. The suite targets six coordination patterns that are common in real deployments but weakly covered in public benchmarks: consult roundtrip, delegation handoff, escalation chain, transfer continuity, parallel delegation, and memory visibility. Each scenario combines user simulation, state assertions, and coordination-specific metrics for context preservation, duplicate-work avoidance, aggregation, latency, and memory isolation. The companion paper reports results for a commercial multi-agent platform, a single-agent baseline, and an open-source planner-worker baseline, together with a failure taxonomy showing that context loss is the dominant coordination failure and that parallel delegation is the hardest pattern in the suite. The benchmark is intended as an open methodology contribution, not as a product benchmark for a single platform.

## Artifact Links

- Benchmark suite: [`nxs-bench/suites/nxs_multi_agent/`](../../suites/nxs_multi_agent/)
- Methodology notes: [`nxs-bench/docs/methodology.md`](../methodology.md)
- LaTeX source in the main repository: `docs/papers/nxs_multi_agent_benchmark/main.tex`
- Supplementary material in the main repository: `docs/papers/nxs_multi_agent_benchmark/supplementary.tex`

## Citation

```bibtex
@misc{nxs2026multiagent,
  title        = {NXS-Multi-Agent: Benchmarking Coordinated Agent Teams},
  author       = {{NXS Research}},
  year         = {2026},
  howpublished = {arXiv preprint, under submission},
  note         = {Benchmark suite available in nxs-bench}
}
```

## What The Paper Adds

- Formal definitions for the six coordination patterns in the suite
- A public task taxonomy and failure taxonomy for coordinated teams
- Comparative results across a commercial multi-agent system, a single-agent baseline, and an open-source planner-worker baseline
- Reproducible benchmark artifacts built on the same public scenario YAML files shipped in `nxs-bench`
