"""
PostgreSQL repository for MedicationRequest resources.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from resources.core.postgres_repository import PostgresRepository
from resources.medication_request.model import MedicationRequest, MedicationRequestStatus
from db.models.medication_request import MedicationRequestORM
from mappers.medication_request import MedicationRequestMapper


class PostgresMedicationRequestRepository(
    PostgresRepository[MedicationRequest, MedicationRequestORM]
):
    """PostgreSQL repository for MedicationRequest resources."""

    orm_class = MedicationRequestORM
    mapper = MedicationRequestMapper()

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)

    def _apply_filters(self, stmt, **filters: Any):
        """Apply MedicationRequest-specific filters."""
        if filters.get("patient_id"):
            stmt = stmt.where(
                MedicationRequestORM.subject_id == filters["patient_id"]
            )
        if filters.get("status"):
            status = filters["status"]
            if isinstance(status, list):
                stmt = stmt.where(MedicationRequestORM.status.in_(status))
            else:
                stmt = stmt.where(MedicationRequestORM.status == status)
        if filters.get("is_controlled") is not None:
            stmt = stmt.where(
                MedicationRequestORM.is_controlled == filters["is_controlled"]
            )
        return stmt.order_by(MedicationRequestORM.authored_on.desc())

    async def get_active_for_patient(self, patient_id: str) -> list[MedicationRequest]:
        """Get all active medication requests for a patient, sorted by start date (most recent first)."""
        results = await self.list(
            patient_id=patient_id,
            status=[MedicationRequestStatus.ACTIVE.value, MedicationRequestStatus.ON_HOLD.value],
        )
        return sorted(results, key=lambda m: m.authored_on, reverse=True)

    async def get_by_patient(self, patient_id: str) -> list[MedicationRequest]:
        """Get all medication requests for a patient (any status)."""
        return await self.list(patient_id=patient_id)

    async def discontinue(self, medication_id: str, reason: str | None = None) -> MedicationRequest | None:
        """
        Discontinue a medication by changing its status to STOPPED.

        Args:
            medication_id: The ID of the medication to discontinue
            reason: Optional reason for discontinuing

        Returns:
            The updated MedicationRequest or None if not found
        """
        medication = await self.get(medication_id)
        if not medication:
            return None

        # Update the status
        medication.status = MedicationRequestStatus.STOPPED
        if reason:
            medication.status_reason = reason

        # Save the update
        await self.update(medication_id, medication)
        return medication
