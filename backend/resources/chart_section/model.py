"""
Chart Section model.

Defines the structure for chart navigation sections with keyboard shortcuts and badges.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


AlertLevel = Literal["none", "info", "warning", "critical"]
SectionIcon = Literal[
    "document",
    "pill",
    "exclamation-triangle",
    "beaker",
    "clipboard-list",
    "heart-pulse",
    "film",
    "users",
]


@dataclass
class KeyboardShortcut:
    """Keyboard shortcut for a chart section."""
    key: str
    modifier: str
    description: str

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "modifier": self.modifier,
            "description": self.description,
        }


@dataclass
class ChartSection:
    """A navigable section of the patient chart."""
    id: str
    name: str
    icon: SectionIcon
    order: int
    has_data: bool
    last_updated: datetime | None
    alert_level: AlertLevel
    badge_count: int | None
    keyboard_shortcut: KeyboardShortcut

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "order": self.order,
            "hasData": self.has_data,
            "lastUpdated": self.last_updated.isoformat() if self.last_updated else None,
            "alertLevel": self.alert_level,
            "badgeCount": self.badge_count,
            "keyboardShortcut": self.keyboard_shortcut.to_dict(),
        }


@dataclass
class ChartSectionsResponse:
    """Response containing all chart sections for a patient."""
    patient_id: str
    sections: list[ChartSection]

    def to_dict(self) -> dict:
        return {
            "patientId": self.patient_id,
            "sections": [s.to_dict() for s in self.sections],
        }
