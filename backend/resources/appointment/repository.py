"""
Appointment repository - data access layer.
"""

from __future__ import annotations

from typing import Any
from datetime import date, datetime
from resources.core import InMemoryRepository
from .model import Appointment, AppointmentStatus


class AppointmentRepository(InMemoryRepository[Appointment]):
    """
    Repository for Appointment resources.
    Currently uses in-memory storage, can be swapped for database later.
    """

    async def list(self, **filters: Any) -> list[Appointment]:
        """
        List appointments with optional filters.

        Supported filters:
        - patient_id: str - Filter by patient ID
        - provider_id: str - Filter by provider ID
        - date: date | str - Filter by date
        - status: str | list[str] - Filter by status(es)
        """
        results = list(self._store.values())

        if "patient_id" in filters:
            patient_id = filters["patient_id"]
            results = [a for a in results if a.patient_id == patient_id]

        if "provider_id" in filters:
            provider_id = filters["provider_id"]
            results = [
                a for a in results
                if a.provider and a.provider.id == provider_id
            ]

        if "date" in filters:
            filter_date = filters["date"]
            if isinstance(filter_date, str):
                filter_date = date.fromisoformat(filter_date)
            results = [a for a in results if a.start.date() == filter_date]

        if "status" in filters:
            status_filter = filters["status"]
            if isinstance(status_filter, str):
                status_filter = [status_filter]
            results = [a for a in results if a.status.value in status_filter]

        # Sort by start time
        results.sort(key=lambda a: a.start)

        return results

    async def get_for_date(self, date_val: date | str, provider_id: str | None = None) -> list[Appointment]:
        """Get all appointments for a specific date."""
        filters = {"date": date_val}
        if provider_id:
            filters["provider_id"] = provider_id
        return await self.list(**filters)

    async def get_by_patient(self, patient_id: str) -> list[Appointment]:
        """Get all appointments for a patient."""
        return await self.list(patient_id=patient_id)

    async def get_upcoming_for_patient(self, patient_id: str) -> list[Appointment]:
        """Get upcoming appointments for a patient."""
        now = datetime.now()
        appointments = await self.list(patient_id=patient_id)
        return [a for a in appointments if a.start > now]
