"""
Patient resource model - FHIR aligned.

A Patient is an individual receiving healthcare services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import ClassVar

from resources.core import (
    DomainResource,
    HumanName,
    Gender,
    Identifier,
    ContactPoint,
    Address,
    Reference,
)


from enum import Enum


class ProblemStatus(str, Enum):
    """Clinical status of a problem."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    RESOLVED = "resolved"
    RULE_OUT = "rule_out"  # Suspected diagnosis being evaluated


class ProblemPriority(str, Enum):
    """Clinical priority for sorting problems."""
    CHRONIC = "chronic"  # Ongoing conditions requiring management
    ACUTE = "acute"      # Current active issues
    INACTIVE = "inactive"
    RESOLVED = "resolved"


class ProblemSeverity(str, Enum):
    """Severity/acuity of a problem."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    WELL_CONTROLLED = "well_controlled"


class ClinicalCategory(str, Enum):
    """Clinical categories for problem grouping."""
    CARDIOVASCULAR = "cardiovascular"
    ENDOCRINE = "endocrine"
    RESPIRATORY = "respiratory"
    MUSCULOSKELETAL = "musculoskeletal"
    NEUROLOGICAL = "neurological"
    GASTROINTESTINAL = "gastrointestinal"
    PSYCHIATRIC = "psychiatric"
    INFECTIOUS = "infectious"
    ONCOLOGY = "oncology"
    RENAL = "renal"
    DERMATOLOGICAL = "dermatological"
    OTHER = "other"


class ProblemComplexity(str, Enum):
    """Complexity indicators for problems."""
    SIMPLE = "simple"  # Basic condition without complications
    WITH_COMPLICATIONS = "with_complications"  # Has related complications
    CONTROLLED = "controlled"  # Chronic condition well managed
    UNCONTROLLED = "uncontrolled"  # Chronic condition not well managed
    PROGRESSIVE = "progressive"  # Worsening over time


@dataclass
class RelatedVisit:
    """Reference to a visit that addressed this problem."""
    visit_id: str
    date: date
    visit_type: str
    provider_name: str | None = None


@dataclass
class RelatedMedication:
    """Reference to a medication linked to this problem."""
    medication_id: str
    name: str
    dosage: str | None = None


@dataclass
class RelatedLabResult:
    """Reference to a lab result linked to this problem."""
    lab_name: str
    most_recent_value: str | None = None
    most_recent_date: date | None = None
    status: str | None = None  # normal, abnormal, critical


@dataclass
class Problem:
    """A clinical problem/condition for the patient."""
    name: str
    icd10_code: str
    onset_date: date
    status: ProblemStatus = ProblemStatus.ACTIVE
    priority: ProblemPriority = ProblemPriority.CHRONIC
    severity: ProblemSeverity | None = None
    documenting_provider: str | None = None
    documented_date: date | None = None
    is_critical: bool = False  # Life-threatening conditions (cancer, severe heart disease, etc.)
    # Resolution tracking fields
    resolved_date: date | None = None  # Date problem was marked resolved
    resolved_by_provider: str | None = None  # Provider who marked it resolved
    # Clinical context fields
    clinical_category: ClinicalCategory | None = None
    complexity: ProblemComplexity | None = None
    parent_problem_code: str | None = None  # ICD-10 code of parent problem (for complications)
    related_visits: list[RelatedVisit] | None = None
    related_medications: list[RelatedMedication] | None = None
    related_labs: list[RelatedLabResult] | None = None

    @property
    def is_new(self) -> bool:
        """Check if problem was documented within last 30 days."""
        if not self.documented_date:
            return False
        days_since_documented = (date.today() - self.documented_date).days
        return days_since_documented <= 30

    @property
    def is_rule_out(self) -> bool:
        """Check if this is a rule-out/suspected diagnosis."""
        return self.status == ProblemStatus.RULE_OUT

    def to_bff_dict(self) -> dict:
        """Convert to BFF-friendly format."""
        result = {
            "name": self.name,
            "icd10Code": self.icd10_code,
            "onsetDate": self.onset_date.isoformat() if self.onset_date else None,
            "status": self.status.value,
            "priority": self.priority.value,
            "isCritical": self.is_critical,
            "isNew": self.is_new,
            "isRuleOut": self.is_rule_out,
        }
        if self.severity:
            result["severity"] = self.severity.value
        if self.documenting_provider:
            result["documentingProvider"] = self.documenting_provider
        if self.documented_date:
            result["documentedDate"] = self.documented_date.isoformat()
        # Resolution tracking fields
        if self.resolved_date:
            result["resolvedDate"] = self.resolved_date.isoformat()
        if self.resolved_by_provider:
            result["resolvedByProvider"] = self.resolved_by_provider
        # Clinical context fields
        if self.clinical_category:
            result["clinicalCategory"] = self.clinical_category.value
        if self.complexity:
            result["complexity"] = self.complexity.value
        if self.parent_problem_code:
            result["parentProblemCode"] = self.parent_problem_code
        if self.related_visits:
            result["relatedVisits"] = [
                {
                    "visitId": v.visit_id,
                    "date": v.date.isoformat() if v.date else None,
                    "visitType": v.visit_type,
                    "providerName": v.provider_name,
                }
                for v in self.related_visits
            ]
        if self.related_medications:
            result["relatedMedications"] = [
                {
                    "medicationId": m.medication_id,
                    "name": m.name,
                    "dosage": m.dosage,
                }
                for m in self.related_medications
            ]
        if self.related_labs:
            result["relatedLabs"] = [
                {
                    "labName": lab.lab_name,
                    "mostRecentValue": lab.most_recent_value,
                    "mostRecentDate": lab.most_recent_date.isoformat() if lab.most_recent_date else None,
                    "status": lab.status,
                }
                for lab in self.related_labs
            ]
        return result


@dataclass
class Insurance:
    """Insurance coverage information."""
    provider: str
    member_id: str


@dataclass
class RecentVitals:
    """Recent vital signs for the patient."""
    date: str
    blood_pressure: str
    weight: str
    temperature: str


@dataclass
class AllergyReviewStatus:
    """
    Tracks when a patient's allergy history was last reviewed.

    This is separate from individual allergy updates - it represents
    a clinician's confirmation that the allergy list is complete and current.
    """
    reviewed_at: datetime
    reviewed_by: Reference | None = None  # Reference to Practitioner who reviewed

    @property
    def is_stale(self) -> bool:
        """Check if the review is older than 1 year."""
        if self.reviewed_at is None:
            return True
        age = datetime.now() - self.reviewed_at
        return age.days > 365

    @property
    def reviewer_name(self) -> str | None:
        """Get the reviewer's display name."""
        if self.reviewed_by and self.reviewed_by.display:
            return self.reviewed_by.display
        return None


@dataclass
class Patient(DomainResource):
    """
    A person receiving healthcare services.

    FHIR Reference: https://www.hl7.org/fhir/patient.html
    """
    resource_type: ClassVar[str] = "Patient"

    # Core demographics
    name: HumanName = field(default_factory=lambda: HumanName(family="Unknown"))
    birth_date: date | None = None
    gender: Gender = Gender.UNKNOWN

    # Identifiers (MRN, etc.)
    identifiers: list[Identifier] = field(default_factory=list)

    # Contact information
    telecom: list[ContactPoint] = field(default_factory=list)
    address: list[Address] = field(default_factory=list)

    # Status
    active: bool = True

    # Clinical data (simplified for BFF)
    problem_list: list[Problem] = field(default_factory=list)
    recent_vitals: RecentVitals | None = None
    insurance: Insurance | None = None
    allergy_review_status: AllergyReviewStatus | None = None

    @property
    def mrn(self) -> str | None:
        """Get the patient's MRN if available."""
        for identifier in self.identifiers:
            if "mrn" in identifier.system.lower():
                return identifier.value
        return None

    @property
    def phone(self) -> str | None:
        """Get the patient's primary phone number if available."""
        for contact in self.telecom:
            if contact.system == "phone":
                return contact.value
        return None

    @property
    def display_name(self) -> str:
        """Get a display-friendly name."""
        return self.name.full_name

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "resourceType": self.resource_type,
            "name": self.display_name,
            "birthDate": self.birth_date.isoformat() if self.birth_date else None,
            "gender": self.gender.value,
            "mrn": self.mrn,
            "active": self.active,
        }

    def to_bff_dict(self) -> dict:
        """Convert to BFF-friendly format (matches current frontend expectations)."""
        result = {
            "id": self.id,
            "name": self.display_name,
            "dateOfBirth": self.birth_date.isoformat() if self.birth_date else None,
            "gender": self.gender.value.capitalize(),
            "mrn": self.mrn,
        }

        if self.phone:
            result["phone"] = self.phone

        if self.insurance:
            result["insurance"] = {
                "provider": self.insurance.provider,
                "memberId": self.insurance.member_id,
            }

        if self.problem_list:
            result["problemList"] = [p.to_bff_dict() for p in self.problem_list]

        if self.recent_vitals:
            result["recentVitals"] = {
                "date": self.recent_vitals.date,
                "bloodPressure": self.recent_vitals.blood_pressure,
                "weight": self.recent_vitals.weight,
                "temperature": self.recent_vitals.temperature,
            }

        if self.allergy_review_status:
            result["allergyReviewStatus"] = {
                "reviewedAt": self.allergy_review_status.reviewed_at.isoformat(),
                "reviewedBy": self.allergy_review_status.reviewer_name,
                "isStale": self.allergy_review_status.is_stale,
            }

        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Patient":
        """Create Patient from dictionary."""
        birth_date = None
        if data.get("birthDate") or data.get("dateOfBirth"):
            date_str = data.get("birthDate") or data.get("dateOfBirth")
            birth_date = date.fromisoformat(date_str)

        gender_str = data.get("gender", "unknown").lower()
        try:
            gender = Gender(gender_str)
        except ValueError:
            gender = Gender.UNKNOWN

        identifiers = []
        if data.get("mrn"):
            identifiers.append(Identifier.mrn(data["mrn"]))

        return cls(
            id=data["id"],
            name=HumanName.from_full_name(data.get("name", "Unknown")),
            birth_date=birth_date,
            gender=gender,
            identifiers=identifiers,
            active=data.get("active", True),
        )
