"""
Services layer.

Business logic that orchestrates resources and provides application functionality.
"""

from .clinical_decision import (
    ClinicalDecisionService,
    AllergyAlert,
    DrugInteraction,
    AllergyOverrideLog,
    InteractionOverrideLog,
)
from .prescribing import (
    PrescribingService,
    PrescriptionResult,
    PatientNotFoundError,
    AllergyConflictError,
    DrugInteractionError,
)
from .scheduling import (
    SchedulingService,
    ScheduleResult,
    ProviderNotFoundError,
    AppointmentNotFoundError,
)
from .medication_search import (
    MedicationSearchService,
    get_common_dosing,
    get_default_duration,
)
from .lab_history import (
    LabHistoryService,
    LabHistoryResponse,
)
from .visit_history import (
    VisitHistoryService,
    VisitHistoryResponse,
)
from .problem_list import (
    ProblemListService,
    ProblemListResponse,
)
from .problem_clinical_context import (
    ProblemClinicalContextService,
)
from .problem_detail import (
    ProblemDetailService,
    ProblemDetailResponse,
)
from .imaging_service import (
    ImagingService,
    ImagingStudiesResponse,
)
from .vitals_service import (
    VitalsService,
    VitalsResponse,
    VitalHistoryResponse,
    CurrentVitalResponse,
    BMIResponse,
)
from .social_family_history_service import (
    SocialFamilyHistoryService,
    SocialFamilyHistoryResponse,
)
from .chart_section_service import (
    ChartSectionService,
    ChartSectionServiceResponse,
from .clinical_alert_service import (
    ClinicalAlertService,
    ClinicalAlertServiceBuilder,
    AlertsResponse,
)
from .alert_generators import (
    AlertGenerator,
    LabAlertGenerator,
    VitalAlertGenerator,
    ImagingAlertGenerator,
    ScreeningAlertGenerator,
    ChronicDiseaseAlertGenerator,
)
from .alert_thresholds import (
    CRITICAL_LAB_THRESHOLDS,
    CRITICAL_VITAL_THRESHOLDS,
    SCREENING_INTERVALS,
    get_lab_severity,
    get_vital_severity,
)

__all__ = [
    # Clinical Decision
    "ClinicalDecisionService",
    "AllergyAlert",
    "DrugInteraction",
    "AllergyOverrideLog",
    "InteractionOverrideLog",
    # Prescribing
    "PrescribingService",
    "PrescriptionResult",
    "PatientNotFoundError",
    "AllergyConflictError",
    "DrugInteractionError",
    # Scheduling
    "SchedulingService",
    "ScheduleResult",
    "ProviderNotFoundError",
    "AppointmentNotFoundError",
    # Medication Search
    "MedicationSearchService",
    "get_common_dosing",
    "get_default_duration",
    # Lab History
    "LabHistoryService",
    "LabHistoryResponse",
    # Visit History
    "VisitHistoryService",
    "VisitHistoryResponse",
    # Problem List
    "ProblemListService",
    "ProblemListResponse",
    # Problem Clinical Context
    "ProblemClinicalContextService",
    # Problem Detail
    "ProblemDetailService",
    "ProblemDetailResponse",
    # Imaging
    "ImagingService",
    "ImagingStudiesResponse",
    # Vitals
    "VitalsService",
    "VitalsResponse",
    "VitalHistoryResponse",
    "CurrentVitalResponse",
    "BMIResponse",
    # Social Family History
    "SocialFamilyHistoryService",
    "SocialFamilyHistoryResponse",
    # Chart Section
    "ChartSectionService",
    "ChartSectionServiceResponse",
    # Clinical Alerts
    "ClinicalAlertService",
    "ClinicalAlertServiceBuilder",
    "AlertsResponse",
    "AlertGenerator",
    "LabAlertGenerator",
    "VitalAlertGenerator",
    "ImagingAlertGenerator",
    "ScreeningAlertGenerator",
    "ChronicDiseaseAlertGenerator",
    "CRITICAL_LAB_THRESHOLDS",
    "CRITICAL_VITAL_THRESHOLDS",
    "SCREENING_INTERVALS",
    "get_lab_severity",
    "get_vital_severity",
]
