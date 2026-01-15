"""
BFF Integration Tests.

These tests verify that the BFF endpoints work correctly with real services
and repositories. Unlike unit tests that mock the service layer, these tests
exercise the complete request flow:

    HTTP Request -> FastAPI Router -> BFF Endpoint -> Service -> Repository -> Response

What these tests verify:
- Correct HTTP status codes for various scenarios
- Response data matches what's in repositories
- Data transformations (FHIR -> BFF format) work correctly
- Error handling propagates correctly through the stack
"""
import asyncio
from datetime import date
from fastapi import status
import pytest


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Test data constants - these match the seeded data
class TestPatients:
    """Known patient data from seed for test assertions."""
    SARAH_JOHNSON = {"id": "patient-001", "name": "Sarah Johnson"}
    MICHAEL_CHEN = {"id": "patient-002", "name": "Michael Chen"}
    EMILY_RODRIGUEZ = {"id": "patient-003", "name": "Emily Rodriguez"}
    ROBERT_THOMPSON = {"id": "patient-006", "name": "Robert Thompson"}
    PATRICIA_MARTINEZ = {"id": "patient-007", "name": "Patricia Martinez"}


class TestProviders:
    """Known provider data from seed."""
    DR_FROST = {"id": "provider-001", "name": "Dr. Elizabeth Frost"}


@pytest.mark.integration
class TestPatientEndpointsIntegration:
    """
    Integration tests for patient endpoints.

    Verifies that patient data flows correctly from repositories
    through services to HTTP responses.
    """

    def test_get_patients_returns_seeded_data(self, client, repositories):
        """GET /patients should return all seeded patients."""
        response = client.get("/patients")
        patients = response.json()

        # Verify we get the seeded patients
        patient_ids = {p["id"] for p in patients}
        assert TestPatients.SARAH_JOHNSON["id"] in patient_ids
        assert TestPatients.MICHAEL_CHEN["id"] in patient_ids
        assert TestPatients.EMILY_RODRIGUEZ["id"] in patient_ids

        # Count should match repository
        repo_patients = run_async(repositories["patient"].list())
        assert len(patients) == len(repo_patients)

    def test_get_patient_detail_includes_allergies_from_allergy_repo(self, client, repositories):
        """GET /patients/{id} should include allergies from allergy repository."""
        response = client.get(f"/patients/{TestPatients.SARAH_JOHNSON['id']}")
        patient = response.json()

        # Verify allergies are included and match repository data
        repo_allergies = run_async(
            repositories["allergy"].get_by_patient(TestPatients.SARAH_JOHNSON["id"])
        )

        assert len(patient["allergies"]) == len(repo_allergies)
        allergen_names = {a["allergen"] for a in patient["allergies"]}
        assert "Penicillin" in allergen_names
        assert "Sulfa" in allergen_names

    def test_get_patient_detail_includes_medications_from_medication_repo(self, client, repositories):
        """GET /patients/{id} should include medications from medication request repository."""
        response = client.get(f"/patients/{TestPatients.SARAH_JOHNSON['id']}")
        patient = response.json()

        # Verify medications are included and match repository data
        repo_medications = run_async(
            repositories["medication_request"].get_active_for_patient(TestPatients.SARAH_JOHNSON["id"])
        )

        assert len(patient["activeMedications"]) == len(repo_medications)

    def test_get_patient_with_no_allergies(self, client):
        """Patient without allergies should return empty allergies list."""
        response = client.get(f"/patients/{TestPatients.EMILY_RODRIGUEZ['id']}")
        patient = response.json()

        assert patient["allergies"] == []

    def test_patient_data_format_matches_bff_contract(self, client):
        """Response format should match BFF API contract (camelCase, correct types)."""
        response = client.get(f"/patients/{TestPatients.SARAH_JOHNSON['id']}")
        patient = response.json()

        # Verify BFF format (camelCase keys)
        assert "id" in patient
        assert "name" in patient
        assert "dateOfBirth" in patient  # camelCase, not snake_case
        assert "mrn" in patient
        assert "allergies" in patient
        assert "activeMedications" in patient

        # Verify types
        assert isinstance(patient["name"], str)
        assert isinstance(patient["dateOfBirth"], str)
        assert isinstance(patient["allergies"], list)


@pytest.mark.integration
class TestAllergyEndpointsIntegration:
    """
    Integration tests for allergy checking endpoints.

    Verifies that allergy and drug interaction checks work correctly
    using real patient data and the clinical decision service.
    """

    def test_allergy_check_uses_patient_allergy_data(self, client):
        """Allergy check should use patient's actual allergies from repository."""
        # Sarah Johnson is allergic to Penicillin (severe)
        response = client.post(
            f"/allergies/{TestPatients.SARAH_JOHNSON['id']}/check-allergy",
            json={"medication_name": "Penicillin"},
        )
        data = response.json()

        assert data["hasConflict"] is True
        assert data["alert"]["allergen"] == "Penicillin"
        assert data["alert"]["severity"] == "severe"
        assert data["alert"]["blocked"] is True

    def test_allergy_check_cross_reactivity_detected(self, client):
        """Should detect cross-reactive medications using clinical decision service."""
        # Sarah is allergic to Penicillin; Amoxicillin is cross-reactive
        response = client.post(
            f"/allergies/{TestPatients.SARAH_JOHNSON['id']}/check-allergy",
            json={"medication_name": "Amoxicillin"},
        )
        data = response.json()

        assert data["hasConflict"] is True
        assert data["alert"]["isCrossReactive"] is True

    def test_drug_interaction_uses_patient_medications(self, client):
        """Drug interaction check should use patient's current medications."""
        # Robert Thompson is on Warfarin
        response = client.post(
            f"/allergies/{TestPatients.ROBERT_THOMPSON['id']}/check-interactions",
            json={"medication_name": "Aspirin"},
        )
        data = response.json()

        assert data["hasInteractions"] is True
        # Should find warfarin interaction
        interacting_drugs = [i["interactingDrug"] for i in data["interactions"]]
        assert any("warfarin" in d.lower() for d in interacting_drugs)

    def test_no_interactions_for_patient_without_conflicting_meds(self, client):
        """Patient without conflicting medications should have no interactions."""
        # Emily Rodriguez is only on Albuterol inhaler
        response = client.post(
            f"/allergies/{TestPatients.EMILY_RODRIGUEZ['id']}/check-interactions",
            json={"medication_name": "Acetaminophen"},
        )
        data = response.json()

        assert data["hasInteractions"] is False
        assert data["interactions"] == []


@pytest.mark.integration
class TestScheduleEndpointsIntegration:
    """
    Integration tests for schedule endpoints.

    Verifies that scheduling works correctly with real patient
    and provider data.
    """

    def test_get_schedule_returns_seeded_appointments(self, client, repositories):
        """GET /schedule should return seeded appointments for today."""
        today = date.today().isoformat()
        response = client.get(f"/schedule?date={today}")
        data = response.json()

        # Verify provider info
        assert data["provider"]["id"] == TestProviders.DR_FROST["id"]

        # Verify appointments are included
        repo_appointments = run_async(
            repositories["appointment"].get_for_date(date.today(), TestProviders.DR_FROST["id"])
        )
        assert len(data["appointments"]) == len(repo_appointments)

    def test_create_appointment_persists_to_repository(self, client, repositories):
        """POST /schedule/appointments should create appointment in repository."""
        today = date.today().isoformat()

        # Create appointment
        response = client.post(
            "/schedule/appointments",
            json={
                "date": today,
                "patient_id": TestPatients.EMILY_RODRIGUEZ["id"],
                "time": "14:00",
                "duration_minutes": 45,
                "visit_type": "New Patient",
                "chief_complaint": "Integration test appointment",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        appointment_id = data["appointment"]["id"]

        # Verify appointment exists in repository
        repo_appointment = run_async(repositories["appointment"].get(appointment_id))
        assert repo_appointment is not None
        assert repo_appointment.duration_minutes == 45
        assert repo_appointment.reason == "Integration test appointment"

    def test_appointment_includes_patient_data(self, client):
        """Created appointment response should include patient details."""
        today = date.today().isoformat()

        response = client.post(
            "/schedule/appointments",
            json={
                "date": today,
                "patient_id": TestPatients.SARAH_JOHNSON["id"],
                "time": "15:00",
            },
        )

        data = response.json()

        # Verify patient data is included in response
        assert data["appointment"]["patient"] is not None
        assert "Johnson" in data["appointment"]["patient"]["name"]


@pytest.mark.integration
class TestMedicationEndpointsIntegration:
    """
    Integration tests for medication endpoints.

    Verifies prescription creation works with real services
    and persists to repositories.
    """

    def test_create_prescription_persists_to_repository(self, client, repositories):
        """POST prescriptions should create medication requests in repository."""
        response = client.post(
            f"/medications/{TestPatients.EMILY_RODRIGUEZ['id']}/prescriptions",
            json={
                "medications": [
                    {
                        "name": "IntegrationTestMed",
                        "dosage": "100mg",
                        "frequency": "twice daily",
                        "duration_days": 14,
                        "instructions": "Take with food",
                    }
                ]
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify medication was created
        assert data["success"] is True
        assert len(data["medications"]) == 1

        # Verify it exists in repository
        med_id = data["medications"][0]["id"]
        repo_med = run_async(repositories["medication_request"].get(med_id))
        assert repo_med is not None
        assert repo_med.medication_name == "IntegrationTestMed"

    def test_get_medication_defaults_returns_appropriate_duration(self, client):
        """GET /medications/defaults should return appropriate duration by drug type."""
        # Antibiotics should have 10-day duration
        response = client.get("/medications/defaults?name=Amoxicillin")
        assert response.json()["defaultDuration"] == 10

        # Chronic meds should have 30-day duration
        response = client.get("/medications/defaults?name=Lisinopril")
        assert response.json()["defaultDuration"] == 30


@pytest.mark.integration
class TestErrorPropagationIntegration:
    """
    Integration tests for error handling across layers.

    Verifies that errors propagate correctly from repositories
    through services to HTTP responses.
    """

    def test_patient_not_found_returns_404(self, client):
        """Non-existent patient should return 404 from repository through to HTTP."""
        response = client.get("/patients/nonexistent-patient-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_provider_not_found_returns_404(self, client):
        """Non-existent provider should return 404."""
        today = date.today().isoformat()
        response = client.get(f"/schedule?date={today}&provider_id=nonexistent-provider")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_invalid_date_returns_400(self, client):
        """Invalid date format should return 400 Bad Request."""
        response = client.get("/schedule?date=not-a-date")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_prescription_for_nonexistent_patient_returns_404(self, client):
        """Prescription for non-existent patient should return 404."""
        response = client.post(
            "/medications/nonexistent-patient/prescriptions",
            json={
                "medications": [
                    {"name": "Test", "dosage": "10mg", "frequency": "daily", "duration_days": 7}
                ]
            },
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
