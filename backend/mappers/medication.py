"""
Medication mapper for domain <-> ORM conversion.
"""

from mappers.base import Mapper
from db.models.medication import MedicationORM
from resources.medication import Medication
from resources.core import CodeableConcept


class MedicationMapper(Mapper[Medication, MedicationORM]):
    """Mapper for Medication <-> MedicationORM conversion."""

    def to_orm(self, domain: Medication) -> MedicationORM:
        """Convert Medication domain model to ORM."""
        return MedicationORM(
            id=domain.id,
            code={
                "code": domain.code.code,
                "display": domain.code.display,
                "system": domain.code.system,
            },
            form=domain.form,
            strength=domain.strength,
            is_controlled=domain.is_controlled,
            common_dosing=domain.common_dosing,
            status=domain.status,
            meta_version_id=domain.meta_version_id,
            meta_last_updated=domain.meta_last_updated,
        )

    def to_domain(self, orm: MedicationORM) -> Medication:
        """Convert MedicationORM to Medication domain model."""
        code_data = orm.code or {}
        return Medication(
            id=orm.id,
            code=CodeableConcept(
                code=code_data.get("code", "unknown"),
                display=code_data.get("display", "Unknown"),
                system=code_data.get("system"),
            ),
            form=orm.form,
            strength=orm.strength,
            is_controlled=orm.is_controlled,
            common_dosing=orm.common_dosing or [],
            status=orm.status,
            meta_version_id=orm.meta_version_id,
            meta_last_updated=orm.meta_last_updated,
        )
