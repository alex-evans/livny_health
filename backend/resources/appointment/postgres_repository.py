"""
PostgreSQL repository for Appointment resources.
"""

from typing import Any
from datetime import datetime, date

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from resources.core.postgres_repository import PostgresRepository
from resources.appointment.model import Appointment
from db.models.appointment import AppointmentORM
from mappers.appointment import AppointmentMapper


class PostgresAppointmentRepository(PostgresRepository[Appointment, AppointmentORM]):
    """PostgreSQL repository for Appointment resources."""

    orm_class = AppointmentORM
    mapper = AppointmentMapper()

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)

    def _apply_filters(self, stmt, **filters: Any):
        """Apply Appointment-specific filters."""
        if filters.get("status"):
            stmt = stmt.where(AppointmentORM.status == filters["status"])
        if filters.get("date"):
            # Filter by date (appointments on a specific day)
            target_date = filters["date"]
            if isinstance(target_date, str):
                target_date = datetime.fromisoformat(target_date).date()
            stmt = stmt.where(
                and_(
                    AppointmentORM.start >= datetime.combine(
                        target_date, datetime.min.time()
                    ),
                    AppointmentORM.start < datetime.combine(
                        target_date, datetime.max.time()
                    ),
                )
            )
        if filters.get("start_after"):
            stmt = stmt.where(AppointmentORM.start >= filters["start_after"])
        if filters.get("start_before"):
            stmt = stmt.where(AppointmentORM.start < filters["start_before"])
        return stmt.order_by(AppointmentORM.start)

    async def get_by_patient(self, patient_id: str) -> list[Appointment]:
        """Get all appointments for a patient."""
        all_appointments = await self.list()
        return [a for a in all_appointments if a.patient_id == patient_id]

    async def get_upcoming_for_patient(self, patient_id: str) -> list[Appointment]:
        """Get upcoming appointments for a patient."""
        now = datetime.now()
        appointments = await self.get_by_patient(patient_id)
        return [a for a in appointments if a.start > now]

    async def get_for_date(
        self, schedule_date: date, provider_id: str
    ) -> list[Appointment]:
        """Get appointments for a specific date and provider."""
        # Get all appointments for the date
        appointments = await self.list(date=schedule_date)

        # Filter by provider (check participants for practitioner with matching ID)
        result = []
        for appt in appointments:
            for participant in appt.participants:
                if participant.actor:
                    ref = participant.actor.reference or ""
                    # Check if this is the matching practitioner
                    # Reference format is "Practitioner/{id}"
                    if ref == f"Practitioner/{provider_id}":
                        result.append(appt)
                        break
        return result
