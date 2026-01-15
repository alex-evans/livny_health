"""
Encounter resource model - FHIR aligned.

Represents an interaction between a patient and healthcare provider.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar
from enum import Enum

from resources.core import (
    DomainResource,
    Reference,
    CodeableConcept,
    Period,
)


class EncounterStatus(str, Enum):
    """Status of the encounter."""
    PLANNED = "planned"
    ARRIVED = "arrived"
    TRIAGED = "triaged"
    IN_PROGRESS = "in-progress"
    ON_HOLD = "on-hold"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class EncounterClass(str, Enum):
    """Classification of the encounter."""
    AMBULATORY = "AMB"  # Outpatient/office visit
    EMERGENCY = "EMER"  # Emergency department
    INPATIENT = "IMP"   # Inpatient
    VIRTUAL = "VR"      # Virtual/telehealth
    HOME = "HH"         # Home health


@dataclass
class EncounterParticipant:
    """A participant in the encounter (provider, nurse, etc.)."""
    individual: Reference
    type: str | None = None  # primary, admitter, attender, etc.


@dataclass
class Encounter(DomainResource):
    """
    An interaction between a patient and healthcare provider(s).

    FHIR Reference: https://www.hl7.org/fhir/encounter.html
    """
    resource_type: ClassVar[str] = "Encounter"

    # Status
    status: EncounterStatus = EncounterStatus.PLANNED

    # Classification
    encounter_class: EncounterClass = EncounterClass.AMBULATORY

    # Type of encounter
    type: CodeableConcept | None = None  # Office Visit, Follow-up, etc.

    # Who is the patient
    subject: Reference = field(default_factory=lambda: Reference(reference="Patient/unknown"))

    # Participants (providers)
    participants: list[EncounterParticipant] = field(default_factory=list)

    # When
    period: Period | None = None

    # Reason for visit
    reason: list[CodeableConcept] = field(default_factory=list)
    chief_complaint: str | None = None

    # Link to appointment that spawned this encounter
    appointment: Reference | None = None

    @property
    def patient_id(self) -> str:
        """Get the patient ID from the subject reference."""
        return self.subject.id

    @property
    def primary_provider(self) -> Reference | None:
        """Get the primary provider for this encounter."""
        for p in self.participants:
            if p.type == "primary" or len(self.participants) == 1:
                return p.individual
        return self.participants[0].individual if self.participants else None

    @property
    def start_time(self) -> datetime | None:
        """Get the encounter start time."""
        return self.period.start if self.period else None

    @property
    def end_time(self) -> datetime | None:
        """Get the encounter end time."""
        return self.period.end if self.period else None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "resourceType": self.resource_type,
            "status": self.status.value,
            "class": self.encounter_class.value,
            "type": self.type.display if self.type else None,
            "subject": self.subject.reference,
            "participants": [
                {
                    "individual": p.individual.reference,
                    "type": p.type,
                }
                for p in self.participants
            ],
            "period": {
                "start": self.period.start.isoformat() if self.period else None,
                "end": self.period.end.isoformat() if self.period and self.period.end else None,
            } if self.period else None,
            "reason": [r.display for r in self.reason],
            "chiefComplaint": self.chief_complaint,
            "appointment": self.appointment.reference if self.appointment else None,
        }

    def to_bff_dict(self) -> dict:
        """Convert to BFF-friendly format."""
        return {
            "id": self.id,
            "status": self.status.value,
            "type": self.type.display if self.type else None,
            "chiefComplaint": self.chief_complaint,
            "startTime": self.start_time.isoformat() if self.start_time else None,
            "endTime": self.end_time.isoformat() if self.end_time else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Encounter":
        """Create Encounter from dictionary."""
        # Parse status
        status_str = data.get("status", "planned").lower().replace("_", "-")
        try:
            status = EncounterStatus(status_str)
        except ValueError:
            status = EncounterStatus.UNKNOWN

        # Parse encounter class
        enc_class_str = data.get("class", "AMB").upper()
        try:
            enc_class = EncounterClass(enc_class_str)
        except ValueError:
            enc_class = EncounterClass.AMBULATORY

        # Parse period
        period = None
        if data.get("period"):
            start = datetime.fromisoformat(data["period"]["start"]) if data["period"].get("start") else datetime.utcnow()
            end = datetime.fromisoformat(data["period"]["end"]) if data["period"].get("end") else None
            period = Period(start=start, end=end)

        # Parse type
        enc_type = None
        if data.get("type"):
            enc_type = CodeableConcept(code=data["type"].lower().replace(" ", "-"), display=data["type"])

        # Parse subject
        subject_ref = data.get("subject", "Patient/unknown")
        if not subject_ref.startswith("Patient/"):
            subject_ref = f"Patient/{subject_ref}"

        return cls(
            id=data["id"],
            status=status,
            encounter_class=enc_class,
            type=enc_type,
            subject=Reference(reference=subject_ref),
            period=period,
            chief_complaint=data.get("chiefComplaint"),
        )
