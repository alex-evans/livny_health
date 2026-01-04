"""
Unit tests for patient-related endpoints.

These tests verify the API contract and response structure
without needing a real database.
"""

import pytest
from fastapi import status


@pytest.mark.unit
class TestGetPatients:
    """Tests for GET /patients endpoint"""
    
    def test_get_patients_returns_200(self, client):
        """Should return 200 OK status"""
        response = client.get("/patients")
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_patients_returns_list(self, client):
        """Should return a list of patients"""
        response = client.get("/patients")
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_patients_structure(self, client):
        """Each patient should have required fields"""
        response = client.get("/patients")
        patients = response.json()
        
        # Check first patient has expected structure
        first_patient = patients[0]
        assert "id" in first_patient
        assert "name" in first_patient
        assert "dateOfBirth" in first_patient
        assert "mrn" in first_patient
    
    def test_get_patients_data_types(self, client):
        """Patient fields should have correct types"""
        response = client.get("/patients")
        first_patient = response.json()[0]
        
        assert isinstance(first_patient["id"], str)
        assert isinstance(first_patient["name"], str)
        assert isinstance(first_patient["dateOfBirth"], str)
        assert isinstance(first_patient["mrn"], str)
    
    def test_get_patients_consistent_data(self, client):
        """Multiple calls should return same data (since using fake data)"""
        response1 = client.get("/patients")
        response2 = client.get("/patients")
        
        assert response1.json() == response2.json()


@pytest.mark.unit
class TestGetPatientById:
    """Tests for GET /patients/{patient_id} endpoint"""
    
    def test_get_patient_by_id_returns_200(self, client):
        """Should return 200 for existing patient"""
        patients = client.get("/patients").json()
        response = client.get(f"/patients/{patients[0]['id']}")
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_patient_by_id_not_found(self, client):
        """Should return 404 for non-existent patient"""
        response = client.get("/patients/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.unit
class TestCreatePatient:
    """Tests for POST /patients endpoint (not implemented yet)"""
    
    @pytest.mark.skip(reason="Endpoint not implemented yet")
    def test_create_patient_success(self, client, sample_patient):
        """Should create patient and return 201"""
        response = client.post("/patients", json=sample_patient)
        assert response.status_code == status.HTTP_201_CREATED
    
    @pytest.mark.skip(reason="Endpoint not implemented yet")
    def test_create_patient_missing_required_field(self, client):
        """Should return 422 when required field is missing"""
        incomplete_data = {
            "first_name": "John"
            # Missing last_name, dob, etc.
        }
        response = client.post("/patients", json=incomplete_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    
    @pytest.mark.skip(reason="Endpoint not implemented yet")
    def test_create_patient_invalid_date_format(self, client):
        """Should return 422 for invalid date format"""
        invalid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "not-a-date",
            "mrn": "MRN-001"
        }
        response = client.post("/patients", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.unit
class TestGetPatientAllergies:
    """Tests for GET /patients/{patient_id}/allergies endpoint"""
    
    def test_get_patient_allergies_returns_200(self, client):
        """Should return 200 for existing patient"""
        patients = client.get("/patients").json()
        response = client.get(f"/patients/{patients[0]['id']}/allergies")
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_patient_allergies_not_found(self, client):
        """Should return 404 for non-existent patient"""
        response = client.get("/patients/99999/allergies")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.unit
class TestGetPatientMedications:
    """Tests for GET /patients/{patient_id}/medications endpoint"""
    
    def test_get_patient_medications_returns_200(self, client):
        """Should return 200 for existing patient"""
        patients = client.get("/patients").json()
        response = client.get(f"/patients/{patients[0]['id']}/medications")
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_patient_medications_not_found(self, client):
        """Should return 404 for non-existent patient"""
        response = client.get("/patients/99999/medications")
        assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.unit
class TestCheckMedicationInteractions:
    """Tests for POST /patients/{patient_id}/check-interactions endpoint"""
    
    def test_check_interactions_returns_200(self, client):
        """Should return 200 for existing patient"""
        patients = client.get("/patients").json()
        payload = {"medication_name": "Aspirin"}
        response = client.post(f"/patients/{patients[0]['id']}/check-interactions", json=payload)
        assert response.status_code == status.HTTP_200_OK
    
    def test_check_interactions_not_found(self, client):
        """Should return 404 for non-existent patient"""
        payload = {"medication_name": "Aspirin"}
        response = client.post("/patients/99999/check-interactions", json=payload)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.unit
class TestSearchMedications:
    """Tests for GET /medications/search endpoint"""
    
    def test_search_medications_returns_200(self, client):
        """Should return 200 for valid query"""
        response = client.get("/medications/search?q=asp")
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_medications_too_short_query(self, client):
        """Should return 422 for too short query"""
        response = client.get("/medications/search?q=as")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.unit
class TestGetMedicationDefaults:
    """Tests for GET /medications/defaults endpoint"""
    
    def test_get_medication_defaults_returns_200(self, client):
        """Should return 200 for valid medication name"""
        response = client.get("/medications/defaults?name=Aspirin")
        assert response.status_code == status.HTTP_200_OK

    def test_get_medication_defaults_missing_name(self, client):
        """Should return 422 when medication name is missing"""
        response = client.get("/medications/defaults")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.unit
class TestCheckPatientAllergy:
    """Tests for POST /patients/{patient_id}/check-allergy endpoint"""
    
    def test_check_allergy_returns_200(self, client):
        """Should return 200 for existing patient"""
        patients = client.get("/patients").json()
        payload = {"medication_name": "Aspirin"}
        response = client.post(f"/patients/{patients[0]['id']}/check-allergy", json=payload)
        assert response.status_code == status.HTTP_200_OK
    
    def test_check_allergy_not_found(self, client):
        """Should return 404 for non-existent patient"""
        payload = {"medication_name": "Aspirin"}
        response = client.post("/patients/99999/check-allergy", json=payload)
        assert response.status_code == status.HTTP_404_NOT_FOUND

