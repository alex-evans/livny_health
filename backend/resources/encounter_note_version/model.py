"""
Encounter Note Version resource model.

Stores historical versions of encounter notes for audit and recovery.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar
from enum import Enum

from resources.core import DomainResource, Reference


class SaveType(str, Enum):
    """Type of save operation."""
    AUTO = "auto"
    MANUAL = "manual"


@dataclass
class EncounterNoteVersion(DomainResource):
    """
    A historical version of an encounter note.

    Used for version history, audit trail, and conflict resolution.
    """
    resource_type: ClassVar[str] = "EncounterNoteVersion"

    # Reference to encounter
    encounter: Reference = field(
        default_factory=lambda: Reference(reference="Encounter/unknown")
    )

    # Version number
    version: int = 1

    # Content
    content: str = ""
    word_count: int = 0

    # Save type
    save_type: SaveType = SaveType.AUTO

    # When this version was created
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def encounter_id(self) -> str:
        """Get the encounter ID from the reference."""
        return self.encounter.id

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "resourceType": self.resource_type,
            "encounter": self.encounter.reference,
            "version": self.version,
            "content": self.content,
            "wordCount": self.word_count,
            "saveType": self.save_type.value,
            "createdAt": self.created_at.isoformat(),
        }

    def to_bff_dict(self) -> dict:
        """Convert to BFF-friendly format."""
        return {
            "id": self.id,
            "encounterId": self.encounter_id,
            "version": self.version,
            "content": self.content,
            "wordCount": self.word_count,
            "saveType": self.save_type.value,
            "createdAt": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EncounterNoteVersion":
        """Create EncounterNoteVersion from dictionary."""
        # Parse save type
        save_type_str = data.get("saveType", "auto").lower()
        try:
            save_type = SaveType(save_type_str)
        except ValueError:
            save_type = SaveType.AUTO

        # Parse encounter reference
        encounter_ref = data.get("encounter", "Encounter/unknown")
        if not encounter_ref.startswith("Encounter/"):
            encounter_ref = f"Encounter/{encounter_ref}"

        # Parse created_at
        created_at = datetime.utcnow()
        if data.get("createdAt"):
            created_at = datetime.fromisoformat(data["createdAt"])

        return cls(
            id=data["id"],
            encounter=Reference(reference=encounter_ref),
            version=data.get("version", 1),
            content=data.get("content", ""),
            word_count=data.get("wordCount", 0),
            save_type=save_type,
            created_at=created_at,
        )
