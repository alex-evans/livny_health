"""
Unit tests for patient-related endpoints.

These tests verify the API contract and response structure
without needing a real database.
"""
from fastapi import status
import pytest


@pytest.mark.unit
class TestGetPatients:
    """Tests for GET /patients endpoint"""

    def test_get_patients_returns_200(self, client, mock_services):
        """Should return 200 OK status"""
        response = client.get("/patients")
        assert response.status_code == status.HTTP_200_OK

    def test_get_patients_returns_list(self, client, mock_services):
        """Should return a list of patients"""
        response = client.get("/patients")
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_patients_structure(self, client, mock_services):
        """Each patient should have required fields"""
        response = client.get("/patients")
        patients = response.json()

        # Check first patient has expected structure
        first_patient = patients[0]
        assert "id" in first_patient
        assert "name" in first_patient
        assert "dateOfBirth" in first_patient
        assert "mrn" in first_patient

    def test_get_patients_data_types(self, client, mock_services):
        """Patient fields should have correct types"""
        response = client.get("/patients")
        first_patient = response.json()[0]

        assert isinstance(first_patient["id"], str)
        assert isinstance(first_patient["name"], str)
        assert isinstance(first_patient["dateOfBirth"], str)
        assert isinstance(first_patient["mrn"], str)

    def test_get_patients_consistent_data(self, client, mock_services):
        """Multiple calls should return same data (since using fake data)"""
        response1 = client.get("/patients")
        response2 = client.get("/patients")

        assert response1.json() == response2.json()

    def test_get_patients_contains_expected_patient(self, client, mock_services):
        """Should contain seeded patient data"""
        response = client.get("/patients")
        patients = response.json()

        patient_ids = [p["id"] for p in patients]
        assert "patient-001" in patient_ids
        assert "patient-002" in patient_ids


@pytest.mark.unit
class TestGetPatientById:
    """Tests for GET /patients/{patient_id} endpoint"""

    def test_get_patient_by_id_returns_200(self, client, mock_services):
        """Should return 200 OK status for valid patient ID"""
        response = client.get("/patients/patient-001")
        assert response.status_code == status.HTTP_200_OK

    def test_get_patient_by_id_structure(self, client, mock_services):
        """Patient should have required fields including allergies and medications"""
        response = client.get("/patients/patient-001")
        patient = response.json()

        assert "id" in patient
        assert "name" in patient
        assert "dateOfBirth" in patient
        assert "mrn" in patient
        assert "allergies" in patient
        assert "activeMedications" in patient

    def test_get_patient_by_id_data_types(self, client, mock_services):
        """Patient fields should have correct types"""
        response = client.get("/patients/patient-001")
        patient = response.json()

        assert isinstance(patient["id"], str)
        assert isinstance(patient["name"], str)
        assert isinstance(patient["dateOfBirth"], str)
        assert isinstance(patient["mrn"], str)
        assert isinstance(patient["allergies"], list)
        assert isinstance(patient["activeMedications"], list)

    def test_get_patient_by_id_not_found(self, client, mock_services):
        """Should return 404 Not Found for invalid patient ID"""
        response = client.get("/patients/unknown-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_patient_by_id_returns_allergies(self, client, mock_services):
        """Should return patient allergies"""
        response = client.get("/patients/patient-001")
        patient = response.json()

        # Patient 001 (Sarah Johnson) has allergies to Penicillin and Sulfa
        assert len(patient["allergies"]) >= 1
        allergens = [a["allergen"] for a in patient["allergies"]]
        assert "Penicillin" in allergens

    def test_get_patient_by_id_returns_medications(self, client, mock_services):
        """Should return patient active medications"""
        response = client.get("/patients/patient-001")
        patient = response.json()

        # Patient 001 has active medications
        assert len(patient["activeMedications"]) >= 1

    def test_get_patient_without_allergies(self, client, mock_services):
        """Patient without allergies should return empty list"""
        response = client.get("/patients/patient-003")
        patient = response.json()

        assert patient["allergies"] == []

    def test_get_patient_correct_data(self, client, mock_services):
        """Should return correct patient data"""
        response = client.get("/patients/patient-001")
        patient = response.json()

        assert patient["id"] == "patient-001"
        assert "Johnson" in patient["name"]

    def test_get_patient_includes_phone(self, client, mock_services):
        """Should return patient phone number"""
        response = client.get("/patients/patient-001")
        patient = response.json()

        assert "phone" in patient
        assert isinstance(patient["phone"], str)
        assert len(patient["phone"]) > 0

    def test_get_patient_phone_format(self, client, mock_services):
        """Phone number should be in expected format"""
        response = client.get("/patients/patient-001")
        patient = response.json()

        # Phone should contain digits and formatting characters
        assert "(" in patient["phone"]
        assert ")" in patient["phone"]
        assert "-" in patient["phone"]

    def test_get_patient_includes_insurance(self, client, mock_services):
        """Should return patient insurance information"""
        response = client.get("/patients/patient-001")
        patient = response.json()

        assert "insurance" in patient
        assert isinstance(patient["insurance"], dict)

    def test_get_patient_insurance_structure(self, client, mock_services):
        """Insurance should have provider and memberId fields"""
        response = client.get("/patients/patient-001")
        patient = response.json()

        insurance = patient["insurance"]
        assert "provider" in insurance
        assert "memberId" in insurance
        assert isinstance(insurance["provider"], str)
        assert isinstance(insurance["memberId"], str)

    def test_get_patient_insurance_has_values(self, client, mock_services):
        """Insurance fields should have non-empty values"""
        response = client.get("/patients/patient-001")
        patient = response.json()

        insurance = patient["insurance"]
        assert len(insurance["provider"]) > 0
        assert len(insurance["memberId"]) > 0

    def test_all_patients_have_phone_and_insurance(self, client, mock_services):
        """All seeded patients should have phone and insurance"""
        response = client.get("/patients")
        patients = response.json()

        for patient in patients:
            # Get full patient details
            detail_response = client.get(f"/patients/{patient['id']}")
            detail = detail_response.json()

            assert "phone" in detail, f"Patient {patient['id']} missing phone"
            assert "insurance" in detail, f"Patient {patient['id']} missing insurance"

