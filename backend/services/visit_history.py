"""
Visit History Service.

Provides visit history retrieval for patients with SOAP notes,
vitals, medications, and orders.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from resources import VisitNote, VisitNoteRepository


@dataclass
class VisitHistoryResponse:
    """Response containing visit history."""
    visits: list[VisitNote]
    total_count: int
    has_more: bool
    offset: int = 0
    limit: int = 50

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "visits": [v.to_bff_dict() for v in self.visits],
            "totalCount": self.total_count,
            "hasMore": self.has_more,
            "offset": self.offset,
            "limit": self.limit,
        }


class VisitHistoryService:
    """
    Service for retrieving patient visit history.

    Provides access to historical visit notes including SOAP notes,
    vitals, medications prescribed, and orders placed.
    """

    def __init__(self, visit_note_repo: VisitNoteRepository):
        self.visit_note_repo = visit_note_repo

    async def get_visit_history(
        self,
        patient_id: str,
        days_back: int = 365,
        include_all: bool = False,
        limit: int = 50,
        offset: int = 0,
        visit_type: str | None = None,
        provider_id: str | None = None,
        diagnosis_code: str | None = None,
        search_query: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> VisitHistoryResponse:
        """
        Get visit history for a patient with filtering and pagination.

        Args:
            patient_id: The patient ID
            days_back: How many days of history to include (default: 365)
            include_all: Include cancelled/no-show visits (default: False)
            limit: Maximum number of visits to return (default: 50)
            offset: Number of visits to skip for pagination (default: 0)
            visit_type: Filter by visit type (e.g., 'office_visit', 'telehealth')
            provider_id: Filter by provider ID
            diagnosis_code: Filter by ICD-10 diagnosis code (partial match)
            search_query: Full-text search in SOAP notes, chief complaint, diagnoses
            date_from: Filter visits on or after this date
            date_to: Filter visits on or before this date

        Returns:
            VisitHistoryResponse with visits and pagination info
        """
        # Build filters for repository
        filters: dict[str, Any] = {"patient_id": patient_id}

        if days_back:
            filters["days_back"] = days_back

        if visit_type:
            filters["visit_type"] = visit_type

        if provider_id:
            filters["provider_id"] = provider_id

        if diagnosis_code:
            filters["diagnosis_code"] = diagnosis_code

        if search_query:
            filters["search_query"] = search_query

        if date_from:
            filters["date_from"] = date_from

        if date_to:
            filters["date_to"] = date_to

        # Get filtered visits from repository
        all_visits = await self.visit_note_repo.list(**filters)

        # Exclude cancelled/no-show if not including all
        if not include_all:
            all_visits = [v for v in all_visits if v.status not in ("cancelled", "no_show")]

        total_count = len(all_visits)

        # Apply pagination
        paginated_visits = all_visits[offset:offset + limit]
        has_more = (offset + len(paginated_visits)) < total_count

        return VisitHistoryResponse(
            visits=paginated_visits,
            total_count=total_count,
            has_more=has_more,
            offset=offset,
            limit=limit,
        )

    async def get_providers_for_patient(self, patient_id: str) -> list[dict]:
        """
        Get all unique providers who have treated a patient.

        Args:
            patient_id: The patient ID

        Returns:
            List of provider dicts with id, name, role, specialty
        """
        return await self.visit_note_repo.get_unique_providers(patient_id)

    async def get_visit_by_id(
        self,
        visit_id: str,
    ) -> VisitNote | None:
        """
        Get a single visit note by ID.

        Args:
            visit_id: The visit note ID

        Returns:
            VisitNote if found, None otherwise
        """
        return await self.visit_note_repo.get(visit_id)

    async def get_visit_by_encounter(
        self,
        encounter_id: str,
    ) -> VisitNote | None:
        """
        Get visit note for a specific encounter.

        Args:
            encounter_id: The encounter ID

        Returns:
            VisitNote if found, None otherwise
        """
        return await self.visit_note_repo.get_by_encounter(encounter_id)
