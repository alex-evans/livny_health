"""
Dependency injection for the BFF layer.

Creates and manages singleton instances of repositories and services.
"""

import sys
from pathlib import Path

# Add backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from resources import (
    PatientRepository,
    PractitionerRepository,
    AllergyIntoleranceRepository,
    MedicationRepository,
    MedicationRequestRepository,
    EncounterRepository,
    AppointmentRepository,
    LabResultRepository,
    VisitNoteRepository,
)
from services import (
    ClinicalDecisionService,
    PrescribingService,
    SchedulingService,
    MedicationSearchService,
    LabHistoryService,
    VisitHistoryService,
)
from services.data_seeder import seed_all


# Singleton repository instances
_patient_repo: PatientRepository | None = None
_practitioner_repo: PractitionerRepository | None = None
_allergy_repo: AllergyIntoleranceRepository | None = None
_medication_repo: MedicationRepository | None = None
_medication_request_repo: MedicationRequestRepository | None = None
_encounter_repo: EncounterRepository | None = None
_appointment_repo: AppointmentRepository | None = None
_lab_result_repo: LabResultRepository | None = None
_visit_note_repo: VisitNoteRepository | None = None

# Singleton service instances
_clinical_decision_service: ClinicalDecisionService | None = None
_prescribing_service: PrescribingService | None = None
_scheduling_service: SchedulingService | None = None
_medication_search_service: MedicationSearchService | None = None
_lab_history_service: LabHistoryService | None = None
_visit_history_service: VisitHistoryService | None = None

# Track if data has been seeded
_data_seeded: bool = False


def get_patient_repo() -> PatientRepository:
    global _patient_repo
    if _patient_repo is None:
        _patient_repo = PatientRepository()
    return _patient_repo


def get_practitioner_repo() -> PractitionerRepository:
    global _practitioner_repo
    if _practitioner_repo is None:
        _practitioner_repo = PractitionerRepository()
    return _practitioner_repo


def get_allergy_repo() -> AllergyIntoleranceRepository:
    global _allergy_repo
    if _allergy_repo is None:
        _allergy_repo = AllergyIntoleranceRepository()
    return _allergy_repo


def get_medication_repo() -> MedicationRepository:
    global _medication_repo
    if _medication_repo is None:
        _medication_repo = MedicationRepository()
    return _medication_repo


def get_medication_request_repo() -> MedicationRequestRepository:
    global _medication_request_repo
    if _medication_request_repo is None:
        _medication_request_repo = MedicationRequestRepository()
    return _medication_request_repo


def get_encounter_repo() -> EncounterRepository:
    global _encounter_repo
    if _encounter_repo is None:
        _encounter_repo = EncounterRepository()
    return _encounter_repo


def get_appointment_repo() -> AppointmentRepository:
    global _appointment_repo
    if _appointment_repo is None:
        _appointment_repo = AppointmentRepository()
    return _appointment_repo


def get_lab_result_repo() -> LabResultRepository:
    global _lab_result_repo
    if _lab_result_repo is None:
        _lab_result_repo = LabResultRepository()
    return _lab_result_repo


def get_clinical_decision_service() -> ClinicalDecisionService:
    global _clinical_decision_service
    if _clinical_decision_service is None:
        _clinical_decision_service = ClinicalDecisionService(
            allergy_repo=get_allergy_repo(),
            medication_request_repo=get_medication_request_repo(),
        )
    return _clinical_decision_service


def get_prescribing_service() -> PrescribingService:
    global _prescribing_service
    if _prescribing_service is None:
        _prescribing_service = PrescribingService(
            patient_repo=get_patient_repo(),
            medication_request_repo=get_medication_request_repo(),
            clinical_decision_service=get_clinical_decision_service(),
        )
    return _prescribing_service


def get_scheduling_service() -> SchedulingService:
    global _scheduling_service
    if _scheduling_service is None:
        _scheduling_service = SchedulingService(
            patient_repo=get_patient_repo(),
            practitioner_repo=get_practitioner_repo(),
            appointment_repo=get_appointment_repo(),
            encounter_repo=get_encounter_repo(),
        )
    return _scheduling_service


def get_medication_search_service() -> MedicationSearchService:
    global _medication_search_service
    if _medication_search_service is None:
        _medication_search_service = MedicationSearchService(
            medication_repo=get_medication_repo(),
        )
    return _medication_search_service


def get_lab_history_service() -> LabHistoryService:
    global _lab_history_service
    if _lab_history_service is None:
        _lab_history_service = LabHistoryService(
            lab_result_repo=get_lab_result_repo(),
        )
    return _lab_history_service


def get_visit_note_repo() -> VisitNoteRepository:
    global _visit_note_repo
    if _visit_note_repo is None:
        _visit_note_repo = VisitNoteRepository()
    return _visit_note_repo


def get_visit_history_service() -> VisitHistoryService:
    global _visit_history_service
    if _visit_history_service is None:
        _visit_history_service = VisitHistoryService(
            visit_note_repo=get_visit_note_repo(),
        )
    return _visit_history_service


def ensure_data_seeded() -> None:
    """Ensure repositories are seeded with initial data."""
    global _data_seeded
    if not _data_seeded:
        seed_all(
            patient_repo=get_patient_repo(),
            practitioner_repo=get_practitioner_repo(),
            allergy_repo=get_allergy_repo(),
            medication_request_repo=get_medication_request_repo(),
            appointment_repo=get_appointment_repo(),
            encounter_repo=get_encounter_repo(),
            visit_note_repo=get_visit_note_repo(),
        )
        _data_seeded = True
