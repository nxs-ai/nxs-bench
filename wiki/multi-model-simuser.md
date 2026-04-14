# Multi-Model SimUser Protocol

## The Problem

A single simulator model creates systematic bias in benchmark results. The simulated user (SimUser) drives the conversation: it decides when to volunteer information, how to phrase requests, and when to give up. These decisions directly affect whether the agent under test succeeds or fails.

Empirically, we observe up to 9 percentage point variance in task pass rates across SimUser models on the same scenario set with the same agent. A cooperative SimUser that provides all requested information in structured sentences inflates pass rates. An uncooperative one that gives terse, ambiguous responses deflates them. Neither reflects ground truth about the agent's capability.

If a benchmark result depends more on which model simulates the user than on which agent is being tested, the result is not measuring the agent.

## The Protocol

Every serious NXS-Bench run must use at least 2 SimUser models from different model families. "Different families" means different base architectures or providers. Two fine-tuned variants of the same base model do not count.

Acceptable combinations:

- Qwen3-8B + GPT-5-mini
- Claude Haiku 4 + Qwen3-8B
- Gemma 3 + Claude Haiku 4

Unacceptable combinations:

- Qwen3-8B + Qwen3-32B (same family)
- GPT-5-mini + GPT-5 (same family)

For each scenario, run the full conversation with each SimUser model independently. Report:

1. Per-model task pass rates
2. Aggregate task pass rate (average across models)
3. Per-model variance (absolute difference between highest and lowest per-model rate)

Configure SimUser models via the `sim_user_models` field in the run configuration.

## Persona Types

NXS-Bench defines 7 persona types. Each persona constrains the SimUser's behavior within a scenario:

| Persona | Behavior |
|---|---|
| `clear_customer` | Provides complete, well-organized information. Responds directly to questions. |
| `vague_customer` | Gives partial information. Uses imprecise language. Requires follow-up questions to extract details. |
| `frustrated_customer` | Expresses dissatisfaction. May repeat complaints. Tests agent empathy and de-escalation. |
| `adversarial_user` | Actively tries to make the agent fail. Provides misleading information, asks for policy violations, attempts social engineering. |
| `multi_language_customer` | Switches between languages mid-conversation. Tests language detection and code-switching handling. |
| `impatient_customer` | Gives short responses. Threatens to leave. Demands speed over thoroughness. |
| `technical_customer` | Uses domain jargon. Provides highly specific information. Expects precise technical responses. |

Scenarios specify which personas are valid via the `personas` field. The runner selects from the allowed set. Some scenarios support multiple personas; others are constrained to a single type (e.g., all NXS-Safety scenarios use `adversarial_user`).

## Interpreting Variance

The variance threshold for a conclusive result is 5 percentage points.

- **Variance <= 5%**: The result is conclusive. Report the aggregate task pass rate.
- **Variance > 5%**: The result is inconclusive. Report per-model rates separately and flag the run for investigation. Do not publish the aggregate rate as a headline number.

Common causes of high variance:

- Scenarios where user phrasing materially affects the agent's tool selection
- Scenarios with `vague_customer` or `multi_language_customer` personas where model-specific language patterns dominate
- Short max-turn budgets where a single misunderstood turn causes failure

When variance exceeds 5%, investigate which specific scenarios diverge before concluding the agent is at fault.

## Quarterly Human Calibration

Every quarter, run 10 scenarios with real human users alongside the standard SimUser run. Select scenarios across multiple domains and difficulty levels.

Compare:

1. Human task pass rate vs. SimUser aggregate task pass rate
2. Turn count distribution (humans vs. SimUser models)
3. Information disclosure patterns (when and how users reveal hidden info)

If human-vs-SimUser divergence exceeds 10 percentage points on calibration scenarios, investigate whether the SimUser persona definitions need revision or whether the scenarios themselves contain ambiguity that humans resolve differently than models.

Human calibration results are published in the benchmark's quarterly calibration report. They do not replace the SimUser-based run but provide a ground-truth reference point.

## Known Artifacts

SimUser models exhibit systematic artifacts that do not match real human behavior:

1. **Information over-disclosure.** SimUser models provide requested information too readily, even when the persona should resist or delay. A `vague_customer` persona still tends to give precise answers when asked directly, whereas a real vague customer might genuinely not know the answer.

2. **Structured language.** SimUser models produce grammatically correct, well-organized text. Real users send fragments, typos, and incomplete thoughts. This underestimates the difficulty of natural language understanding.

3. **Breadth-first exploration.** SimUser models tend to address all parts of an agent's multi-question response. Real users often answer only the first question and ignore the rest.

4. **Consistent persona adherence.** A SimUser assigned `frustrated_customer` maintains frustration uniformly. Real frustrated users oscillate between frustration and cooperation within a single conversation.

5. **Predictable turn structure.** SimUser models produce one message per turn with roughly consistent length. Real users sometimes send multiple short messages in sequence or a single very long message.

6. **No abandonment noise.** SimUser models follow the max-turn budget cleanly. Real users sometimes abandon mid-conversation without a closing signal, reopen after a delay, or switch channels.

These artifacts are mitigated by the multi-model protocol (different models exhibit different artifacts) and by quarterly human calibration. They cannot be fully eliminated. When interpreting benchmark results, treat the reported task pass rate as an upper bound on real-world performance.
