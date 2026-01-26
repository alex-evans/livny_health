"""
PostgreSQL repository for LabResult resources.
"""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from resources.core.postgres_repository import PostgresRepository
from resources.lab_result.model import LabResult, LabResultHistory
from db.models.lab_result import LabResultORM
from mappers.lab_result import LabResultMapper


class PostgresLabResultRepository(PostgresRepository[LabResult, LabResultORM]):
    """PostgreSQL repository for LabResult resources."""

    orm_class = LabResultORM
    mapper = LabResultMapper()

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)

    def _apply_filters(self, stmt, **filters: Any):
        """Apply LabResult-specific filters."""
        if filters.get("patient_id"):
            stmt = stmt.where(LabResultORM.subject_id == filters["patient_id"])
        if filters.get("test_name"):
            stmt = stmt.where(LabResultORM.test_name == filters["test_name"])
        if filters.get("status"):
            stmt = stmt.where(LabResultORM.status == filters["status"])
        if filters.get("panel_id"):
            stmt = stmt.where(LabResultORM.panel_id == filters["panel_id"])
        if filters.get("acknowledged") is not None:
            stmt = stmt.where(LabResultORM.acknowledged == filters["acknowledged"])
        if filters.get("days_back"):
            cutoff = datetime.now() - timedelta(days=filters["days_back"])
            stmt = stmt.where(LabResultORM.collection_date >= cutoff)
        return stmt.order_by(LabResultORM.collection_date.desc())

    async def get_history(
        self,
        patient_id: str,
        test_name: str,
        limit: int = 10,
        days_back: int | None = None,
    ) -> list[LabResultHistory]:
        """
        Get historical results for a specific test.

        Args:
            patient_id: The patient ID
            test_name: The test name to look up
            limit: Maximum number of results to return
            days_back: Optional limit to results within N days

        Returns:
            List of LabResultHistory entries, sorted by date (most recent first)
        """
        filters: dict[str, Any] = {
            "patient_id": patient_id,
            "test_name": test_name,
        }
        if days_back is not None:
            filters["days_back"] = days_back

        results = await self.list(**filters)

        # Sort by collection date (most recent first)
        results.sort(key=lambda r: r.collection_date, reverse=True)

        # Limit results
        results = results[:limit]

        # Convert to history entries
        return [r.to_history_entry() for r in results]

    async def get_by_patient(self, patient_id: str) -> list[LabResult]:
        """Get all lab results for a patient."""
        return await self.list(patient_id=patient_id)

    async def get_available_tests(self, patient_id: str) -> list[str]:
        """Get list of unique test names for a patient."""
        results = await self.get_by_patient(patient_id)
        return list(set(r.test_name for r in results))
