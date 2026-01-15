"""
Appointment resource model - FHIR aligned.

Represents a scheduled healthcare event.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import ClassVar
from enum import Enum

from resources.core import (
    DomainResource,
    Reference,
    CodeableConcept,
)


class AppointmentStatus(str, Enum):
    """Status of the appointment."""
    PROPOSED = "proposed"
    PENDING = "pending"
    BOOKED = "booked"
    ARRIVED = "arrived"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    NO_SHOW = "noshow"
    ENTERED_IN_ERROR = "entered-in-error"
    CHECKED_IN = "checked-in"
    WAITLIST = "waitlist"


@dataclass
class AppointmentParticipant:
    """A participant in the appointment."""
    actor: Reference
    status: str = "accepted"  # accepted, declined, tentative, needs-action
    type: str | None = None  # patient, practitioner, location


@dataclass
class AppointmentFlag:
    """Clinical flag for an appointment."""
    type: str  # critical_lab, overdue_screening, special_needs, new_patient
    message: str


@dataclass
class Appointment(DomainResource):
    """
    A scheduled healthcare event.

    FHIR Reference: https://www.hl7.org/fhir/appointment.html
    """
    resource_type: ClassVar[str] = "Appointment"

    # Status
    status: AppointmentStatus = AppointmentStatus.BOOKED

    # Type of appointment
    appointment_type: CodeableConcept | None = None  # Office Visit, Follow-up, etc.

    # Timing
    start: datetime = field(default_factory=datetime.utcnow)
    end: datetime | None = None
    duration_minutes: int = 30

    # Reason
    reason: str | None = None  # Chief complaint / reason for visit

    # Participants
    participants: list[AppointmentParticipant] = field(default_factory=list)

    # Clinical flags
    flags: list[AppointmentFlag] = field(default_factory=list)

    # Double-booking indicator
    is_double_booked: bool = False

    @property
    def patient(self) -> Reference | None:
        """Get the patient participant."""
        for p in self.participants:
            if p.type == "patient" or p.actor.resource_type == "Patient":
                return p.actor
        return None

    @property
    def patient_id(self) -> str | None:
        """Get the patient ID."""
        patient = self.patient
        return patient.id if patient else None

    @property
    def provider(self) -> Reference | None:
        """Get the provider participant."""
        for p in self.participants:
            if p.type == "practitioner" or p.actor.resource_type == "Practitioner":
                return p.actor
        return None

    @property
    def computed_end(self) -> datetime:
        """Get end time, computing from start + duration if not set."""
        if self.end:
            return self.end
        return self.start + timedelta(minutes=self.duration_minutes)

    @property
    def visit_type(self) -> str:
        """Get the visit type display name."""
        return self.appointment_type.display if self.appointment_type else "Office Visit"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "resourceType": self.resource_type,
            "status": self.status.value,
            "appointmentType": self.appointment_type.display if self.appointment_type else None,
            "start": self.start.isoformat(),
            "end": self.computed_end.isoformat(),
            "durationMinutes": self.duration_minutes,
            "reason": self.reason,
            "participants": [
                {
                    "actor": p.actor.reference,
                    "status": p.status,
                    "type": p.type,
                }
                for p in self.participants
            ],
            "flags": [{"type": f.type, "message": f.message} for f in self.flags],
            "isDoubleBooked": self.is_double_booked,
        }

    def to_bff_dict(self, patient_data: dict | None = None) -> dict:
        """
        Convert to BFF-friendly format (matches current frontend expectations).

        Args:
            patient_data: Optional patient data to include (id, name, dateOfBirth, gender, mrn)
        """
        # Map FHIR status to legacy status names
        status_map = {
            AppointmentStatus.BOOKED: "scheduled",
            AppointmentStatus.ARRIVED: "checked_in",
            AppointmentStatus.CHECKED_IN: "checked_in",
            AppointmentStatus.FULFILLED: "completed",
            AppointmentStatus.CANCELLED: "canceled",
            AppointmentStatus.NO_SHOW: "no_show",
        }
        display_status = status_map.get(self.status, self.status.value)

        result = {
            "id": self.id,
            "appointmentTime": self.start.isoformat(),
            "endTime": self.computed_end.isoformat(),
            "durationMinutes": self.duration_minutes,
            "visitType": self.visit_type,
            "chiefComplaint": self.reason,
            "status": display_status,
            "flags": [{"type": f.type, "message": f.message} for f in self.flags],
            "isDoubleBooked": self.is_double_booked,
        }

        if patient_data:
            result["patient"] = patient_data

        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Appointment":
        """Create Appointment from dictionary."""
        # Parse status
        status_str = data.get("status", "booked").lower().replace("_", "-").replace(" ", "-")
        status_map = {
            "scheduled": AppointmentStatus.BOOKED,
            "checked_in": AppointmentStatus.CHECKED_IN,
            "in_progress": AppointmentStatus.ARRIVED,
            "in-progress": AppointmentStatus.ARRIVED,
            "completed": AppointmentStatus.FULFILLED,
            "canceled": AppointmentStatus.CANCELLED,
            "cancelled": AppointmentStatus.CANCELLED,
            "no_show": AppointmentStatus.NO_SHOW,
            "no-show": AppointmentStatus.NO_SHOW,
            "noshow": AppointmentStatus.NO_SHOW,
        }
        try:
            status = status_map.get(status_str) or AppointmentStatus(status_str)
        except ValueError:
            status = AppointmentStatus.BOOKED

        # Parse start time
        start_str = data.get("start") or data.get("appointmentTime")
        start = datetime.fromisoformat(start_str) if start_str else datetime.utcnow()

        # Parse end time
        end = None
        if data.get("end") or data.get("endTime"):
            end_str = data.get("end") or data.get("endTime")
            end = datetime.fromisoformat(end_str)

        # Parse appointment type
        appt_type = None
        type_str = data.get("appointmentType") or data.get("visitType")
        if type_str:
            appt_type = CodeableConcept(code=type_str.lower().replace(" ", "-"), display=type_str)

        # Parse participants
        participants = []
        if data.get("patient"):
            patient_data = data["patient"]
            patient_id = patient_data.get("id") if isinstance(patient_data, dict) else patient_data
            participants.append(
                AppointmentParticipant(
                    actor=Reference.to("Patient", patient_id, patient_data.get("name") if isinstance(patient_data, dict) else None),
                    type="patient",
                )
            )
        if data.get("provider"):
            provider_data = data["provider"]
            provider_id = provider_data.get("id") if isinstance(provider_data, dict) else provider_data
            participants.append(
                AppointmentParticipant(
                    actor=Reference.to("Practitioner", provider_id),
                    type="practitioner",
                )
            )

        # Parse flags
        flags = []
        for flag_data in data.get("flags", []):
            flags.append(AppointmentFlag(type=flag_data["type"], message=flag_data["message"]))

        return cls(
            id=data["id"],
            status=status,
            appointment_type=appt_type,
            start=start,
            end=end,
            duration_minutes=data.get("durationMinutes", 30),
            reason=data.get("reason") or data.get("chiefComplaint"),
            participants=participants,
            flags=flags,
            is_double_booked=data.get("isDoubleBooked", False),
        )
