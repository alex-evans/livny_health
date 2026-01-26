"""
LabResult mapper for domain <-> ORM conversion.
"""

from mappers.base import Mapper
from db.models.lab_result import LabResultORM
from resources.lab_result import LabResult
from resources.core import Reference


class LabResultMapper(Mapper[LabResult, LabResultORM]):
    """Mapper for LabResult <-> LabResultORM conversion."""

    def to_orm(self, domain: LabResult) -> LabResultORM:
        """Convert LabResult domain model to ORM."""
        return LabResultORM(
            id=domain.id,
            test_name=domain.test_name,
            test_code=domain.test_code,
            value=domain.value,
            unit=domain.unit,
            reference_range=domain.reference_range,
            status=domain.status,
            subject_id=domain.subject.id,
            collection_date=domain.collection_date,
            performing_lab=domain.performing_lab,
            panel_id=domain.panel_id,
            last_updated=domain.last_updated,
            acknowledged=domain.acknowledged,
            acknowledged_by=domain.acknowledged_by,
            acknowledged_at=domain.acknowledged_at,
            meta_version_id=domain.meta_version_id,
            meta_last_updated=domain.meta_last_updated,
        )

    def to_domain(self, orm: LabResultORM) -> LabResult:
        """Convert LabResultORM to LabResult domain model."""
        return LabResult(
            id=orm.id,
            test_name=orm.test_name,
            test_code=orm.test_code,
            value=orm.value,
            unit=orm.unit,
            reference_range=orm.reference_range,
            status=orm.status,
            subject=Reference(reference=f"Patient/{orm.subject_id}"),
            collection_date=orm.collection_date,
            performing_lab=orm.performing_lab,
            panel_id=orm.panel_id,
            last_updated=orm.last_updated,
            acknowledged=orm.acknowledged,
            acknowledged_by=orm.acknowledged_by,
            acknowledged_at=orm.acknowledged_at,
            meta_version_id=orm.meta_version_id,
            meta_last_updated=orm.meta_last_updated,
        )
