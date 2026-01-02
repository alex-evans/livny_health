"""
Unit tests for patient-related endpoints.

These tests verify the API contract and response structure
without needing a real database.
"""
from fastapi import status
from httpx import Response
import pytest
import respx


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


@pytest.mark.unit
class TestGetPatientById:
    """Tests for GET /patients/{patient_id} endpoint"""
    
    def test_get_patient_by_id_returns_200(self, client, mock_services):
        """Should return 200 OK status for valid patient ID"""
        response = client.get("/patients/patient-001")
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_patient_by_id_structure(self, client, mock_services):
        """Patient should have required fields"""
        response = client.get("/patients/patient-001")
        patient = response.json()
        
        assert "id" in patient
        assert "name" in patient
        assert "dateOfBirth" in patient
        assert "mrn" in patient
    
    def test_get_patient_by_id_data_types(self, client, mock_services):
        """Patient fields should have correct types"""
        response = client.get("/patients/patient-001")
        patient = response.json()
        
        assert isinstance(patient["id"], str)
        assert isinstance(patient["name"], str)
        assert isinstance(patient["dateOfBirth"], str)
        assert isinstance(patient["mrn"], str)
    
    def test_get_patient_by_id_not_found(self, client, mock_services):
        """Should return 404 Not Found for invalid patient ID"""
        response = client.get("/patients/unknown-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_patient_by_id_invalid_format(self, client, mock_services):
        """Should return 422 Unprocessable Entity for invalid ID format"""
        response = client.get("/patients/invalid-id-format")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

