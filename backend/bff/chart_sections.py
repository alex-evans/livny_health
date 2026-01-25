"""
API endpoints for chart section navigation.

Provides navigation sections with badge counts, alerts, and keyboard shortcuts.
"""

from fastapi import APIRouter, HTTPException, Path

from bff.dependencies import get_chart_section_service


router = APIRouter(prefix="/patients", tags=["chart-sections"])


@router.get("/{patient_id}/chart/sections")
async def get_chart_sections(
    patient_id: str = Path(..., description="The patient ID"),
):
    """
    Get chart navigation sections for a patient.

    Returns all chart sections with:
    - Badge counts (medications, allergies, etc.)
    - Alert levels (critical, warning, info, none)
    - Keyboard shortcuts
    - Last updated timestamps
    """
    service = get_chart_section_service()
    result = await service.get_chart_sections(patient_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    return result.to_dict()
