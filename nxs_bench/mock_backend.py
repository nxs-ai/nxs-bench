from __future__ import annotations

from copy import deepcopy
from uuid import uuid4


class MockBackend:
    def __init__(self, initial_state: dict | None = None) -> None:
        self._state = deepcopy(initial_state or {})

    def snapshot(self) -> dict:
        return deepcopy(self._state)

    def get(self, entity_type: str, entity_id: str):
        return deepcopy(self._state.get(entity_type, {}).get(entity_id))

    def list_entities(self, entity_type: str) -> dict:
        return deepcopy(self._state.get(entity_type, {}))

    def put(self, entity_type: str, entity_id: str, value: dict) -> dict:
        self._state.setdefault(entity_type, {})
        payload = deepcopy(value)
        payload.setdefault("id", entity_id)
        self._state[entity_type][entity_id] = payload
        return deepcopy(payload)

    def update(self, entity_type: str, entity_id: str, values: dict) -> dict:
        current = self._state.setdefault(entity_type, {}).setdefault(entity_id, {"id": entity_id})
        current.update(deepcopy(values))
        return deepcopy(current)

    def delete(self, entity_type: str, entity_id: str) -> None:
        self._state.setdefault(entity_type, {}).pop(entity_id, None)

    def create_entity(self, entity_type: str, value: dict, entity_id: str | None = None) -> dict:
        candidate_id = entity_id or value.get("id") or f"{entity_type.rstrip('s')}-{uuid4().hex[:8]}"
        return self.put(entity_type, candidate_id, value)

    def first_entity_id(self, entity_type: str) -> str | None:
        entities = self._state.get(entity_type, {})
        return next(iter(entities.keys()), None)
