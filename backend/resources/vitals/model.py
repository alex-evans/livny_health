"""
Vital Signs resource model.

Represents individual vital sign measurements with history tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Literal

from resources.core import DomainResource, Reference


VitalType = Literal[
    "blood_pressure_systolic",
    "blood_pressure_diastolic",
    "heart_rate",
    "temperature",
    "weight",
    "oxygen_saturation",
    "respiratory_rate",
    "height",
]

VitalStatus = Literal["normal", "abnormal", "critical"]

TrendDirection = Literal["increasing", "decreasing", "stable"]

ClinicalSignificance = Literal["good", "concerning", "neutral"]


# Reference ranges for vital signs
VITAL_REFERENCE_RANGES: dict[VitalType, dict] = {
    "blood_pressure_systolic": {"min": 90, "max": 120, "unit": "mmHg", "critical_low": 80, "critical_high": 180},
    "blood_pressure_diastolic": {"min": 60, "max": 80, "unit": "mmHg", "critical_low": 50, "critical_high": 120},
    "heart_rate": {"min": 60, "max": 100, "unit": "bpm", "critical_low": 40, "critical_high": 150},
    "temperature": {"min": 97.0, "max": 99.0, "unit": "°F", "critical_low": 95.0, "critical_high": 103.0},
    "weight": {"min": None, "max": None, "unit": "lbs", "critical_low": None, "critical_high": None},
    "oxygen_saturation": {"min": 95, "max": 100, "unit": "%", "critical_low": 90, "critical_high": None},
    "respiratory_rate": {"min": 12, "max": 20, "unit": "breaths/min", "critical_low": 8, "critical_high": 30},
    "height": {"min": None, "max": None, "unit": "in", "critical_low": None, "critical_high": None},
}

# Clinical interpretation: for these vitals, lower is better
LOWER_IS_BETTER_VITALS: set[VitalType] = {
    "blood_pressure_systolic",
    "blood_pressure_diastolic",
    "heart_rate",
    "weight",
    "respiratory_rate",
}

# Clinical interpretation: for these vitals, higher is better
HIGHER_IS_BETTER_VITALS: set[VitalType] = {
    "oxygen_saturation",
}


@dataclass
class VitalSignHistory:
    """A single historical vital sign entry."""
    id: str
    value: float
    unit: str
    status: VitalStatus
    recorded_at: datetime
    reference_range: str
    recorded_by: str | None = None
    location: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "value": self.value,
            "unit": self.unit,
            "status": self.status,
            "recordedAt": self.recorded_at.isoformat(),
            "referenceRange": self.reference_range,
            "recordedBy": self.recorded_by,
            "location": self.location,
        }


@dataclass
class VitalTrendAnalysis:
    """Analysis of trend direction for a vital sign over time."""
    direction: TrendDirection
    percent_change: float
    absolute_change: float
    previous_value: float
    current_value: float
    previous_date: datetime
    data_points: int
    clinical_significance: ClinicalSignificance

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "direction": self.direction,
            "percentChange": self.percent_change,
            "absoluteChange": self.absolute_change,
            "previousValue": self.previous_value,
            "currentValue": self.current_value,
            "previousDate": self.previous_date.isoformat(),
            "dataPoints": self.data_points,
            "clinicalSignificance": self.clinical_significance,
        }


@dataclass
class VitalSign(DomainResource):
    """
    A single vital sign measurement.

    Represents one measurement for a specific vital type at a specific time.
    """
    resource_type: ClassVar[str] = "Observation"

    # What vital
    vital_type: VitalType = "heart_rate"

    # Result value
    value: float = 0.0
    unit: str = ""
    status: VitalStatus = "normal"

    # For whom
    subject: Reference = field(default_factory=lambda: Reference(reference="Patient/unknown"))

    # When
    recorded_at: datetime = field(default_factory=datetime.utcnow)

    # Additional context
    recorded_by: str | None = None  # Provider/staff who recorded
    location: str | None = None  # Where the vital was taken

    @property
    def patient_id(self) -> str:
        """Get the patient ID from the subject reference."""
        return self.subject.id

    @property
    def reference_range(self) -> str:
        """Get the reference range string for this vital type."""
        ranges = VITAL_REFERENCE_RANGES.get(self.vital_type, {})
        min_val = ranges.get("min")
        max_val = ranges.get("max")
        unit = ranges.get("unit", "")

        if min_val is None and max_val is None:
            return ""
        elif min_val is None:
            return f"<{max_val} {unit}"
        elif max_val is None:
            return f">{min_val} {unit}"
        else:
            return f"{min_val}-{max_val} {unit}"

    @classmethod
    def determine_status(cls, vital_type: VitalType, value: float) -> VitalStatus:
        """Determine the status of a vital sign value."""
        ranges = VITAL_REFERENCE_RANGES.get(vital_type, {})

        critical_low = ranges.get("critical_low")
        critical_high = ranges.get("critical_high")
        min_val = ranges.get("min")
        max_val = ranges.get("max")

        # Check for critical values first
        if critical_low is not None and value < critical_low:
            return "critical"
        if critical_high is not None and value > critical_high:
            return "critical"

        # Check for abnormal values
        if min_val is not None and value < min_val:
            return "abnormal"
        if max_val is not None and value > max_val:
            return "abnormal"

        return "normal"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "resourceType": self.resource_type,
            "vitalType": self.vital_type,
            "value": self.value,
            "unit": self.unit,
            "status": self.status,
            "subject": self.subject.reference,
            "recordedAt": self.recorded_at.isoformat(),
            "recordedBy": self.recorded_by,
            "location": self.location,
            "referenceRange": self.reference_range,
        }

    def to_bff_dict(self) -> dict:
        """Convert to BFF-friendly format."""
        return {
            "id": self.id,
            "vitalType": self.vital_type,
            "value": self.value,
            "unit": self.unit,
            "status": self.status,
            "recordedAt": self.recorded_at.isoformat(),
            "recordedBy": self.recorded_by,
            "location": self.location,
            "referenceRange": self.reference_range,
        }

    def to_history_entry(self) -> VitalSignHistory:
        """Convert to a history entry."""
        return VitalSignHistory(
            id=self.id,
            value=self.value,
            unit=self.unit,
            status=self.status,
            recorded_at=self.recorded_at,
            reference_range=self.reference_range,
            recorded_by=self.recorded_by,
            location=self.location,
        )
