"""
Unit tests for ImagingStudyRepository.

Tests filtering by patient, modality, and date range.
"""
import asyncio
import pytest
from datetime import datetime, timedelta

from resources.imaging_study import (
    ImagingStudy,
    ImagingStudyRepository,
    RadiologyReport,
)


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestImagingStudyRepository:
    """Tests for ImagingStudyRepository."""

    @pytest.fixture
    def repo(self):
        """Create a repository without data."""
        return ImagingStudyRepository()

    @pytest.fixture
    def test_studies(self, repo):
        """Create test imaging studies."""
        now = datetime.now()
        studies = [
            # Recent CT for patient-001
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
            # Older MRI for patient-001
            ImagingStudy(
                id="img-002",
                patient_id="patient-001",
                modality="MRI",
                body_part="Lumbar Spine",
                study_date=now - timedelta(days=100),
                facility="Test Imaging",
                ordering_provider="Dr. Test",
                indication="Back pain",
                report_status="final",
            ),
            # Very old XR for patient-001
            ImagingStudy(
                id="img-003",
                patient_id="patient-001",
                modality="XR",
                body_part="Chest",
                study_date=now - timedelta(days=400),
                facility="Test Imaging",
                ordering_provider="Dr. Test",
                indication="Routine",
                report_status="final",
            ),
            # Study for patient-002
            ImagingStudy(
                id="img-004",
                patient_id="patient-002",
                modality="CT",
                body_part="Abdomen",
                study_date=now - timedelta(days=30),
                facility="Test Imaging",
                ordering_provider="Dr. Test",
                indication="Abdominal pain",
                report_status="final",
            ),
        ]
        for study in studies:
            repo._store[study.id] = study
        return studies

    def test_get_by_patient_returns_all_studies(self, repo, test_studies):
        """get_by_patient should return all studies for a patient."""
        result = run_async(repo.get_by_patient("patient-001"))

        assert len(result) == 3
        patient_ids = {s.patient_id for s in result}
        assert patient_ids == {"patient-001"}

    def test_get_by_patient_empty_for_unknown_patient(self, repo, test_studies):
        """get_by_patient should return empty list for unknown patient."""
        result = run_async(repo.get_by_patient("patient-999"))

        assert result == []

    def test_get_by_patient_and_modality(self, repo, test_studies):
        """get_by_patient_and_modality should filter by modality."""
        result = run_async(repo.get_by_patient_and_modality("patient-001", "CT"))

        assert len(result) == 1
        assert result[0].modality == "CT"
        assert result[0].id == "img-001"

    def test_list_with_days_back_filter(self, repo, test_studies):
        """list should filter by days_back."""
        # Only recent studies within 50 days
        result = run_async(repo.list(patient_id="patient-001", days_back=50))

        assert len(result) == 1
        assert result[0].id == "img-001"

    def test_list_with_modality_filter(self, repo, test_studies):
        """list should filter by modality."""
        result = run_async(repo.list(patient_id="patient-001", modality="MRI"))

        assert len(result) == 1
        assert result[0].modality == "MRI"

    def test_list_with_all_filters(self, repo, test_studies):
        """list should apply all filters together."""
        result = run_async(repo.list(
            patient_id="patient-001",
            modality="CT",
            days_back=30
        ))

        assert len(result) == 1
        assert result[0].id == "img-001"

    def test_crud_create_and_get(self, repo):
        """Should be able to create and get a study."""
        study = ImagingStudy(
            id="new-study",
            patient_id="patient-001",
            modality="XR",
            body_part="Hand",
            study_date=datetime.now(),
            facility="Test",
            ordering_provider="Dr. Test",
            indication="Pain",
            report_status="pending",
        )

        created = run_async(repo.create(study))
        assert created.id == "new-study"

        retrieved = run_async(repo.get("new-study"))
        assert retrieved is not None
        assert retrieved.body_part == "Hand"

    def test_modality_name_auto_populated(self):
        """ImagingStudy should auto-populate modality_name."""
        study = ImagingStudy(
            id="test",
            patient_id="patient-001",
            modality="CT",
            body_part="Chest",
            study_date=datetime.now(),
            facility="Test",
            ordering_provider="Dr. Test",
            indication="Test",
            report_status="pending",
        )

        assert study.modality_name == "Computed Tomography"

    def test_to_dict_serialization(self):
        """ImagingStudy.to_dict() should serialize correctly."""
        study = ImagingStudy(
            id="test",
            patient_id="patient-001",
            modality="MRI",
            body_part="Brain",
            study_date=datetime(2024, 1, 15, 10, 30),
            facility="Test Imaging",
            ordering_provider="Dr. Test",
            reading_radiologist="Dr. Reader",
            indication="Headache",
            series_count=5,
            image_count=245,
            has_images=True,
            report_status="final",
            report=RadiologyReport(
                clinical_indication="Headache",
                technique="MRI with contrast",
                findings="No abnormality",
                impression="Normal MRI",
            ),
        )

        data = study.to_dict()

        assert data["id"] == "test"
        assert data["patientId"] == "patient-001"
        assert data["modality"] == "MRI"
        assert data["modalityName"] == "Magnetic Resonance Imaging"
        assert data["bodyPart"] == "Brain"
        assert data["reportStatus"] == "final"
        assert data["report"] is not None
        assert data["report"]["impression"] == "Normal MRI"
