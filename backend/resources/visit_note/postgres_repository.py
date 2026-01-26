"""
PostgreSQL repository for VisitNote resources.
"""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from resources.core.postgres_repository import PostgresRepository
from resources.visit_note.model import VisitNote
from db.models.visit_note import VisitNoteORM
from mappers.visit_note import VisitNoteMapper


class PostgresVisitNoteRepository(PostgresRepository[VisitNote, VisitNoteORM]):
    """PostgreSQL repository for VisitNote resources."""

    orm_class = VisitNoteORM
    mapper = VisitNoteMapper()

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)

    def _apply_filters(self, stmt, **filters: Any):
        """Apply VisitNote-specific filters."""
        if filters.get("patient_id"):
            stmt = stmt.where(VisitNoteORM.subject_id == filters["patient_id"])
        if filters.get("encounter_id"):
            stmt = stmt.where(VisitNoteORM.encounter_id == filters["encounter_id"])
        if filters.get("visit_type"):
            stmt = stmt.where(VisitNoteORM.visit_type == filters["visit_type"])
        if filters.get("status"):
            stmt = stmt.where(VisitNoteORM.status == filters["status"])
        if filters.get("has_critical_findings") is not None:
            stmt = stmt.where(
                VisitNoteORM.has_critical_findings == filters["has_critical_findings"]
            )
        if filters.get("days_back"):
            cutoff = datetime.utcnow() - timedelta(days=filters["days_back"])
            stmt = stmt.where(VisitNoteORM.date >= cutoff)
        return stmt.order_by(VisitNoteORM.date.desc())

    async def get_by_patient(
        self,
        patient_id: str,
        days_back: int | None = None,
        include_all: bool = False,
    ) -> list[VisitNote]:
        """
        Get all visit notes for a patient.

        Args:
            patient_id: The patient ID
            days_back: Limit to notes within this many days (default: all)
            include_all: If True, include cancelled/no-show visits

        Returns:
            List of visit notes sorted by date (most recent first)
        """
        filters: dict[str, Any] = {"patient_id": patient_id}

        if days_back:
            filters["days_back"] = days_back

        all_notes = await self.list(**filters)

        if not include_all:
            # Exclude cancelled and no_show visits
            return [v for v in all_notes if v.status not in ("cancelled", "no_show")]

        return all_notes

    async def get_by_encounter(self, encounter_id: str) -> VisitNote | None:
        """Get visit note for a specific encounter."""
        results = await self.list(encounter_id=encounter_id)
        return results[0] if results else None

    async def get_unique_providers(self, patient_id: str) -> list[dict]:
        """
        Get unique providers who have treated a patient.

        Returns a list of provider info dicts with id, name, role, and specialty.
        """
        visits = await self.get_by_patient(patient_id, include_all=True)
        seen_ids: set[str] = set()
        providers: list[dict] = []

        for visit in visits:
            if visit.provider and visit.provider.id not in seen_ids:
                seen_ids.add(visit.provider.id)
                providers.append(visit.provider.to_dict())

        return providers
