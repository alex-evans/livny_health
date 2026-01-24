"""
API endpoints for social and family history.
"""

from fastapi import APIRouter, HTTPException, Path, Query

from bff import dependencies


router = APIRouter(prefix='/patients', tags=['social-family-history'])


@router.get("/{patient_id}/social-family-history")
async def get_patient_social_family_history(
    patient_id: str = Path(..., description="The patient ID"),
    include_risk_assessments: bool = Query(True, description="Include calculated risk assessments"),
):
    """
    Get social and family history for a patient with risk assessments.

    Returns social history (smoking, alcohol, occupation, etc.) and family history
    (relatives with conditions, hereditary syndromes) along with:
    - Calculated risk assessments for cardiovascular disease, cancer, and diabetes
    - Contributing factors for each risk
    - Recommendations and screening due dates

    Note: Returns an empty structure (not 404) if history has not been documented.
    """
    # Verify patient exists
    patient_repo = dependencies.get_patient_repo()
    patient = await patient_repo.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get social/family history
    social_family_history_service = dependencies.get_social_family_history_service()
    response = await social_family_history_service.get_social_family_history(
        patient_id=patient_id,
        include_risk_assessments=include_risk_assessments,
    )

    return response.to_dict()
