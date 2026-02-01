"""
Encounter Prompt Service.

Orchestrates prompt generation, retrieval, and lifecycle management.
Prompts are generated when an encounter is opened and guide physicians
through the visit documentation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from resources import (
    Patient,
    PatientRepository,
    Encounter,
    EncounterRepository,
    ClinicalAlertRepository,
)
from resources.encounter_prompt import (
    EncounterPrompt,
    EncounterPromptRepository,
    PromptGenerationResult,
    PromptStatus,
)
from services.prompt_generators import PromptGenerator
from services.encounter_note_service import EncounterNoteService


PromptAction = Literal["address", "skip", "defer"]


class EncounterNotFoundError(Exception):
    """Raised when encounter is not found."""
    pass


class PromptNotFoundError(Exception):
    """Raised when prompt is not found."""
    pass


class PromptNotSkippableError(Exception):
    """Raised when trying to skip a non-skippable prompt."""
    pass


@dataclass
class PromptsResponse:
    """Response containing prompts for an encounter."""
    prompts: list[EncounterPrompt]
    total_count: int
    pending_count: int
    addressed_count: int
    critical_count: int

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "prompts": [p.to_dict() for p in self.prompts],
            "totalCount": self.total_count,
            "pendingCount": self.pending_count,
            "addressedCount": self.addressed_count,
            "criticalCount": self.critical_count,
        }


class EncounterPromptService:
    """
    Service for managing encounter prompts.

    Coordinates prompt generation from multiple sources and manages
    prompt lifecycle (pending -> addressed/skipped/deferred).
    """

    def __init__(
        self,
        prompt_repo: EncounterPromptRepository,
        encounter_repo: EncounterRepository,
        encounter_note_service: EncounterNoteService,
        generators: list[PromptGenerator],
    ):
        """
        Initialize the encounter prompt service.

        Args:
            prompt_repo: Repository for storing prompts
            encounter_repo: Repository for encounters
            encounter_note_service: Service for getting encounter context
            generators: List of prompt generators
        """
        self.prompt_repo = prompt_repo
        self.encounter_repo = encounter_repo
        self.encounter_note_service = encounter_note_service
        self.generators = generators

    async def generate_prompts(
        self,
        encounter_id: str,
        visit_type: str = "follow_up",
    ) -> PromptGenerationResult:
        """
        Generate prompts for an encounter.

        This runs all generators, collects prompts, sorts by priority,
        and stores them for the encounter.

        Args:
            encounter_id: The encounter ID
            visit_type: Type of visit (follow_up, annual_physical, urgent)

        Returns:
            PromptGenerationResult with generated prompts

        Raises:
            EncounterNotFoundError: If encounter not found
        """
        # Get encounter with context
        try:
            encounter_with_context = await self.encounter_note_service.get_encounter_with_context(
                encounter_id
            )
        except Exception as e:
            raise EncounterNotFoundError(f"Encounter {encounter_id} not found: {e}")

        encounter = encounter_with_context.encounter
        context = encounter_with_context.context

        # Get patient
        patient_id = encounter.patient_id
        # We need the full patient object for condition checks
        # The context has problems but we need the Patient object
        # Get it from the patient repo via encounter note service
        patient = await self._get_patient(patient_id)
        if not patient:
            raise EncounterNotFoundError(f"Patient {patient_id} not found")

        # Clear existing prompts for this encounter
        await self.prompt_repo.clear_encounter_prompts(encounter_id)

        # Run all generators and collect prompts
        all_prompts: list[EncounterPrompt] = []
        for generator in self.generators:
            try:
                prompts = await generator.generate_prompts(
                    encounter_id=encounter_id,
                    patient=patient,
                    context=context,
                    visit_type=visit_type,
                )
                all_prompts.extend(prompts)
            except Exception as e:
                # Log error but don't fail - other generators can still run
                print(f"Error in prompt generator {generator.__class__.__name__}: {e}")

        # Sort prompts by order (alerts first due to negative order numbers)
        all_prompts.sort(key=lambda p: p.prompt_order)

        # Reassign sequential order numbers
        for i, prompt in enumerate(all_prompts):
            prompt.prompt_order = i

        # Save all prompts
        await self.prompt_repo.bulk_create(all_prompts)

        # Build result
        critical_count = sum(1 for p in all_prompts if p.alert_level == "critical")

        return PromptGenerationResult(
            prompts=all_prompts,
            total_count=len(all_prompts),
            pending_count=len(all_prompts),  # All new prompts are pending
            critical_count=critical_count,
        )

    async def _get_patient(self, patient_id: str) -> Patient | None:
        """Get patient from the encounter note service's patient repo."""
        return await self.encounter_note_service.patient_repo.get(patient_id)

    async def get_encounter_prompts(
        self,
        encounter_id: str,
        status: PromptStatus | list[PromptStatus] | None = None,
    ) -> PromptsResponse:
        """
        Get prompts for an encounter.

        Args:
            encounter_id: The encounter ID
            status: Optional status filter

        Returns:
            PromptsResponse with prompts and counts
        """
        # Verify encounter exists
        encounter = await self.encounter_repo.get(encounter_id)
        if not encounter:
            raise EncounterNotFoundError(f"Encounter {encounter_id} not found")

        prompts = await self.prompt_repo.get_by_encounter(encounter_id, status=status)

        # Calculate counts
        total_count = len(prompts)
        pending_count = sum(1 for p in prompts if p.status == "pending")
        addressed_count = sum(1 for p in prompts if p.status == "addressed")
        critical_count = sum(1 for p in prompts if p.alert_level == "critical")

        return PromptsResponse(
            prompts=prompts,
            total_count=total_count,
            pending_count=pending_count,
            addressed_count=addressed_count,
            critical_count=critical_count,
        )

    async def update_prompt(
        self,
        encounter_id: str,
        prompt_id: str,
        action: PromptAction,
        user_id: str,
        response_data: dict | None = None,
        skip_reason: str | None = None,
    ) -> EncounterPrompt:
        """
        Update a prompt's status.

        Args:
            encounter_id: The encounter ID
            prompt_id: The prompt ID
            action: The action to take (address, skip, defer)
            user_id: The user performing the action
            response_data: Optional response data (for address action)
            skip_reason: Optional reason for skipping

        Returns:
            Updated EncounterPrompt

        Raises:
            PromptNotFoundError: If prompt not found
            PromptNotSkippableError: If trying to skip a non-skippable prompt
        """
        prompt = await self.prompt_repo.get(prompt_id)
        if not prompt or prompt.encounter_id != encounter_id:
            raise PromptNotFoundError(f"Prompt {prompt_id} not found")

        if action == "address":
            prompt.address(by_id=user_id, response=response_data)
        elif action == "skip":
            if not prompt.is_skippable:
                raise PromptNotSkippableError(
                    f"Prompt {prompt_id} cannot be skipped"
                )
            prompt.skip(by_id=user_id, reason=skip_reason)
        elif action == "defer":
            prompt.defer(by_id=user_id)

        await self.prompt_repo.update(prompt_id, prompt)
        return prompt

    async def reorder_prompts(
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

        Raises:
            EncounterNotFoundError: If encounter not found
        """
        # Verify encounter exists
        encounter = await self.encounter_repo.get(encounter_id)
        if not encounter:
            raise EncounterNotFoundError(f"Encounter {encounter_id} not found")

        return await self.prompt_repo.update_prompt_orders(encounter_id, prompt_ids)


class EncounterPromptServiceBuilder:
    """Builder for creating EncounterPromptService with all generators wired."""

    @staticmethod
    def build(
        prompt_repo: EncounterPromptRepository,
        encounter_repo: EncounterRepository,
        encounter_note_service: EncounterNoteService,
        patient_repo: PatientRepository | None = None,
        alert_repo: ClinicalAlertRepository | None = None,
    ) -> EncounterPromptService:
        """
        Build an EncounterPromptService with appropriate generators.

        Args:
            prompt_repo: Repository for prompts
            encounter_repo: Repository for encounters
            encounter_note_service: Service for encounter context
            patient_repo: Optional patient repository
            alert_repo: Optional clinical alert repository

        Returns:
            Configured EncounterPromptService
        """
        from services.prompt_generators import (
            VisitTypePromptGenerator,
            ConditionPromptGenerator,
            AlertPromptGenerator,
            FollowUpPromptGenerator,
        )

        generators: list[PromptGenerator] = []

        # Always add visit type generator
        generators.append(VisitTypePromptGenerator())

        # Add condition generator if patient repo available
        if patient_repo:
            generators.append(ConditionPromptGenerator(patient_repo))

        # Add alert generator if alert repo available
        if alert_repo:
            generators.append(AlertPromptGenerator(alert_repo))

        # Always add follow-up generator (uses context from visit notes)
        generators.append(FollowUpPromptGenerator())

        return EncounterPromptService(
            prompt_repo=prompt_repo,
            encounter_repo=encounter_repo,
            encounter_note_service=encounter_note_service,
            generators=generators,
        )
