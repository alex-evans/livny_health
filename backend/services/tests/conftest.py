"""
Fixtures for services tests.
"""
import asyncio
import pytest
import sys
from pathlib import Path

# Add parent directories to Python path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from resources import (
    PatientRepository,
    PractitionerRepository,
    AllergyIntoleranceRepository,
    MedicationRepository,
    MedicationRequestRepository,
    EncounterRepository,
    AppointmentRepository,
    VisitNoteRepository,
)
from services import (
    ClinicalDecisionService,
    PrescribingService,
    SchedulingService,
    MedicationSearchService,
    VisitHistoryService,
)
from services.data_seeder import seed_all


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.fixture(scope="module")
def repositories():
    """Create and seed repositories for testing."""
    patient_repo = PatientRepository()
    practitioner_repo = PractitionerRepository()
    allergy_repo = AllergyIntoleranceRepository()
    medication_repo = MedicationRepository()
    medication_request_repo = MedicationRequestRepository()
    encounter_repo = EncounterRepository()
    appointment_repo = AppointmentRepository()
    visit_note_repo = VisitNoteRepository()

    # Seed with test data
    seed_all(
        patient_repo=patient_repo,
        practitioner_repo=practitioner_repo,
        allergy_repo=allergy_repo,
        medication_request_repo=medication_request_repo,
        appointment_repo=appointment_repo,
        encounter_repo=encounter_repo,
        visit_note_repo=visit_note_repo,
    )

    return {
        "patient": patient_repo,
        "practitioner": practitioner_repo,
        "allergy": allergy_repo,
        "medication": medication_repo,
        "medication_request": medication_request_repo,
        "encounter": encounter_repo,
        "appointment": appointment_repo,
        "visit_note": visit_note_repo,
    }


@pytest.fixture
def clinical_decision_service(repositories):
    """Create a ClinicalDecisionService for testing."""
    return ClinicalDecisionService(
        allergy_repo=repositories["allergy"],
        medication_request_repo=repositories["medication_request"],
    )


@pytest.fixture
def prescribing_service(repositories, clinical_decision_service):
    """Create a PrescribingService for testing."""
    return PrescribingService(
        patient_repo=repositories["patient"],
        medication_request_repo=repositories["medication_request"],
        clinical_decision_service=clinical_decision_service,
    )


@pytest.fixture
def scheduling_service(repositories):
    """Create a SchedulingService for testing."""
    return SchedulingService(
        patient_repo=repositories["patient"],
        practitioner_repo=repositories["practitioner"],
        appointment_repo=repositories["appointment"],
        encounter_repo=repositories["encounter"],
    )


@pytest.fixture
def medication_search_service(repositories):
    """Create a MedicationSearchService for testing."""
    return MedicationSearchService(
        medication_repo=repositories["medication"],
    )


@pytest.fixture
def visit_history_service(repositories):
    """Create a VisitHistoryService for testing."""
    return VisitHistoryService(
        visit_note_repo=repositories["visit_note"],
    )
