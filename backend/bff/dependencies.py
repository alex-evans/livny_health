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
    ImagingStudyRepository,
    VitalSignRepository,
    SocialFamilyHistoryRepository,
    ClinicalAlertRepository,
)
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
    ClinicalAlertService,
    ClinicalAlertServiceBuilder,
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
_imaging_study_repo: ImagingStudyRepository | None = None
_vitals_repo: VitalSignRepository | None = None
_social_family_history_repo: SocialFamilyHistoryRepository | None = None
_clinical_alert_repo: ClinicalAlertRepository | None = None

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
_clinical_alert_service: ClinicalAlertService | None = None

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


def get_imaging_study_repo() -> ImagingStudyRepository:
    global _imaging_study_repo
    if _imaging_study_repo is None:
        _imaging_study_repo = ImagingStudyRepository()
    return _imaging_study_repo


def get_imaging_service() -> ImagingService:
    global _imaging_service
    if _imaging_service is None:
        _imaging_service = ImagingService(
            imaging_study_repo=get_imaging_study_repo(),
        )
    return _imaging_service


def get_vitals_repo() -> VitalSignRepository:
    global _vitals_repo
    if _vitals_repo is None:
        _vitals_repo = VitalSignRepository()
    return _vitals_repo


def get_vitals_service() -> VitalsService:
    global _vitals_service
    if _vitals_service is None:
        _vitals_service = VitalsService(
            vitals_repo=get_vitals_repo(),
        )
    return _vitals_service


def get_social_family_history_repo() -> SocialFamilyHistoryRepository:
    global _social_family_history_repo
    if _social_family_history_repo is None:
        _social_family_history_repo = SocialFamilyHistoryRepository()
    return _social_family_history_repo


def get_social_family_history_service() -> SocialFamilyHistoryService:
    global _social_family_history_service
    if _social_family_history_service is None:
        _social_family_history_service = SocialFamilyHistoryService(
            social_family_history_repo=get_social_family_history_repo(),
        )
    return _social_family_history_service


def get_clinical_alert_repo() -> ClinicalAlertRepository:
    global _clinical_alert_repo
    if _clinical_alert_repo is None:
        _clinical_alert_repo = ClinicalAlertRepository()
    return _clinical_alert_repo


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
