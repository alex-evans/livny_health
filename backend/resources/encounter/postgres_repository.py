"""
PostgreSQL repository for Encounter resources.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from resources.core.postgres_repository import PostgresRepository
from resources.encounter.model import Encounter, EncounterStatus
from db.models.encounter import EncounterORM
from mappers.encounter import EncounterMapper


class PostgresEncounterRepository(PostgresRepository[Encounter, EncounterORM]):
    """PostgreSQL repository for Encounter resources."""

    orm_class = EncounterORM
    mapper = EncounterMapper()

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)

    def _apply_filters(self, stmt, **filters: Any):
        """Apply Encounter-specific filters."""
        if filters.get("patient_id"):
            stmt = stmt.where(EncounterORM.subject_id == filters["patient_id"])
        if filters.get("status"):
            status = filters["status"]
            if isinstance(status, list):
                stmt = stmt.where(EncounterORM.status.in_(status))
            else:
                stmt = stmt.where(EncounterORM.status == status)
        if filters.get("encounter_class"):
            stmt = stmt.where(
                EncounterORM.encounter_class == filters["encounter_class"]
            )
        if filters.get("appointment_id"):
            stmt = stmt.where(EncounterORM.appointment_id == filters["appointment_id"])
        return stmt

    async def get_active_for_patient(self, patient_id: str) -> Encounter | None:
        """Get the current active encounter for a patient."""
        results = await self.list(
            patient_id=patient_id,
            status=[EncounterStatus.IN_PROGRESS.value],
        )
        return results[0] if results else None

    async def get_by_patient(self, patient_id: str) -> list[Encounter]:
        """Get all encounters for a patient."""
        return await self.list(patient_id=patient_id)

    async def get_by_appointment(self, appointment_id: str) -> Encounter | None:
        """Get encounter linked to an appointment."""
        results = await self.list(appointment_id=appointment_id)
        return results[0] if results else None
