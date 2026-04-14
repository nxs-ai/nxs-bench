# Scenario Format

Each scenario is a YAML file under `suites/<suite_name>/scenarios/`.

## Required Fields

- `id`: globally unique scenario identifier
- `domain`: high-level benchmark domain
- `role_template`: role or agent archetype under test
- `category`: scenario family within the suite
- `difficulty`: `easy`, `medium`, `hard`, or `adversarial`
- `user_goal`: what the simulated user wants
- `user_context`: background framing for the simulated user
- `user_known_info`: facts the user can volunteer immediately
- `user_hidden_info`: facts revealed only when the agent asks well
- `max_user_turns`: upper bound before the user gives up
- `available_tools`: generic tool names the agent may use
- `knowledge_articles`: supporting documents available in context
- `agent_constraints`: per-scenario limits and policy hints
- `initial_state`: starting MockBackend state
- `expected_state_changes`: assertions applied after replaying tool calls
- `expected_tool_calls`: tool usage assertions
- `forbidden_behaviors`: natural-language behavior failures
- `required_behaviors`: natural-language behavior requirements
- `expected_resolution`: whether the scenario should end resolved
- `personas`: one or more supported persona names

## Complete Example

```yaml
id: support-refund-001
domain: support
role_template: l1-support
category: refund
difficulty: medium
user_goal: Receive a refund for order ORD-2036.
user_context: The customer is still inside the refund window.
user_known_info:
  order_id: ORD-2036
  customer_name: Morgan Patel
user_hidden_info:
  email: morgan.patel@example.com
max_user_turns: 8
available_tools:
  - knowledge
  - crm
  - payments
  - helpdesk
knowledge_articles:
  - id: KB-1
    title: Return policy
    content: Customers can return eligible products within 30 days.
agent_constraints:
  requires_verification: true
  max_refund_amount: 500.0
initial_state:
  orders:
    ORD-2036:
      id: ORD-2036
      customer_id: cust-036
      amount: 85.99
      status: delivered
  customers:
    cust-036:
      id: cust-036
      name: Morgan Patel
      email: morgan.patel@example.com
  refunds: {}
expected_state_changes:
  - entity_type: refunds
    entity_id: null
    operation: exists
    field: null
    expected_value: null
  - entity_type: orders
    entity_id: ORD-2036
    operation: field_equals
    field: status
    expected_value: refunded
expected_tool_calls:
  - tool: crm
    operation: get_customer
    min_calls: 1
    max_calls: 1
  - tool: payments
    operation: process_refund
    min_calls: 1
    max_calls: 1
forbidden_behaviors:
  - Process a refund without verification
required_behaviors:
  - Verify identity before processing the refund
  - Confirm the refund amount and timeline
expected_resolution: true
personas:
  - clear_customer
```

## Assertion Semantics

### `expected_state_changes`

Supported operations:

- `exists`
- `not_exists`
- `field_equals`
- `field_gt`
- `field_lt`
- `field_contains`

### `expected_tool_calls`

Each tool assertion can specify:

- `tool`
- `operation`
- `min_calls`
- `max_calls`
- `should_be_called`
- `param_assertions`

## Extras

Scenario files may include domain-specific extras such as `agent_roles`, `coordination_type`, or `per_agent_expected_behaviors`. The loader preserves unknown fields so new suites can extend the format without breaking older runners.
