"""
Encounter Note Version mapper for domain <-> ORM conversion.
"""

from mappers.base import Mapper
from db.models.encounter_note_version import EncounterNoteVersionORM
from resources.encounter_note_version import EncounterNoteVersion, SaveType
from resources.core import Reference


class EncounterNoteVersionMapper(Mapper[EncounterNoteVersion, EncounterNoteVersionORM]):
    """Mapper for EncounterNoteVersion <-> EncounterNoteVersionORM conversion."""

    def to_orm(self, domain: EncounterNoteVersion) -> EncounterNoteVersionORM:
        """Convert EncounterNoteVersion domain model to ORM."""
        return EncounterNoteVersionORM(
            id=domain.id,
            encounter_id=domain.encounter.id,
            version=domain.version,
            content=domain.content,
            word_count=domain.word_count,
            save_type=domain.save_type.value,
            created_at=domain.created_at,
            meta_version_id=domain.meta_version_id,
            meta_last_updated=domain.meta_last_updated,
        )

    def to_domain(self, orm: EncounterNoteVersionORM) -> EncounterNoteVersion:
        """Convert EncounterNoteVersionORM to EncounterNoteVersion domain model."""
        # Parse save type
        try:
            save_type = SaveType(orm.save_type)
        except ValueError:
            save_type = SaveType.AUTO

        return EncounterNoteVersion(
            id=orm.id,
            encounter=Reference(reference=f"Encounter/{orm.encounter_id}"),
            version=orm.version,
            content=orm.content,
            word_count=orm.word_count,
            save_type=save_type,
            created_at=orm.created_at,
            meta_version_id=orm.meta_version_id,
            meta_last_updated=orm.meta_last_updated,
        )
