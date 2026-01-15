"""
Medication repository - data access layer.
"""

from __future__ import annotations

from typing import Any
from resources.core import InMemoryRepository
from .model import Medication


class MedicationRepository(InMemoryRepository[Medication]):
    """
    Repository for Medication resources.
    Currently uses in-memory storage, can be swapped for database later.
    """

    async def list(self, **filters: Any) -> list[Medication]:
        """
        List medications with optional filters.

        Supported filters:
        - name: str - Filter by name (partial match)
        - is_controlled: bool - Filter by controlled status
        - status: str - Filter by status
        """
        results = list(self._store.values())

        if "name" in filters:
            name_filter = filters["name"].lower()
            results = [m for m in results if name_filter in m.name.lower()]

        if "is_controlled" in filters:
            results = [m for m in results if m.is_controlled == filters["is_controlled"]]

        if "status" in filters:
            results = [m for m in results if m.status == filters["status"]]

        return results

    async def search(self, query: str) -> list[Medication]:
        """Search medications by name (partial match)."""
        query_lower = query.lower()
        return [m for m in self._store.values() if query_lower in m.name.lower()]
