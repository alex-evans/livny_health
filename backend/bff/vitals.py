"""
API endpoints for vital signs.
"""

from fastapi import APIRouter, HTTPException, Path, Query

from bff import dependencies


router = APIRouter(prefix='/patients', tags=['vitals'])


@router.get("/{patient_id}/vitals")
async def get_patient_vitals(
    patient_id: str = Path(..., description="The patient ID"),
    months: int = Query(12, ge=1, le=60, description="Number of months of history for trend analysis"),
    include_trends: bool = Query(True, description="Include trend analysis and sparkline data"),
):
    """
    Get current vital signs for a patient with optional trend analysis.

    Returns the most recent value for each vital type (blood pressure, heart rate,
    temperature, weight, oxygen saturation, respiratory rate) along with:
    - Trend indicators showing direction of change
    - Sparkline data for mini-charts
    - BMI calculation (if height and weight are available)
    - Clinical significance of trends
    """
    # Verify patient exists
    patient_repo = dependencies.get_patient_repo()
    patient = await patient_repo.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get vitals
    vitals_service = dependencies.get_vitals_service()
    vitals_response = await vitals_service.get_current_vitals(
        patient_id=patient_id,
        months=months,
        include_trends=include_trends,
    )

    return vitals_response.to_dict()


@router.get("/{patient_id}/vitals/{vital_type}/history")
async def get_vital_history(
    patient_id: str = Path(..., description="The patient ID"),
    vital_type: str = Path(..., description="The vital type (e.g., heart_rate, blood_pressure_systolic)"),
    days_back: int = Query(365, ge=1, le=3650, description="Number of days of history to retrieve"),
):
    """
    Get historical vital signs for a specific vital type.

    Returns history entries and trend analysis for the specified vital type.
    Valid vital types:
    - blood_pressure_systolic
    - blood_pressure_diastolic
    - heart_rate
    - temperature
    - weight
    - oxygen_saturation
    - respiratory_rate
    - height
    """
    # Verify patient exists
    patient_repo = dependencies.get_patient_repo()
    patient = await patient_repo.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Validate vital type
    valid_types = [
        "blood_pressure_systolic",
        "blood_pressure_diastolic",
        "heart_rate",
        "temperature",
        "weight",
        "oxygen_saturation",
        "respiratory_rate",
        "height",
    ]
    if vital_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid vital type. Must be one of: {', '.join(valid_types)}"
        )

    # Get vital history
    vitals_service = dependencies.get_vitals_service()
    history_response = await vitals_service.get_vital_history(
        patient_id=patient_id,
        vital_type=vital_type,  # type: ignore
        days_back=days_back,
    )

    if not history_response:
        raise HTTPException(
            status_code=404,
            detail=f"No vital history found for type '{vital_type}'"
        )

    return history_response.to_dict()
