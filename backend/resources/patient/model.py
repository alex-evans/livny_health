"""
Patient resource model - FHIR aligned.

A Patient is an individual receiving healthcare services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import ClassVar

from resources.core import (
    DomainResource,
    HumanName,
    Gender,
    Identifier,
    ContactPoint,
    Address,
)


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

    @property
    def mrn(self) -> str | None:
        """Get the patient's MRN if available."""
        for identifier in self.identifiers:
            if "mrn" in identifier.system.lower():
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
            "birthDate": self.birth_date.isoformat() if self.birth_date else None,
            "gender": self.gender.value,
            "mrn": self.mrn,
            "active": self.active,
        }

    def to_bff_dict(self) -> dict:
        """Convert to BFF-friendly format (matches current frontend expectations)."""
        return {
            "id": self.id,
            "name": self.display_name,
            "dateOfBirth": self.birth_date.isoformat() if self.birth_date else None,
            "gender": self.gender.value.capitalize(),
            "mrn": self.mrn,
        }

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
