"""
ClinicalAlert mapper for domain <-> ORM conversion.
"""

from datetime import datetime

from mappers.base import Mapper
from db.models.clinical_alert import ClinicalAlertORM
from resources.clinical_alert import ClinicalAlert, AlertAcknowledgment


class ClinicalAlertMapper(Mapper[ClinicalAlert, ClinicalAlertORM]):
    """Mapper for ClinicalAlert <-> ClinicalAlertORM conversion."""

    def to_orm(self, domain: ClinicalAlert) -> ClinicalAlertORM:
        """Convert ClinicalAlert domain model to ORM."""
        return ClinicalAlertORM(
            id=domain.id,
            patient_id=domain.patient_id,
            alert_type=domain.alert_type,
            severity=domain.severity,
            status=domain.status,
            title=domain.title,
            description=domain.description,
            generated_at=domain.generated_at,
            source=domain.source,
            source_id=domain.source_id,
            source_link=domain.source_link,
            context=domain.context,
            recommended_actions=domain.recommended_actions,
            acknowledgment={
                "acknowledged_by": domain.acknowledgment.acknowledged_by,
                "acknowledged_at": domain.acknowledgment.acknowledged_at.isoformat(),
                "note": domain.acknowledgment.note,
            }
            if domain.acknowledgment
            else None,
            dismissed_at=domain.dismissed_at,
            dismissed_by=domain.dismissed_by,
            dismissed_reason=domain.dismissed_reason,
            meta_version_id=domain.meta_version_id,
            meta_last_updated=domain.meta_last_updated,
        )

    def to_domain(self, orm: ClinicalAlertORM) -> ClinicalAlert:
        """Convert ClinicalAlertORM to ClinicalAlert domain model."""
        acknowledgment = None
        if orm.acknowledgment:
            acknowledgment = AlertAcknowledgment(
                acknowledged_by=orm.acknowledgment["acknowledged_by"],
                acknowledged_at=datetime.fromisoformat(
                    orm.acknowledgment["acknowledged_at"]
                ),
                note=orm.acknowledgment.get("note"),
            )

        return ClinicalAlert(
            id=orm.id,
            patient_id=orm.patient_id,
            alert_type=orm.alert_type,
            severity=orm.severity,
            status=orm.status,
            title=orm.title,
            description=orm.description,
            generated_at=orm.generated_at,
            source=orm.source,
            source_id=orm.source_id,
            source_link=orm.source_link,
            context=orm.context or {},
            recommended_actions=orm.recommended_actions or [],
            acknowledgment=acknowledgment,
            dismissed_at=orm.dismissed_at,
            dismissed_by=orm.dismissed_by,
            dismissed_reason=orm.dismissed_reason,
            meta_version_id=orm.meta_version_id,
            meta_last_updated=orm.meta_last_updated,
        )
