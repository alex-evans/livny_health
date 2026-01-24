"""
Clinical Alert resource model.

Represents clinical alerts that flag critical patient information
such as abnormal labs, critical vitals, overdue screenings, and drug interactions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Literal

from resources.core import DomainResource


AlertType = Literal[
    "critical_lab",
    "critical_vital",
    "critical_imaging",
    "drug_interaction",
    "overdue_screening",
    "chronic_disease",
]

AlertSeverity = Literal["critical", "high", "medium"]

AlertStatus = Literal["active", "acknowledged", "dismissed"]


@dataclass
class AlertAcknowledgment:
    """Records when and by whom an alert was acknowledged."""
    acknowledged_by: str
    acknowledged_at: datetime
    note: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "acknowledgedBy": self.acknowledged_by,
            "acknowledgedAt": self.acknowledged_at.isoformat(),
            "note": self.note,
        }


@dataclass
class ClinicalAlert(DomainResource):
    """
    A clinical alert for a patient.

    Alerts are generated on-demand when a patient chart is opened,
    based on critical labs, vitals, screenings, and drug interactions.
    Only acknowledgment/dismissal state is persisted.
    """
    resource_type: ClassVar[str] = "ClinicalAlert"

    # Required fields
    patient_id: str = ""
    alert_type: AlertType = "critical_lab"
    severity: AlertSeverity = "medium"
    status: AlertStatus = "active"
    title: str = ""
    description: str = ""
    generated_at: datetime = field(default_factory=datetime.utcnow)

    # Source information
    source: str = ""  # "Lab Result", "Vital Signs", "Imaging", etc.
    source_id: str = ""  # ID of the source record
    source_link: str | None = None  # URL or path to navigate to source

    # Additional context (flexible per-type data)
    context: dict = field(default_factory=dict)

    # Recommended actions
    recommended_actions: list[str] = field(default_factory=list)

    # Acknowledgment tracking
    acknowledgment: AlertAcknowledgment | None = None

    # Dismissal tracking
    dismissed_at: datetime | None = None
    dismissed_by: str | None = None
    dismissed_reason: str | None = None

    def acknowledge(self, by: str, note: str | None = None) -> None:
        """Mark the alert as acknowledged."""
        self.status = "acknowledged"
        self.acknowledgment = AlertAcknowledgment(
            acknowledged_by=by,
            acknowledged_at=datetime.utcnow(),
            note=note,
        )

    def dismiss(self, by: str, reason: str | None = None) -> None:
        """Mark the alert as dismissed."""
        self.status = "dismissed"
        self.dismissed_at = datetime.utcnow()
        self.dismissed_by = by
        self.dismissed_reason = reason

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "resourceType": self.resource_type,
            "patientId": self.patient_id,
            "alertType": self.alert_type,
            "severity": self.severity,
            "status": self.status,
            "title": self.title,
            "description": self.description,
            "generatedAt": self.generated_at.isoformat(),
            "source": self.source,
            "sourceId": self.source_id,
            "sourceLink": self.source_link,
            "context": self.context,
            "recommendedActions": self.recommended_actions,
            "acknowledgment": self.acknowledgment.to_dict() if self.acknowledgment else None,
            "dismissedAt": self.dismissed_at.isoformat() if self.dismissed_at else None,
            "dismissedBy": self.dismissed_by,
            "dismissedReason": self.dismissed_reason,
        }

    def to_bff_dict(self) -> dict:
        """Convert to BFF-friendly format."""
        return self.to_dict()


@dataclass
class AlertSummary:
    """Summary of alert counts by severity."""
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0

    @property
    def total_active(self) -> int:
        """Total number of active alerts."""
        return self.critical_count + self.high_count + self.medium_count

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "criticalCount": self.critical_count,
            "highCount": self.high_count,
            "mediumCount": self.medium_count,
            "totalActive": self.total_active,
        }
