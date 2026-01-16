"""
FHIR-aligned resources package.

This package contains all resource models and repositories for the EHR system.
"""

from .patient import Patient, PatientRepository, Problem, RecentVitals, Insurance
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

__all__ = [
    # Patient
    "Patient",
    "PatientRepository",
    "Problem",
    "RecentVitals",
    "Insurance",
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
]
