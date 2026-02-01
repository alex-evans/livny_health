"""
FHIR-aligned resources package.

This package contains all resource models and repositories for the EHR system.
"""

from .patient import (
    Patient,
    PatientRepository,
    Problem,
    ProblemStatus,
    ProblemPriority,
    ProblemSeverity,
    ClinicalCategory,
    ProblemComplexity,
    RelatedVisit,
    RelatedMedication,
    RelatedLabResult,
    RecentVitals,
    Insurance,
    AllergyReviewStatus,
)
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
from .visit_note import (
    VisitNote,
    SOAPNote,
    VisitVitals,
    VisitMedication,
    VisitOrder,
    VisitDiagnosis,
    VisitProvider,
    MedicationAction,
    OrderType,
    OrderStatus,
    OrderPriority,
    VisitNoteRepository,
)
from .imaging_study import (
    ImagingStudy,
    ImagingModality,
    ReportStatus,
    RadiologyReport,
    ComparisonStudy,
    MODALITY_NAMES,
    ImagingStudyRepository,
)
from .vitals import (
    VitalSign,
    VitalSignHistory,
    VitalTrendAnalysis,
    VitalType,
    VitalStatus,
    TrendDirection,
    ClinicalSignificance,
    VITAL_REFERENCE_RANGES,
    LOWER_IS_BETTER_VITALS,
    HIGHER_IS_BETTER_VITALS,
    VitalSignRepository,
)
from .social_family_history import (
    SocialFamilyHistory,
    SocialHistory,
    FamilyHistory,
    SmokingHistory,
    AlcoholHistory,
    SubstanceUseHistory,
    FamilyMember,
    FamilyMemberCondition,
    SignificantCondition,
    RiskAssessment,
    SmokingStatus,
    AlcoholUse,
    SubstanceUseLevel,
    ExerciseLevel,
    DietType,
    MaritalStatus,
    RelativeDegree,
    RelativeType,
    RiskLevel,
    AdoptionStatus,
    RELATIVE_DEGREE_MAP,
    SocialFamilyHistoryRepository,
)
from .chart_section import (
    AlertLevel,
    SectionIcon,
    KeyboardShortcut,
    ChartSection,
    ChartSectionsResponse,
)
from .clinical_alert import (
    ClinicalAlert,
    AlertAcknowledgment,
    AlertSummary,
    AlertType,
    AlertSeverity,
    AlertStatus,
    ClinicalAlertRepository,
)
from .encounter_note_version import (
    EncounterNoteVersion,
    SaveType,
    EncounterNoteVersionRepository,
)
from .encounter_status_history import (
    EncounterStatusHistory,
    EncounterStatusHistoryRepository,
)
from .encounter_prompt import (
    EncounterPrompt,
    PromptGenerationResult,
    PromptType,
    PromptStatus,
    ViewerSection,
    EncounterPromptRepository,
)

__all__ = [
    # Patient
    "Patient",
    "PatientRepository",
    "Problem",
    "ProblemStatus",
    "ProblemPriority",
    "ProblemSeverity",
    "ClinicalCategory",
    "ProblemComplexity",
    "RelatedVisit",
    "RelatedMedication",
    "RelatedLabResult",
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
    # VisitNote
    "VisitNote",
    "SOAPNote",
    "VisitVitals",
    "VisitMedication",
    "VisitOrder",
    "VisitDiagnosis",
    "VisitProvider",
    "MedicationAction",
    "OrderType",
    "OrderStatus",
    "OrderPriority",
    "VisitNoteRepository",
    # ImagingStudy
    "ImagingStudy",
    "ImagingModality",
    "ReportStatus",
    "RadiologyReport",
    "ComparisonStudy",
    "MODALITY_NAMES",
    "ImagingStudyRepository",
    # VitalSigns
    "VitalSign",
    "VitalSignHistory",
    "VitalTrendAnalysis",
    "VitalType",
    "VitalStatus",
    "TrendDirection",
    "ClinicalSignificance",
    "VITAL_REFERENCE_RANGES",
    "LOWER_IS_BETTER_VITALS",
    "HIGHER_IS_BETTER_VITALS",
    "VitalSignRepository",
    # SocialFamilyHistory
    "SocialFamilyHistory",
    "SocialHistory",
    "FamilyHistory",
    "SmokingHistory",
    "AlcoholHistory",
    "SubstanceUseHistory",
    "FamilyMember",
    "FamilyMemberCondition",
    "SignificantCondition",
    "RiskAssessment",
    "SmokingStatus",
    "AlcoholUse",
    "SubstanceUseLevel",
    "ExerciseLevel",
    "DietType",
    "MaritalStatus",
    "RelativeDegree",
    "RelativeType",
    "RiskLevel",
    "AdoptionStatus",
    "RELATIVE_DEGREE_MAP",
    "SocialFamilyHistoryRepository",
    # ChartSection
    "AlertLevel",
    "SectionIcon",
    "KeyboardShortcut",
    "ChartSection",
    "ChartSectionsResponse",
    # ClinicalAlert
    "ClinicalAlert",
    "AlertAcknowledgment",
    "AlertSummary",
    "AlertType",
    "AlertSeverity",
    "AlertStatus",
    "ClinicalAlertRepository",
    # EncounterNoteVersion
    "EncounterNoteVersion",
    "SaveType",
    "EncounterNoteVersionRepository",
    # EncounterStatusHistory
    "EncounterStatusHistory",
    "EncounterStatusHistoryRepository",
    # EncounterPrompt
    "EncounterPrompt",
    "PromptGenerationResult",
    "PromptType",
    "PromptStatus",
    "ViewerSection",
    "EncounterPromptRepository",
]
