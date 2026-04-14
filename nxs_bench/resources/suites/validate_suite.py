from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]

SUITES_ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class DomainSpec:
    directory: str
    suite_name: str
    domain_value: str
    scenario_count: int
    inspired_by: str
    role_template: str | None = None


DOMAIN_SPECS: tuple[DomainSpec, ...] = (
    DomainSpec(
        directory="nxs_support",
        suite_name="NXS-Support",
        domain_value="support",
        scenario_count=100,
        inspired_by="Sierra tau-bench retail/airline/telecom",
        role_template="l1-support",
    ),
    DomainSpec(
        directory="nxs_sales",
        suite_name="NXS-Sales",
        domain_value="sales",
        scenario_count=50,
        inspired_by="Original",
        role_template="sdr",
    ),
    DomainSpec(
        directory="nxs_knowledge",
        suite_name="NXS-Knowledge",
        domain_value="knowledge",
        scenario_count=50,
        inspired_by="Sierra tau-Knowledge (banking)",
        role_template="knowledge-analyst",
    ),
    DomainSpec(
        directory="nxs_multi_agent",
        suite_name="NXS-Multi-Agent",
        domain_value="multi_agent",
        scenario_count=30,
        inspired_by="Original",
        role_template="coordinator",
    ),
    DomainSpec(
        directory="nxs_trust",
        suite_name="NXS-Trust",
        domain_value="trust",
        scenario_count=40,
        inspired_by="Original",
        role_template="l1-support",
    ),
    DomainSpec(
        directory="nxs_voice",
        suite_name="NXS-Voice",
        domain_value="voice",
        scenario_count=30,
        inspired_by="Sierra tau-Voice",
        role_template="voice-support",
    ),
    DomainSpec(
        directory="nxs_safety",
        suite_name="NXS-Safety",
        domain_value="safety",
        scenario_count=260,
        inspired_by="Adversarial suite (Section 3)",
        role_template="security-guard",
    ),
    DomainSpec(
        directory="nxs_mcp",
        suite_name="NXS-MCP",
        domain_value="mcp",
        scenario_count=30,
        inspired_by="LiveMCPBench",
        role_template="integration-operator",
    ),
    DomainSpec(
        directory="nxs_groundedness",
        suite_name="NXS-Groundedness",
        domain_value="groundedness",
        scenario_count=30,
        inspired_by="FACTS Grounding",
        role_template="knowledge-analyst",
    ),
    DomainSpec(
        directory="nxs_hardened",
        suite_name="NXS-Hardened",
        domain_value="hardened",
        scenario_count=25,
        inspired_by="FORTRESS + ST-WebAgentBench",
        role_template="compliance-guard",
    ),
)

DOMAIN_BY_DIRECTORY = {spec.directory: spec for spec in DOMAIN_SPECS}
TOTAL_EXPECTED_SCENARIOS = sum(spec.scenario_count for spec in DOMAIN_SPECS)
PERSONA_KEYS = (
    "clear_customer",
    "vague_customer",
    "frustrated_customer",
    "adversarial_user",
    "multi_language_customer",
    "impatient_customer",
    "technical_customer",
)
DIFFICULTIES = ("easy", "medium", "hard", "adversarial")
SCENARIO_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*-\d{3}$")
ALLOWED_AUDIO_CONDITIONS = {
    "clean",
    "coffee_shop",
    "street",
    "accent_variation",
    "interruption",
    "spelling_verification",
    "connection_issues",
}
ALLOWED_COORDINATION_TYPES = {
    "consult_roundtrip",
    "delegation_handoff",
    "escalation_chain",
    "transfer_continuity",
    "parallel_delegation",
    "memory_visibility",
}
SAFETY_CATEGORY_COUNTS = {
    "prompt_injection": 50,
    "identity_override": 25,
    "data_exfiltration": 30,
    "jailbreak_patterns": 40,
    "social_engineering": 20,
    "cross_tenant_probing": 15,
    "encoding_attacks": 20,
    "multi_turn_escalation": 25,
    "indirect_injection_via_tool_results": 20,
    "agentic_vulnerability_owasp": 15,
}
SUPPORT_CATEGORY_MINIMUMS = {
    "simple_inquiry": 8,
    "order_status": 5,
    "refund": 5,
    "technical_troubleshooting": 5,
    "account_management": 5,
    "complaint_handling": 4,
    "multi_part_request": 3,
    "edge_case": 3,
    "out_of_scope": 2,
}
SALES_CATEGORY_MINIMUMS = {
    "prospect_research": 8,
    "lead_qualification": 6,
    "outreach_drafting": 6,
    "follow_up": 4,
    "crm_updates": 3,
    "multi_prospect_batch": 3,
}
STATE_ASSERTION_OPERATIONS = {"exists", "not_exists", "field_equals", "field_gt", "field_lt"}
BASE_REQUIRED_FIELDS = [
    "id",
    "domain",
    "role_template",
    "category",
    "difficulty",
    "user_goal",
    "user_context",
    "user_known_info",
    "user_hidden_info",
    "max_user_turns",
    "available_tools",
    "knowledge_articles",
    "agent_constraints",
    "initial_state",
    "expected_state_changes",
    "expected_tool_calls",
    "forbidden_behaviors",
    "required_behaviors",
    "expected_resolution",
]
SCENARIO_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": [*BASE_REQUIRED_FIELDS, "personas"],
    "properties": {
        "id": {"type": "string"},
        "domain": {"type": "string"},
        "role_template": {"type": "string"},
        "category": {"type": "string"},
        "difficulty": {"type": "string", "enum": list(DIFFICULTIES)},
        "user_goal": {"type": "string"},
        "user_context": {"type": "string"},
        "user_known_info": {"type": "object"},
        "user_hidden_info": {"type": "object"},
        "max_user_turns": {"type": "integer"},
        "available_tools": {"type": "array", "items": {"type": "string"}},
        "knowledge_articles": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "title", "content"],
                "properties": {
                    "id": {"type": "string"},
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                },
                "additionalProperties": True,
            },
        },
        "agent_constraints": {"type": "object"},
        "initial_state": {"type": "object"},
        "expected_state_changes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["entity_type", "entity_id", "operation", "field", "expected_value"],
                "properties": {
                    "entity_type": {"type": "string"},
                    "entity_id": {"type": ["string", "null"]},
                    "operation": {"type": "string"},
                    "field": {"type": ["string", "null"]},
                },
                "additionalProperties": True,
            },
        },
        "expected_tool_calls": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["tool", "operation"],
                "properties": {
                    "tool": {"type": "string"},
                    "operation": {"type": "string"},
                    "should_be_called": {"type": "boolean"},
                    "min_calls": {"type": "integer"},
                    "max_calls": {"type": ["integer", "null"]},
                    "param_assertions": {"type": ["object", "null"]},
                },
                "additionalProperties": True,
            },
        },
        "forbidden_behaviors": {"type": "array", "items": {"type": "string"}},
        "required_behaviors": {"type": "array", "items": {"type": "string"}},
        "expected_resolution": {"type": "boolean"},
        "scoring_weights": {"type": ["object", "null"]},
        "personas": {"type": "array", "minItems": 1, "items": {"type": "string"}},
    },
    "additionalProperties": True,
}


@dataclass
class LoadedScenario:
    path: Path
    payload: dict[str, Any]


def main() -> int:
    errors: list[str] = []
    total_loaded = 0
    seen_ids: set[str] = set()

    for spec in DOMAIN_SPECS:
        loaded = _load_suite(spec=spec, errors=errors, seen_ids=seen_ids)
        total_loaded += len(loaded)

    if total_loaded != TOTAL_EXPECTED_SCENARIOS:
        errors.append(
            f"Expected {TOTAL_EXPECTED_SCENARIOS} scenarios across all suites, found {total_loaded}."
        )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Validated {TOTAL_EXPECTED_SCENARIOS} scenarios across {len(DOMAIN_SPECS)} suites.")
    return 0


def _load_suite(*, spec: DomainSpec, errors: list[str], seen_ids: set[str]) -> list[LoadedScenario]:
    suite_root = SUITES_ROOT / spec.directory
    suite_path = suite_root / "suite.yaml"
    scenarios_dir = suite_root / "scenarios"
    if not suite_path.exists():
        errors.append(f"Missing suite metadata file: {suite_path.relative_to(REPO_ROOT)}")
        return []
    if not scenarios_dir.exists():
        errors.append(f"Missing scenarios directory: {scenarios_dir.relative_to(REPO_ROOT)}")
        return []

    metadata = _read_yaml_mapping(suite_path, errors)
    scenario_paths = sorted(scenarios_dir.glob("*.yaml"))
    if len(scenario_paths) != spec.scenario_count:
        errors.append(
            f"{spec.directory}: expected {spec.scenario_count} scenarios, found {len(scenario_paths)}."
        )

    loaded: list[LoadedScenario] = []
    for path in scenario_paths:
        payload = _read_yaml_mapping(path, errors)
        if not payload:
            continue
        _validate_schema(payload, SCENARIO_SCHEMA, path.relative_to(REPO_ROOT).as_posix(), errors)
        _validate_common_payload(spec=spec, path=path, payload=payload, errors=errors, seen_ids=seen_ids)
        if not _validate_assertion_structures(payload=payload, path=path, errors=errors):
            continue
        loaded.append(LoadedScenario(path=path, payload=payload))

    _validate_suite_metadata(spec=spec, metadata=metadata, loaded=loaded, errors=errors)
    _validate_domain(spec=spec, loaded=loaded, errors=errors)
    print(f"{spec.directory}: {len(loaded)} scenarios validated")
    return loaded


def _read_yaml_mapping(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - reported to caller
        errors.append(f"{path.relative_to(REPO_ROOT)} failed to load: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"{path.relative_to(REPO_ROOT)} must contain a YAML mapping at the top level.")
        return {}
    return payload


def _validate_schema(value: Any, schema: dict[str, Any], path: str, errors: list[str]) -> None:
    allowed_types = schema.get("type")
    if allowed_types is not None and not _matches_type(value, allowed_types):
        errors.append(f"{path}: expected type {allowed_types}, found {type(value).__name__}.")
        return

    enum = schema.get("enum")
    if enum is not None and value not in enum:
        errors.append(f"{path}: expected one of {enum}, found {value!r}.")
        return

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required key {key!r}.")
        properties = schema.get("properties", {})
        allow_additional = schema.get("additionalProperties", True)
        for key, item in value.items():
            child_schema = properties.get(key)
            child_path = f"{path}.{key}"
            if child_schema is None:
                if allow_additional is False:
                    errors.append(f"{child_path}: additional properties are not allowed.")
                continue
            _validate_schema(item, child_schema, child_path, errors)
        return

    if isinstance(value, list):
        min_items = schema.get("minItems")
        if min_items is not None and len(value) < min_items:
            errors.append(f"{path}: expected at least {min_items} items, found {len(value)}.")
        item_schema = schema.get("items")
        if item_schema is None:
            return
        for index, item in enumerate(value):
            _validate_schema(item, item_schema, f"{path}[{index}]", errors)


def _matches_type(value: Any, allowed_types: str | list[str]) -> bool:
    candidates = [allowed_types] if isinstance(allowed_types, str) else list(allowed_types)
    for candidate in candidates:
        if candidate == "null" and value is None:
            return True
        if candidate == "string" and isinstance(value, str):
            return True
        if candidate == "boolean" and isinstance(value, bool):
            return True
        if candidate == "integer" and isinstance(value, int) and not isinstance(value, bool):
            return True
        if candidate == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
        if candidate == "array" and isinstance(value, list):
            return True
        if candidate == "object" and isinstance(value, dict):
            return True
    return False


def _validate_common_payload(
    *,
    spec: DomainSpec,
    path: Path,
    payload: dict[str, Any],
    errors: list[str],
    seen_ids: set[str],
) -> None:
    scenario_id = payload.get("id")
    if isinstance(scenario_id, str):
        if scenario_id in seen_ids:
            errors.append(f"{path.relative_to(REPO_ROOT)} duplicates scenario id {scenario_id!r}.")
        seen_ids.add(scenario_id)
        if not SCENARIO_ID_PATTERN.fullmatch(scenario_id):
            errors.append(f"{path.relative_to(REPO_ROOT)} has invalid scenario id format {scenario_id!r}.")

    if payload.get("domain") != spec.domain_value:
        errors.append(
            f"{path.relative_to(REPO_ROOT)} expected domain {spec.domain_value!r}, found {payload.get('domain')!r}."
        )

    if spec.role_template is not None and payload.get("role_template") != spec.role_template:
        errors.append(
            f"{path.relative_to(REPO_ROOT)} expected role_template {spec.role_template!r}, "
            f"found {payload.get('role_template')!r}."
        )

    file_category = _path_category(path)
    payload_category = payload.get("category")
    if file_category != payload_category:
        errors.append(
            f"{path.relative_to(REPO_ROOT)} expected category {file_category!r} from file name, "
            f"found {payload_category!r}."
        )

    personas = payload.get("personas")
    if not isinstance(personas, list) or not personas:
        errors.append(f"{path.relative_to(REPO_ROOT)} must define a non-empty personas list.")
    else:
        invalid = [persona for persona in personas if persona not in PERSONA_KEYS]
        if invalid:
            errors.append(f"{path.relative_to(REPO_ROOT)} uses unknown personas: {invalid}.")

    initial_state = payload.get("initial_state")
    if isinstance(initial_state, dict):
        for entity_type, entity_payload in initial_state.items():
            if not isinstance(entity_type, str) or not isinstance(entity_payload, dict):
                errors.append(
                    f"{path.relative_to(REPO_ROOT)} initial_state entries must be mappings keyed by entity type."
                )
                break

    articles = payload.get("knowledge_articles")
    if isinstance(articles, list):
        article_ids = [article.get("id") for article in articles if isinstance(article, dict)]
        if len(article_ids) != len(set(article_ids)):
            errors.append(f"{path.relative_to(REPO_ROOT)} contains duplicate knowledge article ids.")


def _path_category(path: Path) -> str:
    stem = path.stem
    if "_" not in stem:
        return stem
    return stem.rsplit("_", 1)[0]


def _validate_assertion_structures(
    *,
    payload: dict[str, Any],
    path: Path,
    errors: list[str],
) -> bool:
    state_assertions = payload.get("expected_state_changes")
    tool_assertions = payload.get("expected_tool_calls")
    if not isinstance(state_assertions, list) or not isinstance(tool_assertions, list):
        return False

    for assertion in state_assertions:
        if not isinstance(assertion, dict):
            errors.append(f"{path.relative_to(REPO_ROOT)} state assertions must be mappings.")
            return False
        operation = assertion.get("operation")
        field = assertion.get("field")
        if operation in {"field_equals", "field_gt", "field_lt"} and field is None:
            errors.append(
                f"{path.relative_to(REPO_ROOT)} state assertion {operation!r} requires field."
            )
        if operation not in STATE_ASSERTION_OPERATIONS:
            errors.append(
                f"{path.relative_to(REPO_ROOT)} has unsupported state assertion operation {operation!r}."
            )

    for assertion in tool_assertions:
        if not isinstance(assertion, dict):
            errors.append(f"{path.relative_to(REPO_ROOT)} tool assertions must be mappings.")
            return False
        min_calls = assertion.get("min_calls", 1)
        max_calls = assertion.get("max_calls")
        if not isinstance(min_calls, int):
            errors.append(f"{path.relative_to(REPO_ROOT)} tool assertion min_calls must be an integer.")
            continue
        if min_calls < 0:
            errors.append(f"{path.relative_to(REPO_ROOT)} has negative min_calls for tool assertion.")
        if max_calls is not None and (not isinstance(max_calls, int) or max_calls < min_calls):
            errors.append(f"{path.relative_to(REPO_ROOT)} has max_calls below min_calls.")
    return True


def _validate_suite_metadata(
    *,
    spec: DomainSpec,
    metadata: dict[str, Any],
    loaded: list[LoadedScenario],
    errors: list[str],
) -> None:
    suite_path = SUITES_ROOT / spec.directory / "suite.yaml"
    required_keys = {
        "name",
        "version",
        "task_count",
        "description",
        "inspired_by",
        "difficulty_distribution",
        "persona_distribution",
    }
    missing = sorted(required_keys - metadata.keys())
    if missing:
        errors.append(f"{suite_path.relative_to(REPO_ROOT)} missing metadata keys: {missing}.")
        return

    if metadata["name"] != spec.suite_name:
        errors.append(f"{suite_path.relative_to(REPO_ROOT)} expected name {spec.suite_name!r}.")
    if str(metadata["version"]) != "1.0":
        errors.append(f"{suite_path.relative_to(REPO_ROOT)} expected version '1.0'.")
    if int(metadata["task_count"]) != len(loaded):
        errors.append(
            f"{suite_path.relative_to(REPO_ROOT)} task_count={metadata['task_count']} "
            f"does not match {len(loaded)} scenarios."
        )
    if not isinstance(metadata["description"], str) or not metadata["description"].strip():
        errors.append(f"{suite_path.relative_to(REPO_ROOT)} must include a non-empty description.")
    if str(metadata["inspired_by"]) != spec.inspired_by:
        errors.append(
            f"{suite_path.relative_to(REPO_ROOT)} expected inspired_by {spec.inspired_by!r}, "
            f"found {metadata['inspired_by']!r}."
        )

    expected_difficulty_distribution = Counter(item.payload["difficulty"] for item in loaded)
    expected_persona_distribution = Counter()
    for item in loaded:
        for persona in item.payload["personas"]:
            expected_persona_distribution[str(persona)] += 1

    if dict(metadata["difficulty_distribution"]) != dict(expected_difficulty_distribution):
        errors.append(
            f"{suite_path.relative_to(REPO_ROOT)} difficulty_distribution does not match actual counts."
        )
    if dict(metadata["persona_distribution"]) != dict(expected_persona_distribution):
        errors.append(
            f"{suite_path.relative_to(REPO_ROOT)} persona_distribution does not match actual counts."
        )


def _validate_domain(*, spec: DomainSpec, loaded: list[LoadedScenario], errors: list[str]) -> None:
    if spec.directory == "nxs_support":
        _validate_support(loaded=loaded, errors=errors)
    elif spec.directory == "nxs_sales":
        _validate_sales(loaded=loaded, errors=errors)
    elif spec.directory == "nxs_knowledge":
        _validate_knowledge(loaded=loaded, errors=errors)
    elif spec.directory == "nxs_multi_agent":
        _validate_multi_agent(loaded=loaded, errors=errors)
    elif spec.directory == "nxs_trust":
        _validate_trust(loaded=loaded, errors=errors)
    elif spec.directory == "nxs_voice":
        _validate_voice(loaded=loaded, errors=errors)
    elif spec.directory == "nxs_safety":
        _validate_safety(loaded=loaded, errors=errors)
    elif spec.directory == "nxs_mcp":
        _validate_mcp(loaded=loaded, errors=errors)
    elif spec.directory == "nxs_groundedness":
        _validate_groundedness(loaded=loaded, errors=errors)
    elif spec.directory == "nxs_hardened":
        _validate_hardened(loaded=loaded, errors=errors)


def _validate_support(*, loaded: list[LoadedScenario], errors: list[str]) -> None:
    counts = Counter(item.payload["category"] for item in loaded)
    for category, minimum in SUPPORT_CATEGORY_MINIMUMS.items():
        if counts[category] < minimum:
            errors.append(f"nxs_support must contain at least {minimum} {category} scenarios.")

    difficulty_counts = Counter(item.payload["difficulty"] for item in loaded)
    if difficulty_counts != {"easy": 30, "medium": 40, "hard": 20, "adversarial": 10}:
        errors.append("nxs_support must use the 30/40/20/10 difficulty distribution.")


def _validate_sales(*, loaded: list[LoadedScenario], errors: list[str]) -> None:
    counts = Counter(item.payload["category"] for item in loaded)
    for category, minimum in SALES_CATEGORY_MINIMUMS.items():
        if counts[category] < minimum:
            errors.append(f"nxs_sales must contain at least {minimum} {category} scenarios.")

    operations = {
        (str(call["tool"]), str(call["operation"]))
        for item in loaded
        for call in item.payload["expected_tool_calls"]
        if isinstance(call, dict)
    }
    required_operations = {
        ("crm", "get_company"),
        ("crm", "get_contacts"),
        ("crm", "update_deal"),
        ("research", "search_web"),
        ("research", "get_linkedin_profile"),
        ("email", "draft_email"),
        ("email", "send_email"),
    }
    missing = sorted(required_operations - operations)
    if missing:
        errors.append(f"nxs_sales is missing tool coverage for: {missing}.")


def _validate_knowledge(*, loaded: list[LoadedScenario], errors: list[str]) -> None:
    categories = Counter(item.payload["category"] for item in loaded)
    for category in ("single_hop", "multi_hop", "irrelevant_query", "contradictory_info"):
        if categories[category] == 0:
            errors.append(f"nxs_knowledge must cover category {category!r}.")

    for item in loaded:
        articles = item.payload["knowledge_articles"]
        if len(articles) < 10:
            errors.append(f"{item.path.relative_to(REPO_ROOT)} must include at least 10 knowledge articles.")
        citation_ids = item.payload.get("citation_ids")
        if not isinstance(citation_ids, list):
            errors.append(f"{item.path.relative_to(REPO_ROOT)} must include citation_ids.")
            continue
        article_ids = {article["id"] for article in articles}
        missing = [citation_id for citation_id in citation_ids if citation_id not in article_ids]
        if missing:
            errors.append(f"{item.path.relative_to(REPO_ROOT)} citation_ids missing from knowledge_articles: {missing}.")


def _validate_multi_agent(*, loaded: list[LoadedScenario], errors: list[str]) -> None:
    counts = Counter()
    for item in loaded:
        coordination_type = item.payload.get("coordination_type")
        if coordination_type not in ALLOWED_COORDINATION_TYPES:
            errors.append(
                f"{item.path.relative_to(REPO_ROOT)} has invalid coordination_type {coordination_type!r}."
            )
        else:
            counts[str(coordination_type)] += 1
        agent_roles = item.payload.get("agent_roles")
        if not isinstance(agent_roles, list) or len(agent_roles) < 2:
            errors.append(f"{item.path.relative_to(REPO_ROOT)} must define at least two agent_roles.")
        expectations = item.payload.get("per_agent_expected_behaviors")
        if not isinstance(expectations, dict) or not expectations:
            errors.append(
                f"{item.path.relative_to(REPO_ROOT)} must define per_agent_expected_behaviors."
            )

    for coordination_type in ALLOWED_COORDINATION_TYPES:
        if counts[coordination_type] == 0:
            errors.append(f"nxs_multi_agent must cover coordination_type {coordination_type!r}.")


def _validate_trust(*, loaded: list[LoadedScenario], errors: list[str]) -> None:
    counts = Counter()
    for item in loaded:
        trust_tier = item.payload["agent_constraints"].get("trust_tier")
        if trust_tier not in {0, 1, 2, 3}:
            errors.append(f"{item.path.relative_to(REPO_ROOT)} has invalid trust_tier {trust_tier!r}.")
            continue
        counts[int(trust_tier)] += 1

    for trust_tier in range(4):
        if counts[trust_tier] != 10:
            errors.append(f"nxs_trust must contain exactly 10 scenarios for trust tier {trust_tier}.")


def _validate_voice(*, loaded: list[LoadedScenario], errors: list[str]) -> None:
    accents: set[str] = set()
    for item in loaded:
        audio_condition = item.payload.get("audio_condition")
        if audio_condition not in ALLOWED_AUDIO_CONDITIONS:
            errors.append(f"{item.path.relative_to(REPO_ROOT)} has invalid audio_condition {audio_condition!r}.")
        if audio_condition == "accent_variation":
            accent_profile = item.payload.get("accent_profile")
            if accent_profile not in {"Gulf Arabic", "Indian English", "British English"}:
                errors.append(
                    f"{item.path.relative_to(REPO_ROOT)} must use a supported accent_profile."
                )
            else:
                accents.add(str(accent_profile))

    if accents != {"Gulf Arabic", "Indian English", "British English"}:
        errors.append("nxs_voice must include Gulf Arabic, Indian English, and British English accent scenarios.")


def _validate_safety(*, loaded: list[LoadedScenario], errors: list[str]) -> None:
    counts = Counter(item.payload["category"] for item in loaded)
    if counts != Counter(SAFETY_CATEGORY_COUNTS):
        errors.append(f"nxs_safety category counts do not match expected values: {dict(counts)}.")

    for item in loaded:
        if item.payload["difficulty"] != "adversarial":
            errors.append(f"{item.path.relative_to(REPO_ROOT)} must use adversarial difficulty.")
        if item.payload["expected_resolution"] is not False:
            errors.append(f"{item.path.relative_to(REPO_ROOT)} must set expected_resolution to false.")
        if not item.payload.get("attack_vector"):
            errors.append(f"{item.path.relative_to(REPO_ROOT)} must define attack_vector.")


def _validate_mcp(*, loaded: list[LoadedScenario], errors: list[str]) -> None:
    categories = Counter(item.payload["category"] for item in loaded)
    for category in (
        "tool_discovery",
        "auth_negotiation",
        "error_handling",
        "rate_limit_compliance",
        "timeout_recovery",
    ):
        if categories[category] == 0:
            errors.append(f"nxs_mcp must cover category {category!r}.")

    connector_types = {item.payload.get("connector_type") for item in loaded}
    if len({value for value in connector_types if isinstance(value, str)}) < 10:
        errors.append("nxs_mcp must cover at least 10 connector types.")

    tier_one_write_cases = [
        item
        for item in loaded
        if item.payload["agent_constraints"].get("trust_tier") == 1 and item.payload.get("operation_type") == "write"
    ]
    if not tier_one_write_cases:
        errors.append("nxs_mcp must include Tier 1 write-operation failure cases.")


def _validate_groundedness(*, loaded: list[LoadedScenario], errors: list[str]) -> None:
    for item in loaded:
        articles = item.payload["knowledge_articles"]
        token_count = sum(len(str(article.get("content", "")).split()) for article in articles)
        if token_count < 8000 or token_count > 32000:
            errors.append(
                f"{item.path.relative_to(REPO_ROOT)} must provide 8K-32K tokens of grounding context, found {token_count}."
            )
        scoring_targets = item.payload.get("scoring_targets")
        if not isinstance(scoring_targets, dict):
            errors.append(f"{item.path.relative_to(REPO_ROOT)} must define scoring_targets.")
            continue
        if set(scoring_targets) != {"groundedness_rate", "hallucination_rate"}:
            errors.append(
                f"{item.path.relative_to(REPO_ROOT)} scoring_targets must include groundedness_rate and hallucination_rate."
            )


def _validate_hardened(*, loaded: list[LoadedScenario], errors: list[str]) -> None:
    for item in loaded:
        if not item.payload.get("attack_vector"):
            errors.append(f"{item.path.relative_to(REPO_ROOT)} must define attack_vector.")
        if not item.payload.get("policy_constraint"):
            errors.append(f"{item.path.relative_to(REPO_ROOT)} must define policy_constraint.")


if __name__ == "__main__":
    raise SystemExit(main())
