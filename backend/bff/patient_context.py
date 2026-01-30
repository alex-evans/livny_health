"""
Patient Context BFF endpoint.

Provides patient context data for the frontend with mode-aware filtering.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Literal

from bff.dependencies import get_patient_context_service
from services import PatientContextNotFoundError


router = APIRouter(prefix="/patients", tags=["Patient Context"])


@router.get("/{patient_id}/context")
async def get_patient_context(
    patient_id: str,
    encounter_id: str | None = Query(default=None, description="Optional encounter ID"),
    mode: Literal["review", "documentation"] = Query(
        default="review",
        description="Context mode: 'review' for full history, 'documentation' for today-focused"
    ),
):
    """
    Get comprehensive patient context for clinical workflow.

    Returns enriched patient data including:
    - Vitals with trends
    - Medications with categories and high-alert flags
    - Allergies ordered by severity
    - Problems
    - Recent labs with abnormal flags
    - Recent visits with days-ago calculation
    - Quick summary for context bar

    Modes:
    - 'review': Full patient history, all sections expanded
    - 'documentation': Today-focused, vitals prominent, history condensed
    """
    service = get_patient_context_service()

    try:
        context = await service.get_patient_context(
            patient_id=patient_id,
            encounter_id=encounter_id,
            mode=mode,
        )
        return context.to_dict()
    except PatientContextNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{patient_id}/context/quick")
async def get_quick_context(patient_id: str):
    """
    Get quick context summary for the context bar.

    Returns a minimal summary with:
    - Primary vital (BP or HR)
    - Top 3 medication names
    - Critical allergies
    - Key lab result
    - Problem count
    """
    service = get_patient_context_service()

    try:
        summary = await service.get_quick_context_summary(patient_id)
        return summary.to_dict()
    except PatientContextNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
