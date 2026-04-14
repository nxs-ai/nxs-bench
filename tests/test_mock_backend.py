from nxs_bench.assertions import StateAssertion, ToolAssertion
from nxs_bench.mock_backend import MockBackend
from nxs_bench.mock_mcp import MockMCPGateway


def test_mock_backend_replays_tool_calls_and_state_assertions() -> None:
    backend = MockBackend(
        {
            "orders": {
                "ORD-1": {
                    "id": "ORD-1",
                    "customer_id": "cust-1",
                    "amount": 42.5,
                    "status": "delivered",
                }
            },
            "refunds": {},
        }
    )
    gateway = MockMCPGateway(backend=backend)

    gateway.replay_tool_calls(
        [
            {
                "tool": "payments",
                "operation": "process_refund",
                "arguments": {"order_id": "ORD-1", "customer_id": "cust-1", "amount": 42.5},
            }
        ]
    )

    refund_exists = StateAssertion(
        entity_type="refunds",
        entity_id=None,
        operation="exists",
        field=None,
        expected_value=None,
    ).check(backend)
    status_updated = StateAssertion(
        entity_type="orders",
        entity_id="ORD-1",
        operation="field_equals",
        field="status",
        expected_value="refunded",
    ).check(backend)
    tool_used = ToolAssertion(
        tool="payments",
        operation="process_refund",
        min_calls=1,
        max_calls=1,
    ).check(gateway.recorded_calls)

    assert refund_exists.passed is True
    assert status_updated.passed is True
    assert tool_used.passed is True


def test_mock_backend_snapshot_isolated_from_mutation() -> None:
    backend = MockBackend({"tickets": {}})
    snapshot = backend.snapshot()
    snapshot["tickets"]["temp"] = {"id": "temp"}

    assert backend.snapshot()["tickets"] == {}
