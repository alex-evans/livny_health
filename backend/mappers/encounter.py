"""
Encounter mapper for domain <-> ORM conversion.
"""

from datetime import datetime

from mappers.base import Mapper
from db.models.encounter import EncounterORM
from resources.encounter import (
    Encounter,
    EncounterStatus,
    EncounterClass,
    EncounterParticipant,
)
from resources.core import CodeableConcept, Reference, Period


class EncounterMapper(Mapper[Encounter, EncounterORM]):
    """Mapper for Encounter <-> EncounterORM conversion."""

    def to_orm(self, domain: Encounter) -> EncounterORM:
        """Convert Encounter domain model to ORM."""
        return EncounterORM(
            id=domain.id,
            status=domain.status.value,
            encounter_class=domain.encounter_class.value,
            type={
                "code": domain.type.code,
                "display": domain.type.display,
                "system": domain.type.system,
            }
            if domain.type
            else None,
            subject_id=domain.subject.id,
            participants=[
                {
                    "individual": {
                        "reference": p.individual.reference,
                        "display": p.individual.display,
                    },
                    "type": p.type,
                }
                for p in domain.participants
            ],
            period={
                "start": domain.period.start.isoformat(),
                "end": domain.period.end.isoformat() if domain.period.end else None,
            }
            if domain.period
            else None,
            reason=[
                {"code": r.code, "display": r.display, "system": r.system}
                for r in domain.reason
            ],
            chief_complaint=domain.chief_complaint,
            appointment_id=domain.appointment.id if domain.appointment else None,
            # Note fields
            note_content=domain.note_content,
            note_version=domain.note_version,
            note_word_count=domain.note_word_count,
            note_updated_at=domain.note_updated_at,
            # Workflow timestamps
            opened_at=domain.opened_at,
            completed_at=domain.completed_at,
            signed_at=domain.signed_at,
            reopened_at=domain.reopened_at,
            # Signature tracking
            signed_by_id=domain.signed_by_id,
            signed_by_name=domain.signed_by_name,
            # Metadata
            meta_version_id=domain.meta_version_id,
            meta_last_updated=domain.meta_last_updated,
        )

    def to_domain(self, orm: EncounterORM) -> Encounter:
        """Convert EncounterORM to Encounter domain model."""
        # Parse status
        try:
            status = EncounterStatus(orm.status)
        except ValueError:
            status = EncounterStatus.SCHEDULED

        # Parse encounter class
        try:
            encounter_class = EncounterClass(orm.encounter_class)
        except ValueError:
            encounter_class = EncounterClass.AMBULATORY

        # Parse type
        enc_type = None
        if orm.type:
            enc_type = CodeableConcept(
                code=orm.type.get("code", ""),
                display=orm.type.get("display", ""),
                system=orm.type.get("system"),
            )

        # Parse participants
        participants = []
        for p in orm.participants or []:
            individual = p.get("individual", {})
            participants.append(
                EncounterParticipant(
                    individual=Reference(
                        reference=individual.get("reference", ""),
                        display=individual.get("display"),
                    ),
                    type=p.get("type"),
                )
            )

        # Parse period
        period = None
        if orm.period:
            period = Period(
                start=datetime.fromisoformat(orm.period["start"]),
                end=datetime.fromisoformat(orm.period["end"])
                if orm.period.get("end")
                else None,
            )

        # Parse reason
        reason = []
        for r in orm.reason or []:
            reason.append(
                CodeableConcept(
                    code=r.get("code", ""),
                    display=r.get("display", ""),
                    system=r.get("system"),
                )
            )

        return Encounter(
            id=orm.id,
            status=status,
            encounter_class=encounter_class,
            type=enc_type,
            subject=Reference(reference=f"Patient/{orm.subject_id}"),
            participants=participants,
            period=period,
            reason=reason,
            chief_complaint=orm.chief_complaint,
            appointment=Reference(reference=f"Appointment/{orm.appointment_id}")
            if orm.appointment_id
            else None,
            # Note fields
            note_content=orm.note_content,
            note_version=orm.note_version,
            note_word_count=orm.note_word_count,
            note_updated_at=orm.note_updated_at,
            # Workflow timestamps
            opened_at=orm.opened_at,
            completed_at=orm.completed_at,
            signed_at=orm.signed_at,
            reopened_at=orm.reopened_at,
            # Signature tracking
            signed_by_id=orm.signed_by_id,
            signed_by_name=orm.signed_by_name,
            # Metadata
            meta_version_id=orm.meta_version_id,
            meta_last_updated=orm.meta_last_updated,
        )
