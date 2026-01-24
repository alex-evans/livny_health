"""
Social and Family History repository - data access layer.
"""

from __future__ import annotations

from typing import Any

from resources.core import InMemoryRepository
from .model import SocialFamilyHistory


class SocialFamilyHistoryRepository(InMemoryRepository[SocialFamilyHistory]):
    """
    Repository for SocialFamilyHistory resources.
    Currently uses in-memory storage with mock data.
    """

    def __init__(self):
        super().__init__()
        # Data will be seeded by the data_seeder

    async def list(self, **filters: Any) -> list[SocialFamilyHistory]:
        """
        List social/family histories with optional filters.

        Supported filters:
        - patient_id: str - Filter by patient ID
        """
        results = list(self._store.values())

        if "patient_id" in filters:
            patient_ref = f"Patient/{filters['patient_id']}"
            results = [r for r in results if r.subject.reference == patient_ref]

        return results

    async def get_by_patient(self, patient_id: str) -> SocialFamilyHistory | None:
        """
        Get the social/family history for a specific patient.

        Args:
            patient_id: The patient ID

        Returns:
            SocialFamilyHistory or None if not found
        """
        results = await self.list(patient_id=patient_id)
        return results[0] if results else None
