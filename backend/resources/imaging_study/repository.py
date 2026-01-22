"""
Imaging Study repository - data access layer.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from resources.core import InMemoryRepository
from .model import ImagingStudy, ImagingModality


class ImagingStudyRepository(InMemoryRepository[ImagingStudy]):
    """
    Repository for ImagingStudy resources.
    Currently uses in-memory storage with mock data.
    """

    def __init__(self):
        super().__init__()

    async def list(self, **filters: Any) -> list[ImagingStudy]:
        """
        List imaging studies with optional filters.

        Supported filters:
        - patient_id: str - Filter by patient ID
        - modality: str - Filter by modality
        - days_back: int - Filter to studies within N days
        """
        results = list(self._store.values())

        if "patient_id" in filters:
            results = [s for s in results if s.patient_id == filters["patient_id"]]

        if "modality" in filters:
            modality_filter = filters["modality"].upper()
            results = [s for s in results if s.modality == modality_filter]

        if "days_back" in filters:
            cutoff = datetime.now() - timedelta(days=filters["days_back"])
            results = [s for s in results if s.study_date >= cutoff]

        return results

    async def get_by_patient(self, patient_id: str) -> list[ImagingStudy]:
        """Get all imaging studies for a patient."""
        return await self.list(patient_id=patient_id)

    async def get_by_patient_and_modality(
        self, patient_id: str, modality: ImagingModality
    ) -> list[ImagingStudy]:
        """Get imaging studies for a patient filtered by modality."""
        return await self.list(patient_id=patient_id, modality=modality)
