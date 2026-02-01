"""
Encounter Prompt repository - in-memory data access layer.

Stores and retrieves encounter prompts that guide physicians through encounters.
"""

from __future__ import annotations

from typing import Any

from resources.core import InMemoryRepository
from .model import EncounterPrompt, PromptStatus


class EncounterPromptRepository(InMemoryRepository[EncounterPrompt]):
    """
    Repository for EncounterPrompt resources.

    Provides storage and retrieval of prompts generated for encounters.
    """

    def __init__(self):
        super().__init__()

    async def list(self, **filters: Any) -> list[EncounterPrompt]:
        """
        List encounter prompts with optional filters.

        Supported filters:
        - encounter_id: str - Filter by encounter ID
        - status: str | list[str] - Filter by status(es)
        - prompt_type: str | list[str] - Filter by prompt type(s)
        - viewer_section: str - Filter by viewer section
        """
        results = list(self._store.values())

        if "encounter_id" in filters:
            encounter_id = filters["encounter_id"]
            results = [r for r in results if r.encounter_id == encounter_id]

        if "status" in filters:
            status_filter = filters["status"]
            if isinstance(status_filter, str):
                status_filter = [status_filter]
            results = [r for r in results if r.status in status_filter]

        if "prompt_type" in filters:
            type_filter = filters["prompt_type"]
            if isinstance(type_filter, str):
                type_filter = [type_filter]
            results = [r for r in results if r.prompt_type in type_filter]

        if "viewer_section" in filters:
            section_filter = filters["viewer_section"]
            results = [r for r in results if r.viewer_section == section_filter]

        return results

    async def get_by_encounter(
        self,
        encounter_id: str,
        status: PromptStatus | list[PromptStatus] | None = None,
    ) -> list[EncounterPrompt]:
        """
        Get prompts for a specific encounter.

        Args:
            encounter_id: The encounter ID
            status: Optional status filter (single status or list of statuses)

        Returns:
            List of EncounterPrompt objects sorted by prompt_order
        """
        filters: dict[str, Any] = {"encounter_id": encounter_id}
        if status is not None:
            filters["status"] = status

        results = await self.list(**filters)

        # Sort by prompt_order
        results.sort(key=lambda p: p.prompt_order)

        return results

    async def clear_encounter_prompts(self, encounter_id: str) -> int:
        """
        Remove all prompts for an encounter.

        Used when regenerating prompts from scratch.

        Args:
            encounter_id: The encounter ID

        Returns:
            Number of prompts removed
        """
        prompts = await self.get_by_encounter(encounter_id)
        count = 0
        for prompt in prompts:
            await self.delete(prompt.id)
            count += 1
        return count

    async def bulk_create(self, prompts: list[EncounterPrompt]) -> list[EncounterPrompt]:
        """
        Create multiple prompts at once.

        Args:
            prompts: List of prompts to create

        Returns:
            List of created prompts
        """
        created = []
        for prompt in prompts:
            await self.create(prompt)
            created.append(prompt)
        return created

    async def update_prompt_orders(
        self,
        encounter_id: str,
        prompt_ids: list[str],
    ) -> list[EncounterPrompt]:
        """
        Reorder prompts within an encounter.

        Args:
            encounter_id: The encounter ID
            prompt_ids: List of prompt IDs in desired order

        Returns:
            List of updated prompts
        """
        updated = []
        for order, prompt_id in enumerate(prompt_ids):
            prompt = await self.get(prompt_id)
            if prompt and prompt.encounter_id == encounter_id:
                prompt.prompt_order = order
                await self.update(prompt_id, prompt)
                updated.append(prompt)

        updated.sort(key=lambda p: p.prompt_order)
        return updated
