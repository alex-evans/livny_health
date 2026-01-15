"""
Patient repository - data access layer.
"""

from __future__ import annotations

from typing import Any
from resources.core import InMemoryRepository
from .model import Patient


class PatientRepository(InMemoryRepository[Patient]):
    """
    Repository for Patient resources.
    Currently uses in-memory storage, can be swapped for database later.
    """

    async def list(self, **filters: Any) -> list[Patient]:
        """
        List patients with optional filters.

        Supported filters:
        - active: bool - Filter by active status
        - name: str - Filter by name (partial match)
        - mrn: str - Filter by MRN (exact match)
        """
        results = list(self._store.values())

        if "active" in filters:
            results = [p for p in results if p.active == filters["active"]]

        if "name" in filters:
            name_filter = filters["name"].lower()
            results = [p for p in results if name_filter in p.display_name.lower()]

        if "mrn" in filters:
            results = [p for p in results if p.mrn == filters["mrn"]]

        return results

    async def get_by_mrn(self, mrn: str) -> Patient | None:
        """Find a patient by MRN."""
        for patient in self._store.values():
            if patient.mrn == mrn:
                return patient
        return None
