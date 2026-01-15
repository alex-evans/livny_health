"""
Medication resource model - FHIR aligned.

Represents a drug product (not a prescription).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

from resources.core import (
    DomainResource,
    CodeableConcept,
)


@dataclass
class Medication(DomainResource):
    """
    A medication product - the drug itself, not a prescription.

    FHIR Reference: https://www.hl7.org/fhir/medication.html
    """
    resource_type: ClassVar[str] = "Medication"

    # Drug identification
    code: CodeableConcept = field(default_factory=lambda: CodeableConcept(code="unknown", display="Unknown"))

    # Form and strength
    form: str | None = None  # tablet, capsule, solution, etc.
    strength: str | None = None  # 500mg, 10mg/5ml, etc.

    # Clinical properties
    is_controlled: bool = False  # Is this a controlled substance?

    # Common dosing patterns (for UI suggestions)
    common_dosing: list[str] = field(default_factory=list)

    # Status
    status: str = "active"  # active | inactive | entered-in-error

    @property
    def name(self) -> str:
        """Get the medication name."""
        return self.code.display

    @property
    def display_name(self) -> str:
        """Get full display name with strength and form."""
        parts = [self.code.display]
        if self.strength:
            parts.append(self.strength)
        if self.form:
            parts.append(self.form)
        return " ".join(parts)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "resourceType": self.resource_type,
            "code": {
                "code": self.code.code,
                "display": self.code.display,
            },
            "name": self.name,
            "form": self.form,
            "strength": self.strength,
            "isControlled": self.is_controlled,
            "commonDosing": self.common_dosing,
            "status": self.status,
        }

    def to_bff_dict(self) -> dict:
        """Convert to BFF-friendly format (matches current frontend expectations)."""
        return {
            "id": self.id,
            "name": self.display_name,
            "strength": self.strength,
            "form": self.form,
            "commonDosing": self.common_dosing,
            "isControlled": self.is_controlled,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Medication":
        """Create Medication from dictionary."""
        # Handle both FHIR and legacy formats
        name = data.get("name") or data.get("code", {}).get("display", "Unknown")

        # Extract base name (without strength/form) if needed
        base_name = name.split()[0] if " " in name else name

        return cls(
            id=data["id"],
            code=CodeableConcept(
                code=data.get("code", {}).get("code") or base_name.lower(),
                display=name,
                system=data.get("code", {}).get("system"),
            ),
            form=data.get("form"),
            strength=data.get("strength"),
            is_controlled=data.get("isControlled", False),
            common_dosing=data.get("commonDosing", []),
            status=data.get("status", "active"),
        )
