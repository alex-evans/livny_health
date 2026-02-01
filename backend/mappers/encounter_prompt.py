"""
EncounterPrompt mapper for domain <-> ORM conversion.
"""

from mappers.base import Mapper
from db.models.encounter_prompt import EncounterPromptORM
from resources.encounter_prompt import EncounterPrompt


class EncounterPromptMapper(Mapper[EncounterPrompt, EncounterPromptORM]):
    """Mapper for EncounterPrompt <-> EncounterPromptORM conversion."""

    def to_orm(self, domain: EncounterPrompt) -> EncounterPromptORM:
        """Convert EncounterPrompt domain model to ORM."""
        return EncounterPromptORM(
            id=domain.id,
            encounter_id=domain.encounter_id,
            prompt_type=domain.prompt_type,
            prompt_subtype=domain.prompt_subtype,
            prompt_text=domain.prompt_text,
            prompt_order=domain.prompt_order,
            status=domain.status,
            response_data=domain.response_data if domain.response_data else None,
            viewer_section=domain.viewer_section,
            alert_level=domain.alert_level,
            is_skippable=domain.is_skippable,
            source_reference=domain.source_reference,
            source_context=domain.source_context if domain.source_context else None,
            addressed_at=domain.addressed_at,
            addressed_by_id=domain.addressed_by_id,
            meta_version_id=domain.meta_version_id,
            meta_last_updated=domain.meta_last_updated,
        )

    def to_domain(self, orm: EncounterPromptORM) -> EncounterPrompt:
        """Convert EncounterPromptORM to EncounterPrompt domain model."""
        return EncounterPrompt(
            id=orm.id,
            encounter_id=orm.encounter_id,
            prompt_type=orm.prompt_type,
            prompt_subtype=orm.prompt_subtype,
            prompt_text=orm.prompt_text,
            prompt_order=orm.prompt_order,
            status=orm.status,
            response_data=orm.response_data or {},
            viewer_section=orm.viewer_section,
            alert_level=orm.alert_level,
            is_skippable=orm.is_skippable,
            source_reference=orm.source_reference,
            source_context=orm.source_context or {},
            addressed_at=orm.addressed_at,
            addressed_by_id=orm.addressed_by_id,
            meta_version_id=orm.meta_version_id,
            meta_last_updated=orm.meta_last_updated,
        )
