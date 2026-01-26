"""
PostgreSQL repository for Practitioner resources.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from resources.core.postgres_repository import PostgresRepository
from resources.practitioner.model import Practitioner
from db.models.practitioner import PractitionerORM
from mappers.practitioner import PractitionerMapper


class PostgresPractitionerRepository(PostgresRepository[Practitioner, PractitionerORM]):
    """PostgreSQL repository for Practitioner resources."""

    orm_class = PractitionerORM
    mapper = PractitionerMapper()

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)

    def _apply_filters(self, stmt, **filters: Any):
        """Apply Practitioner-specific filters."""
        if filters.get("active") is not None:
            stmt = stmt.where(PractitionerORM.active == filters["active"])
        if filters.get("name"):
            name_filter = f"%{filters['name']}%"
            stmt = stmt.where(PractitionerORM.name_family.ilike(name_filter))
        return stmt
