"""
Unit tests for medication-related endpoints.

These tests verify the API contract and response structure
for medication search and prescription functionality.
"""
from fastapi import status
import pytest


@pytest.mark.unit
class TestSearchMedications:
    """Tests for GET /medications/search endpoint"""

    def test_search_medications_returns_200(self, client, mock_services):
        """Should return 200 OK status for valid search"""
        response = client.get("/medications/search?q=lisinopril")
        assert response.status_code == status.HTTP_200_OK

    def test_search_medications_returns_list(self, client, mock_services):
        """Should return a list of medications"""
        response = client.get("/medications/search?q=aspirin")
        data = response.json()

        assert isinstance(data, list)

    def test_search_medications_query_required(self, client, mock_services):
        """Should return 422 when query is missing"""
        response = client.get("/medications/search")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_search_medications_min_length(self, client, mock_services):
        """Should return 422 when query is too short"""
        response = client.get("/medications/search?q=ab")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.unit
class TestGetMedicationDefaults:
    """Tests for GET /medications/defaults endpoint"""

    def test_get_defaults_returns_200(self, client, mock_services):
        """Should return 200 OK status for valid medication"""
        response = client.get("/medications/defaults?name=Lisinopril")
        assert response.status_code == status.HTTP_200_OK

    def test_get_defaults_structure(self, client, mock_services):
        """Should return default prescription values"""
        response = client.get("/medications/defaults?name=Lisinopril")
        data = response.json()

        # Response should have dosing information
        assert isinstance(data, dict)

    def test_get_defaults_name_required(self, client, mock_services):
        """Should return 422 when name is missing"""
        response = client.get("/medications/defaults")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.unit
class TestCreatePrescription:
    """Tests for POST /medications/{patient_id}/prescriptions endpoint"""

    def test_create_prescription_returns_200(self, client, mock_services):
        """Should return 200 OK status for valid prescription"""
        response = client.post(
            "/medications/patient-001/prescriptions",
            json={
                "medications": [
                    {
                        "name": "Amoxicillin",
                        "dosage": "500mg",
                        "frequency": "three times daily",
                        "duration_days": 10,
                        "instructions": "Take with food",
                    }
                ]
            },
        )
        assert response.status_code == status.HTTP_200_OK

    def test_create_prescription_structure(self, client, mock_services):
        """Response should have success and medications fields"""
        response = client.post(
            "/medications/patient-002/prescriptions",
            json={
                "medications": [
                    {
                        "name": "Ibuprofen",
                        "dosage": "400mg",
                        "frequency": "as needed",
                        "duration_days": 7,
                    }
                ]
            },
        )
        data = response.json()

        assert "success" in data
        assert data["success"] is True
        assert "medications" in data

    def test_create_prescription_patient_not_found(self, client, mock_services):
        """Should return 404 for unknown patient"""
        response = client.post(
            "/medications/unknown-patient/prescriptions",
            json={
                "medications": [
                    {
                        "name": "Test Med",
                        "dosage": "10mg",
                        "frequency": "daily",
                        "duration_days": 30,
                    }
                ]
            },
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_prescription_missing_required_fields(self, client, mock_services):
        """Should return 422 for missing required fields"""
        response = client.post(
            "/medications/patient-001/prescriptions",
            json={
                "medications": [
                    {
                        "name": "Test Med",
                        # Missing required fields
                    }
                ]
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_prescription_empty_medications(self, client, mock_services):
        """Should handle empty medications list"""
        response = client.post(
            "/medications/patient-001/prescriptions",
            json={"medications": []},
        )
        # Empty list should be valid but return empty results
        assert response.status_code == status.HTTP_200_OK

    def test_create_multiple_prescriptions(self, client, mock_services):
        """Should handle multiple medications in one request"""
        response = client.post(
            "/medications/patient-003/prescriptions",
            json={
                "medications": [
                    {
                        "name": "Medication A",
                        "dosage": "10mg",
                        "frequency": "daily",
                        "duration_days": 30,
                    },
                    {
                        "name": "Medication B",
                        "dosage": "20mg",
                        "frequency": "twice daily",
                        "duration_days": 14,
                    },
                ]
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["medications"]) == 2
