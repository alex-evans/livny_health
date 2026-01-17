"""
MedicationRequest resource model - FHIR aligned.

Represents an order/prescription for medication.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import ClassVar, Literal
from enum import Enum

from resources.core import (
    DomainResource,
    Reference,
    CodeableConcept,
    Quantity,
)


class MedicationRequestStatus(str, Enum):
    """Status of the medication request."""
    ACTIVE = "active"
    ON_HOLD = "on-hold"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    STOPPED = "stopped"
    DRAFT = "draft"
    UNKNOWN = "unknown"


class MedicationRequestIntent(str, Enum):
    """Intent of the medication request."""
    PROPOSAL = "proposal"
    PLAN = "plan"
    ORDER = "order"
    ORIGINAL_ORDER = "original-order"
    REFLEX_ORDER = "reflex-order"
    FILLER_ORDER = "filler-order"
    INSTANCE_ORDER = "instance-order"
    OPTION = "option"


@dataclass
class Dosage:
    """Dosage instructions for a medication."""
    text: str  # Human readable dosage instructions
    dose: str | None = None  # e.g., "500mg"
    frequency: str | None = None  # e.g., "twice daily"
    route: str | None = None  # e.g., "oral"
    duration_days: int | None = None
    as_needed: bool = False
    additional_instructions: str | None = None


class MedicationForm(str, Enum):
    """Form of the medication."""
    TABLET = "tablet"
    CAPSULE = "capsule"
    LIQUID = "liquid"
    INJECTION = "injection"
    TOPICAL = "topical"
    INHALER = "inhaler"
    PATCH = "patch"
    CREAM = "cream"
    SOLUTION = "solution"


@dataclass
class MedicationRequest(DomainResource):
    """
    An order or prescription for medication.

    FHIR Reference: https://www.hl7.org/fhir/medicationrequest.html
    """
    resource_type: ClassVar[str] = "MedicationRequest"

    # Status and intent
    status: MedicationRequestStatus = MedicationRequestStatus.ACTIVE
    intent: MedicationRequestIntent = MedicationRequestIntent.ORDER

    # What medication
    medication: CodeableConcept = field(
        default_factory=lambda: CodeableConcept(code="unknown", display="Unknown")
    )

    # Medication details
    brand_name: str | None = None  # e.g., "Lipitor", "Zestril"
    strength: str | None = None  # e.g., "10mg", "500mg"
    form: MedicationForm | None = None  # e.g., tablet, capsule, inhaler
    is_controlled: bool = False  # DEA scheduled controlled substance

    # For whom
    subject: Reference = field(default_factory=lambda: Reference(reference="Patient/unknown"))

    # Context
    encounter: Reference | None = None  # When written during an encounter

    # Who wrote it
    requester: Reference | None = None  # The prescriber

    # When
    authored_on: datetime = field(default_factory=datetime.utcnow)

    # Dosage
    dosage_instruction: list[Dosage] = field(default_factory=list)

    # Dispensing
    dispense_quantity: Quantity | None = None
    dispense_refills: int = 0

    # Status reason (why stopped, cancelled, etc.)
    status_reason: str | None = None

    # Additional clinical info
    pharmacy: str | None = None  # Dispensing pharmacy name
    indication: str | None = None  # Clinical reason for prescribing
    prescriber_notes: str | None = None  # Additional notes from prescriber
    drug_class: str | None = None  # Medication class (e.g., "Antihypertensive", "Statin")

    @property
    def medication_name(self) -> str:
        """Get the medication name."""
        return self.medication.display

    @property
    def patient_id(self) -> str:
        """Get the patient ID from the subject reference."""
        return self.subject.id

    @property
    def primary_dosage(self) -> Dosage | None:
        """Get the primary dosage instruction."""
        return self.dosage_instruction[0] if self.dosage_instruction else None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "resourceType": self.resource_type,
            "status": self.status.value,
            "intent": self.intent.value,
            "medication": {
                "code": self.medication.code,
                "display": self.medication.display,
            },
            "subject": self.subject.reference,
            "encounter": self.encounter.reference if self.encounter else None,
            "requester": self.requester.reference if self.requester else None,
            "authoredOn": self.authored_on.isoformat(),
            "dosageInstruction": [
                {
                    "text": d.text,
                    "dose": d.dose,
                    "frequency": d.frequency,
                    "route": d.route,
                    "durationDays": d.duration_days,
                    "asNeeded": d.as_needed,
                }
                for d in self.dosage_instruction
            ],
            "dispenseQuantity": self.dispense_quantity.value if self.dispense_quantity else None,
            "dispenseRefills": self.dispense_refills,
        }

    # Route abbreviation mapping
    ROUTE_ABBREVIATIONS: ClassVar[dict[str, str]] = {
        "oral": "PO",
        "intravenous": "IV",
        "intramuscular": "IM",
        "subcutaneous": "SubQ",
        "topical": "topical",
        "inhalation": "inhaled",
        "sublingual": "SL",
        "rectal": "PR",
        "ophthalmic": "ophthalmic",
        "otic": "otic",
        "nasal": "nasal",
        "transdermal": "transdermal",
    }

    def to_bff_dict(self) -> dict:
        """Convert to BFF-friendly format (matches current frontend expectations)."""
        dosage = self.primary_dosage
        route = dosage.route if dosage else None
        route_abbrev = self.ROUTE_ABBREVIATIONS.get(route, route) if route else None

        return {
            "id": self.id,
            "name": self.medication_name,
            "brandName": self.brand_name,
            "strength": self.strength,
            "form": self.form.value if self.form else None,
            "dosage": dosage.dose if dosage else None,
            "frequency": dosage.frequency if dosage else None,
            "route": route_abbrev,
            "started": self.authored_on.strftime("%m/%d/%Y"),
            "prescriber": self.requester.display if self.requester and self.requester.display else None,
            "status": self._get_display_status(),
            "isPRN": dosage.as_needed if dosage else False,
            "isControlled": self.is_controlled,
            # Additional fields for detail view
            "pharmacy": self.pharmacy,
            "refillsRemaining": self.dispense_refills,
            "indication": self.indication,
            "prescriberNotes": self.prescriber_notes,
            "drugClass": self.drug_class,
        }

    def _get_display_status(self) -> str:
        """Get a display-friendly status."""
        status_map = {
            MedicationRequestStatus.ACTIVE: "Active",
            MedicationRequestStatus.DRAFT: "Pending transmission",
            MedicationRequestStatus.ON_HOLD: "On Hold",
            MedicationRequestStatus.COMPLETED: "Completed",
            MedicationRequestStatus.CANCELLED: "Cancelled",
            MedicationRequestStatus.STOPPED: "Stopped",
        }
        return status_map.get(self.status, self.status.value)

    @classmethod
    def from_dict(cls, data: dict, patient_id: str | None = None) -> "MedicationRequest":
        """Create MedicationRequest from dictionary."""
        # Parse status
        status_str = data.get("status", "active").lower().replace(" ", "-")
        try:
            status = MedicationRequestStatus(status_str)
        except ValueError:
            # Handle legacy status values
            if "pending" in status_str:
                status = MedicationRequestStatus.DRAFT
            else:
                status = MedicationRequestStatus.ACTIVE

        # Parse authored date
        authored_on = datetime.utcnow()
        if data.get("authoredOn") or data.get("started"):
            date_str = data.get("authoredOn") or data.get("started")
            try:
                authored_on = datetime.fromisoformat(date_str)
            except ValueError:
                try:
                    authored_on = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    pass

        # Build dosage
        dosage_instruction = []
        if data.get("dosage") or data.get("frequency"):
            dosage_instruction.append(
                Dosage(
                    text=f"{data.get('dosage', '')} {data.get('frequency', '')}".strip(),
                    dose=data.get("dosage"),
                    frequency=data.get("frequency"),
                    duration_days=data.get("duration_days"),
                )
            )

        # Get patient reference
        subject_ref = data.get("subject") or (f"Patient/{patient_id}" if patient_id else "Patient/unknown")
        if isinstance(subject_ref, str) and not subject_ref.startswith("Patient/"):
            subject_ref = f"Patient/{subject_ref}"

        # Get medication name
        med_name = data.get("name") or data.get("medication", {}).get("display", "Unknown")

        return cls(
            id=data["id"],
            status=status,
            medication=CodeableConcept(
                code=med_name.lower().replace(" ", "-"),
                display=med_name,
            ),
            subject=Reference(reference=subject_ref) if isinstance(subject_ref, str) else subject_ref,
            authored_on=authored_on,
            dosage_instruction=dosage_instruction,
        )
