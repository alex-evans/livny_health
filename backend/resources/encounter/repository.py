"""
Encounter repository - data access layer.
"""

from __future__ import annotations

from typing import Any
from datetime import datetime, date
from resources.core import InMemoryRepository
from .model import Encounter, EncounterStatus


class EncounterRepository(InMemoryRepository[Encounter]):
    """
    Repository for Encounter resources.
    Currently uses in-memory storage, can be swapped for database later.
    """

    async def list(self, **filters: Any) -> list[Encounter]:
        """
        List encounters with optional filters.

        Supported filters:
        - patient_id: str - Filter by patient ID
        - status: str | list[str] - Filter by status(es)
        - provider_id: str - Filter by provider ID
        - date: date - Filter by date (encounters that occurred on this date)
        - appointment_id: str - Filter by appointment ID
        """
        results = list(self._store.values())

        if "patient_id" in filters:
            patient_ref = f"Patient/{filters['patient_id']}"
            results = [e for e in results if e.subject.reference == patient_ref]

        if "status" in filters:
            status_filter = filters["status"]
            if isinstance(status_filter, str):
                status_filter = [status_filter]
            results = [e for e in results if e.status.value in status_filter]

        if "provider_id" in filters:
            provider_ref = f"Practitioner/{filters['provider_id']}"
            results = [
                e for e in results
                if any(p.individual.reference == provider_ref for p in e.participants)
            ]

        if "date" in filters:
            filter_date = filters["date"]
            if isinstance(filter_date, str):
                filter_date = date.fromisoformat(filter_date)
            results = [
                e for e in results
                if e.period and e.period.start.date() == filter_date
            ]

        if "appointment_id" in filters:
            appt_ref = f"Appointment/{filters['appointment_id']}"
            results = [e for e in results if e.appointment and e.appointment.reference == appt_ref]

        return results

    async def get_active_for_patient(self, patient_id: str) -> Encounter | None:
        """Get the current active encounter for a patient."""
        results = await self.list(
            patient_id=patient_id,
            status=[EncounterStatus.IN_PROGRESS.value, EncounterStatus.ARRIVED.value],
        )
        return results[0] if results else None

    async def get_by_patient(self, patient_id: str) -> list[Encounter]:
        """Get all encounters for a patient."""
        return await self.list(patient_id=patient_id)

    async def get_by_appointment(self, appointment_id: str) -> Encounter | None:
        """Get encounter linked to an appointment."""
        results = await self.list(appointment_id=appointment_id)
        return results[0] if results else None
