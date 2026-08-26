from __future__ import annotations

from enum import StrEnum
from typing import Any


class AllocationIDs(StrEnum):
    BLUEPRINT = "bp"
    FILE_PATH = "fp"
    FILE_UPLOADER = "fu"
    EXTRACTION_FIELD = "field"
    QUESTION = "q"
    QUESTION_ITEM = "qi"
    FILTER_CONDITION = "fc"


class LocalIdAllocator:
    """
    Assigns namespaced, sequential local ids to model instances during export.

    Local ids (e.g. "bp-1", "field-3") stand in for real primary keys within
    a single exported payload, so that relationships between objects
    (e.g. a ProcessingRule's link to its ExtractionField) can be represented
    portably, without depending on database primary keys that won't survive
    a JSON round-trip or even necessarily an in-app copy.
    """

    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self._assigned: dict[tuple[str, int], str] = {}

    def get_or_create(self, namespace: str, pk: int) -> str:
        key = (namespace, pk)
        if key not in self._assigned:
            self._counters[namespace] = self._counters.get(namespace, 0) + 1
            self._assigned[key] = f"{namespace}-{self._counters[namespace]}"
        return self._assigned[key]


class IdMap:
    """
    Resolves local ids (assigned during export via LocalIdAllocator) to the
    newly created live model instances during import/build.

    Looking up an id that was never registered (a dangling/malformed
    reference) returns None rather than raising, so callers can decide
    whether that's tolerable (e.g. DonationBlueprint.backup_for) or should
    surface as a validation error (e.g. a FilterCondition with no target).
    """

    def __init__(self) -> None:
        self._objects: dict[str, Any] = {}

    def register(self, local_id: str | None, obj: Any) -> None:  # noqa: ANN401
        if local_id is None:
            return
        self._objects[local_id] = obj

    def get(self, local_id: str | None) -> Any | None:  # noqa: ANN401
        if local_id is None:
            return None
        return self._objects.get(local_id)
