"""
Core infrastructure for FHIR-aligned resources.
"""

from .types import (
    Reference,
    CodeableConcept,
    Period,
    Quantity,
    HumanName,
    ContactPoint,
    Address,
    Gender,
    Identifier,
)
from .repository import Repository, InMemoryRepository, generate_id
from .model import Resource, DomainResource

__all__ = [
    # Types
    "Reference",
    "CodeableConcept",
    "Period",
    "Quantity",
    "HumanName",
    "ContactPoint",
    "Address",
    "Gender",
    "Identifier",
    # Repository
    "Repository",
    "InMemoryRepository",
    "generate_id",
    # Models
    "Resource",
    "DomainResource",
]
