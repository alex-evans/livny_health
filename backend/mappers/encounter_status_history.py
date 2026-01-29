"""
Encounter Status History mapper for domain <-> ORM conversion.
"""

from mappers.base import Mapper
from db.models.encounter_status_history import EncounterStatusHistoryORM
from resources.encounter_status_history import EncounterStatusHistory


class EncounterStatusHistoryMapper(Mapper[EncounterStatusHistory, EncounterStatusHistoryORM]):
    """Mapper for EncounterStatusHistory <-> EncounterStatusHistoryORM conversion."""

    def to_orm(self, domain: EncounterStatusHistory) -> EncounterStatusHistoryORM:
        """Convert EncounterStatusHistory domain model to ORM."""
        return EncounterStatusHistoryORM(
            id=domain.id,
            encounter_id=domain.encounter_id,
            from_status=domain.from_status,
            to_status=domain.to_status,
            changed_by_id=domain.changed_by_id,
            changed_by_name=domain.changed_by_name,
            changed_at=domain.changed_at,
            reason=domain.reason,
            ip_address=domain.ip_address,
            user_agent=domain.user_agent,
            meta_version_id=domain.meta_version_id,
            meta_last_updated=domain.meta_last_updated,
        )

    def to_domain(self, orm: EncounterStatusHistoryORM) -> EncounterStatusHistory:
        """Convert EncounterStatusHistoryORM to EncounterStatusHistory domain model."""
        return EncounterStatusHistory(
            id=orm.id,
            encounter_id=orm.encounter_id,
            from_status=orm.from_status,
            to_status=orm.to_status,
            changed_by_id=orm.changed_by_id,
            changed_by_name=orm.changed_by_name,
            changed_at=orm.changed_at,
            reason=orm.reason,
            ip_address=orm.ip_address,
            user_agent=orm.user_agent,
            meta_version_id=orm.meta_version_id,
            meta_last_updated=orm.meta_last_updated,
        )
