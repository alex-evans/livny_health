"""
FHIR-aligned resources package.

This package contains all resource models and repositories for the EHR system.
"""

from .patient import Patient, PatientRepository, Problem, RecentVitals, Insurance, AllergyReviewStatus
from .practitioner import Practitioner, PractitionerRepository
from .allergy_intolerance import (
    AllergyIntolerance,
    AllergyReaction,
    AllergyCategory,
    AllergyCriticality,
    AllergyIntoleranceRepository,
)
from .medication import Medication, MedicationRepository
from .medication_request import (
    MedicationRequest,
    MedicationRequestStatus,
    MedicationRequestIntent,
    MedicationForm,
    Dosage,
    MedicationRequestRepository,
)
from .encounter import (
    Encounter,
    EncounterStatus,
    EncounterClass,
    EncounterParticipant,
    EncounterRepository,
)
from .appointment import (
    Appointment,
    AppointmentStatus,
    AppointmentParticipant,
    AppointmentFlag,
    AppointmentRepository,
)
from .lab_result import (
    LabResult,
    LabResultHistory,
    LabResultStatus,
    TrendAnalysis,
    LabResultRepository,
)

__all__ = [
    # Patient
    "Patient",
    "PatientRepository",
    "Problem",
    "RecentVitals",
    "Insurance",
    "AllergyReviewStatus",
    # Practitioner
    "Practitioner",
    "PractitionerRepository",
    # AllergyIntolerance
    "AllergyIntolerance",
    "AllergyReaction",
    "AllergyCategory",
    "AllergyCriticality",
    "AllergyIntoleranceRepository",
    # Medication
    "Medication",
    "MedicationRepository",
    # MedicationRequest
    "MedicationRequest",
    "MedicationRequestStatus",
    "MedicationRequestIntent",
    "MedicationForm",
    "Dosage",
    "MedicationRequestRepository",
    # Encounter
    "Encounter",
    "EncounterStatus",
    "EncounterClass",
    "EncounterParticipant",
    "EncounterRepository",
    # Appointment
    "Appointment",
    "AppointmentStatus",
    "AppointmentParticipant",
    "AppointmentFlag",
    "AppointmentRepository",
    # LabResult
    "LabResult",
    "LabResultHistory",
    "LabResultStatus",
    "TrendAnalysis",
    "LabResultRepository",
]
