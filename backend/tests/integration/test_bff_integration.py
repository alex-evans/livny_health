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
    JAMES_WILLIAMS = {"id": "patient-004", "name": "James Williams"}
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

    def test_get_patient_medications_sorted_by_start_date_descending(self, client):
        """GET /patients/{id} should return medications sorted by start date (most recent first)."""
        # Patricia Martinez has 4 medications with different start dates:
        # - Sertraline: 2023-08-01 (most recent)
        # - Warfarin: 2023-02-10
        # - Simvastatin: 2022-05-15
        # - Lisinopril: 2021-11-20 (oldest)
        response = client.get(f"/patients/{TestPatients.PATRICIA_MARTINEZ['id']}")
        patient = response.json()

        medications = patient["activeMedications"]
        assert len(medications) == 4

        # Verify the expected order (most recent first)
        medication_names = [med["name"] for med in medications]
        assert medication_names[0] == "Sertraline"  # 08/01/2023 (most recent)
        assert medication_names[1] == "Warfarin"    # 02/10/2023
        assert medication_names[2] == "Simvastatin" # 05/15/2022
        assert medication_names[3] == "Lisinopril"  # 11/20/2021 (oldest)

        # Verify the dates are in MM/DD/YYYY format
        started_dates = [med["started"] for med in medications]
        assert started_dates[0] == "08/01/2023"
        assert started_dates[1] == "02/10/2023"
        assert started_dates[2] == "05/15/2022"
        assert started_dates[3] == "11/20/2021"

    def test_get_patient_medications_include_all_required_fields(self, client):
        """GET /patients/{id} should return medications with all required display fields."""
        response = client.get(f"/patients/{TestPatients.SARAH_JOHNSON['id']}")
        patient = response.json()

        medications = patient["activeMedications"]
        assert len(medications) == 7

        # Find Lisinopril to test all fields
        lisinopril = next((m for m in medications if m["name"] == "Lisinopril"), None)
        assert lisinopril is not None

        # Verify all required fields are present
        assert "name" in lisinopril
        assert "brandName" in lisinopril
        assert "strength" in lisinopril
        assert "form" in lisinopril
        assert "frequency" in lisinopril
        assert "route" in lisinopril
        assert "started" in lisinopril
        assert "prescriber" in lisinopril

        # Verify field values
        assert lisinopril["name"] == "Lisinopril"
        assert lisinopril["brandName"] == "Zestril"
        assert lisinopril["strength"] == "10mg"
        assert lisinopril["form"] == "tablet"
        assert lisinopril["frequency"] == "once daily"
        assert lisinopril["route"] == "PO"  # Route abbreviation
        assert lisinopril["started"] == "06/15/2023"  # MM/DD/YYYY format
        assert lisinopril["prescriber"] == "Dr. Elizabeth Frost"

    def test_get_patient_medications_inhaler_has_correct_form_and_route(self, client):
        """GET /patients/{id} should return correct form and route for inhaler medications."""
        # Emily Rodriguez has an Albuterol inhaler (PRN medication)
        response = client.get(f"/patients/{TestPatients.EMILY_RODRIGUEZ['id']}")
        patient = response.json()

        medications = patient["activeMedications"]
        assert len(medications) == 1

        albuterol = medications[0]
        assert albuterol["name"] == "Albuterol"
        assert albuterol["brandName"] == "ProAir HFA"
        assert albuterol["strength"] == "90mcg/actuation"
        assert albuterol["form"] == "inhaler"
        assert albuterol["route"] == "inhaled"  # Route abbreviation
        assert albuterol["frequency"] == "as needed"
        assert albuterol["prescriber"] == "Dr. Elizabeth Frost"
        assert albuterol["isPRN"] is True  # PRN medication
        assert albuterol["isControlled"] is False  # Not a controlled substance

    def test_get_patient_medication_without_brand_name(self, client):
        """Medications without brand names should return null for brandName."""
        response = client.get(f"/patients/{TestPatients.SARAH_JOHNSON['id']}")
        patient = response.json()

        medications = patient["activeMedications"]
        aspirin = next((m for m in medications if m["name"] == "Aspirin"), None)
        assert aspirin is not None
        assert aspirin["brandName"] is None  # Aspirin has no brand name

    def test_get_patient_medication_controlled_substance_flag(self, client):
        """Controlled substances should have isControlled flag set to true."""
        # James Williams has Gabapentin which is a controlled substance
        response = client.get(f"/patients/{TestPatients.JAMES_WILLIAMS['id']}")
        patient = response.json()

        medications = patient["activeMedications"]
        gabapentin = next((m for m in medications if m["name"] == "Gabapentin"), None)
        assert gabapentin is not None
        assert gabapentin["isControlled"] is True  # Schedule V controlled substance
        assert gabapentin["isPRN"] is False  # Not a PRN medication

    def test_get_patient_medication_prn_and_controlled(self, client):
        """Medications can be both PRN and controlled."""
        # Sarah Johnson has Tramadol which is both PRN and controlled
        response = client.get(f"/patients/{TestPatients.SARAH_JOHNSON['id']}")
        patient = response.json()

        medications = patient["activeMedications"]
        tramadol = next((m for m in medications if m["name"] == "Tramadol"), None)
        assert tramadol is not None
        assert tramadol["isPRN"] is True  # As needed medication
        assert tramadol["isControlled"] is True  # Schedule IV controlled substance

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
