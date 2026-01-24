"""
Social and Family History resource model.

Represents patient social history (smoking, alcohol, occupation, etc.) and family
history (relatives with conditions, hereditary syndromes) along with risk assessments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import ClassVar, Literal

from resources.core import DomainResource, Reference


# Type definitions
SmokingStatus = Literal[
    "current_daily",
    "current_occasional",
    "former",
    "never",
    "unknown",
]

AlcoholUse = Literal[
    "none",
    "occasional",
    "moderate",
    "heavy",
    "in_recovery",
    "unknown",
]

SubstanceUseLevel = Literal[
    "none",
    "past",
    "current",
    "in_recovery",
    "unknown",
]

ExerciseLevel = Literal[
    "sedentary",
    "light",
    "moderate",
    "active",
    "very_active",
    "unknown",
]

DietType = Literal[
    "regular",
    "vegetarian",
    "vegan",
    "low_sodium",
    "low_carb",
    "diabetic",
    "heart_healthy",
    "other",
    "unknown",
]

MaritalStatus = Literal[
    "single",
    "married",
    "partnered",
    "divorced",
    "widowed",
    "separated",
    "unknown",
]

RelativeDegree = Literal[
    "first",
    "second",
    "third",
]

RelativeType = Literal[
    "mother",
    "father",
    "sister",
    "brother",
    "daughter",
    "son",
    "maternal_grandmother",
    "maternal_grandfather",
    "paternal_grandmother",
    "paternal_grandfather",
    "maternal_aunt",
    "maternal_uncle",
    "paternal_aunt",
    "paternal_uncle",
    "niece",
    "nephew",
    "cousin",
    "half_sibling",
    "other",
]

RiskLevel = Literal[
    "low",
    "moderate",
    "high",
]

AdoptionStatus = Literal[
    "not_adopted",
    "adopted_known_history",
    "adopted_unknown_history",
    "unknown",
]


# Maps relative types to their degree
RELATIVE_DEGREE_MAP: dict[RelativeType, RelativeDegree] = {
    "mother": "first",
    "father": "first",
    "sister": "first",
    "brother": "first",
    "daughter": "first",
    "son": "first",
    "maternal_grandmother": "second",
    "maternal_grandfather": "second",
    "paternal_grandmother": "second",
    "paternal_grandfather": "second",
    "maternal_aunt": "second",
    "maternal_uncle": "second",
    "paternal_aunt": "second",
    "paternal_uncle": "second",
    "half_sibling": "second",
    "niece": "second",
    "nephew": "second",
    "cousin": "third",
    "other": "third",
}


@dataclass
class SmokingHistory:
    """Smoking/tobacco history details."""
    status: SmokingStatus = "unknown"
    pack_years: float | None = None  # Number of pack-years
    quit_date: date | None = None
    notes: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "status": self.status,
            "packYears": self.pack_years,
            "quitDate": self.quit_date.isoformat() if self.quit_date else None,
            "notes": self.notes,
        }


@dataclass
class AlcoholHistory:
    """Alcohol use history details."""
    use_level: AlcoholUse = "unknown"
    drinks_per_week: int | None = None
    history_of_abuse: bool = False
    notes: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "useLevel": self.use_level,
            "drinksPerWeek": self.drinks_per_week,
            "historyOfAbuse": self.history_of_abuse,
            "notes": self.notes,
        }


@dataclass
class SubstanceUseHistory:
    """Substance use history details."""
    level: SubstanceUseLevel = "unknown"
    substances: list[str] = field(default_factory=list)
    iv_drug_use: bool = False
    notes: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "level": self.level,
            "substances": self.substances,
            "ivDrugUse": self.iv_drug_use,
            "notes": self.notes,
        }


@dataclass
class SocialHistory:
    """Complete social history for a patient."""
    smoking: SmokingHistory = field(default_factory=SmokingHistory)
    alcohol: AlcoholHistory = field(default_factory=AlcoholHistory)
    substance_use: SubstanceUseHistory = field(default_factory=SubstanceUseHistory)
    occupation: str | None = None
    occupation_hazards: list[str] = field(default_factory=list)
    living_situation: str | None = None
    marital_status: MaritalStatus = "unknown"
    exercise: ExerciseLevel = "unknown"
    diet: DietType = "unknown"
    diet_notes: str | None = None
    last_reviewed: datetime | None = None
    reviewed_by: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "smoking": self.smoking.to_dict(),
            "alcohol": self.alcohol.to_dict(),
            "substanceUse": self.substance_use.to_dict(),
            "occupation": self.occupation,
            "occupationHazards": self.occupation_hazards,
            "livingSituation": self.living_situation,
            "maritalStatus": self.marital_status,
            "exercise": self.exercise,
            "diet": self.diet,
            "dietNotes": self.diet_notes,
            "lastReviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
            "reviewedBy": self.reviewed_by,
        }


@dataclass
class FamilyMemberCondition:
    """A condition affecting a family member."""
    condition_name: str
    icd10_code: str | None = None
    age_at_onset: int | None = None
    notes: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "conditionName": self.condition_name,
            "icd10Code": self.icd10_code,
            "ageAtOnset": self.age_at_onset,
            "notes": self.notes,
        }


@dataclass
class FamilyMember:
    """A family member with their health history."""
    id: str
    relative_type: RelativeType
    is_living: bool = True
    age_at_death: int | None = None
    cause_of_death: str | None = None
    conditions: list[FamilyMemberCondition] = field(default_factory=list)

    @property
    def degree(self) -> RelativeDegree:
        """Get the degree of relationship."""
        return RELATIVE_DEGREE_MAP.get(self.relative_type, "third")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "relativeType": self.relative_type,
            "degree": self.degree,
            "isLiving": self.is_living,
            "ageAtDeath": self.age_at_death,
            "causeOfDeath": self.cause_of_death,
            "conditions": [c.to_dict() for c in self.conditions],
        }


@dataclass
class SignificantCondition:
    """A condition with significant family history."""
    condition_name: str
    icd10_code: str | None = None
    affected_relatives: list[str] = field(default_factory=list)  # List of relative types
    notes: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "conditionName": self.condition_name,
            "icd10Code": self.icd10_code,
            "affectedRelatives": self.affected_relatives,
            "notes": self.notes,
        }


@dataclass
class FamilyHistory:
    """Complete family history for a patient."""
    family_members: list[FamilyMember] = field(default_factory=list)
    significant_conditions: list[SignificantCondition] = field(default_factory=list)
    hereditary_syndromes: list[str] = field(default_factory=list)
    adoption_status: AdoptionStatus = "not_adopted"
    last_reviewed: datetime | None = None
    reviewed_by: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "familyMembers": [fm.to_dict() for fm in self.family_members],
            "significantConditions": [sc.to_dict() for sc in self.significant_conditions],
            "hereditarySyndromes": self.hereditary_syndromes,
            "adoptionStatus": self.adoption_status,
            "lastReviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
            "reviewedBy": self.reviewed_by,
        }


@dataclass
class RiskAssessment:
    """A calculated health risk assessment."""
    risk_type: str  # e.g., "cardiovascular", "cancer", "diabetes"
    risk_level: RiskLevel
    contributing_factors: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    screening_due: date | None = None
    calculated_at: datetime = field(default_factory=datetime.utcnow)
    notes: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "riskType": self.risk_type,
            "riskLevel": self.risk_level,
            "contributingFactors": self.contributing_factors,
            "recommendations": self.recommendations,
            "screeningDue": self.screening_due.isoformat() if self.screening_due else None,
            "calculatedAt": self.calculated_at.isoformat(),
            "notes": self.notes,
        }


@dataclass
class SocialFamilyHistory(DomainResource):
    """
    Combined social and family history for a patient.

    Represents the complete social history (smoking, alcohol, occupation, etc.)
    and family history (relatives, conditions, syndromes) with calculated risk
    assessments.
    """
    resource_type: ClassVar[str] = "SocialFamilyHistory"

    # For whom
    subject: Reference = field(default_factory=lambda: Reference(reference="Patient/unknown"))

    # History sections
    social_history: SocialHistory = field(default_factory=SocialHistory)
    family_history: FamilyHistory = field(default_factory=FamilyHistory)

    # Calculated risk assessments
    risk_assessments: list[RiskAssessment] = field(default_factory=list)

    @property
    def patient_id(self) -> str:
        """Get the patient ID from the subject reference."""
        return self.subject.id

    @property
    def last_reviewed(self) -> datetime | None:
        """Get the most recent review date from either history section."""
        social_reviewed = self.social_history.last_reviewed
        family_reviewed = self.family_history.last_reviewed

        if social_reviewed and family_reviewed:
            return max(social_reviewed, family_reviewed)
        return social_reviewed or family_reviewed

    @property
    def has_high_risk(self) -> bool:
        """Check if any risk assessment is high."""
        return any(ra.risk_level == "high" for ra in self.risk_assessments)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "resourceType": self.resource_type,
            "subject": self.subject.reference,
            "socialHistory": self.social_history.to_dict(),
            "familyHistory": self.family_history.to_dict(),
            "riskAssessments": [ra.to_dict() for ra in self.risk_assessments],
            "lastReviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
            "hasHighRisk": self.has_high_risk,
        }

    def to_bff_dict(self) -> dict:
        """Convert to BFF-friendly format."""
        return {
            "socialHistory": self.social_history.to_dict(),
            "familyHistory": self.family_history.to_dict(),
            "riskAssessments": [ra.to_dict() for ra in self.risk_assessments],
            "lastReviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
            "hasHighRisk": self.has_high_risk,
        }
