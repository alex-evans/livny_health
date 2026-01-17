"""
MedicationRequest repository - data access layer.
"""

from __future__ import annotations

from typing import Any
from resources.core import InMemoryRepository
from .model import MedicationRequest, MedicationRequestStatus


class MedicationRequestRepository(InMemoryRepository[MedicationRequest]):
    """
    Repository for MedicationRequest resources.
    Currently uses in-memory storage, can be swapped for database later.
    """

    async def list(self, **filters: Any) -> list[MedicationRequest]:
        """
        List medication requests with optional filters.

        Supported filters:
        - patient_id: str - Filter by patient ID
        - status: str | list[str] - Filter by status(es)
        - requester_id: str - Filter by prescriber ID
        - encounter_id: str - Filter by encounter ID
        """
        results = list(self._store.values())

        if "patient_id" in filters:
            patient_ref = f"Patient/{filters['patient_id']}"
            results = [r for r in results if r.subject.reference == patient_ref]

        if "status" in filters:
            status_filter = filters["status"]
            if isinstance(status_filter, str):
                status_filter = [status_filter]
            results = [r for r in results if r.status.value in status_filter]

        if "requester_id" in filters:
            requester_ref = f"Practitioner/{filters['requester_id']}"
            results = [r for r in results if r.requester and r.requester.reference == requester_ref]

        if "encounter_id" in filters:
            encounter_ref = f"Encounter/{filters['encounter_id']}"
            results = [r for r in results if r.encounter and r.encounter.reference == encounter_ref]

        return results

    async def get_active_for_patient(self, patient_id: str) -> list[MedicationRequest]:
        """Get all active medication requests for a patient, sorted by start date (most recent first)."""
        results = await self.list(
            patient_id=patient_id,
            status=[MedicationRequestStatus.ACTIVE.value, MedicationRequestStatus.ON_HOLD.value],
        )
        return sorted(results, key=lambda m: m.authored_on, reverse=True)

    async def get_by_patient(self, patient_id: str) -> list[MedicationRequest]:
        """Get all medication requests for a patient (any status)."""
        return await self.list(patient_id=patient_id)

    async def discontinue(self, medication_id: str, reason: str | None = None) -> MedicationRequest | None:
        """
        Discontinue a medication by changing its status to STOPPED.

        Args:
            medication_id: The ID of the medication to discontinue
            reason: Optional reason for discontinuing

        Returns:
            The updated MedicationRequest or None if not found
        """
        medication = await self.get(medication_id)
        if not medication:
            return None

        # Update the status
        medication.status = MedicationRequestStatus.STOPPED
        if reason:
            medication.status_reason = reason

        # Save the update
        await self.update(medication_id, medication)
        return medication
