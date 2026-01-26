"""
MedicationRequest mapper for domain <-> ORM conversion.
"""

from datetime import datetime

from mappers.base import Mapper
from db.models.medication_request import MedicationRequestORM
from resources.medication_request import (
    MedicationRequest,
    MedicationRequestStatus,
    MedicationRequestIntent,
    MedicationForm,
    Dosage,
)
from resources.core import CodeableConcept, Reference, Quantity


class MedicationRequestMapper(Mapper[MedicationRequest, MedicationRequestORM]):
    """Mapper for MedicationRequest <-> MedicationRequestORM conversion."""

    def to_orm(self, domain: MedicationRequest) -> MedicationRequestORM:
        """Convert MedicationRequest domain model to ORM."""
        return MedicationRequestORM(
            id=domain.id,
            status=domain.status.value,
            intent=domain.intent.value,
            medication={
                "code": domain.medication.code,
                "display": domain.medication.display,
                "system": domain.medication.system,
            },
            brand_name=domain.brand_name,
            strength=domain.strength,
            form=domain.form.value if domain.form else None,
            is_controlled=domain.is_controlled,
            subject_id=domain.subject.id,
            encounter_id=domain.encounter.id if domain.encounter else None,
            requester={
                "reference": domain.requester.reference,
                "display": domain.requester.display,
            }
            if domain.requester
            else None,
            authored_on=domain.authored_on,
            dosage_instruction=[
                {
                    "text": d.text,
                    "dose": d.dose,
                    "frequency": d.frequency,
                    "route": d.route,
                    "duration_days": d.duration_days,
                    "as_needed": d.as_needed,
                    "additional_instructions": d.additional_instructions,
                }
                for d in domain.dosage_instruction
            ],
            dispense_quantity={
                "value": domain.dispense_quantity.value,
                "unit": domain.dispense_quantity.unit,
                "code": domain.dispense_quantity.code,
            }
            if domain.dispense_quantity
            else None,
            dispense_refills=domain.dispense_refills,
            status_reason=domain.status_reason,
            pharmacy=domain.pharmacy,
            indication=domain.indication,
            prescriber_notes=domain.prescriber_notes,
            drug_class=domain.drug_class,
            meta_version_id=domain.meta_version_id,
            meta_last_updated=domain.meta_last_updated,
        )

    def to_domain(self, orm: MedicationRequestORM) -> MedicationRequest:
        """Convert MedicationRequestORM to MedicationRequest domain model."""
        med_data = orm.medication or {}

        # Parse status
        try:
            status = MedicationRequestStatus(orm.status)
        except ValueError:
            status = MedicationRequestStatus.ACTIVE

        # Parse intent
        try:
            intent = MedicationRequestIntent(orm.intent)
        except ValueError:
            intent = MedicationRequestIntent.ORDER

        # Parse form
        form = None
        if orm.form:
            try:
                form = MedicationForm(orm.form)
            except ValueError:
                pass

        # Parse dosage instructions
        dosage_instruction = []
        for d in orm.dosage_instruction or []:
            dosage_instruction.append(
                Dosage(
                    text=d.get("text", ""),
                    dose=d.get("dose"),
                    frequency=d.get("frequency"),
                    route=d.get("route"),
                    duration_days=d.get("duration_days"),
                    as_needed=d.get("as_needed", False),
                    additional_instructions=d.get("additional_instructions"),
                )
            )

        # Parse dispense quantity
        dispense_quantity = None
        if orm.dispense_quantity:
            dispense_quantity = Quantity(
                value=orm.dispense_quantity["value"],
                unit=orm.dispense_quantity["unit"],
                code=orm.dispense_quantity.get("code"),
            )

        # Parse requester
        requester = None
        if orm.requester:
            requester = Reference(
                reference=orm.requester["reference"],
                display=orm.requester.get("display"),
            )

        return MedicationRequest(
            id=orm.id,
            status=status,
            intent=intent,
            medication=CodeableConcept(
                code=med_data.get("code", "unknown"),
                display=med_data.get("display", "Unknown"),
                system=med_data.get("system"),
            ),
            brand_name=orm.brand_name,
            strength=orm.strength,
            form=form,
            is_controlled=orm.is_controlled,
            subject=Reference(reference=f"Patient/{orm.subject_id}"),
            encounter=Reference(reference=f"Encounter/{orm.encounter_id}")
            if orm.encounter_id
            else None,
            requester=requester,
            authored_on=orm.authored_on,
            dosage_instruction=dosage_instruction,
            dispense_quantity=dispense_quantity,
            dispense_refills=orm.dispense_refills,
            status_reason=orm.status_reason,
            pharmacy=orm.pharmacy,
            indication=orm.indication,
            prescriber_notes=orm.prescriber_notes,
            drug_class=orm.drug_class,
            meta_version_id=orm.meta_version_id,
            meta_last_updated=orm.meta_last_updated,
        )
