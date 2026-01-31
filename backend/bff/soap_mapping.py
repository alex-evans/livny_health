"""
API endpoint for SOAP mapping.

Parses clinical note content into structured SOAP sections for display.
"""

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel

from bff import dependencies


router = APIRouter(prefix="/encounters", tags=["encounters"])


class SOAPMappingRequest(BaseModel):
    """Request body for SOAP mapping."""
    content: str


@router.post("/{encounter_id}/soap-mapping")
async def get_soap_mapping(
    request: SOAPMappingRequest,
    encounter_id: str = Path(..., description="The encounter ID"),
):
    """
    Parse clinical note content into SOAP sections.

    This endpoint takes the current note content and returns a structured
    mapping of Subjective, Objective, Assessment, and Plan sections with
    completeness indicators.

    The mapping uses keyword-based section detection. If explicit section
    markers aren't found, it attempts to infer sections from content patterns.

    Request body:
    - content: The clinical note text to parse

    Returns:
    - subjective: Section with content, completeness, wordCount
    - objective: Section with content, completeness, wordCount
    - assessment: Section with content, completeness, wordCount
    - plan: Section with content, completeness, wordCount
    - overallCompleteness: 'empty' | 'partial' | 'complete'

    Completeness thresholds:
    - empty: 0 words
    - partial: 1-29 words
    - complete: 30+ words
    """
    # Verify encounter exists
    encounter_repo = dependencies.get_encounter_repo()
    encounter = await encounter_repo.get(encounter_id)
    if not encounter:
        raise HTTPException(
            status_code=404,
            detail=f"Encounter {encounter_id} not found",
        )

    soap_mapping_service = dependencies.get_soap_mapping_service()
    result = soap_mapping_service.parse(request.content)
    return result.to_dict()
