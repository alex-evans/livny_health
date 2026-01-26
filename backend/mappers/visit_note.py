"""
VisitNote mapper for domain <-> ORM conversion.
"""

from datetime import datetime

from mappers.base import Mapper
from db.models.visit_note import VisitNoteORM
from resources.visit_note import (
    VisitNote,
    SOAPNote,
    VisitVitals,
    VisitMedication,
    VisitOrder,
    VisitDiagnosis,
    VisitProvider,
    MedicationAction,
    OrderType,
    OrderStatus,
    OrderPriority,
)
from resources.core import Reference


class VisitNoteMapper(Mapper[VisitNote, VisitNoteORM]):
    """Mapper for VisitNote <-> VisitNoteORM conversion."""

    def to_orm(self, domain: VisitNote) -> VisitNoteORM:
        """Convert VisitNote domain model to ORM."""
        return VisitNoteORM(
            id=domain.id,
            encounter_id=domain.encounter.id,
            subject_id=domain.subject.id,
            visit_type=domain.visit_type,
            status=domain.status,
            date=domain.date,
            chief_complaint=domain.chief_complaint,
            location=domain.location,
            duration=domain.duration,
            provider=self._provider_to_dict(domain.provider)
            if domain.provider
            else None,
            diagnoses=[self._diagnosis_to_dict(d) for d in domain.diagnoses],
            soap_note=self._soap_to_dict(domain.soap_note)
            if domain.soap_note
            else None,
            vitals=self._vitals_to_dict(domain.vitals) if domain.vitals else None,
            medications=[self._medication_to_dict(m) for m in domain.medications],
            orders=[self._order_to_dict(o) for o in domain.orders],
            notes=domain.notes,
            has_critical_findings=domain.has_critical_findings,
            critical_findings_summary=domain.critical_findings_summary,
            has_follow_up_required=domain.has_follow_up_required,
            follow_up_summary=domain.follow_up_summary,
            meta_version_id=domain.meta_version_id,
            meta_last_updated=domain.meta_last_updated,
        )

    def to_domain(self, orm: VisitNoteORM) -> VisitNote:
        """Convert VisitNoteORM to VisitNote domain model."""
        return VisitNote(
            id=orm.id,
            encounter=Reference(reference=f"Encounter/{orm.encounter_id}"),
            subject=Reference(reference=f"Patient/{orm.subject_id}"),
            visit_type=orm.visit_type,
            status=orm.status,
            date=orm.date,
            chief_complaint=orm.chief_complaint,
            location=orm.location,
            duration=orm.duration,
            provider=self._dict_to_provider(orm.provider) if orm.provider else None,
            diagnoses=[self._dict_to_diagnosis(d) for d in (orm.diagnoses or [])],
            soap_note=self._dict_to_soap(orm.soap_note) if orm.soap_note else None,
            vitals=self._dict_to_vitals(orm.vitals) if orm.vitals else None,
            medications=[
                self._dict_to_medication(m) for m in (orm.medications or [])
            ],
            orders=[self._dict_to_order(o) for o in (orm.orders or [])],
            notes=orm.notes,
            has_critical_findings=orm.has_critical_findings,
            critical_findings_summary=orm.critical_findings_summary,
            has_follow_up_required=orm.has_follow_up_required,
            follow_up_summary=orm.follow_up_summary,
            meta_version_id=orm.meta_version_id,
            meta_last_updated=orm.meta_last_updated,
        )

    def _provider_to_dict(self, p: VisitProvider) -> dict:
        return {
            "id": p.id,
            "name": p.name,
            "role": p.role,
            "specialty": p.specialty,
        }

    def _dict_to_provider(self, d: dict) -> VisitProvider:
        return VisitProvider(
            id=d["id"],
            name=d["name"],
            role=d["role"],
            specialty=d.get("specialty"),
        )

    def _diagnosis_to_dict(self, d: VisitDiagnosis) -> dict:
        return {
            "code": d.code,
            "description": d.description,
            "is_primary": d.is_primary,
        }

    def _dict_to_diagnosis(self, d: dict) -> VisitDiagnosis:
        return VisitDiagnosis(
            code=d["code"],
            description=d["description"],
            is_primary=d.get("is_primary", False),
        )

    def _soap_to_dict(self, s: SOAPNote) -> dict:
        return {
            "subjective": s.subjective,
            "objective": s.objective,
            "assessment": s.assessment,
            "plan": s.plan,
        }

    def _dict_to_soap(self, d: dict) -> SOAPNote:
        return SOAPNote(
            subjective=d.get("subjective", ""),
            objective=d.get("objective", ""),
            assessment=d.get("assessment", ""),
            plan=d.get("plan", ""),
        )

    def _vitals_to_dict(self, v: VisitVitals) -> dict:
        result = {}
        if v.blood_pressure_systolic is not None:
            result["blood_pressure_systolic"] = v.blood_pressure_systolic
        if v.blood_pressure_diastolic is not None:
            result["blood_pressure_diastolic"] = v.blood_pressure_diastolic
        if v.heart_rate is not None:
            result["heart_rate"] = v.heart_rate
        if v.temperature is not None:
            result["temperature"] = v.temperature
            result["temperature_unit"] = v.temperature_unit
        if v.weight is not None:
            result["weight"] = v.weight
            result["weight_unit"] = v.weight_unit
        if v.oxygen_saturation is not None:
            result["oxygen_saturation"] = v.oxygen_saturation
        if v.respiratory_rate is not None:
            result["respiratory_rate"] = v.respiratory_rate
        if v.recorded_at:
            result["recorded_at"] = v.recorded_at.isoformat()
        return result

    def _dict_to_vitals(self, d: dict) -> VisitVitals:
        recorded_at = None
        if d.get("recorded_at"):
            recorded_at = datetime.fromisoformat(d["recorded_at"])
        return VisitVitals(
            blood_pressure_systolic=d.get("blood_pressure_systolic"),
            blood_pressure_diastolic=d.get("blood_pressure_diastolic"),
            heart_rate=d.get("heart_rate"),
            temperature=d.get("temperature"),
            temperature_unit=d.get("temperature_unit", "F"),
            weight=d.get("weight"),
            weight_unit=d.get("weight_unit", "lbs"),
            oxygen_saturation=d.get("oxygen_saturation"),
            respiratory_rate=d.get("respiratory_rate"),
            recorded_at=recorded_at,
        )

    def _medication_to_dict(self, m: VisitMedication) -> dict:
        return {
            "id": m.id,
            "name": m.name,
            "dosage": m.dosage,
            "frequency": m.frequency,
            "action": m.action.value,
            "route": m.route,
            "instructions": m.instructions,
        }

    def _dict_to_medication(self, d: dict) -> VisitMedication:
        return VisitMedication(
            id=d["id"],
            name=d["name"],
            dosage=d["dosage"],
            frequency=d["frequency"],
            action=MedicationAction(d.get("action", "prescribed")),
            route=d.get("route"),
            instructions=d.get("instructions"),
        )

    def _order_to_dict(self, o: VisitOrder) -> dict:
        result = {
            "id": o.id,
            "order_type": o.order_type.value,
            "name": o.name,
            "status": o.status.value,
            "ordered_at": o.ordered_at.isoformat(),
            "priority": o.priority.value,
        }
        if o.completed_at:
            result["completed_at"] = o.completed_at.isoformat()
        if o.result:
            result["result"] = o.result
        return result

    def _dict_to_order(self, d: dict) -> VisitOrder:
        completed_at = None
        if d.get("completed_at"):
            completed_at = datetime.fromisoformat(d["completed_at"])
        return VisitOrder(
            id=d["id"],
            order_type=OrderType(d.get("order_type", "other")),
            name=d["name"],
            status=OrderStatus(d.get("status", "ordered")),
            ordered_at=datetime.fromisoformat(d["ordered_at"]),
            completed_at=completed_at,
            result=d.get("result"),
            priority=OrderPriority(d.get("priority", "routine")),
        )
