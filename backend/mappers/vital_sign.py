"""
VitalSign mapper for domain <-> ORM conversion.
"""

from mappers.base import Mapper
from db.models.vital_sign import VitalSignORM
from resources.vitals import VitalSign, VITAL_REFERENCE_RANGES
from resources.core import Reference


class VitalSignMapper(Mapper[VitalSign, VitalSignORM]):
    """Mapper for VitalSign <-> VitalSignORM conversion."""

    def to_orm(self, domain: VitalSign) -> VitalSignORM:
        """Convert VitalSign domain model to ORM."""
        return VitalSignORM(
            id=domain.id,
            vital_type=domain.vital_type,
            value=domain.value,
            unit=domain.unit,
            status=domain.status,
            subject_id=domain.subject.id,
            recorded_at=domain.recorded_at,
            recorded_by=domain.recorded_by,
            location=domain.location,
            meta_version_id=domain.meta_version_id,
            meta_last_updated=domain.meta_last_updated,
        )

    def to_domain(self, orm: VitalSignORM) -> VitalSign:
        """Convert VitalSignORM to VitalSign domain model."""
        return VitalSign(
            id=orm.id,
            vital_type=orm.vital_type,
            value=orm.value,
            unit=orm.unit,
            status=orm.status,
            subject=Reference(reference=f"Patient/{orm.subject_id}"),
            recorded_at=orm.recorded_at,
            recorded_by=orm.recorded_by,
            location=orm.location,
            meta_version_id=orm.meta_version_id,
            meta_last_updated=orm.meta_last_updated,
        )
