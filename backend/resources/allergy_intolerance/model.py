"""
AllergyIntolerance resource model - FHIR aligned.

Records risk of harmful or undesirable physiological response.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Literal
from enum import Enum

from resources.core import (
    DomainResource,
    Reference,
    CodeableConcept,
)


class AllergyCategory(str, Enum):
    """Category of the allergy."""
    FOOD = "food"
    MEDICATION = "medication"
    ENVIRONMENT = "environment"
    BIOLOGIC = "biologic"


class AllergyCriticality(str, Enum):
    """Criticality/severity of the allergy."""
    LOW = "low"
    HIGH = "high"
    UNABLE_TO_ASSESS = "unable-to-assess"


class AllergyVerificationStatus(str, Enum):
    """Verification status of the allergy."""
    UNCONFIRMED = "unconfirmed"
    CONFIRMED = "confirmed"
    REFUTED = "refuted"
    ENTERED_IN_ERROR = "entered-in-error"


@dataclass
class AllergyReaction:
    """Details of a reaction to the allergen."""
    manifestation: str  # How the reaction manifests (e.g., "Anaphylaxis", "Rash")
    severity: Literal["mild", "moderate", "severe"] = "moderate"
    description: str | None = None


@dataclass
class AllergyIntolerance(DomainResource):
    """
    Risk of harmful or undesirable physiological response unique to an individual.

    FHIR Reference: https://www.hl7.org/fhir/allergyintolerance.html
    """
    resource_type: ClassVar[str] = "AllergyIntolerance"

    # Who has the allergy
    patient: Reference = field(default_factory=lambda: Reference(reference="Patient/unknown"))

    # What they're allergic to
    code: CodeableConcept = field(default_factory=lambda: CodeableConcept(code="unknown", display="Unknown"))

    # Category and criticality
    category: AllergyCategory = AllergyCategory.MEDICATION
    criticality: AllergyCriticality = AllergyCriticality.HIGH

    # Status
    clinical_status: Literal["active", "inactive", "resolved"] = "active"
    verification_status: AllergyVerificationStatus = AllergyVerificationStatus.CONFIRMED

    # Reactions
    reactions: list[AllergyReaction] = field(default_factory=list)

    # When recorded
    recorded_date: datetime | None = None
    recorder: Reference | None = None  # Who recorded the allergy
    last_updated: datetime | None = None  # When last updated
    notes: str | None = None  # Additional notes

    @property
    def allergen(self) -> str:
        """Get the allergen name."""
        return self.code.display

    @property
    def severity(self) -> str:
        """Get the primary reaction severity."""
        if self.reactions:
            return self.reactions[0].severity
        return "moderate"

    @property
    def reaction(self) -> str:
        """Get the primary reaction manifestation."""
        if self.reactions:
            return self.reactions[0].manifestation
        return "Unknown"

    @property
    def is_anaphylaxis(self) -> bool:
        """Check if any reaction is anaphylaxis."""
        if not self.reactions:
            return False
        anaphylaxis_terms = ["anaphylaxis", "anaphylactic"]
        for reaction in self.reactions:
            manifestation_lower = reaction.manifestation.lower()
            if any(term in manifestation_lower for term in anaphylaxis_terms):
                return True
        return False

    @property
    def allergy_type(self) -> str:
        """Get the allergy type for frontend display (drug, food, environmental, other)."""
        category_map = {
            AllergyCategory.MEDICATION: "drug",
            AllergyCategory.FOOD: "food",
            AllergyCategory.ENVIRONMENT: "environmental",
            AllergyCategory.BIOLOGIC: "other",
        }
        return category_map.get(self.category, "other")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "resourceType": self.resource_type,
            "patient": self.patient.reference,
            "code": {
                "code": self.code.code,
                "display": self.code.display,
            },
            "category": self.category.value,
            "criticality": self.criticality.value,
            "clinicalStatus": self.clinical_status,
            "verificationStatus": self.verification_status.value,
            "reactions": [
                {
                    "manifestation": r.manifestation,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.reactions
            ],
            "recordedDate": self.recorded_date.isoformat() if self.recorded_date else None,
        }

    @property
    def documenting_provider(self) -> str | None:
        """Get the documenting provider name from the recorder reference."""
        if self.recorder and self.recorder.display:
            return self.recorder.display
        return None

    def to_bff_dict(self) -> dict:
        """Convert to BFF-friendly format (matches current frontend expectations)."""
        return {
            "id": self.id,
            "allergen": self.allergen,
            "type": self.allergy_type,
            "reaction": self.reaction,
            "severity": self.severity,
            "isAnaphylaxis": self.is_anaphylaxis,
            "documented": self.recorded_date.strftime("%Y-%m-%d") if self.recorded_date else None,
            "clinicalStatus": self.clinical_status,
            "verificationStatus": self.verification_status.value,
            "lastUpdated": self.last_updated.strftime("%Y-%m-%d") if self.last_updated else None,
            "documentingProvider": self.documenting_provider,
            "notes": self.notes,
            "reactions": [
                {
                    "manifestation": r.manifestation,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.reactions
            ],
        }

    @classmethod
    def from_dict(cls, data: dict, patient_id: str | None = None) -> "AllergyIntolerance":
        """Create AllergyIntolerance from dictionary."""
        # Handle legacy format
        allergen = data.get("allergen") or data.get("code", {}).get("display", "Unknown")

        # Parse severity to criticality mapping
        severity = data.get("severity", "moderate")
        criticality_map = {
            "severe": AllergyCriticality.HIGH,
            "moderate": AllergyCriticality.HIGH,
            "mild": AllergyCriticality.LOW,
        }
        criticality = criticality_map.get(severity, AllergyCriticality.HIGH)

        # Build reactions
        reactions = []
        reaction_text = data.get("reaction")
        if reaction_text:
            reactions.append(AllergyReaction(manifestation=reaction_text, severity=severity))

        # Parse recorded date
        recorded_date = None
        if data.get("documented") or data.get("recordedDate"):
            date_str = data.get("documented") or data.get("recordedDate")
            try:
                recorded_date = datetime.fromisoformat(date_str)
            except ValueError:
                try:
                    recorded_date = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    pass

        # Get patient reference
        patient_ref = data.get("patient") or f"Patient/{patient_id}" if patient_id else "Patient/unknown"
        if not patient_ref.startswith("Patient/"):
            patient_ref = f"Patient/{patient_ref}"

        return cls(
            id=data["id"],
            patient=Reference(reference=patient_ref),
            code=CodeableConcept(code=allergen.lower().replace(" ", "-"), display=allergen),
            criticality=criticality,
            reactions=reactions,
            recorded_date=recorded_date,
        )
