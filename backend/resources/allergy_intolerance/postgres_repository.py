"""
PostgreSQL repository for AllergyIntolerance resources.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from resources.core.postgres_repository import PostgresRepository
from resources.allergy_intolerance.model import AllergyIntolerance
from db.models.allergy_intolerance import AllergyIntoleranceORM
from mappers.allergy_intolerance import AllergyIntoleranceMapper


class PostgresAllergyIntoleranceRepository(
    PostgresRepository[AllergyIntolerance, AllergyIntoleranceORM]
):
    """PostgreSQL repository for AllergyIntolerance resources."""

    orm_class = AllergyIntoleranceORM
    mapper = AllergyIntoleranceMapper()

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)

    def _apply_filters(self, stmt, **filters: Any):
        """Apply AllergyIntolerance-specific filters."""
        if filters.get("patient_id"):
            stmt = stmt.where(
                AllergyIntoleranceORM.patient_id == filters["patient_id"]
            )
        if filters.get("clinical_status"):
            stmt = stmt.where(
                AllergyIntoleranceORM.clinical_status == filters["clinical_status"]
            )
        if filters.get("category"):
            stmt = stmt.where(AllergyIntoleranceORM.category == filters["category"])
        if filters.get("criticality"):
            stmt = stmt.where(
                AllergyIntoleranceORM.criticality == filters["criticality"]
            )
        return stmt

    async def get_by_patient(
        self, patient_id: str, include_inactive: bool = False
    ) -> list[AllergyIntolerance]:
        """
        Get allergies for a patient.

        Args:
            patient_id: The patient ID
            include_inactive: If True, returns all allergies including inactive/resolved.
                             If False (default), returns only active allergies.
        """
        if include_inactive:
            return await self.list(patient_id=patient_id)
        return await self.list(patient_id=patient_id, clinical_status="active")

    async def get_all_by_patient(self, patient_id: str) -> list[AllergyIntolerance]:
        """Get all allergies for a patient including inactive and resolved."""
        return await self.list(patient_id=patient_id)
