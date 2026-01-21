"""
Visit Note repository - data access layer.
"""

from __future__ import annotations

from typing import Any
from datetime import datetime, timedelta

from resources.core import InMemoryRepository
from .model import VisitNote


class VisitNoteRepository(InMemoryRepository[VisitNote]):
    """
    Repository for VisitNote resources.
    Currently uses in-memory storage, can be swapped for database later.
    """

    async def list(self, **filters: Any) -> list[VisitNote]:
        """
        List visit notes with optional filters.

        Supported filters:
        - patient_id: str - Filter by patient ID
        - encounter_id: str - Filter by encounter ID
        - status: str | list[str] - Filter by status(es)
        - visit_type: str | list[str] - Filter by visit type(s)
        - days_back: int - Filter to notes within this many days
        - provider_id: str - Filter by provider ID
        - diagnosis_code: str - Filter by ICD-10 diagnosis code (partial match)
        - search_query: str - Full-text search in SOAP notes, chief complaint, and diagnoses
        - date_from: datetime - Filter visits on or after this date
        - date_to: datetime - Filter visits on or before this date
        """
        results = list(self._store.values())

        if "patient_id" in filters:
            patient_ref = f"Patient/{filters['patient_id']}"
            results = [v for v in results if v.subject.reference == patient_ref]

        if "encounter_id" in filters:
            encounter_ref = f"Encounter/{filters['encounter_id']}"
            results = [v for v in results if v.encounter.reference == encounter_ref]

        if "status" in filters:
            status_filter = filters["status"]
            if isinstance(status_filter, str):
                status_filter = [status_filter]
            results = [v for v in results if v.status in status_filter]

        if "visit_type" in filters:
            type_filter = filters["visit_type"]
            if isinstance(type_filter, str):
                type_filter = [type_filter]
            results = [v for v in results if v.visit_type in type_filter]

        if "days_back" in filters:
            cutoff = datetime.utcnow() - timedelta(days=filters["days_back"])
            results = [v for v in results if v.date >= cutoff]

        # Provider filter
        if "provider_id" in filters:
            provider_id = filters["provider_id"]
            results = [v for v in results if v.provider and v.provider.id == provider_id]

        # Diagnosis code filter (partial match)
        if "diagnosis_code" in filters:
            code_filter = filters["diagnosis_code"].upper()
            results = [
                v for v in results
                if any(code_filter in d.code.upper() for d in v.diagnoses)
            ]

        # Date range filters
        if "date_from" in filters:
            date_from = filters["date_from"]
            results = [v for v in results if v.date >= date_from]

        if "date_to" in filters:
            date_to = filters["date_to"]
            # Include the entire day by checking <= end of day
            results = [v for v in results if v.date <= date_to]

        # Full-text search in SOAP notes, chief complaint, and diagnoses
        if "search_query" in filters:
            query = filters["search_query"].lower()
            results = [v for v in results if self._matches_search(v, query)]

        # Sort by date descending (most recent first)
        results.sort(key=lambda v: v.date, reverse=True)

        return results

    def _matches_search(self, visit: VisitNote, query: str) -> bool:
        """Check if a visit matches the search query."""
        # Search in chief complaint
        if query in visit.chief_complaint.lower():
            return True

        # Search in diagnoses
        for diagnosis in visit.diagnoses:
            if query in diagnosis.code.lower() or query in diagnosis.description.lower():
                return True

        # Search in SOAP note
        if visit.soap_note:
            soap = visit.soap_note
            if (
                query in soap.subjective.lower()
                or query in soap.objective.lower()
                or query in soap.assessment.lower()
                or query in soap.plan.lower()
            ):
                return True

        # Search in notes
        if visit.notes and query in visit.notes.lower():
            return True

        return False

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

        if not include_all:
            # Exclude cancelled and no_show visits
            all_notes = await self.list(**filters)
            return [v for v in all_notes if v.status not in ("cancelled", "no_show")]

        return await self.list(**filters)

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
