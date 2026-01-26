"""
PostgreSQL repository for Patient resources.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from resources.core.postgres_repository import PostgresRepository
from resources.core import Reference
from resources.patient.model import Patient, AllergyReviewStatus
from db.models.patient import PatientORM
from mappers.patient import PatientMapper


class PostgresPatientRepository(PostgresRepository[Patient, PatientORM]):
    """PostgreSQL repository for Patient resources."""

    orm_class = PatientORM
    mapper = PatientMapper()

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)

    def _apply_filters(self, stmt, **filters: Any):
        """Apply Patient-specific filters."""
        if filters.get("active") is not None:
            stmt = stmt.where(PatientORM.active == filters["active"])
        if filters.get("name"):
            # Case-insensitive partial match on family name
            name_filter = f"%{filters['name']}%"
            stmt = stmt.where(PatientORM.name_family.ilike(name_filter))
        if filters.get("gender"):
            stmt = stmt.where(PatientORM.gender == filters["gender"])
        return stmt

    async def get_by_mrn(self, mrn: str) -> Patient | None:
        """Get a patient by their MRN identifier."""
        async with self._session_factory() as session:
            # Search in JSONB identifiers array
            stmt = select(PatientORM).where(
                PatientORM.identifiers.contains([{"value": mrn}])
            )
            result = await session.execute(stmt)
            orm_model = result.scalar_one_or_none()
            if orm_model is None:
                return None
            return self.mapper.to_domain(orm_model)

    async def mark_allergies_reviewed(
        self,
        patient_id: str,
        reviewer_id: str | None = None,
        reviewer_name: str | None = None,
    ) -> Patient | None:
        """
        Mark a patient's allergy history as reviewed.

        Args:
            patient_id: The patient ID
            reviewer_id: Optional practitioner ID who reviewed
            reviewer_name: Optional practitioner name for display

        Returns:
            Updated Patient or None if not found
        """
        patient = await self.get(patient_id)
        if not patient:
            return None

        reviewer_ref = None
        if reviewer_id:
            reviewer_ref = Reference.to("Practitioner", reviewer_id, reviewer_name)

        patient.allergy_review_status = AllergyReviewStatus(
            reviewed_at=datetime.now(),
            reviewed_by=reviewer_ref,
        )

        await self.update(patient_id, patient)
        return patient
