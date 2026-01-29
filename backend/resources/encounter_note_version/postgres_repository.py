"""
PostgreSQL repository for EncounterNoteVersion resources.
"""

from typing import Any

from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from resources.core.postgres_repository import PostgresRepository
from resources.encounter_note_version.model import EncounterNoteVersion
from db.models.encounter_note_version import EncounterNoteVersionORM
from mappers.encounter_note_version import EncounterNoteVersionMapper


class PostgresEncounterNoteVersionRepository(
    PostgresRepository[EncounterNoteVersion, EncounterNoteVersionORM]
):
    """PostgreSQL repository for EncounterNoteVersion resources."""

    orm_class = EncounterNoteVersionORM
    mapper = EncounterNoteVersionMapper()

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)

    def _apply_filters(self, stmt, **filters: Any):
        """Apply EncounterNoteVersion-specific filters."""
        if filters.get("encounter_id"):
            stmt = stmt.where(
                EncounterNoteVersionORM.encounter_id == filters["encounter_id"]
            )
        # Order by version descending by default
        stmt = stmt.order_by(desc(EncounterNoteVersionORM.version))
        return stmt

    async def get_by_encounter(
        self, encounter_id: str
    ) -> list[EncounterNoteVersion]:
        """Get all versions for an encounter, sorted by version descending."""
        return await self.list(encounter_id=encounter_id)

    async def get_latest_version(
        self, encounter_id: str
    ) -> EncounterNoteVersion | None:
        """Get the latest version for an encounter."""
        versions = await self.get_by_encounter(encounter_id)
        return versions[0] if versions else None

    async def get_version(
        self, encounter_id: str, version: int
    ) -> EncounterNoteVersion | None:
        """Get a specific version for an encounter."""
        versions = await self.list(encounter_id=encounter_id)
        for v in versions:
            if v.version == version:
                return v
        return None
