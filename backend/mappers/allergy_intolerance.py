"""
AllergyIntolerance mapper for domain <-> ORM conversion.
"""

from datetime import datetime

from mappers.base import Mapper
from db.models.allergy_intolerance import AllergyIntoleranceORM
from resources.allergy_intolerance import (
    AllergyIntolerance,
    AllergyCategory,
    AllergyCriticality,
    AllergyVerificationStatus,
    AllergyReaction,
)
from resources.core import CodeableConcept, Reference


class AllergyIntoleranceMapper(Mapper[AllergyIntolerance, AllergyIntoleranceORM]):
    """Mapper for AllergyIntolerance <-> AllergyIntoleranceORM conversion."""

    def to_orm(self, domain: AllergyIntolerance) -> AllergyIntoleranceORM:
        """Convert AllergyIntolerance domain model to ORM."""
        return AllergyIntoleranceORM(
            id=domain.id,
            patient_id=domain.patient.id,
            code={
                "code": domain.code.code,
                "display": domain.code.display,
                "system": domain.code.system,
            },
            category=domain.category.value,
            criticality=domain.criticality.value,
            clinical_status=domain.clinical_status,
            verification_status=domain.verification_status.value,
            reactions=[
                {
                    "manifestation": r.manifestation,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in domain.reactions
            ],
            recorded_date=domain.recorded_date,
            recorder={
                "reference": domain.recorder.reference,
                "display": domain.recorder.display,
            }
            if domain.recorder
            else None,
            last_updated=domain.last_updated,
            notes=domain.notes,
            meta_version_id=domain.meta_version_id,
            meta_last_updated=domain.meta_last_updated,
        )

    def to_domain(self, orm: AllergyIntoleranceORM) -> AllergyIntolerance:
        """Convert AllergyIntoleranceORM to AllergyIntolerance domain model."""
        code_data = orm.code or {}

        # Parse category
        try:
            category = AllergyCategory(orm.category)
        except ValueError:
            category = AllergyCategory.MEDICATION

        # Parse criticality
        try:
            criticality = AllergyCriticality(orm.criticality)
        except ValueError:
            criticality = AllergyCriticality.HIGH

        # Parse verification status
        try:
            verification_status = AllergyVerificationStatus(orm.verification_status)
        except ValueError:
            verification_status = AllergyVerificationStatus.CONFIRMED

        # Parse reactions
        reactions = []
        for r in orm.reactions or []:
            reactions.append(
                AllergyReaction(
                    manifestation=r["manifestation"],
                    severity=r.get("severity", "moderate"),
                    description=r.get("description"),
                )
            )

        # Parse recorder
        recorder = None
        if orm.recorder:
            recorder = Reference(
                reference=orm.recorder["reference"],
                display=orm.recorder.get("display"),
            )

        return AllergyIntolerance(
            id=orm.id,
            patient=Reference(reference=f"Patient/{orm.patient_id}"),
            code=CodeableConcept(
                code=code_data.get("code", "unknown"),
                display=code_data.get("display", "Unknown"),
                system=code_data.get("system"),
            ),
            category=category,
            criticality=criticality,
            clinical_status=orm.clinical_status,
            verification_status=verification_status,
            reactions=reactions,
            recorded_date=orm.recorded_date,
            recorder=recorder,
            last_updated=orm.last_updated,
            notes=orm.notes,
            meta_version_id=orm.meta_version_id,
            meta_last_updated=orm.meta_last_updated,
        )
