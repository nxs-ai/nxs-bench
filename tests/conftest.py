import sys
from pathlib import Path

import pytest
import yaml


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))


@pytest.fixture
def sample_suite_root(tmp_path: Path) -> Path:
    root = tmp_path / "bench-data"
    suite_dir = root / "nxs_support"
    scenario_dir = suite_dir / "scenarios"
    scenario_dir.mkdir(parents=True)

    suite_payload = {
        "name": "NXS-Support",
        "version": "1.0",
        "task_count": 1,
        "description": "Minimal support suite for tests.",
        "difficulty_distribution": {"easy": 1, "medium": 0, "hard": 0, "adversarial": 0},
        "persona_distribution": {
            "clear_customer": 1,
            "vague_customer": 0,
            "frustrated_customer": 0,
            "multi_language_customer": 0,
            "impatient_customer": 0,
            "technical_customer": 0,
            "adversarial_user": 0,
        },
    }
    scenario_payload = {
        "id": "support-refund-001",
        "domain": "support",
        "role_template": "l1-support",
        "category": "refund",
        "difficulty": "easy",
        "user_goal": "I need a refund for order ORD-1.",
        "user_context": "The purchase is inside the refund window.",
        "user_known_info": {"order_id": "ORD-1", "customer_name": "Taylor"},
        "user_hidden_info": {"email": "taylor@example.com"},
        "max_user_turns": 2,
        "available_tools": ["knowledge", "payments", "crm"],
        "knowledge_articles": [
            {
                "id": "KB-1",
                "title": "Refund Policy",
                "content": "Eligible orders can be refunded within 30 days.",
            }
        ],
        "agent_constraints": {"requires_verification": True, "max_refund_amount": 500.0},
        "initial_state": {
            "orders": {
                "ORD-1": {
                    "id": "ORD-1",
                    "customer_id": "cust-1",
                    "amount": 42.5,
                    "status": "delivered",
                }
            },
            "customers": {
                "cust-1": {
                    "id": "cust-1",
                    "name": "Taylor",
                    "email": "taylor@example.com",
                }
            },
            "refunds": {},
        },
        "expected_state_changes": [
            {
                "entity_type": "refunds",
                "entity_id": None,
                "operation": "exists",
                "field": None,
                "expected_value": None,
            },
            {
                "entity_type": "orders",
                "entity_id": "ORD-1",
                "operation": "field_equals",
                "field": "status",
                "expected_value": "refunded",
            },
        ],
        "expected_tool_calls": [
            {"tool": "payments", "operation": "process_refund", "min_calls": 1, "max_calls": 1}
        ],
        "forbidden_behaviors": ["Reveal internal-only tooling details"],
        "required_behaviors": ["Confirm the refund timeline"],
        "expected_resolution": True,
        "personas": ["clear_customer"],
    }

    (suite_dir / "suite.yaml").write_text(yaml.safe_dump(suite_payload, sort_keys=False), encoding="utf-8")
    (scenario_dir / "refund_001.yaml").write_text(
        yaml.safe_dump(scenario_payload, sort_keys=False), encoding="utf-8"
    )
    return root
