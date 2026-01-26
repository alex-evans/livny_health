"""
SQLAlchemy ORM models for all domain resources.

These models represent the database schema for PostgreSQL storage.
Complex nested data structures are stored as JSONB columns.
"""

from db.models.patient import PatientORM
from db.models.practitioner import PractitionerORM
from db.models.medication import MedicationORM
from db.models.medication_request import MedicationRequestORM
from db.models.allergy_intolerance import AllergyIntoleranceORM
from db.models.encounter import EncounterORM
from db.models.appointment import AppointmentORM
from db.models.lab_result import LabResultORM
from db.models.vital_sign import VitalSignORM
from db.models.visit_note import VisitNoteORM
from db.models.imaging_study import ImagingStudyORM
from db.models.social_family_history import SocialFamilyHistoryORM
from db.models.clinical_alert import ClinicalAlertORM

__all__ = [
    "PatientORM",
    "PractitionerORM",
    "MedicationORM",
    "MedicationRequestORM",
    "AllergyIntoleranceORM",
    "EncounterORM",
    "AppointmentORM",
    "LabResultORM",
    "VitalSignORM",
    "VisitNoteORM",
    "ImagingStudyORM",
    "SocialFamilyHistoryORM",
    "ClinicalAlertORM",
]
