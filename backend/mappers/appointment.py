"""
Appointment mapper for domain <-> ORM conversion.
"""

from datetime import datetime

from mappers.base import Mapper
from db.models.appointment import AppointmentORM
from resources.appointment import (
    Appointment,
    AppointmentStatus,
    AppointmentParticipant,
    AppointmentFlag,
)
from resources.core import CodeableConcept, Reference


class AppointmentMapper(Mapper[Appointment, AppointmentORM]):
    """Mapper for Appointment <-> AppointmentORM conversion."""

    def to_orm(self, domain: Appointment) -> AppointmentORM:
        """Convert Appointment domain model to ORM."""
        return AppointmentORM(
            id=domain.id,
            status=domain.status.value,
            appointment_type={
                "code": domain.appointment_type.code,
                "display": domain.appointment_type.display,
                "system": domain.appointment_type.system,
            }
            if domain.appointment_type
            else None,
            start=domain.start,
            end=domain.end,
            duration_minutes=domain.duration_minutes,
            reason=domain.reason,
            participants=[
                {
                    "actor": {
                        "reference": p.actor.reference,
                        "display": p.actor.display,
                    },
                    "status": p.status,
                    "type": p.type,
                }
                for p in domain.participants
            ],
            flags=[{"type": f.type, "message": f.message} for f in domain.flags],
            is_double_booked=domain.is_double_booked,
            meta_version_id=domain.meta_version_id,
            meta_last_updated=domain.meta_last_updated,
        )

    def to_domain(self, orm: AppointmentORM) -> Appointment:
        """Convert AppointmentORM to Appointment domain model."""
        # Parse status
        try:
            status = AppointmentStatus(orm.status)
        except ValueError:
            status = AppointmentStatus.BOOKED

        # Parse appointment type
        appt_type = None
        if orm.appointment_type:
            appt_type = CodeableConcept(
                code=orm.appointment_type.get("code", ""),
                display=orm.appointment_type.get("display", ""),
                system=orm.appointment_type.get("system"),
            )

        # Parse participants
        participants = []
        for p in orm.participants or []:
            actor = p.get("actor", {})
            participants.append(
                AppointmentParticipant(
                    actor=Reference(
                        reference=actor.get("reference", ""),
                        display=actor.get("display"),
                    ),
                    status=p.get("status", "accepted"),
                    type=p.get("type"),
                )
            )

        # Parse flags
        flags = []
        for f in orm.flags or []:
            flags.append(AppointmentFlag(type=f["type"], message=f["message"]))

        return Appointment(
            id=orm.id,
            status=status,
            appointment_type=appt_type,
            start=orm.start,
            end=orm.end,
            duration_minutes=orm.duration_minutes,
            reason=orm.reason,
            participants=participants,
            flags=flags,
            is_double_booked=orm.is_double_booked,
            meta_version_id=orm.meta_version_id,
            meta_last_updated=orm.meta_last_updated,
        )
