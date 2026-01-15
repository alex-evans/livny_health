"""
Practitioner repository - data access layer.
"""

from __future__ import annotations

from typing import Any
from resources.core import InMemoryRepository
from .model import Practitioner


class PractitionerRepository(InMemoryRepository[Practitioner]):
    """
    Repository for Practitioner resources.
    Currently uses in-memory storage, can be swapped for database later.
    """

    async def list(self, **filters: Any) -> list[Practitioner]:
        """
        List practitioners with optional filters.

        Supported filters:
        - active: bool - Filter by active status
        - name: str - Filter by name (partial match)
        """
        results = list(self._store.values())

        if "active" in filters:
            results = [p for p in results if p.active == filters["active"]]

        if "name" in filters:
            name_filter = filters["name"].lower()
            results = [p for p in results if name_filter in p.display_name.lower()]

        return results

    async def get_by_npi(self, npi: str) -> Practitioner | None:
        """Find a practitioner by NPI."""
        for practitioner in self._store.values():
            if practitioner.npi == npi:
                return practitioner
        return None
