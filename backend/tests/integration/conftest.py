"""
Fixtures for integration tests.

Unlike unit test fixtures which mock dependencies, integration test fixtures
provide real implementations that allow testing the full stack.
"""
import asyncio
import pytest
import sys
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient

from main import app
from bff.dependencies import (
    ensure_data_seeded,
    get_patient_repo,
    get_practitioner_repo,
    get_allergy_repo,
    get_medication_repo,
    get_medication_request_repo,
    get_encounter_repo,
    get_appointment_repo,
    get_lab_result_repo,
    get_clinical_decision_service,
    get_prescribing_service,
    get_scheduling_service,
    get_medication_search_service,
    get_lab_history_service,
)


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.fixture(scope="module")
def seeded_app():
    """
    Provides a FastAPI test client with seeded data.

    Scope is 'module' so data is seeded once per test module,
    making tests faster while still providing isolation between modules.
    """
    ensure_data_seeded()
    return TestClient(app)


@pytest.fixture
def client(seeded_app):
    """Alias for seeded_app for cleaner test signatures."""
    return seeded_app


@pytest.fixture(scope="module")
def repositories():
    """
    Provides access to all repositories with seeded data.

    These are the real in-memory repositories, not mocks.
    Integration tests use these to verify data changes.
    """
    ensure_data_seeded()
    return {
        "patient": get_patient_repo(),
        "practitioner": get_practitioner_repo(),
        "allergy": get_allergy_repo(),
        "medication": get_medication_repo(),
        "medication_request": get_medication_request_repo(),
        "encounter": get_encounter_repo(),
        "appointment": get_appointment_repo(),
        "lab_result": get_lab_result_repo(),
    }


@pytest.fixture(scope="module")
def services():
    """
    Provides access to all services with real dependencies.

    Unlike unit tests where services have mocked dependencies,
    integration test services use real repositories.
    """
    ensure_data_seeded()
    return {
        "clinical_decision": get_clinical_decision_service(),
        "prescribing": get_prescribing_service(),
        "scheduling": get_scheduling_service(),
        "medication_search": get_medication_search_service(),
        "lab_history": get_lab_history_service(),
    }


# Test data constants - these match the seeded data
class TestPatients:
    """Known patient data from seed for test assertions."""
    SARAH_JOHNSON = {
        "id": "patient-001",
        "name": "Sarah Johnson",
        "allergies": ["Penicillin", "Sulfa"],
        "allergy_severities": {"Penicillin": "severe", "Sulfa": "moderate"},
    }
    MICHAEL_CHEN = {
        "id": "patient-002",
        "name": "Michael Chen",
        "allergies": ["Aspirin"],
    }
    EMILY_RODRIGUEZ = {
        "id": "patient-003",
        "name": "Emily Rodriguez",
        "allergies": [],  # No allergies
    }
    ROBERT_THOMPSON = {
        "id": "patient-006",
        "name": "Robert Thompson",
        "medications": ["Warfarin", "Lisinopril"],
    }
    PATRICIA_MARTINEZ = {
        "id": "patient-007",
        "name": "Patricia Martinez",
        "medications": ["Warfarin", "Simvastatin", "Sertraline", "Lisinopril"],
    }


class TestProviders:
    """Known provider data from seed."""
    DR_FROST = {
        "id": "provider-001",
        "name": "Dr. Elizabeth Frost",
    }
