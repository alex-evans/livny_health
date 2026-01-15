"""
Practitioner resource model - FHIR aligned.

A Practitioner is a person involved in the healthcare process.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

from resources.core import (
    DomainResource,
    HumanName,
    Gender,
    Identifier,
    ContactPoint,
    CodeableConcept,
)


@dataclass
class Practitioner(DomainResource):
    """
    A person who is directly or indirectly involved in the provisioning of healthcare.

    FHIR Reference: https://www.hl7.org/fhir/practitioner.html
    """
    resource_type: ClassVar[str] = "Practitioner"

    # Core demographics
    name: HumanName = field(default_factory=lambda: HumanName(family="Unknown"))
    gender: Gender = Gender.UNKNOWN

    # Identifiers (NPI, DEA, etc.)
    identifiers: list[Identifier] = field(default_factory=list)

    # Contact information
    telecom: list[ContactPoint] = field(default_factory=list)

    # Qualifications (MD, DO, NP, etc.)
    qualifications: list[CodeableConcept] = field(default_factory=list)

    # Status
    active: bool = True

    @property
    def npi(self) -> str | None:
        """Get the practitioner's NPI if available."""
        for identifier in self.identifiers:
            if "npi" in identifier.system.lower():
                return identifier.value
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
            "gender": self.gender.value,
            "npi": self.npi,
            "active": self.active,
            "qualifications": [q.display for q in self.qualifications],
        }

    def to_bff_dict(self) -> dict:
        """Convert to BFF-friendly format."""
        return {
            "id": self.id,
            "name": self.display_name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Practitioner":
        """Create Practitioner from dictionary."""
        gender_str = data.get("gender", "unknown").lower()
        try:
            gender = Gender(gender_str)
        except ValueError:
            gender = Gender.UNKNOWN

        identifiers = []
        if data.get("npi"):
            identifiers.append(Identifier(system="http://hl7.org/fhir/sid/us-npi", value=data["npi"]))

        return cls(
            id=data["id"],
            name=HumanName.from_full_name(data.get("name", "Unknown")),
            gender=gender,
            identifiers=identifiers,
            active=data.get("active", True),
        )
