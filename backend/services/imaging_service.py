"""
Imaging Service.

Provides imaging study retrieval with filtering and sorting.
"""

from dataclasses import dataclass

from resources.imaging_study import ImagingStudy, ImagingStudyRepository, ImagingModality


@dataclass
class ImagingStudiesResponse:
    """Response containing imaging studies list."""
    studies: list[ImagingStudy]
    total_count: int

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "studies": [s.to_dict() for s in self.studies],
            "totalCount": self.total_count,
        }


class ImagingService:
    """
    Service for retrieving imaging studies.
    """

    def __init__(self, imaging_study_repo: ImagingStudyRepository):
        self.imaging_study_repo = imaging_study_repo

    async def get_studies_for_patient(
        self,
        patient_id: str,
        modality_filter: ImagingModality | None = None,
        days_back: int = 730,  # 2 years default
    ) -> ImagingStudiesResponse:
        """
        Get imaging studies for a patient.

        Args:
            patient_id: The patient ID
            modality_filter: Optional modality to filter by
            days_back: How many days of history to include (default 2 years)

        Returns:
            ImagingStudiesResponse with studies sorted by date (newest first)
        """
        filters: dict = {
            "patient_id": patient_id,
            "days_back": days_back,
        }
        if modality_filter:
            filters["modality"] = modality_filter

        studies = await self.imaging_study_repo.list(**filters)

        # Sort by study date (most recent first)
        studies.sort(key=lambda s: s.study_date, reverse=True)

        return ImagingStudiesResponse(
            studies=studies,
            total_count=len(studies),
        )
