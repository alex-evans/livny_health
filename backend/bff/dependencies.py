"""
Dependency injection for the BFF layer.

Creates and manages singleton instances of repositories and services.
Supports both in-memory and PostgreSQL backends based on configuration.
"""

import sys
from pathlib import Path
from typing import Any

# Add backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from config import get_settings

# In-memory repository imports
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
    ImagingStudyRepository,
    VitalSignRepository,
    SocialFamilyHistoryRepository,
    ClinicalAlertRepository,
)

# PostgreSQL repository imports
from resources.patient.postgres_repository import PostgresPatientRepository
from resources.practitioner.postgres_repository import PostgresPractitionerRepository
from resources.medication.postgres_repository import PostgresMedicationRepository
from resources.medication_request.postgres_repository import (
    PostgresMedicationRequestRepository,
)
from resources.allergy_intolerance.postgres_repository import (
    PostgresAllergyIntoleranceRepository,
)
from resources.encounter.postgres_repository import PostgresEncounterRepository
from resources.appointment.postgres_repository import PostgresAppointmentRepository
from resources.lab_result.postgres_repository import PostgresLabResultRepository
from resources.vitals.postgres_repository import PostgresVitalSignRepository
from resources.visit_note.postgres_repository import PostgresVisitNoteRepository
from resources.imaging_study.postgres_repository import PostgresImagingStudyRepository
from resources.social_family_history.postgres_repository import (
    PostgresSocialFamilyHistoryRepository,
)
from resources.clinical_alert.postgres_repository import PostgresClinicalAlertRepository

# Service imports
from services import (
    ClinicalDecisionService,
    PrescribingService,
    SchedulingService,
    MedicationSearchService,
    LabHistoryService,
    VisitHistoryService,
    ProblemListService,
    ProblemClinicalContextService,
    ProblemDetailService,
    ImagingService,
    VitalsService,
    SocialFamilyHistoryService,
    ChartSectionService,
    ClinicalAlertService,
    ClinicalAlertServiceBuilder,
)
from services.data_seeder import seed_all


# Session factory for postgres (initialized at startup)
_session_factory = None


# Singleton repository instances
_patient_repo = None
_practitioner_repo = None
_allergy_repo = None
_medication_repo = None
_medication_request_repo = None
_encounter_repo = None
_appointment_repo = None
_lab_result_repo = None
_visit_note_repo = None
_imaging_study_repo = None
_vitals_repo = None
_social_family_history_repo = None
_clinical_alert_repo = None

# Singleton service instances
_clinical_decision_service: ClinicalDecisionService | None = None
_prescribing_service: PrescribingService | None = None
_scheduling_service: SchedulingService | None = None
_medication_search_service: MedicationSearchService | None = None
_lab_history_service: LabHistoryService | None = None
_visit_history_service: VisitHistoryService | None = None
_problem_list_service: ProblemListService | None = None
_problem_clinical_context_service: ProblemClinicalContextService | None = None
_problem_detail_service: ProblemDetailService | None = None
_imaging_service: ImagingService | None = None
_vitals_service: VitalsService | None = None
_social_family_history_service: SocialFamilyHistoryService | None = None
_chart_section_service: ChartSectionService | None = None
_clinical_alert_service: ClinicalAlertService | None = None

# Track if data has been seeded
_data_seeded: bool = False


def _is_postgres() -> bool:
    """Check if using postgres backend."""
    return get_settings().storage_backend == "postgres"


def set_session_factory(factory) -> None:
    """Set the session factory for postgres repositories."""
    global _session_factory
    _session_factory = factory


def get_session_factory():
    """Get the session factory for postgres repositories."""
    return _session_factory


def get_patient_repo():
    global _patient_repo
    if _patient_repo is None:
        if _is_postgres():
            _patient_repo = PostgresPatientRepository(_session_factory)
        else:
            _patient_repo = PatientRepository()
    return _patient_repo


def get_practitioner_repo():
    global _practitioner_repo
    if _practitioner_repo is None:
        if _is_postgres():
            _practitioner_repo = PostgresPractitionerRepository(_session_factory)
        else:
            _practitioner_repo = PractitionerRepository()
    return _practitioner_repo


def get_allergy_repo():
    global _allergy_repo
    if _allergy_repo is None:
        if _is_postgres():
            _allergy_repo = PostgresAllergyIntoleranceRepository(_session_factory)
        else:
            _allergy_repo = AllergyIntoleranceRepository()
    return _allergy_repo


def get_medication_repo():
    global _medication_repo
    if _medication_repo is None:
        if _is_postgres():
            _medication_repo = PostgresMedicationRepository(_session_factory)
        else:
            _medication_repo = MedicationRepository()
    return _medication_repo


def get_medication_request_repo():
    global _medication_request_repo
    if _medication_request_repo is None:
        if _is_postgres():
            _medication_request_repo = PostgresMedicationRequestRepository(
                _session_factory
            )
        else:
            _medication_request_repo = MedicationRequestRepository()
    return _medication_request_repo


def get_encounter_repo():
    global _encounter_repo
    if _encounter_repo is None:
        if _is_postgres():
            _encounter_repo = PostgresEncounterRepository(_session_factory)
        else:
            _encounter_repo = EncounterRepository()
    return _encounter_repo


def get_appointment_repo():
    global _appointment_repo
    if _appointment_repo is None:
        if _is_postgres():
            _appointment_repo = PostgresAppointmentRepository(_session_factory)
        else:
            _appointment_repo = AppointmentRepository()
    return _appointment_repo


def get_lab_result_repo():
    global _lab_result_repo
    if _lab_result_repo is None:
        if _is_postgres():
            _lab_result_repo = PostgresLabResultRepository(_session_factory)
        else:
            _lab_result_repo = LabResultRepository()
    return _lab_result_repo


def get_visit_note_repo():
    global _visit_note_repo
    if _visit_note_repo is None:
        if _is_postgres():
            _visit_note_repo = PostgresVisitNoteRepository(_session_factory)
        else:
            _visit_note_repo = VisitNoteRepository()
    return _visit_note_repo


def get_imaging_study_repo():
    global _imaging_study_repo
    if _imaging_study_repo is None:
        if _is_postgres():
            _imaging_study_repo = PostgresImagingStudyRepository(_session_factory)
        else:
            _imaging_study_repo = ImagingStudyRepository()
    return _imaging_study_repo


def get_vitals_repo():
    global _vitals_repo
    if _vitals_repo is None:
        if _is_postgres():
            _vitals_repo = PostgresVitalSignRepository(_session_factory)
        else:
            _vitals_repo = VitalSignRepository()
    return _vitals_repo


def get_social_family_history_repo():
    global _social_family_history_repo
    if _social_family_history_repo is None:
        if _is_postgres():
            _social_family_history_repo = PostgresSocialFamilyHistoryRepository(
                _session_factory
            )
        else:
            _social_family_history_repo = SocialFamilyHistoryRepository()
    return _social_family_history_repo


def get_clinical_alert_repo():
    global _clinical_alert_repo
    if _clinical_alert_repo is None:
        if _is_postgres():
            _clinical_alert_repo = PostgresClinicalAlertRepository(_session_factory)
        else:
            _clinical_alert_repo = ClinicalAlertRepository()
    return _clinical_alert_repo


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


def get_visit_history_service() -> VisitHistoryService:
    global _visit_history_service
    if _visit_history_service is None:
        _visit_history_service = VisitHistoryService(
            visit_note_repo=get_visit_note_repo(),
        )
    return _visit_history_service


def get_problem_list_service() -> ProblemListService:
    global _problem_list_service
    if _problem_list_service is None:
        _problem_list_service = ProblemListService(
            patient_repo=get_patient_repo(),
        )
    return _problem_list_service


def get_problem_clinical_context_service() -> ProblemClinicalContextService:
    global _problem_clinical_context_service
    if _problem_clinical_context_service is None:
        _problem_clinical_context_service = ProblemClinicalContextService(
            patient_repo=get_patient_repo(),
            medication_repo=get_medication_request_repo(),
            visit_note_repo=get_visit_note_repo(),
            lab_result_repo=get_lab_result_repo(),
        )
    return _problem_clinical_context_service


def get_problem_detail_service() -> ProblemDetailService:
    global _problem_detail_service
    if _problem_detail_service is None:
        _problem_detail_service = ProblemDetailService(
            patient_repo=get_patient_repo(),
            medication_repo=get_medication_request_repo(),
            visit_note_repo=get_visit_note_repo(),
        )
    return _problem_detail_service


def get_imaging_service() -> ImagingService:
    global _imaging_service
    if _imaging_service is None:
        _imaging_service = ImagingService(
            imaging_study_repo=get_imaging_study_repo(),
        )
    return _imaging_service


def get_vitals_service() -> VitalsService:
    global _vitals_service
    if _vitals_service is None:
        _vitals_service = VitalsService(
            vitals_repo=get_vitals_repo(),
        )
    return _vitals_service


def get_social_family_history_service() -> SocialFamilyHistoryService:
    global _social_family_history_service
    if _social_family_history_service is None:
        _social_family_history_service = SocialFamilyHistoryService(
            social_family_history_repo=get_social_family_history_repo(),
        )
    return _social_family_history_service


def get_chart_section_service() -> ChartSectionService:
    global _chart_section_service
    if _chart_section_service is None:
        _chart_section_service = ChartSectionService(
            patient_repo=get_patient_repo(),
            allergy_repo=get_allergy_repo(),
            medication_request_repo=get_medication_request_repo(),
            visit_note_repo=get_visit_note_repo(),
            lab_result_repo=get_lab_result_repo(),
            imaging_study_repo=get_imaging_study_repo(),
            vitals_repo=get_vitals_repo(),
            social_family_history_repo=get_social_family_history_repo(),
        )
    return _chart_section_service


def get_clinical_alert_service() -> ClinicalAlertService:
    global _clinical_alert_service
    if _clinical_alert_service is None:
        _clinical_alert_service = ClinicalAlertServiceBuilder.build(
            alert_repo=get_clinical_alert_repo(),
            lab_result_repo=get_lab_result_repo(),
            vitals_repo=get_vitals_repo(),
            imaging_repo=get_imaging_study_repo(),
            patient_repo=get_patient_repo(),
            medication_request_repo=get_medication_request_repo(),
        )
    return _clinical_alert_service


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
            imaging_study_repo=get_imaging_study_repo(),
            vitals_repo=get_vitals_repo(),
            social_family_history_repo=get_social_family_history_repo(),
        )
        _data_seeded = True


async def ensure_data_seeded_async() -> None:
    """Ensure repositories are seeded with initial data (async version for postgres)."""
    global _data_seeded
    if not _data_seeded:
        from services.data_seeder import seed_all_async

        await seed_all_async(
            patient_repo=get_patient_repo(),
            practitioner_repo=get_practitioner_repo(),
            allergy_repo=get_allergy_repo(),
            medication_request_repo=get_medication_request_repo(),
            appointment_repo=get_appointment_repo(),
            encounter_repo=get_encounter_repo(),
            visit_note_repo=get_visit_note_repo(),
            imaging_study_repo=get_imaging_study_repo(),
            vitals_repo=get_vitals_repo(),
            social_family_history_repo=get_social_family_history_repo(),
            lab_result_repo=get_lab_result_repo(),
        )
        _data_seeded = True


def reset_singletons() -> None:
    """Reset all singleton instances. Useful for testing."""
    global _patient_repo, _practitioner_repo, _allergy_repo, _medication_repo
    global _medication_request_repo, _encounter_repo, _appointment_repo
    global _lab_result_repo, _visit_note_repo, _imaging_study_repo, _vitals_repo
    global _social_family_history_repo, _clinical_alert_repo
    global _clinical_decision_service, _prescribing_service, _scheduling_service
    global _medication_search_service, _lab_history_service, _visit_history_service
    global _problem_list_service, _problem_clinical_context_service
    global _problem_detail_service, _imaging_service, _vitals_service
    global _social_family_history_service, _chart_section_service
    global _clinical_alert_service, _data_seeded

    _patient_repo = None
    _practitioner_repo = None
    _allergy_repo = None
    _medication_repo = None
    _medication_request_repo = None
    _encounter_repo = None
    _appointment_repo = None
    _lab_result_repo = None
    _visit_note_repo = None
    _imaging_study_repo = None
    _vitals_repo = None
    _social_family_history_repo = None
    _clinical_alert_repo = None
    _clinical_decision_service = None
    _prescribing_service = None
    _scheduling_service = None
    _medication_search_service = None
    _lab_history_service = None
    _visit_history_service = None
    _problem_list_service = None
    _problem_clinical_context_service = None
    _problem_detail_service = None
    _imaging_service = None
    _vitals_service = None
    _social_family_history_service = None
    _chart_section_service = None
    _clinical_alert_service = None
    _data_seeded = False
