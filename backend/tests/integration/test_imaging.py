"""
Imaging Studies Integration Tests.

Tests for the imaging endpoint and service.
Verifies that imaging data flows correctly from repositories
through services to HTTP responses.
"""
import asyncio
import pytest
from fastapi import status


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Test patient IDs that match the seeded data
TEST_PATIENT_001 = "patient-001"  # Has imaging studies
TEST_PATIENT_004 = "patient-004"  # Has imaging studies including pending
TEST_PATIENT_005 = "patient-005"  # No imaging studies


@pytest.mark.integration
class TestImagingEndpointIntegration:
    """
    Integration tests for imaging endpoint.

    Verifies that imaging data flows correctly from repositories
    through services to HTTP responses.
    """

    def test_get_imaging_studies_returns_data(self, client):
        """GET /imaging/{id}/studies should return imaging studies."""
        response = client.get(f"/imaging/{TEST_PATIENT_001}/studies")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure
        assert "studies" in data
        assert "totalCount" in data

        # Verify we have studies
        assert data["totalCount"] > 0
        assert len(data["studies"]) > 0

    def test_get_imaging_studies_sorted_by_date(self, client):
        """Studies should be sorted by date, newest first."""
        response = client.get(f"/imaging/{TEST_PATIENT_001}/studies")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        dates = [s["studyDate"] for s in data["studies"]]
        assert dates == sorted(dates, reverse=True)

    def test_get_imaging_studies_with_modality_filter(self, client):
        """GET /imaging/{id}/studies with modality should filter results."""
        response = client.get(f"/imaging/{TEST_PATIENT_001}/studies?modality=CT")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # All returned studies should be CT
        for study in data["studies"]:
            assert study["modality"] == "CT"

    def test_get_imaging_studies_with_days_back_filter(self, client):
        """GET /imaging/{id}/studies with days_back should filter by date."""
        # Get recent studies (30 days)
        response_short = client.get(
            f"/imaging/{TEST_PATIENT_001}/studies",
            params={"days_back": 30}
        )

        # Get all studies (2 years)
        response_long = client.get(
            f"/imaging/{TEST_PATIENT_001}/studies",
            params={"days_back": 730}
        )

        assert response_short.status_code == status.HTTP_200_OK
        assert response_long.status_code == status.HTTP_200_OK

        short_count = response_short.json()["totalCount"]
        long_count = response_long.json()["totalCount"]

        # Short range should have fewer or equal studies
        assert short_count <= long_count

    def test_get_imaging_studies_empty_for_patient_without_studies(self, client):
        """Should return empty list for patient without imaging studies."""
        response = client.get(f"/imaging/{TEST_PATIENT_005}/studies")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["totalCount"] == 0
        assert data["studies"] == []


@pytest.mark.integration
class TestImagingStudyStructure:
    """Tests for imaging study data structure."""

    def test_study_has_all_required_fields(self, client):
        """Each study should have all required fields."""
        response = client.get(f"/imaging/{TEST_PATIENT_001}/studies")
        studies = response.json()["studies"]

        required_fields = [
            "id", "patientId", "modality", "modalityName", "bodyPart",
            "studyDate", "facility", "orderingProvider", "indication",
            "seriesCount", "imageCount", "hasImages", "reportStatus"
        ]

        for study in studies:
            for field in required_fields:
                assert field in study, f"Missing field: {field}"

    def test_final_report_has_all_fields(self, client):
        """Final reports should have all required sections."""
        response = client.get(f"/imaging/{TEST_PATIENT_001}/studies")
        studies = response.json()["studies"]

        # Find studies with final reports
        final_studies = [s for s in studies if s["reportStatus"] == "final" and s.get("report")]
        assert len(final_studies) > 0

        report = final_studies[0]["report"]
        assert "clinicalIndication" in report
        assert "technique" in report
        assert "findings" in report
        assert "impression" in report
        assert "criticalFinding" in report
        assert "comparisonStudies" in report

    def test_pending_study_has_no_report(self, client):
        """Pending studies should have no report or null report."""
        response = client.get(f"/imaging/{TEST_PATIENT_004}/studies")
        studies = response.json()["studies"]

        pending_studies = [s for s in studies if s["reportStatus"] == "pending"]
        for study in pending_studies:
            assert study.get("report") is None


@pytest.mark.integration
class TestImagingServiceIntegration:
    """
    Integration tests for ImagingService.

    Tests the service layer directly with real repositories.
    """

    def test_service_returns_correct_patient_studies(self, client):
        """Service should return studies only for the specified patient."""
        # Get studies for two different patients
        response1 = client.get(f"/imaging/{TEST_PATIENT_001}/studies")
        response2 = client.get(f"/imaging/{TEST_PATIENT_004}/studies")

        studies1 = response1.json()["studies"]
        studies2 = response2.json()["studies"]

        # All studies should belong to their respective patients
        for study in studies1:
            assert study["patientId"] == TEST_PATIENT_001

        for study in studies2:
            assert study["patientId"] == TEST_PATIENT_004

    def test_service_handles_multiple_modalities(self, client):
        """Service should return studies of different modalities."""
        response = client.get(f"/imaging/{TEST_PATIENT_001}/studies")
        studies = response.json()["studies"]

        modalities = {s["modality"] for s in studies}
        # Patient-001 should have multiple modality types
        assert len(modalities) > 1


@pytest.mark.integration
class TestImagingReportContent:
    """Tests for radiology report content."""

    def test_report_impression_is_readable(self, client):
        """Report impressions should contain meaningful text."""
        response = client.get(f"/imaging/{TEST_PATIENT_001}/studies")
        studies = response.json()["studies"]

        for study in studies:
            if study.get("report"):
                impression = study["report"]["impression"]
                assert len(impression) > 10, "Impression should have meaningful content"

    def test_report_findings_is_readable(self, client):
        """Report findings should contain detailed text."""
        response = client.get(f"/imaging/{TEST_PATIENT_001}/studies")
        studies = response.json()["studies"]

        for study in studies:
            if study.get("report"):
                findings = study["report"]["findings"]
                assert len(findings) > 10, "Findings should have meaningful content"

    def test_comparison_studies_structure(self, client):
        """Comparison studies should have proper structure."""
        response = client.get(f"/imaging/{TEST_PATIENT_001}/studies")
        studies = response.json()["studies"]

        for study in studies:
            if study.get("report") and study["report"].get("comparisonStudies"):
                for comp in study["report"]["comparisonStudies"]:
                    assert "studyId" in comp
                    assert "date" in comp
                    assert "modality" in comp
                    assert "bodyPart" in comp


@pytest.mark.integration
class TestImagingRepository:
    """Tests for the ImagingStudyRepository."""

    def test_repository_returns_seeded_data(self):
        """Repository should return seeded imaging studies."""
        from bff.dependencies import get_imaging_study_repo, ensure_data_seeded

        ensure_data_seeded()
        repo = get_imaging_study_repo()

        studies = run_async(repo.get_by_patient(TEST_PATIENT_001))
        assert len(studies) > 0

    def test_repository_filters_by_modality(self):
        """Repository should filter by modality."""
        from bff.dependencies import get_imaging_study_repo, ensure_data_seeded

        ensure_data_seeded()
        repo = get_imaging_study_repo()

        ct_studies = run_async(repo.get_by_patient_and_modality(TEST_PATIENT_001, "CT"))
        all_studies = run_async(repo.get_by_patient(TEST_PATIENT_001))

        assert len(ct_studies) <= len(all_studies)
        for study in ct_studies:
            assert study.modality == "CT"
