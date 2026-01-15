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
]
