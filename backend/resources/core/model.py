"""
Base model for all FHIR-aligned resources.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar


@dataclass
class Resource:
    """
    Base class for all FHIR-aligned resources.

    All resources have:
    - id: Unique identifier
    - resource_type: The type of resource (Patient, Encounter, etc.)
    - meta: Metadata about the resource (version, last updated)
    """
    id: str
    resource_type: ClassVar[str] = "Resource"

    def to_dict(self) -> dict:
        """Convert resource to dictionary for JSON serialization."""
        raise NotImplementedError("Subclasses must implement to_dict()")

    @classmethod
    def from_dict(cls, data: dict) -> "Resource":
        """Create resource from dictionary."""
        raise NotImplementedError("Subclasses must implement from_dict()")


@dataclass
class DomainResource(Resource):
    """
    Base class for domain resources (clinical data).
    Adds common metadata fields.
    """
    meta_version_id: str = "1"
    meta_last_updated: datetime = field(default_factory=datetime.utcnow)
