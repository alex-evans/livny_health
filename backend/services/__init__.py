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
]
