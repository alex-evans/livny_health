"""
Encounter Status History resource model.

Represents a record of an encounter status change for audit purposes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar

from resources.core import DomainResource


@dataclass
class EncounterStatusHistory(DomainResource):
    """
    A record of an encounter status change.

    Used for audit trail and compliance tracking.
    """

    resource_type: ClassVar[str] = "EncounterStatusHistory"

    # Reference to encounter
    encounter_id: str = ""

    # Status transition
    from_status: str | None = None  # null for initial creation
    to_status: str = ""

    # Who made the change
    changed_by_id: str | None = None
    changed_by_name: str | None = None

    # When
    changed_at: datetime | None = None

    # Reason for change (optional)
    reason: str | None = None

    # Request context for audit
    ip_address: str | None = None
    user_agent: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "encounterId": self.encounter_id,
            "fromStatus": self.from_status,
            "toStatus": self.to_status,
            "changedById": self.changed_by_id,
            "changedByName": self.changed_by_name,
            "changedAt": self.changed_at.isoformat() if self.changed_at else None,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EncounterStatusHistory":
        """Create from dictionary."""
        changed_at = None
        if data.get("changedAt"):
            changed_at = datetime.fromisoformat(data["changedAt"])

        return cls(
            id=data.get("id", ""),
            encounter_id=data.get("encounterId", ""),
            from_status=data.get("fromStatus"),
            to_status=data.get("toStatus", ""),
            changed_by_id=data.get("changedById"),
            changed_by_name=data.get("changedByName"),
            changed_at=changed_at,
            reason=data.get("reason"),
            ip_address=data.get("ipAddress"),
            user_agent=data.get("userAgent"),
        )
