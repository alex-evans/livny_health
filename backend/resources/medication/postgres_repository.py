"""
PostgreSQL repository for Medication resources.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from resources.core.postgres_repository import PostgresRepository
from resources.medication.model import Medication
from db.models.medication import MedicationORM
from mappers.medication import MedicationMapper


class PostgresMedicationRepository(PostgresRepository[Medication, MedicationORM]):
    """PostgreSQL repository for Medication resources."""

    orm_class = MedicationORM
    mapper = MedicationMapper()

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)

    def _apply_filters(self, stmt, **filters: Any):
        """Apply Medication-specific filters."""
        if filters.get("status"):
            stmt = stmt.where(MedicationORM.status == filters["status"])
        if filters.get("is_controlled") is not None:
            stmt = stmt.where(MedicationORM.is_controlled == filters["is_controlled"])
        return stmt

    async def search(self, query: str, limit: int = 20) -> list[Medication]:
        """Search medications by name (in code.display)."""
        async with self._session_factory() as session:
            # Search in JSONB code.display field
            stmt = (
                select(MedicationORM)
                .where(
                    MedicationORM.code["display"]
                    .astext.ilike(f"%{query}%")
                )
                .limit(limit)
            )
            result = await session.execute(stmt)
            orm_models = result.scalars().all()
            return [self.mapper.to_domain(orm) for orm in orm_models]
