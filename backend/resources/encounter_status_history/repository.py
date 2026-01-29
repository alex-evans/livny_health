"""
Encounter Status History repository - data access layer.
"""

from __future__ import annotations

from typing import Any
from resources.core import InMemoryRepository
from .model import EncounterStatusHistory


class EncounterStatusHistoryRepository(InMemoryRepository[EncounterStatusHistory]):
    """
    Repository for EncounterStatusHistory resources.
    Currently uses in-memory storage, can be swapped for database later.
    """

    async def list(self, **filters: Any) -> list[EncounterStatusHistory]:
        """
        List encounter status history entries with optional filters.

        Supported filters:
        - encounter_id: str - Filter by encounter ID
        """
        results = list(self._store.values())

        if "encounter_id" in filters:
            results = [h for h in results if h.encounter_id == filters["encounter_id"]]

        # Sort by changed_at descending (newest first)
        results.sort(key=lambda h: h.changed_at or h.meta_last_updated, reverse=True)
        return results

    async def get_by_encounter(
        self, encounter_id: str
    ) -> list[EncounterStatusHistory]:
        """Get all status history entries for an encounter, sorted by time descending."""
        return await self.list(encounter_id=encounter_id)
