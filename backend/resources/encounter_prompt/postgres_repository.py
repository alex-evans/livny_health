"""
PostgreSQL repository for EncounterPrompt resources.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from resources.core.postgres_repository import PostgresRepository
from resources.encounter_prompt.model import EncounterPrompt, PromptStatus
from db.models.encounter_prompt import EncounterPromptORM
from mappers.encounter_prompt import EncounterPromptMapper


class PostgresEncounterPromptRepository(
    PostgresRepository[EncounterPrompt, EncounterPromptORM]
):
    """PostgreSQL repository for EncounterPrompt resources."""

    orm_class = EncounterPromptORM
    mapper = EncounterPromptMapper()

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)

    def _apply_filters(self, stmt, **filters: Any):
        """Apply EncounterPrompt-specific filters."""
        if filters.get("encounter_id"):
            stmt = stmt.where(EncounterPromptORM.encounter_id == filters["encounter_id"])
        if filters.get("status"):
            status_filter = filters["status"]
            if isinstance(status_filter, list):
                stmt = stmt.where(EncounterPromptORM.status.in_(status_filter))
            else:
                stmt = stmt.where(EncounterPromptORM.status == status_filter)
        if filters.get("prompt_type"):
            type_filter = filters["prompt_type"]
            if isinstance(type_filter, list):
                stmt = stmt.where(EncounterPromptORM.prompt_type.in_(type_filter))
            else:
                stmt = stmt.where(EncounterPromptORM.prompt_type == type_filter)
        if filters.get("viewer_section"):
            stmt = stmt.where(EncounterPromptORM.viewer_section == filters["viewer_section"])
        return stmt.order_by(EncounterPromptORM.prompt_order)

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
