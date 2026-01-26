"""
PostgreSQL repository for SocialFamilyHistory resources.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from resources.core.postgres_repository import PostgresRepository
from resources.social_family_history.model import SocialFamilyHistory
from db.models.social_family_history import SocialFamilyHistoryORM
from mappers.social_family_history import SocialFamilyHistoryMapper


class PostgresSocialFamilyHistoryRepository(
    PostgresRepository[SocialFamilyHistory, SocialFamilyHistoryORM]
):
    """PostgreSQL repository for SocialFamilyHistory resources."""

    orm_class = SocialFamilyHistoryORM
    mapper = SocialFamilyHistoryMapper()

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)

    def _apply_filters(self, stmt, **filters: Any):
        """Apply SocialFamilyHistory-specific filters."""
        if filters.get("patient_id"):
            stmt = stmt.where(
                SocialFamilyHistoryORM.subject_id == filters["patient_id"]
            )
        return stmt

    async def get_by_patient(self, patient_id: str) -> SocialFamilyHistory | None:
        """Get social/family history for a specific patient."""
        async with self._session_factory() as session:
            stmt = select(SocialFamilyHistoryORM).where(
                SocialFamilyHistoryORM.subject_id == patient_id
            )
            result = await session.execute(stmt)
            orm_model = result.scalar_one_or_none()
            if orm_model is None:
                return None
            return self.mapper.to_domain(orm_model)
