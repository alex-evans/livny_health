"""
PostgreSQL repository for EncounterStatusHistory resources.
"""

from typing import Any

from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from resources.core.postgres_repository import PostgresRepository
from resources.encounter_status_history.model import EncounterStatusHistory
from db.models.encounter_status_history import EncounterStatusHistoryORM
from mappers.encounter_status_history import EncounterStatusHistoryMapper


class PostgresEncounterStatusHistoryRepository(
    PostgresRepository[EncounterStatusHistory, EncounterStatusHistoryORM]
):
    """PostgreSQL repository for EncounterStatusHistory resources."""

    orm_class = EncounterStatusHistoryORM
    mapper = EncounterStatusHistoryMapper()

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)

    def _apply_filters(self, stmt, **filters: Any):
        """Apply EncounterStatusHistory-specific filters."""
        if filters.get("encounter_id"):
            stmt = stmt.where(
                EncounterStatusHistoryORM.encounter_id == filters["encounter_id"]
            )
        # Order by changed_at descending by default
        stmt = stmt.order_by(desc(EncounterStatusHistoryORM.changed_at))
        return stmt

    async def get_by_encounter(
        self, encounter_id: str
    ) -> list[EncounterStatusHistory]:
        """Get all status history entries for an encounter, sorted by time descending."""
        return await self.list(encounter_id=encounter_id)
