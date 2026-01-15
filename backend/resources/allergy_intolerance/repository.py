"""
AllergyIntolerance repository - data access layer.
"""

from __future__ import annotations

from typing import Any
from resources.core import InMemoryRepository
from .model import AllergyIntolerance


class AllergyIntoleranceRepository(InMemoryRepository[AllergyIntolerance]):
    """
    Repository for AllergyIntolerance resources.
    Currently uses in-memory storage, can be swapped for database later.
    """

    async def list(self, **filters: Any) -> list[AllergyIntolerance]:
        """
        List allergies with optional filters.

        Supported filters:
        - patient_id: str - Filter by patient ID
        - clinical_status: str - Filter by clinical status (active, inactive, resolved)
        - category: str - Filter by category (medication, food, etc.)
        """
        results = list(self._store.values())

        if "patient_id" in filters:
            patient_ref = f"Patient/{filters['patient_id']}"
            results = [a for a in results if a.patient.reference == patient_ref]

        if "clinical_status" in filters:
            results = [a for a in results if a.clinical_status == filters["clinical_status"]]

        if "category" in filters:
            results = [a for a in results if a.category.value == filters["category"]]

        return results

    async def get_by_patient(self, patient_id: str) -> list[AllergyIntolerance]:
        """Get all allergies for a patient."""
        return await self.list(patient_id=patient_id, clinical_status="active")
