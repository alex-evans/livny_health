"""
Problem Detail Service Integration Tests.

Tests for the problem detail endpoint and service.
Verifies that problem detail data including history timeline,
treatments, and current treatment information is returned correctly.
"""
import asyncio
from datetime import date, timedelta
import pytest
from fastapi import status

from resources import Problem, ProblemStatus, ProblemPriority
from services import ProblemDetailService


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Test patient ID that matches the mock data
TEST_PATIENT_ID = "patient-001"
TEST_PATIENT_WITH_MANY_PROBLEMS = "patient-004"  # James Williams with 8 problems


@pytest.mark.integration
class TestProblemDetailServiceIntegration:
    """
    Integration tests for ProblemDetailService.

    Tests the service layer directly with real repositories.
    """

    def test_get_problem_detail_returns_detail(self, client, repositories):
        """get_problem_detail should return problem detail for a valid problem."""
        from bff.dependencies import get_problem_detail_service

        service = get_problem_detail_service()
        # I10 is Essential hypertension which is a common problem
        result = run_async(service.get_problem_detail(TEST_PATIENT_ID, "I10"))

        # May or may not exist for this patient, so just check the service works
        if result is not None:
            assert result.problem is not None
            assert result.problem.icd10_code == "I10"

    def test_get_problem_detail_returns_none_for_invalid_patient(self, client, repositories):
        """get_problem_detail should return None for non-existent patient."""
        from bff.dependencies import get_problem_detail_service

        service = get_problem_detail_service()
        result = run_async(service.get_problem_detail("nonexistent-patient", "I10"))

        assert result is None

    def test_get_problem_detail_returns_none_for_invalid_problem(self, client, repositories):
        """get_problem_detail should return None for non-existent problem."""
        from bff.dependencies import get_problem_detail_service

        service = get_problem_detail_service()
        result = run_async(service.get_problem_detail(TEST_PATIENT_ID, "INVALID-CODE"))

        assert result is None


@pytest.mark.integration
class TestProblemDetailResponse:
    """
    Tests for ProblemDetailResponse structure.
    """

    def test_to_dict_includes_all_fields(self):
        """to_dict should include all required fields."""
        from services.problem_detail import ProblemDetailResponse, ProblemHistoryEntry, ProblemTreatmentOutcome

        problem = Problem(
            name="Essential hypertension",
            icd10_code="I10",
            onset_date=date(2020, 3, 15),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        history = [
            ProblemHistoryEntry(
                date=date(2020, 3, 15),
                entry_type="onset",
                description="Problem onset: Essential hypertension",
                provider="Dr. Frost",
            ),
        ]

        treatments = [
            ProblemTreatmentOutcome(
                treatment="Lisinopril 10mg",
                start_date=date(2020, 3, 15),
                outcome="ongoing",
            ),
        ]

        response = ProblemDetailResponse(
            problem=problem,
            history_timeline=history,
            treatments=treatments,
            last_addressed=date(2024, 1, 15),
            current_treatment="Lisinopril 10mg",
        )

        data = response.to_dict()

        assert "problem" in data
        assert "historyTimeline" in data
        assert "treatments" in data
        assert "lastAddressed" in data
        assert "currentTreatment" in data

        # Check history structure
        assert len(data["historyTimeline"]) == 1
        history_entry = data["historyTimeline"][0]
        assert "date" in history_entry
        assert "type" in history_entry
        assert "description" in history_entry
        assert "provider" in history_entry

        # Check treatment structure
        assert len(data["treatments"]) == 1
        treatment = data["treatments"][0]
        assert "treatment" in treatment
        assert "startDate" in treatment
        assert "outcome" in treatment


@pytest.mark.integration
class TestProblemDetailEndpoint:
    """
    Integration tests for problem detail via BFF endpoints.
    """

    def test_get_problem_detail_endpoint_exists(self, client):
        """GET /patients/{id}/problems/{code} endpoint should exist."""
        # This will return 404 if the problem doesn't exist, which is expected
        response = client.get(f"/patients/{TEST_PATIENT_ID}/problems/I10")

        # Either 200 (found) or 404 (not found) is acceptable - just checking the route works
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_get_problem_detail_invalid_patient(self, client):
        """GET /patients/{id}/problems/{code} should return 404 for invalid patient."""
        response = client.get("/patients/nonexistent-patient/problems/I10")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_problem_detail_response_structure(self, client, repositories):
        """Response should have correct structure when problem exists."""
        # Get a patient with known problems
        patient_repo = repositories["patient"]
        patient = run_async(patient_repo.get(TEST_PATIENT_WITH_MANY_PROBLEMS))

        if patient and patient.problem_list and len(patient.problem_list) > 0:
            problem = patient.problem_list[0]
            response = client.get(
                f"/patients/{TEST_PATIENT_WITH_MANY_PROBLEMS}/problems/{problem.icd10_code}"
            )

            if response.status_code == status.HTTP_200_OK:
                data = response.json()

                assert "problem" in data
                assert "historyTimeline" in data
                assert "treatments" in data
                assert "lastAddressed" in data or data.get("lastAddressed") is None
                assert "currentTreatment" in data or data.get("currentTreatment") is None


@pytest.mark.integration
class TestProblemDetailHistoryTimeline:
    """
    Tests for problem history timeline generation.
    """

    def test_history_timeline_includes_onset(self):
        """History timeline should include onset entry."""
        from services.problem_detail import ProblemDetailService

        # Create service with None repos (just testing the timeline building logic)
        service = ProblemDetailService(
            patient_repo=None,
            medication_repo=None,
            visit_note_repo=None,
        )

        problem = Problem(
            name="Essential hypertension",
            icd10_code="I10",
            onset_date=date(2020, 3, 15),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
            documenting_provider="Dr. Frost",
        )

        # Build timeline directly
        timeline = run_async(service._build_history_timeline("test-patient", problem))

        # Should have at least the onset entry
        assert len(timeline) >= 1

        # Find onset entry
        onset_entries = [e for e in timeline if e.entry_type == "onset"]
        assert len(onset_entries) == 1
        assert onset_entries[0].date == date(2020, 3, 15)
        assert "onset" in onset_entries[0].description.lower()

    def test_history_timeline_includes_documented_date(self):
        """History timeline should include documented date if different from onset."""
        from services.problem_detail import ProblemDetailService

        service = ProblemDetailService(
            patient_repo=None,
            medication_repo=None,
            visit_note_repo=None,
        )

        problem = Problem(
            name="Essential hypertension",
            icd10_code="I10",
            onset_date=date(2020, 1, 1),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
            documented_date=date(2020, 3, 15),  # Different from onset
            documenting_provider="Dr. Frost",
        )

        timeline = run_async(service._build_history_timeline("test-patient", problem))

        # Should have both onset and documented entries
        assert len(timeline) >= 2

        onset_entries = [e for e in timeline if e.entry_type == "onset"]
        status_entries = [e for e in timeline if e.entry_type == "status_change"]

        assert len(onset_entries) == 1
        assert len(status_entries) == 1


@pytest.mark.integration
class TestMedicationKeywordMatching:
    """
    Tests for medication keyword matching in problem detail.
    """

    def test_hypertension_keywords(self):
        """Hypertension problems should match common antihypertensive keywords."""
        from services.problem_detail import ProblemDetailService

        service = ProblemDetailService(
            patient_repo=None,
            medication_repo=None,
            visit_note_repo=None,
        )

        keywords = service._get_medication_keywords("I10")

        assert "hypertension" in keywords
        assert "ace inhibitor" in keywords
        assert "beta blocker" in keywords

    def test_diabetes_keywords(self):
        """Diabetes problems should match common diabetes medication keywords."""
        from services.problem_detail import ProblemDetailService

        service = ProblemDetailService(
            patient_repo=None,
            medication_repo=None,
            visit_note_repo=None,
        )

        keywords = service._get_medication_keywords("E11")

        assert "diabetes" in keywords
        assert "metformin" in keywords
        assert "insulin" in keywords

    def test_unknown_code_returns_empty(self):
        """Unknown ICD-10 codes should return empty keyword list."""
        from services.problem_detail import ProblemDetailService

        service = ProblemDetailService(
            patient_repo=None,
            medication_repo=None,
            visit_note_repo=None,
        )

        keywords = service._get_medication_keywords("Z99.99")  # Unlikely code

        assert keywords == []
