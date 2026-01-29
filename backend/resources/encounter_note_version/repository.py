"""
Encounter Note Version repository - data access layer.
"""

from __future__ import annotations

from typing import Any
from resources.core import InMemoryRepository
from .model import EncounterNoteVersion


class EncounterNoteVersionRepository(InMemoryRepository[EncounterNoteVersion]):
    """
    Repository for EncounterNoteVersion resources.
    Currently uses in-memory storage, can be swapped for database later.
    """

    async def list(self, **filters: Any) -> list[EncounterNoteVersion]:
        """
        List encounter note versions with optional filters.

        Supported filters:
        - encounter_id: str - Filter by encounter ID
        """
        results = list(self._store.values())

        if "encounter_id" in filters:
            encounter_ref = f"Encounter/{filters['encounter_id']}"
            results = [v for v in results if v.encounter.reference == encounter_ref]

        # Sort by version descending (newest first)
        results.sort(key=lambda v: v.version, reverse=True)
        return results

    async def get_by_encounter(self, encounter_id: str) -> list[EncounterNoteVersion]:
        """Get all versions for an encounter, sorted by version descending."""
        return await self.list(encounter_id=encounter_id)

    async def get_latest_version(self, encounter_id: str) -> EncounterNoteVersion | None:
        """Get the latest version for an encounter."""
        versions = await self.get_by_encounter(encounter_id)
        return versions[0] if versions else None

    async def get_version(
        self, encounter_id: str, version: int
    ) -> EncounterNoteVersion | None:
        """Get a specific version for an encounter."""
        versions = await self.list(encounter_id=encounter_id)
        for v in versions:
            if v.version == version:
                return v
        return None
