"""
Vital Signs repository - data access layer.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from resources.core import InMemoryRepository
from .model import VitalSign, VitalSignHistory, VitalType


class VitalSignRepository(InMemoryRepository[VitalSign]):
    """
    Repository for VitalSign resources.
    Currently uses in-memory storage with mock data.
    """

    def __init__(self):
        super().__init__()
        # Data will be seeded by the data_seeder

    async def list(self, **filters: Any) -> list[VitalSign]:
        """
        List vital signs with optional filters.

        Supported filters:
        - patient_id: str - Filter by patient ID
        - vital_type: VitalType - Filter by vital type
        - status: str | list[str] - Filter by status(es)
        - days_back: int - Filter to results within N days
        """
        results = list(self._store.values())

        if "patient_id" in filters:
            patient_ref = f"Patient/{filters['patient_id']}"
            results = [r for r in results if r.subject.reference == patient_ref]

        if "vital_type" in filters:
            vital_type = filters["vital_type"]
            results = [r for r in results if r.vital_type == vital_type]

        if "status" in filters:
            status_filter = filters["status"]
            if isinstance(status_filter, str):
                status_filter = [status_filter]
            results = [r for r in results if r.status in status_filter]

        if "days_back" in filters:
            cutoff = datetime.now() - timedelta(days=filters["days_back"])
            results = [r for r in results if r.recorded_at >= cutoff]

        return results

    async def get_history(
        self,
        patient_id: str,
        vital_type: VitalType,
        limit: int = 20,
        days_back: int | None = None,
    ) -> list[VitalSignHistory]:
        """
        Get historical results for a specific vital type.

        Args:
            patient_id: The patient ID
            vital_type: The vital type to look up
            limit: Maximum number of results to return
            days_back: Optional limit to results within N days

        Returns:
            List of VitalSignHistory entries, sorted by date (most recent first)
        """
        filters: dict[str, Any] = {
            "patient_id": patient_id,
            "vital_type": vital_type,
        }
        if days_back is not None:
            filters["days_back"] = days_back

        results = await self.list(**filters)

        # Sort by recorded_at (most recent first)
        results.sort(key=lambda r: r.recorded_at, reverse=True)

        # Limit results
        results = results[:limit]

        # Convert to history entries
        return [r.to_history_entry() for r in results]

    async def get_current_vitals(self, patient_id: str) -> dict[VitalType, VitalSign]:
        """
        Get the most recent vital sign for each type.

        Args:
            patient_id: The patient ID

        Returns:
            Dictionary mapping vital type to most recent VitalSign
        """
        results = await self.list(patient_id=patient_id)

        # Group by vital type and get most recent for each
        current: dict[VitalType, VitalSign] = {}
        for vital in results:
            existing = current.get(vital.vital_type)
            if existing is None or vital.recorded_at > existing.recorded_at:
                current[vital.vital_type] = vital

        return current

    async def get_by_patient(self, patient_id: str) -> list[VitalSign]:
        """Get all vital signs for a patient."""
        return await self.list(patient_id=patient_id)

    async def get_available_vital_types(self, patient_id: str) -> list[VitalType]:
        """Get list of unique vital types for a patient."""
        results = await self.get_by_patient(patient_id)
        return list(set(r.vital_type for r in results))
