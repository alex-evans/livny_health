"""
Patient mapper for domain <-> ORM conversion.
"""

from datetime import date, datetime

from mappers.base import Mapper
from db.models.patient import PatientORM
from resources.patient import (
    Patient,
    Problem,
    ProblemStatus,
    ProblemPriority,
    ProblemSeverity,
    ClinicalCategory,
    ProblemComplexity,
    RelatedVisit,
    RelatedMedication,
    RelatedLabResult,
    Insurance,
    RecentVitals,
    AllergyReviewStatus,
)
from resources.core import (
    HumanName,
    Gender,
    Identifier,
    ContactPoint,
    Address,
    Reference,
)


class PatientMapper(Mapper[Patient, PatientORM]):
    """Mapper for Patient <-> PatientORM conversion."""

    def to_orm(self, domain: Patient) -> PatientORM:
        """Convert Patient domain model to ORM."""
        return PatientORM(
            id=domain.id,
            name_family=domain.name.family,
            name_given=domain.name.given,
            name_prefix=domain.name.prefix,
            name_suffix=domain.name.suffix,
            birth_date=domain.birth_date,
            gender=domain.gender.value,
            active=domain.active,
            identifiers=[
                {"system": i.system, "value": i.value} for i in domain.identifiers
            ],
            telecom=[
                {"system": t.system, "value": t.value, "use": t.use}
                for t in domain.telecom
            ],
            address=[
                {
                    "line": a.line,
                    "city": a.city,
                    "state": a.state,
                    "postal_code": a.postal_code,
                    "country": a.country,
                }
                for a in domain.address
            ],
            problem_list=[self._problem_to_dict(p) for p in domain.problem_list],
            recent_vitals=self._vitals_to_dict(domain.recent_vitals)
            if domain.recent_vitals
            else None,
            insurance=self._insurance_to_dict(domain.insurance)
            if domain.insurance
            else None,
            allergy_review_status=self._allergy_review_to_dict(
                domain.allergy_review_status
            )
            if domain.allergy_review_status
            else None,
            meta_version_id=domain.meta_version_id,
            meta_last_updated=domain.meta_last_updated,
        )

    def to_domain(self, orm: PatientORM) -> Patient:
        """Convert PatientORM to Patient domain model."""
        return Patient(
            id=orm.id,
            name=HumanName(
                family=orm.name_family,
                given=orm.name_given or [],
                prefix=orm.name_prefix or [],
                suffix=orm.name_suffix or [],
            ),
            birth_date=orm.birth_date,
            gender=Gender(orm.gender) if orm.gender else Gender.UNKNOWN,
            active=orm.active,
            identifiers=[
                Identifier(system=i["system"], value=i["value"])
                for i in (orm.identifiers or [])
            ],
            telecom=[
                ContactPoint(system=t["system"], value=t["value"], use=t.get("use"))
                for t in (orm.telecom or [])
            ],
            address=[
                Address(
                    line=a.get("line", []),
                    city=a.get("city"),
                    state=a.get("state"),
                    postal_code=a.get("postal_code"),
                    country=a.get("country"),
                )
                for a in (orm.address or [])
            ],
            problem_list=[
                self._dict_to_problem(p) for p in (orm.problem_list or [])
            ],
            recent_vitals=self._dict_to_vitals(orm.recent_vitals)
            if orm.recent_vitals
            else None,
            insurance=self._dict_to_insurance(orm.insurance)
            if orm.insurance
            else None,
            allergy_review_status=self._dict_to_allergy_review(orm.allergy_review_status)
            if orm.allergy_review_status
            else None,
            meta_version_id=orm.meta_version_id,
            meta_last_updated=orm.meta_last_updated,
        )

    def _problem_to_dict(self, p: Problem) -> dict:
        """Convert Problem to dictionary for JSONB storage."""
        result = {
            "name": p.name,
            "icd10_code": p.icd10_code,
            "onset_date": p.onset_date.isoformat() if p.onset_date else None,
            "status": p.status.value,
            "priority": p.priority.value,
            "is_critical": p.is_critical,
        }
        if p.severity:
            result["severity"] = p.severity.value
        if p.documenting_provider:
            result["documenting_provider"] = p.documenting_provider
        if p.documented_date:
            result["documented_date"] = p.documented_date.isoformat()
        if p.resolved_date:
            result["resolved_date"] = p.resolved_date.isoformat()
        if p.resolved_by_provider:
            result["resolved_by_provider"] = p.resolved_by_provider
        if p.clinical_category:
            result["clinical_category"] = p.clinical_category.value
        if p.complexity:
            result["complexity"] = p.complexity.value
        if p.parent_problem_code:
            result["parent_problem_code"] = p.parent_problem_code
        if p.related_visits:
            result["related_visits"] = [
                {
                    "visit_id": v.visit_id,
                    "date": v.date.isoformat() if v.date else None,
                    "visit_type": v.visit_type,
                    "provider_name": v.provider_name,
                }
                for v in p.related_visits
            ]
        if p.related_medications:
            result["related_medications"] = [
                {
                    "medication_id": m.medication_id,
                    "name": m.name,
                    "dosage": m.dosage,
                }
                for m in p.related_medications
            ]
        if p.related_labs:
            result["related_labs"] = [
                {
                    "lab_name": lab.lab_name,
                    "most_recent_value": lab.most_recent_value,
                    "most_recent_date": lab.most_recent_date.isoformat()
                    if lab.most_recent_date
                    else None,
                    "status": lab.status,
                }
                for lab in p.related_labs
            ]
        return result

    def _dict_to_problem(self, d: dict) -> Problem:
        """Convert dictionary from JSONB to Problem."""
        related_visits = None
        if d.get("related_visits"):
            related_visits = [
                RelatedVisit(
                    visit_id=v["visit_id"],
                    date=date.fromisoformat(v["date"]) if v.get("date") else None,
                    visit_type=v["visit_type"],
                    provider_name=v.get("provider_name"),
                )
                for v in d["related_visits"]
            ]

        related_medications = None
        if d.get("related_medications"):
            related_medications = [
                RelatedMedication(
                    medication_id=m["medication_id"],
                    name=m["name"],
                    dosage=m.get("dosage"),
                )
                for m in d["related_medications"]
            ]

        related_labs = None
        if d.get("related_labs"):
            related_labs = [
                RelatedLabResult(
                    lab_name=lab["lab_name"],
                    most_recent_value=lab.get("most_recent_value"),
                    most_recent_date=date.fromisoformat(lab["most_recent_date"])
                    if lab.get("most_recent_date")
                    else None,
                    status=lab.get("status"),
                )
                for lab in d["related_labs"]
            ]

        return Problem(
            name=d["name"],
            icd10_code=d["icd10_code"],
            onset_date=date.fromisoformat(d["onset_date"]) if d.get("onset_date") else date.today(),
            status=ProblemStatus(d.get("status", "active")),
            priority=ProblemPriority(d.get("priority", "chronic")),
            severity=ProblemSeverity(d["severity"]) if d.get("severity") else None,
            documenting_provider=d.get("documenting_provider"),
            documented_date=date.fromisoformat(d["documented_date"])
            if d.get("documented_date")
            else None,
            is_critical=d.get("is_critical", False),
            resolved_date=date.fromisoformat(d["resolved_date"])
            if d.get("resolved_date")
            else None,
            resolved_by_provider=d.get("resolved_by_provider"),
            clinical_category=ClinicalCategory(d["clinical_category"])
            if d.get("clinical_category")
            else None,
            complexity=ProblemComplexity(d["complexity"])
            if d.get("complexity")
            else None,
            parent_problem_code=d.get("parent_problem_code"),
            related_visits=related_visits,
            related_medications=related_medications,
            related_labs=related_labs,
        )

    def _vitals_to_dict(self, v: RecentVitals) -> dict:
        """Convert RecentVitals to dictionary."""
        return {
            "date": v.date,
            "blood_pressure": v.blood_pressure,
            "weight": v.weight,
            "temperature": v.temperature,
        }

    def _dict_to_vitals(self, d: dict) -> RecentVitals:
        """Convert dictionary to RecentVitals."""
        return RecentVitals(
            date=d["date"],
            blood_pressure=d["blood_pressure"],
            weight=d["weight"],
            temperature=d["temperature"],
        )

    def _insurance_to_dict(self, i: Insurance) -> dict:
        """Convert Insurance to dictionary."""
        return {
            "provider": i.provider,
            "member_id": i.member_id,
        }

    def _dict_to_insurance(self, d: dict) -> Insurance:
        """Convert dictionary to Insurance."""
        return Insurance(
            provider=d["provider"],
            member_id=d["member_id"],
        )

    def _allergy_review_to_dict(self, ar: AllergyReviewStatus) -> dict:
        """Convert AllergyReviewStatus to dictionary."""
        result = {"reviewed_at": ar.reviewed_at.isoformat()}
        if ar.reviewed_by:
            result["reviewed_by"] = {
                "reference": ar.reviewed_by.reference,
                "display": ar.reviewed_by.display,
            }
        return result

    def _dict_to_allergy_review(self, d: dict) -> AllergyReviewStatus:
        """Convert dictionary to AllergyReviewStatus."""
        reviewed_by = None
        if d.get("reviewed_by"):
            reviewed_by = Reference(
                reference=d["reviewed_by"]["reference"],
                display=d["reviewed_by"].get("display"),
            )
        return AllergyReviewStatus(
            reviewed_at=datetime.fromisoformat(d["reviewed_at"]),
            reviewed_by=reviewed_by,
        )
