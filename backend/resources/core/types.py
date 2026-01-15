"""
FHIR-aligned base types used across all resources.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Generic, TypeVar, Literal
from enum import Enum


# Resource type variable for generic references
T = TypeVar("T")


@dataclass
class Reference(Generic[T]):
    """
    A reference to another resource.
    In FHIR, references link resources together.
    """
    reference: str  # e.g., "Patient/patient-001"
    display: str | None = None  # Human-readable name

    @property
    def resource_type(self) -> str:
        """Extract resource type from reference string."""
        return self.reference.split("/")[0] if "/" in self.reference else ""

    @property
    def id(self) -> str:
        """Extract ID from reference string."""
        return self.reference.split("/")[1] if "/" in self.reference else self.reference

    @classmethod
    def to(cls, resource_type: str, resource_id: str, display: str | None = None) -> "Reference":
        """Create a reference to a resource."""
        return cls(reference=f"{resource_type}/{resource_id}", display=display)


@dataclass
class CodeableConcept:
    """
    A coded concept with display text.
    Used for things like allergy types, medication codes, etc.
    """
    code: str
    display: str
    system: str | None = None  # e.g., "http://snomed.info/sct"


@dataclass
class Period:
    """A time period with start and optional end."""
    start: datetime
    end: datetime | None = None


@dataclass
class Quantity:
    """A measured amount with unit."""
    value: float
    unit: str
    code: str | None = None  # Unit code (e.g., "mg")


@dataclass
class HumanName:
    """A human name with parts."""
    family: str  # Last name
    given: list[str] = field(default_factory=list)  # First, middle names
    prefix: list[str] = field(default_factory=list)  # Dr., Mr., etc.
    suffix: list[str] = field(default_factory=list)  # Jr., III, etc.

    @property
    def full_name(self) -> str:
        """Get the full formatted name."""
        parts = []
        if self.prefix:
            parts.extend(self.prefix)
        parts.extend(self.given)
        parts.append(self.family)
        if self.suffix:
            parts.extend(self.suffix)
        return " ".join(parts)

    @classmethod
    def from_full_name(cls, full_name: str) -> "HumanName":
        """Parse a full name string into parts (simple parsing)."""
        parts = full_name.split()
        if len(parts) >= 2:
            return cls(family=parts[-1], given=parts[:-1])
        return cls(family=full_name)


@dataclass
class ContactPoint:
    """Contact information (phone, email, etc.)."""
    system: Literal["phone", "email", "fax", "url"]
    value: str
    use: Literal["home", "work", "mobile"] | None = None


@dataclass
class Address:
    """A postal address."""
    line: list[str] = field(default_factory=list)
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None


class Gender(str, Enum):
    """Administrative gender."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


@dataclass
class Identifier:
    """
    An identifier for a resource (MRN, SSN, etc.).
    """
    system: str  # e.g., "http://hospital.org/mrn"
    value: str   # e.g., "MRN-10001"

    @classmethod
    def mrn(cls, value: str) -> "Identifier":
        """Create an MRN identifier."""
        return cls(system="http://livny.health/mrn", value=value)
