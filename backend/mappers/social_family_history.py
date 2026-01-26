"""
SocialFamilyHistory mapper for domain <-> ORM conversion.
"""

from datetime import datetime, date

from mappers.base import Mapper
from db.models.social_family_history import SocialFamilyHistoryORM
from resources.social_family_history import (
    SocialFamilyHistory,
    SocialHistory,
    FamilyHistory,
    SmokingHistory,
    AlcoholHistory,
    SubstanceUseHistory,
    FamilyMember,
    FamilyMemberCondition,
    SignificantCondition,
    RiskAssessment,
)
from resources.core import Reference


class SocialFamilyHistoryMapper(Mapper[SocialFamilyHistory, SocialFamilyHistoryORM]):
    """Mapper for SocialFamilyHistory <-> SocialFamilyHistoryORM conversion."""

    def to_orm(self, domain: SocialFamilyHistory) -> SocialFamilyHistoryORM:
        """Convert SocialFamilyHistory domain model to ORM."""
        return SocialFamilyHistoryORM(
            id=domain.id,
            subject_id=domain.subject.id,
            social_history=self._social_history_to_dict(domain.social_history),
            family_history=self._family_history_to_dict(domain.family_history),
            risk_assessments=[
                self._risk_assessment_to_dict(ra) for ra in domain.risk_assessments
            ],
            meta_version_id=domain.meta_version_id,
            meta_last_updated=domain.meta_last_updated,
        )

    def to_domain(self, orm: SocialFamilyHistoryORM) -> SocialFamilyHistory:
        """Convert SocialFamilyHistoryORM to SocialFamilyHistory domain model."""
        return SocialFamilyHistory(
            id=orm.id,
            subject=Reference(reference=f"Patient/{orm.subject_id}"),
            social_history=self._dict_to_social_history(orm.social_history or {}),
            family_history=self._dict_to_family_history(orm.family_history or {}),
            risk_assessments=[
                self._dict_to_risk_assessment(ra) for ra in (orm.risk_assessments or [])
            ],
            meta_version_id=orm.meta_version_id,
            meta_last_updated=orm.meta_last_updated,
        )

    def _social_history_to_dict(self, sh: SocialHistory) -> dict:
        return {
            "smoking": {
                "status": sh.smoking.status,
                "pack_years": sh.smoking.pack_years,
                "quit_date": sh.smoking.quit_date.isoformat()
                if sh.smoking.quit_date
                else None,
                "notes": sh.smoking.notes,
            },
            "alcohol": {
                "use_level": sh.alcohol.use_level,
                "drinks_per_week": sh.alcohol.drinks_per_week,
                "history_of_abuse": sh.alcohol.history_of_abuse,
                "notes": sh.alcohol.notes,
            },
            "substance_use": {
                "level": sh.substance_use.level,
                "substances": sh.substance_use.substances,
                "iv_drug_use": sh.substance_use.iv_drug_use,
                "notes": sh.substance_use.notes,
            },
            "occupation": sh.occupation,
            "occupation_hazards": sh.occupation_hazards,
            "living_situation": sh.living_situation,
            "marital_status": sh.marital_status,
            "exercise": sh.exercise,
            "diet": sh.diet,
            "diet_notes": sh.diet_notes,
            "last_reviewed": sh.last_reviewed.isoformat()
            if sh.last_reviewed
            else None,
            "reviewed_by": sh.reviewed_by,
        }

    def _dict_to_social_history(self, d: dict) -> SocialHistory:
        smoking_data = d.get("smoking", {})
        alcohol_data = d.get("alcohol", {})
        substance_data = d.get("substance_use", {})

        return SocialHistory(
            smoking=SmokingHistory(
                status=smoking_data.get("status", "unknown"),
                pack_years=smoking_data.get("pack_years"),
                quit_date=date.fromisoformat(smoking_data["quit_date"])
                if smoking_data.get("quit_date")
                else None,
                notes=smoking_data.get("notes"),
            ),
            alcohol=AlcoholHistory(
                use_level=alcohol_data.get("use_level", "unknown"),
                drinks_per_week=alcohol_data.get("drinks_per_week"),
                history_of_abuse=alcohol_data.get("history_of_abuse", False),
                notes=alcohol_data.get("notes"),
            ),
            substance_use=SubstanceUseHistory(
                level=substance_data.get("level", "unknown"),
                substances=substance_data.get("substances", []),
                iv_drug_use=substance_data.get("iv_drug_use", False),
                notes=substance_data.get("notes"),
            ),
            occupation=d.get("occupation"),
            occupation_hazards=d.get("occupation_hazards", []),
            living_situation=d.get("living_situation"),
            marital_status=d.get("marital_status", "unknown"),
            exercise=d.get("exercise", "unknown"),
            diet=d.get("diet", "unknown"),
            diet_notes=d.get("diet_notes"),
            last_reviewed=datetime.fromisoformat(d["last_reviewed"])
            if d.get("last_reviewed")
            else None,
            reviewed_by=d.get("reviewed_by"),
        )

    def _family_history_to_dict(self, fh: FamilyHistory) -> dict:
        return {
            "family_members": [
                {
                    "id": fm.id,
                    "relative_type": fm.relative_type,
                    "is_living": fm.is_living,
                    "age_at_death": fm.age_at_death,
                    "cause_of_death": fm.cause_of_death,
                    "conditions": [
                        {
                            "condition_name": c.condition_name,
                            "icd10_code": c.icd10_code,
                            "age_at_onset": c.age_at_onset,
                            "notes": c.notes,
                        }
                        for c in fm.conditions
                    ],
                }
                for fm in fh.family_members
            ],
            "significant_conditions": [
                {
                    "condition_name": sc.condition_name,
                    "icd10_code": sc.icd10_code,
                    "affected_relatives": sc.affected_relatives,
                    "notes": sc.notes,
                }
                for sc in fh.significant_conditions
            ],
            "hereditary_syndromes": fh.hereditary_syndromes,
            "adoption_status": fh.adoption_status,
            "last_reviewed": fh.last_reviewed.isoformat()
            if fh.last_reviewed
            else None,
            "reviewed_by": fh.reviewed_by,
        }

    def _dict_to_family_history(self, d: dict) -> FamilyHistory:
        family_members = []
        for fm in d.get("family_members", []):
            conditions = []
            for c in fm.get("conditions", []):
                conditions.append(
                    FamilyMemberCondition(
                        condition_name=c["condition_name"],
                        icd10_code=c.get("icd10_code"),
                        age_at_onset=c.get("age_at_onset"),
                        notes=c.get("notes"),
                    )
                )
            family_members.append(
                FamilyMember(
                    id=fm["id"],
                    relative_type=fm["relative_type"],
                    is_living=fm.get("is_living", True),
                    age_at_death=fm.get("age_at_death"),
                    cause_of_death=fm.get("cause_of_death"),
                    conditions=conditions,
                )
            )

        significant_conditions = []
        for sc in d.get("significant_conditions", []):
            significant_conditions.append(
                SignificantCondition(
                    condition_name=sc["condition_name"],
                    icd10_code=sc.get("icd10_code"),
                    affected_relatives=sc.get("affected_relatives", []),
                    notes=sc.get("notes"),
                )
            )

        return FamilyHistory(
            family_members=family_members,
            significant_conditions=significant_conditions,
            hereditary_syndromes=d.get("hereditary_syndromes", []),
            adoption_status=d.get("adoption_status", "not_adopted"),
            last_reviewed=datetime.fromisoformat(d["last_reviewed"])
            if d.get("last_reviewed")
            else None,
            reviewed_by=d.get("reviewed_by"),
        )

    def _risk_assessment_to_dict(self, ra: RiskAssessment) -> dict:
        return {
            "risk_type": ra.risk_type,
            "risk_level": ra.risk_level,
            "contributing_factors": ra.contributing_factors,
            "recommendations": ra.recommendations,
            "screening_due": ra.screening_due.isoformat()
            if ra.screening_due
            else None,
            "calculated_at": ra.calculated_at.isoformat(),
            "notes": ra.notes,
        }

    def _dict_to_risk_assessment(self, d: dict) -> RiskAssessment:
        return RiskAssessment(
            risk_type=d["risk_type"],
            risk_level=d["risk_level"],
            contributing_factors=d.get("contributing_factors", []),
            recommendations=d.get("recommendations", []),
            screening_due=date.fromisoformat(d["screening_due"])
            if d.get("screening_due")
            else None,
            calculated_at=datetime.fromisoformat(d["calculated_at"])
            if d.get("calculated_at")
            else datetime.utcnow(),
            notes=d.get("notes"),
        )
