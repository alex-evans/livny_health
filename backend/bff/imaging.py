"""
API endpoints for imaging studies.
"""

from fastapi import APIRouter, HTTPException, Path, Query

from bff.dependencies import get_imaging_service


router = APIRouter(prefix="/imaging", tags=["imaging"])


@router.get("/{patient_id}/studies")
async def get_imaging_studies(
    patient_id: str = Path(..., description="The patient ID"),
    modality: str | None = Query(None, description="Filter by modality (CT, MRI, XR, etc.)"),
    days_back: int = Query(730, description="Number of days to look back (default 2 years)"),
):
    """
    Get imaging studies for a patient.

    Returns studies sorted by date (newest first) with optional filtering.
    """
    service = get_imaging_service()

    response = await service.get_studies_for_patient(
        patient_id=patient_id,
        modality_filter=modality,
        days_back=days_back,
    )

    return response.to_dict()
