"""
Lab Result resource model.

Represents individual lab test results with history tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Literal

from resources.core import DomainResource, Reference


LabResultStatus = Literal["normal", "abnormal", "critical", "pending", "in_progress"]


@dataclass
class LabResultHistory:
    """A single historical lab result entry."""
    id: str
    value: str
    unit: str
    status: LabResultStatus
    collection_date: datetime
    reference_range: str
    performing_lab: str | None = None
    last_updated: datetime | None = None
    acknowledged: bool = True
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "value": self.value,
            "unit": self.unit,
            "status": self.status,
            "collectionDate": self.collection_date.isoformat(),
            "referenceRange": self.reference_range,
            "performingLab": self.performing_lab,
            "lastUpdated": self.last_updated.isoformat() if self.last_updated else None,
            "acknowledged": self.acknowledged,
            "acknowledgedBy": self.acknowledged_by,
            "acknowledgedAt": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
        }


@dataclass
class TrendAnalysis:
    """Analysis of trend direction for a lab result over time."""
    direction: Literal["increasing", "decreasing", "stable"]
    percent_change: float
    absolute_change: float
    first_value: float
    last_value: float
    data_points: int

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "direction": self.direction,
            "percentChange": self.percent_change,
            "absoluteChange": self.absolute_change,
            "firstValue": self.first_value,
            "lastValue": self.last_value,
            "dataPoints": self.data_points,
        }


@dataclass
class LabResult(DomainResource):
    """
    A single lab test result.

    Represents one measurement for a specific test at a specific time.
    """
    resource_type: ClassVar[str] = "Observation"

    # What test
    test_name: str = ""
    test_code: str | None = None  # LOINC code

    # Result value
    value: str = ""
    unit: str = ""
    reference_range: str = ""
    status: LabResultStatus = "normal"

    # For whom
    subject: Reference = field(default_factory=lambda: Reference(reference="Patient/unknown"))

    # When
    collection_date: datetime = field(default_factory=datetime.utcnow)

    # Additional context
    performing_lab: str | None = None
    panel_id: str | None = None  # If part of a panel

    # Data completeness tracking
    last_updated: datetime | None = None  # When the result was last updated in the system
    acknowledged: bool = True  # Whether a provider has acknowledged this result
    acknowledged_by: str | None = None  # Provider ID who acknowledged
    acknowledged_at: datetime | None = None  # When it was acknowledged

    @property
    def patient_id(self) -> str:
        """Get the patient ID from the subject reference."""
        return self.subject.id

    @property
    def numeric_value(self) -> float | None:
        """Parse numeric value from string (handles values like '>100' or '<5')."""
        cleaned = self.value.replace("<", "").replace(">", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "resourceType": self.resource_type,
            "testName": self.test_name,
            "testCode": self.test_code,
            "value": self.value,
            "unit": self.unit,
            "referenceRange": self.reference_range,
            "status": self.status,
            "subject": self.subject.reference,
            "collectionDate": self.collection_date.isoformat(),
            "performingLab": self.performing_lab,
            "panelId": self.panel_id,
            "lastUpdated": self.last_updated.isoformat() if self.last_updated else None,
            "acknowledged": self.acknowledged,
            "acknowledgedBy": self.acknowledged_by,
            "acknowledgedAt": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
        }

    def to_bff_dict(self) -> dict:
        """Convert to BFF-friendly format."""
        return {
            "id": self.id,
            "testName": self.test_name,
            "value": self.value,
            "unit": self.unit,
            "referenceRange": self.reference_range,
            "status": self.status,
            "collectionDate": self.collection_date.isoformat(),
            "performingLab": self.performing_lab,
            "lastUpdated": self.last_updated.isoformat() if self.last_updated else None,
            "acknowledged": self.acknowledged,
            "acknowledgedBy": self.acknowledged_by,
            "acknowledgedAt": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
        }

    def to_history_entry(self) -> LabResultHistory:
        """Convert to a history entry."""
        return LabResultHistory(
            id=self.id,
            value=self.value,
            unit=self.unit,
            status=self.status,
            collection_date=self.collection_date,
            reference_range=self.reference_range,
            performing_lab=self.performing_lab,
            last_updated=self.last_updated,
            acknowledged=self.acknowledged,
            acknowledged_by=self.acknowledged_by,
            acknowledged_at=self.acknowledged_at,
        )
