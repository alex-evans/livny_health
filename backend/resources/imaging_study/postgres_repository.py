"""
PostgreSQL repository for ImagingStudy resources.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from resources.core.postgres_repository import PostgresRepository
from resources.imaging_study.model import ImagingStudy, ImagingModality
from db.models.imaging_study import ImagingStudyORM
from mappers.imaging_study import ImagingStudyMapper


class PostgresImagingStudyRepository(PostgresRepository[ImagingStudy, ImagingStudyORM]):
    """PostgreSQL repository for ImagingStudy resources."""

    orm_class = ImagingStudyORM
    mapper = ImagingStudyMapper()

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)

    def _apply_filters(self, stmt, **filters: Any):
        """Apply ImagingStudy-specific filters."""
        if filters.get("patient_id"):
            stmt = stmt.where(ImagingStudyORM.patient_id == filters["patient_id"])
        if filters.get("modality"):
            stmt = stmt.where(ImagingStudyORM.modality == filters["modality"])
        if filters.get("report_status"):
            stmt = stmt.where(ImagingStudyORM.report_status == filters["report_status"])
        if filters.get("body_part"):
            stmt = stmt.where(ImagingStudyORM.body_part == filters["body_part"])
        return stmt.order_by(ImagingStudyORM.study_date.desc())

    async def get_by_patient(self, patient_id: str) -> list[ImagingStudy]:
        """Get all imaging studies for a patient."""
        return await self.list(patient_id=patient_id)

    async def get_by_patient_and_modality(
        self, patient_id: str, modality: ImagingModality
    ) -> list[ImagingStudy]:
        """Get imaging studies for a patient filtered by modality."""
        return await self.list(patient_id=patient_id, modality=modality)
