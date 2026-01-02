
import pytest
import respx
import sys
from pathlib import Path
from httpx import Response

# Add parent directory to Python path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from fastapi.testclient import TestClient

from main import app

SERVICES_URL = "http://localhost:8001"


@pytest.fixture
def client():
    """
    FastAPI test client for making requests to your endpoints.
    This is synchronous and perfect for simple API testing.
    """
    return TestClient(app)


@pytest.fixture
def mock_services():
    """Mock the services layer HTTP responses"""
    with respx.mock:
        # Mock GET /patients (list)
        respx.get(f"{SERVICES_URL}/patients").mock(
            return_value=Response(200, json=[
                {"id": "patient-001", "name": "Sarah Johnson", "dateOfBirth": "1985-03-15", "mrn": "MRN-10001"},
                {"id": "patient-002", "name": "Michael Chen", "dateOfBirth": "1972-08-22", "mrn": "MRN-10002"},
            ])
        )

        # Mock GET /patients/{id} - valid patient
        respx.get(f"{SERVICES_URL}/patients/patient-001").mock(
            return_value=Response(200, json={
                "id": "patient-001", "name": "Sarah Johnson", "dateOfBirth": "1985-03-15", "mrn": "MRN-10001"
            })
        )

        # Mock GET /patients/{id}/allergies
        respx.get(f"{SERVICES_URL}/patients/patient-001/allergies").mock(
            return_value=Response(200, json=[
                {"id": "allergy-1", "allergen": "Penicillin", "reaction": "Anaphylaxis", "severity": "severe", "documented": "2020-01-15"},
            ])
        )

        # Mock GET /patients/{id}/medications
        respx.get(f"{SERVICES_URL}/patients/patient-001/medications").mock(
            return_value=Response(200, json=[
                {"id": "med-1", "name": "Lisinopril", "dosage": "10mg", "frequency": "daily", "started": "2023-06-15"},
            ])
        )

        # Mock 404 for unknown patient
        respx.get(f"{SERVICES_URL}/patients/unknown-id").mock(return_value=Response(404))
        respx.get(f"{SERVICES_URL}/patients/unknown-id/allergies").mock(return_value=Response(404))
        respx.get(f"{SERVICES_URL}/patients/unknown-id/medications").mock(return_value=Response(404))

        # Mock 422 Unprocessable Content for invalid ID format
        respx.get(f"{SERVICES_URL}/patients/invalid-id-format").mock(return_value=Response(422))
        respx.get(f"{SERVICES_URL}/patients/invalid-id-format/allergies").mock(return_value=Response(422))
        respx.get(f"{SERVICES_URL}/patients/invalid-id-format/medications").mock(return_value=Response(422))

        yield
