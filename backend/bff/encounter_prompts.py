"""
API endpoints for encounter prompts.

Provides endpoints to generate, retrieve, and update prompts that guide
physicians through clinical encounters.
"""

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel
from typing import Literal

from bff import dependencies
from services.encounter_prompt_service import (
    EncounterNotFoundError,
    PromptNotFoundError,
    PromptNotSkippableError,
)


router = APIRouter(prefix='/encounters', tags=['encounter-prompts'])


class GeneratePromptsRequest(BaseModel):
    """Request body for generating prompts."""
    visitType: Literal["follow_up", "annual_physical", "urgent"] = "follow_up"


class UpdatePromptRequest(BaseModel):
    """Request body for updating a prompt."""
    action: Literal["address", "skip", "defer"]
    userId: str
    responseData: dict | None = None
    skipReason: str | None = None


class ReorderPromptsRequest(BaseModel):
    """Request body for reordering prompts."""
    promptIds: list[str]


@router.post("/{encounter_id}/generate-prompts")
async def generate_prompts(
    request: GeneratePromptsRequest,
    encounter_id: str = Path(..., description="The encounter ID"),
):
    """
    Generate prompts for an encounter.

    Generates contextual prompts based on:
    - Visit type (follow_up, annual_physical, urgent)
    - Patient conditions (diabetes, hypertension, etc.)
    - Active clinical alerts
    - Follow-up items from previous visits

    Request body:
    - visitType: The type of visit (default: follow_up)

    Returns:
    - prompts: List of generated prompts
    - totalCount: Total number of prompts
    - pendingCount: Number of pending prompts
    - criticalCount: Number of critical prompts
    """
    prompt_service = dependencies.get_encounter_prompt_service()

    try:
        result = await prompt_service.generate_prompts(
            encounter_id=encounter_id,
            visit_type=request.visitType,
        )
        return result.to_dict()
    except EncounterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{encounter_id}/prompts")
async def get_prompts(
    encounter_id: str = Path(..., description="The encounter ID"),
    status: str | None = None,
):
    """
    Get prompts for an encounter.

    Query parameters:
    - status: Filter by status (pending, addressed, skipped, deferred)
              Can be comma-separated for multiple values

    Returns:
    - prompts: List of prompts sorted by order
    - totalCount: Total number of prompts
    - pendingCount: Number of pending prompts
    - addressedCount: Number of addressed prompts
    - criticalCount: Number of critical prompts
    """
    prompt_service = dependencies.get_encounter_prompt_service()

    # Parse status filter
    status_filter = None
    if status:
        status_filter = [s.strip() for s in status.split(",")]

    try:
        result = await prompt_service.get_encounter_prompts(
            encounter_id=encounter_id,
            status=status_filter,
        )
        return result.to_dict()
    except EncounterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{encounter_id}/prompts/{prompt_id}")
async def update_prompt(
    request: UpdatePromptRequest,
    encounter_id: str = Path(..., description="The encounter ID"),
    prompt_id: str = Path(..., description="The prompt ID"),
):
    """
    Update a prompt's status.

    Actions:
    - address: Mark the prompt as addressed (with optional response data)
    - skip: Skip the prompt (if skippable, with optional reason)
    - defer: Defer the prompt for later

    Request body:
    - action: The action to take
    - userId: The user performing the action
    - responseData: Optional response data (for address action)
    - skipReason: Optional reason for skipping

    Returns:
    - Updated prompt object
    """
    prompt_service = dependencies.get_encounter_prompt_service()

    try:
        result = await prompt_service.update_prompt(
            encounter_id=encounter_id,
            prompt_id=prompt_id,
            action=request.action,
            user_id=request.userId,
            response_data=request.responseData,
            skip_reason=request.skipReason,
        )
        return result.to_dict()
    except EncounterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PromptNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PromptNotSkippableError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "not_skippable",
                "message": str(e),
            }
        )


@router.post("/{encounter_id}/prompts/reorder")
async def reorder_prompts(
    request: ReorderPromptsRequest,
    encounter_id: str = Path(..., description="The encounter ID"),
):
    """
    Reorder prompts within an encounter.

    Allows physicians to customize the order they want to address prompts.

    Request body:
    - promptIds: List of prompt IDs in desired order

    Returns:
    - prompts: List of reordered prompts
    """
    prompt_service = dependencies.get_encounter_prompt_service()

    try:
        result = await prompt_service.reorder_prompts(
            encounter_id=encounter_id,
            prompt_ids=request.promptIds,
        )
        return {
            "prompts": [p.to_dict() for p in result],
        }
    except EncounterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
