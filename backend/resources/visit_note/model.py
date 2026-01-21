"""
Visit Note resource models.

Contains models for clinical documentation associated with encounters:
- SOAP notes (Subjective, Objective, Assessment, Plan)
- Vital signs
- Medications prescribed/modified during visit
- Clinical orders (labs, imaging, referrals)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Literal
from enum import Enum

from resources.core import DomainResource, Reference


class MedicationAction(str, Enum):
    """Action taken on a medication during a visit."""
    PRESCRIBED = "prescribed"
    MODIFIED = "modified"
    DISCONTINUED = "discontinued"
    CONTINUED = "continued"


class OrderType(str, Enum):
    """Type of clinical order."""
    LAB = "lab"
    IMAGING = "imaging"
    REFERRAL = "referral"
    PROCEDURE = "procedure"
    OTHER = "other"


class OrderStatus(str, Enum):
    """Status of a clinical order."""
    ORDERED = "ordered"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderPriority(str, Enum):
    """Priority of a clinical order."""
    ROUTINE = "routine"
    URGENT = "urgent"
    STAT = "stat"


@dataclass
class SOAPNote:
    """
    SOAP Note structure for clinical documentation.

    SOAP is a standard format for documenting patient encounters:
    - Subjective: Patient's description of symptoms, history
    - Objective: Physical exam findings, observations
    - Assessment: Clinical assessment/diagnosis
    - Plan: Treatment plan
    """
    subjective: str
    objective: str
    assessment: str
    plan: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "subjective": self.subjective,
            "objective": self.objective,
            "assessment": self.assessment,
            "plan": self.plan,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SOAPNote":
        """Create SOAPNote from dictionary."""
        return cls(
            subjective=data.get("subjective", ""),
            objective=data.get("objective", ""),
            assessment=data.get("assessment", ""),
            plan=data.get("plan", ""),
        )


@dataclass
class VisitVitals:
    """
    Vital signs recorded during a visit.
    """
    blood_pressure_systolic: int | None = None  # mmHg
    blood_pressure_diastolic: int | None = None  # mmHg
    heart_rate: int | None = None  # bpm
    temperature: float | None = None
    temperature_unit: Literal["F", "C"] = "F"
    weight: float | None = None
    weight_unit: Literal["lbs", "kg"] = "lbs"
    oxygen_saturation: int | None = None  # percentage
    respiratory_rate: int | None = None  # breaths per minute
    recorded_at: datetime | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {}
        if self.blood_pressure_systolic is not None:
            result["bloodPressureSystolic"] = self.blood_pressure_systolic
        if self.blood_pressure_diastolic is not None:
            result["bloodPressureDiastolic"] = self.blood_pressure_diastolic
        if self.heart_rate is not None:
            result["heartRate"] = self.heart_rate
        if self.temperature is not None:
            result["temperature"] = self.temperature
            result["temperatureUnit"] = self.temperature_unit
        if self.weight is not None:
            result["weight"] = self.weight
            result["weightUnit"] = self.weight_unit
        if self.oxygen_saturation is not None:
            result["oxygenSaturation"] = self.oxygen_saturation
        if self.respiratory_rate is not None:
            result["respiratoryRate"] = self.respiratory_rate
        if self.recorded_at:
            result["recordedAt"] = self.recorded_at.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "VisitVitals":
        """Create VisitVitals from dictionary."""
        recorded_at = None
        if data.get("recordedAt"):
            recorded_at = datetime.fromisoformat(data["recordedAt"])

        return cls(
            blood_pressure_systolic=data.get("bloodPressureSystolic"),
            blood_pressure_diastolic=data.get("bloodPressureDiastolic"),
            heart_rate=data.get("heartRate"),
            temperature=data.get("temperature"),
            temperature_unit=data.get("temperatureUnit", "F"),
            weight=data.get("weight"),
            weight_unit=data.get("weightUnit", "lbs"),
            oxygen_saturation=data.get("oxygenSaturation"),
            respiratory_rate=data.get("respiratoryRate"),
            recorded_at=recorded_at,
        )

    @property
    def blood_pressure_display(self) -> str | None:
        """Get formatted blood pressure string."""
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"
        return None


@dataclass
class VisitMedication:
    """
    Medication prescribed or modified during a visit.
    """
    id: str
    name: str
    dosage: str
    frequency: str
    action: MedicationAction
    route: str | None = None  # oral, IV, topical, etc.
    instructions: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "id": self.id,
            "name": self.name,
            "dosage": self.dosage,
            "frequency": self.frequency,
            "action": self.action.value,
        }
        if self.route:
            result["route"] = self.route
        if self.instructions:
            result["instructions"] = self.instructions
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "VisitMedication":
        """Create VisitMedication from dictionary."""
        action = data.get("action", "prescribed")
        if isinstance(action, str):
            action = MedicationAction(action)

        return cls(
            id=data["id"],
            name=data["name"],
            dosage=data["dosage"],
            frequency=data["frequency"],
            action=action,
            route=data.get("route"),
            instructions=data.get("instructions"),
        )


@dataclass
class VisitOrder:
    """
    Clinical order placed during a visit (lab, imaging, referral, etc.).
    """
    id: str
    order_type: OrderType
    name: str  # e.g., "CBC", "Chest X-ray", "Cardiology consult"
    status: OrderStatus
    ordered_at: datetime
    completed_at: datetime | None = None
    result: str | None = None  # Brief result summary if available
    priority: OrderPriority = OrderPriority.ROUTINE

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "id": self.id,
            "orderType": self.order_type.value,
            "name": self.name,
            "status": self.status.value,
            "orderedAt": self.ordered_at.isoformat(),
            "priority": self.priority.value,
        }
        if self.completed_at:
            result["completedAt"] = self.completed_at.isoformat()
        if self.result:
            result["result"] = self.result
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "VisitOrder":
        """Create VisitOrder from dictionary."""
        order_type = data.get("orderType", "other")
        if isinstance(order_type, str):
            order_type = OrderType(order_type)

        status = data.get("status", "ordered")
        if isinstance(status, str):
            status = OrderStatus(status)

        priority = data.get("priority", "routine")
        if isinstance(priority, str):
            priority = OrderPriority(priority)

        completed_at = None
        if data.get("completedAt"):
            completed_at = datetime.fromisoformat(data["completedAt"])

        return cls(
            id=data["id"],
            order_type=order_type,
            name=data["name"],
            status=status,
            ordered_at=datetime.fromisoformat(data["orderedAt"]),
            completed_at=completed_at,
            result=data.get("result"),
            priority=priority,
        )


@dataclass
class VisitDiagnosis:
    """Diagnosis associated with a visit."""
    code: str  # ICD-10 code
    description: str
    is_primary: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "code": self.code,
            "description": self.description,
            "isPrimary": self.is_primary,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VisitDiagnosis":
        """Create VisitDiagnosis from dictionary."""
        return cls(
            code=data["code"],
            description=data["description"],
            is_primary=data.get("isPrimary", False),
        )


@dataclass
class VisitProvider:
    """Provider information for a visit."""
    id: str
    name: str
    role: str  # "Attending", "Resident", "NP", "PA"
    specialty: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "id": self.id,
            "name": self.name,
            "role": self.role,
        }
        if self.specialty:
            result["specialty"] = self.specialty
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "VisitProvider":
        """Create VisitProvider from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            role=data["role"],
            specialty=data.get("specialty"),
        )


@dataclass
class VisitNote(DomainResource):
    """
    Complete visit note associated with an encounter.

    Contains all clinical documentation for a visit including:
    - SOAP note
    - Vital signs
    - Medications prescribed/modified
    - Clinical orders
    """
    resource_type: ClassVar[str] = "VisitNote"

    # Reference to the encounter this note is for
    encounter: Reference = field(default_factory=lambda: Reference(reference="Encounter/unknown"))

    # Reference to the patient
    subject: Reference = field(default_factory=lambda: Reference(reference="Patient/unknown"))

    # Visit details
    # Valid visit types: office_visit, telehealth, urgent_care, emergency,
    # hospital_admission, procedure, lab_only, follow_up, annual_physical
    visit_type: str = "office_visit"
    status: str = "completed"
    date: datetime = field(default_factory=datetime.utcnow)
    chief_complaint: str = ""
    location: str | None = None
    duration: int | None = None  # minutes

    # Provider
    provider: VisitProvider | None = None

    # Diagnoses
    diagnoses: list[VisitDiagnosis] = field(default_factory=list)

    # Clinical documentation
    soap_note: SOAPNote | None = None
    vitals: VisitVitals | None = None
    medications: list[VisitMedication] = field(default_factory=list)
    orders: list[VisitOrder] = field(default_factory=list)

    # Brief summary (for preview)
    notes: str | None = None

    # Timeline enhancement fields
    has_critical_findings: bool = False
    critical_findings_summary: str | None = None
    has_follow_up_required: bool = False
    follow_up_summary: str | None = None

    @property
    def patient_id(self) -> str:
        """Get the patient ID from the subject reference."""
        return self.subject.id

    @property
    def encounter_id(self) -> str:
        """Get the encounter ID from the encounter reference."""
        return self.encounter.id

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "id": self.id,
            "resourceType": self.resource_type,
            "encounter": self.encounter.reference,
            "subject": self.subject.reference,
            "visitType": self.visit_type,
            "status": self.status,
            "date": self.date.isoformat(),
            "chiefComplaint": self.chief_complaint,
            "diagnoses": [d.to_dict() for d in self.diagnoses],
        }

        if self.location:
            result["location"] = self.location
        if self.duration:
            result["duration"] = self.duration
        if self.provider:
            result["provider"] = self.provider.to_dict()
        if self.soap_note:
            result["soapNote"] = self.soap_note.to_dict()
        if self.vitals:
            result["vitals"] = self.vitals.to_dict()
        if self.medications:
            result["medications"] = [m.to_dict() for m in self.medications]
        if self.orders:
            result["orders"] = [o.to_dict() for o in self.orders]
        if self.notes:
            result["notes"] = self.notes
        # Timeline enhancement fields
        if self.has_critical_findings:
            result["hasCriticalFindings"] = self.has_critical_findings
        if self.critical_findings_summary:
            result["criticalFindingsSummary"] = self.critical_findings_summary
        if self.has_follow_up_required:
            result["hasFollowUpRequired"] = self.has_follow_up_required
        if self.follow_up_summary:
            result["followUpSummary"] = self.follow_up_summary

        return result

    def to_bff_dict(self) -> dict:
        """Convert to BFF-friendly format for the frontend."""
        result = {
            "id": self.id,
            "date": self.date.isoformat(),
            "visitType": self.visit_type,
            "status": self.status,
            "chiefComplaint": self.chief_complaint,
            "diagnoses": [d.to_dict() for d in self.diagnoses],
            "provider": self.provider.to_dict() if self.provider else None,
        }

        if self.location:
            result["location"] = self.location
        if self.duration:
            result["duration"] = self.duration
        if self.notes:
            result["notes"] = self.notes
        if self.soap_note:
            result["soapNote"] = self.soap_note.to_dict()
        if self.vitals:
            result["vitals"] = self.vitals.to_dict()
        if self.medications:
            result["medications"] = [m.to_dict() for m in self.medications]
        if self.orders:
            result["orders"] = [o.to_dict() for o in self.orders]
        # Timeline enhancement fields
        if self.has_critical_findings:
            result["hasCriticalFindings"] = self.has_critical_findings
        if self.critical_findings_summary:
            result["criticalFindingsSummary"] = self.critical_findings_summary
        if self.has_follow_up_required:
            result["hasFollowUpRequired"] = self.has_follow_up_required
        if self.follow_up_summary:
            result["followUpSummary"] = self.follow_up_summary

        return result

    @classmethod
    def from_dict(cls, data: dict) -> "VisitNote":
        """Create VisitNote from dictionary."""
        # Parse encounter reference
        encounter_ref = data.get("encounter", "Encounter/unknown")
        if not encounter_ref.startswith("Encounter/"):
            encounter_ref = f"Encounter/{encounter_ref}"

        # Parse subject reference
        subject_ref = data.get("subject", "Patient/unknown")
        if not subject_ref.startswith("Patient/"):
            subject_ref = f"Patient/{subject_ref}"

        # Parse date
        date = datetime.utcnow()
        if data.get("date"):
            date = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))

        # Parse provider
        provider = None
        if data.get("provider"):
            provider = VisitProvider.from_dict(data["provider"])

        # Parse diagnoses
        diagnoses = []
        for d in data.get("diagnoses", []):
            diagnoses.append(VisitDiagnosis.from_dict(d))

        # Parse SOAP note
        soap_note = None
        if data.get("soapNote"):
            soap_note = SOAPNote.from_dict(data["soapNote"])

        # Parse vitals
        vitals = None
        if data.get("vitals"):
            vitals = VisitVitals.from_dict(data["vitals"])

        # Parse medications
        medications = []
        for m in data.get("medications", []):
            medications.append(VisitMedication.from_dict(m))

        # Parse orders
        orders = []
        for o in data.get("orders", []):
            orders.append(VisitOrder.from_dict(o))

        return cls(
            id=data["id"],
            encounter=Reference(reference=encounter_ref),
            subject=Reference(reference=subject_ref),
            visit_type=data.get("visitType", "office_visit"),
            status=data.get("status", "completed"),
            date=date,
            chief_complaint=data.get("chiefComplaint", ""),
            location=data.get("location"),
            duration=data.get("duration"),
            provider=provider,
            diagnoses=diagnoses,
            soap_note=soap_note,
            vitals=vitals,
            medications=medications,
            orders=orders,
            notes=data.get("notes"),
            # Timeline enhancement fields
            has_critical_findings=data.get("hasCriticalFindings", False),
            critical_findings_summary=data.get("criticalFindingsSummary"),
            has_follow_up_required=data.get("hasFollowUpRequired", False),
            follow_up_summary=data.get("followUpSummary"),
        )
