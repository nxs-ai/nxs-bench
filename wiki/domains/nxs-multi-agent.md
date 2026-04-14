# Domain: NXS-Multi-Agent

## Overview

NXS-Multi-Agent is a 30-scenario benchmark for coordinated agent teams. It tests whether multiple agents can consult, delegate, escalate, transfer, fan out, and share memory without losing context or duplicating work. Each coordination pattern has 5 scenarios. The difficulty distribution is 6 easy, 12 medium, 9 hard, 3 adversarial.

Single-agent benchmarks measure whether one agent can complete a task. NXS-Multi-Agent measures whether a team of agents can complete a task that requires coordination. The failure modes are different: context loss during handoff, duplicated subtasks, failed aggregation, and memory isolation violations.

## Coordination Patterns

### Consult Roundtrip (5 scenarios)

A coordinator agent consults a specialist agent, receives an answer, and uses it in the final response. The specialist does not take over the conversation.

**What is measured:** The coordinator must send a well-formed consultation request, receive the response, and incorporate it into the final answer without dropping context.

**Common failure:** The coordinator sends a vague consultation request, gets a generic answer, and produces a response that does not reflect the specialist's input.

### Delegation Handoff (5 scenarios)

A coordinator delegates a complete subtask to another agent with enough context for the receiving agent to finish it independently. The coordinator does not re-engage until the subtask is complete.

**What is measured:** The delegated context must be sufficient (no back-and-forth required). The receiving agent must complete the subtask and return results. The coordinator must incorporate the results.

**Common failure:** Insufficient context in the delegation, causing the receiving agent to ask the coordinator for clarification (breaking the handoff pattern).

### Escalation Chain (5 scenarios)

A request crosses multiple agent boundaries. For example: front-line agent to supervisor agent to compliance agent. Each handoff must preserve the full context chain.

**What is measured:** Context preservation across 2+ handoffs. Each agent in the chain receives the full history from prior agents. No information is dropped.

**Common failure:** The second handoff loses context from the first. The compliance agent receives only the supervisor's summary, not the original customer request.

### Transfer Continuity (5 scenarios)

A live conversation moves from one serving agent to another. The user should not need to repeat information. The receiving agent picks up where the previous agent left off.

**What is measured:** The receiving agent demonstrates awareness of prior conversation turns. No repeated questions. No contradictory statements.

**Common failure:** The receiving agent greets the user as if starting a new conversation and re-asks questions already answered.

### Parallel Delegation (5 scenarios)

A coordinator fans out multiple subtasks concurrently and aggregates the returned results into a single coherent response.

**What is measured:** All subtasks are dispatched. Results from all branches are collected. The final response synthesizes all results rather than presenting them as disconnected fragments.

**Common failure:** One branch's results are lost during aggregation. The coordinator responds with partial results, omitting a branch.

### Memory Visibility (5 scenarios)

Team-shared memory must be retrievable across agents. Private memory must remain isolated to the owning agent.

**What is measured:** Agent A stores a fact in shared memory. Agent B retrieves it correctly. Agent A stores a fact in private memory. Agent B cannot access it.

**Common failure:** Private memory leaks to other agents, or shared memory is not retrievable by team members.

## Scenario Structure

NXS-Multi-Agent scenarios extend the standard scenario format with additional fields:

| Field | Purpose |
|---|---|
| `agent_roles` | List of agent roles involved (e.g., `support_lead`, `billing_specialist`) |
| `coordination_type` | Which of the 6 patterns this scenario tests |
| `per_agent_expected_behaviors` | Behavior assertions per agent role, not just for the overall conversation |

State assertions verify coordination outcomes (e.g., `coordination_records.coord-001.status = completed`, `results_aggregated = true`). Tool assertions verify the correct coordination tools were called (`consult`, `delegate`, `transfer`, `memory`).

## Scoring Details

Task pass requires:

1. **State assertions pass.** The coordination record reaches `completed` status with all expected fields set.
2. **Tool assertions pass.** The correct coordination operations were used (consult for consult scenarios, delegate for delegation scenarios, etc.).
3. **Behavior assertions pass.** Both conversation-level and per-agent behaviors are satisfied.

A scenario where the end result is correct but the coordination pattern was wrong (e.g., the coordinator did all the work itself instead of delegating) fails the tool assertions.

## Coordination Metrics

Beyond pass/fail, each scenario evaluates coordination-specific metrics:

| Metric | Description |
|---|---|
| Context preservation | Was information from earlier agents available to later agents? |
| Duplicate work avoidance | Were subtasks dispatched to multiple agents when only one was needed? |
| Aggregation completeness | Did the final response include results from all delegated subtasks? |
| Coordination latency | How many extra turns were caused by coordination overhead? |
| Memory isolation | Did private memory stay private and shared memory stay accessible? |

These metrics are reported in the results JSON under `coordination_metrics` for each scenario.

## Baseline Results

From the draft benchmark snapshot:

| System | Pass@1 | Pass^5 |
|---|---|---|
| NXS (multi-agent platform) | 86.7% | 63.3% |

Pass^5 drops significantly because coordination failures are non-deterministic. An agent team that passes 4 out of 5 runs fails Pass^5 for that scenario. Parallel delegation is the hardest pattern, with the lowest per-pattern task pass rate.

## Failure Taxonomy

| Failure Type | Frequency | Description |
|---|---|---|
| Context loss | Most common | Information is dropped during handoff or delegation. The receiving agent lacks context the sending agent had. |
| Duplicate work | Common | The coordinator dispatches the same subtask to multiple agents, or re-does a subtask that was already completed by a delegate. |
| Aggregation failure | Common | The coordinator collects results from branches but the final response omits or contradicts one branch. |
| Memory leak | Rare | Private memory is accessible to agents outside the owning agent's scope. |
| Unnecessary coordination | Rare | The coordinator dispatches a coordination call when the task could be handled by a single agent. |

## Companion Paper

Full methodology and comparative baselines: [NXS-Multi-Agent: Benchmarking Coordinated Agent Teams](../../docs/papers/nxs_multi_agent_benchmark.md). arXiv preprint pending.
