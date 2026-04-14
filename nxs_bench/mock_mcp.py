from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable
from uuid import uuid4

from .assertions import normalize_tool_call
from .mock_backend import MockBackend


ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


class MockMCPGateway:
    def __init__(self, backend: MockBackend | None = None) -> None:
        self.backend = backend or MockBackend()
        self.recorded_calls: list[dict[str, Any]] = []
        self._handlers: dict[tuple[str, str], ToolHandler] = {}
        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        self.register_tool("knowledge", "search", self._knowledge_search)
        self.register_tool("crm", "get_customer", self._get_customer)
        self.register_tool("crm", "get_order", self._get_order)
        self.register_tool("payments", "process_refund", self._process_refund)
        self.register_tool("helpdesk", "create_ticket", self._create_ticket)
        self.register_tool("helpdesk", "get_ticket", self._get_ticket)
        self.register_tool("coordination", "delegation_handoff", self._complete_coordination)
        self.register_tool("coordination", "consult_roundtrip", self._complete_coordination)
        self.register_tool("coordination", "parallel_delegation", self._complete_coordination)
        self.register_tool("coordination", "transfer_continuity", self._complete_coordination)
        self.register_tool("coordination", "memory_visibility", self._complete_coordination)
        self.register_tool("coordination", "escalation_chain", self._complete_coordination)

    def register_tool(self, tool: str, operation: str, handler: ToolHandler) -> None:
        self._handlers[(tool, operation)] = handler

    def replay_tool_calls(self, tool_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for raw_call in tool_calls:
            call = normalize_tool_call(raw_call)
            self.recorded_calls.append(deepcopy(call))
            handler = self._handlers.get((call["tool"], call["operation"]))
            if handler:
                results.append(handler(call.get("arguments", {})))
            else:
                results.append({"status": "ignored", "tool": call["tool"], "operation": call["operation"]})
        return results

    def tool_definitions(self, available_tools: list[str]) -> list[dict[str, Any]]:
        definitions = []
        for tool_name in available_tools:
            definitions.append(
                {
                    "name": tool_name,
                    "description": f"Mock {tool_name} tool for benchmark scenarios.",
                    "input_schema": {"type": "object"},
                }
            )
        return definitions

    def _knowledge_search(self, arguments: dict[str, Any]) -> dict[str, Any]:
        query = str(arguments.get("query", "")).lower()
        articles = self.backend.list_entities("knowledge_articles")
        matches = [
            article
            for article in articles.values()
            if query in str(article.get("title", "")).lower() or query in str(article.get("content", "")).lower()
        ]
        return {"matches": matches}

    def _get_customer(self, arguments: dict[str, Any]) -> dict[str, Any]:
        customer_id = arguments.get("customer_id")
        if customer_id:
            return {"customer": self.backend.get("customers", customer_id)}
        email = arguments.get("email")
        customers = self.backend.list_entities("customers")
        customer = next((item for item in customers.values() if item.get("email") == email), None)
        return {"customer": customer}

    def _get_order(self, arguments: dict[str, Any]) -> dict[str, Any]:
        order_id = arguments.get("order_id")
        return {"order": self.backend.get("orders", order_id)} if order_id else {"order": None}

    def _process_refund(self, arguments: dict[str, Any]) -> dict[str, Any]:
        order_id = arguments.get("order_id")
        order = self.backend.get("orders", order_id) if order_id else None
        refund_id = arguments.get("refund_id") or f"refund-{uuid4().hex[:8]}"
        amount = arguments.get("amount", order.get("amount") if order else 0.0)
        refund = {
            "id": refund_id,
            "order_id": order_id,
            "customer_id": arguments.get("customer_id") or (order or {}).get("customer_id"),
            "amount": amount,
            "status": "processed",
        }
        self.backend.put("refunds", refund_id, refund)
        if order_id and order:
            self.backend.update("orders", order_id, {"status": "refunded"})
        return {"refund": refund}

    def _create_ticket(self, arguments: dict[str, Any]) -> dict[str, Any]:
        ticket_id = arguments.get("ticket_id") or f"ticket-{uuid4().hex[:8]}"
        ticket = {
            "id": ticket_id,
            "status": arguments.get("status", "open"),
            "summary": arguments.get("summary", "Benchmark-generated ticket"),
        }
        self.backend.put("tickets", ticket_id, ticket)
        return {"ticket": ticket}

    def _get_ticket(self, arguments: dict[str, Any]) -> dict[str, Any]:
        ticket_id = arguments.get("ticket_id")
        return {"ticket": self.backend.get("tickets", ticket_id)} if ticket_id else {"ticket": None}

    def _complete_coordination(self, arguments: dict[str, Any]) -> dict[str, Any]:
        record_id = arguments.get("coordination_id") or self.backend.first_entity_id("coordination_records")
        if record_id:
            current = self.backend.get("coordination_records", record_id) or {"id": record_id}
            updates = {
                "status": "completed",
                "results_aggregated": True,
                "context_preserved": True,
            }
            if "duplicate_work" in current:
                updates["duplicate_work"] = False
            self.backend.update("coordination_records", record_id, updates)
        return {"coordination_id": record_id, "status": "completed"}
