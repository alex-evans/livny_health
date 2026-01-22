"""
Unit tests for ImagingService.

Tests imaging study retrieval, filtering, and sorting.
"""
import asyncio
import pytest
from datetime import datetime, timedelta

from resources.imaging_study import ImagingStudy, ImagingStudyRepository
from services.imaging_service import ImagingService


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestImagingService:
    """Tests for ImagingService."""

    @pytest.fixture
    def repo(self):
        """Create a repository with test data."""
        repo = ImagingStudyRepository()
        now = datetime.now()

        studies = [
            ImagingStudy(
                id="img-001",
                patient_id="patient-001",
                modality="CT",
                body_part="Chest",
                study_date=now - timedelta(days=10),
                facility="Test Imaging",
                ordering_provider="Dr. Test",
                indication="Cough",
                report_status="final",
            ),
            ImagingStudy(
                id="img-002",
                patient_id="patient-001",
                modality="MRI",
                body_part="Brain",
                study_date=now - timedelta(days=30),
                facility="Test Imaging",
                ordering_provider="Dr. Test",
                indication="Headache",
                report_status="final",
            ),
            ImagingStudy(
                id="img-003",
                patient_id="patient-001",
                modality="XR",
                body_part="Chest",
                study_date=now - timedelta(days=60),
                facility="Test Imaging",
                ordering_provider="Dr. Test",
                indication="Routine",
                report_status="final",
            ),
            ImagingStudy(
                id="img-004",
                patient_id="patient-001",
                modality="CT",
                body_part="Abdomen",
                study_date=now - timedelta(days=800),  # > 2 years
                facility="Test Imaging",
                ordering_provider="Dr. Test",
                indication="Pain",
                report_status="final",
            ),
        ]
        repo._seed(studies)
        return repo

    @pytest.fixture
    def service(self, repo):
        """Create a service with the test repository."""
        return ImagingService(imaging_study_repo=repo)

    def test_get_studies_returns_sorted_by_date(self, service):
        """get_studies_for_patient should return studies sorted newest first."""
        response = run_async(service.get_studies_for_patient("patient-001"))

        assert response.total_count >= 3
        # Verify sorted by date (newest first)
        dates = [s.study_date for s in response.studies]
        assert dates == sorted(dates, reverse=True)

    def test_get_studies_default_days_back(self, service):
        """get_studies_for_patient with default days_back=730 should exclude old studies."""
        response = run_async(service.get_studies_for_patient("patient-001"))

        # Should not include the study from 800 days ago
        assert response.total_count == 3
        study_ids = {s.id for s in response.studies}
        assert "img-004" not in study_ids

    def test_get_studies_with_modality_filter(self, service):
        """get_studies_for_patient should filter by modality."""
        response = run_async(service.get_studies_for_patient(
            "patient-001",
            modality_filter="CT"
        ))

        # Should only return CT studies (within 2 years)
        assert response.total_count == 1
        assert all(s.modality == "CT" for s in response.studies)

    def test_get_studies_with_days_back_filter(self, service):
        """get_studies_for_patient should respect days_back filter."""
        response = run_async(service.get_studies_for_patient(
            "patient-001",
            days_back=45
        ))

        # Should only include studies within 45 days
        assert response.total_count == 2
        study_ids = {s.id for s in response.studies}
        assert "img-001" in study_ids
        assert "img-002" in study_ids

    def test_get_studies_empty_for_unknown_patient(self, service):
        """get_studies_for_patient should return empty for unknown patient."""
        response = run_async(service.get_studies_for_patient("patient-999"))

        assert response.total_count == 0
        assert response.studies == []

    def test_response_to_dict(self, service):
        """ImagingStudiesResponse.to_dict() should serialize correctly."""
        response = run_async(service.get_studies_for_patient("patient-001"))

        data = response.to_dict()

        assert "studies" in data
        assert "totalCount" in data
        assert isinstance(data["studies"], list)
        assert data["totalCount"] == len(data["studies"])

        if data["studies"]:
            study = data["studies"][0]
            assert "id" in study
            assert "modality" in study
            assert "bodyPart" in study
            assert "studyDate" in study
