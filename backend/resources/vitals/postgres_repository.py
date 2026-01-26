"""
PostgreSQL repository for VitalSign resources.
"""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from resources.core.postgres_repository import PostgresRepository
from resources.vitals.model import VitalSign, VitalSignHistory, VitalType
from db.models.vital_sign import VitalSignORM
from mappers.vital_sign import VitalSignMapper


class PostgresVitalSignRepository(PostgresRepository[VitalSign, VitalSignORM]):
    """PostgreSQL repository for VitalSign resources."""

    orm_class = VitalSignORM
    mapper = VitalSignMapper()

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)

    def _apply_filters(self, stmt, **filters: Any):
        """Apply VitalSign-specific filters."""
        if filters.get("patient_id"):
            stmt = stmt.where(VitalSignORM.subject_id == filters["patient_id"])
        if filters.get("vital_type"):
            stmt = stmt.where(VitalSignORM.vital_type == filters["vital_type"])
        if filters.get("status"):
            stmt = stmt.where(VitalSignORM.status == filters["status"])
        if filters.get("days_back"):
            cutoff = datetime.now() - timedelta(days=filters["days_back"])
            stmt = stmt.where(VitalSignORM.recorded_at >= cutoff)
        return stmt.order_by(VitalSignORM.recorded_at.desc())

    async def get_current_vitals(self, patient_id: str) -> dict[VitalType, VitalSign]:
        """
        Get the most recent vital sign for each type.

        Args:
            patient_id: The patient ID

        Returns:
            Dictionary mapping vital type to most recent VitalSign
        """
        results = await self.list(patient_id=patient_id)

        # Group by vital type and get most recent for each
        current: dict[VitalType, VitalSign] = {}
        for vital in results:
            existing = current.get(vital.vital_type)
            if existing is None or vital.recorded_at > existing.recorded_at:
                current[vital.vital_type] = vital

        return current

    async def get_history(
        self,
        patient_id: str,
        vital_type: VitalType,
        limit: int = 20,
        days_back: int | None = None,
    ) -> list[VitalSignHistory]:
        """
        Get historical results for a specific vital type.

        Args:
            patient_id: The patient ID
            vital_type: The vital type to look up
            limit: Maximum number of results to return
            days_back: Optional limit to results within N days

        Returns:
            List of VitalSignHistory entries, sorted by date (most recent first)
        """
        filters: dict[str, Any] = {
            "patient_id": patient_id,
            "vital_type": vital_type,
        }
        if days_back is not None:
            filters["days_back"] = days_back

        results = await self.list(**filters)

        # Sort by recorded_at (most recent first)
        results.sort(key=lambda r: r.recorded_at, reverse=True)

        # Limit results
        results = results[:limit]

        # Convert to history entries
        return [r.to_history_entry() for r in results]

    async def get_by_patient(self, patient_id: str) -> list[VitalSign]:
        """Get all vital signs for a patient."""
        return await self.list(patient_id=patient_id)

    async def get_available_vital_types(self, patient_id: str) -> list[VitalType]:
        """Get list of unique vital types for a patient."""
        results = await self.get_by_patient(patient_id)
        return list(set(r.vital_type for r in results))
