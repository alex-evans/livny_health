"""
API endpoints for clinical alerts.
"""

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel

from bff import dependencies


router = APIRouter(prefix='/patients', tags=['alerts'])


class AcknowledgeRequest(BaseModel):
    """Request body for acknowledging an alert."""
    by: str
    note: str | None = None


class DismissRequest(BaseModel):
    """Request body for dismissing an alert."""
    by: str
    reason: str | None = None


@router.get("/{patient_id}/alerts")
async def get_patient_alerts(
    patient_id: str = Path(..., description="The patient ID"),
    status: str = Query("active", description="Filter by status: active, acknowledged, dismissed, or all"),
):
    """
    Get clinical alerts for a patient.

    Returns alerts sorted by severity (critical first) and then by date.
    Includes summary counts by severity level.

    Alert types:
    - critical_lab: Critical laboratory values requiring immediate attention
    - critical_vital: Critical vital signs
    - critical_imaging: Critical imaging findings
    - drug_interaction: Drug-drug interactions
    - overdue_screening: Overdue preventive screenings
    - chronic_disease: Chronic disease management concerns
    """
    # Verify patient exists
    patient_repo = dependencies.get_patient_repo()
    patient = await patient_repo.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Parse status filter
    if status == "all":
        status_filter = ["active", "acknowledged", "dismissed"]
    else:
        valid_statuses = ["active", "acknowledged", "dismissed"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}, or 'all'"
            )
        status_filter = status

    # Get alerts
    alert_service = dependencies.get_clinical_alert_service()
    response = await alert_service.get_patient_alerts(
        patient_id=patient_id,
        status=status_filter,
    )

    return response.to_dict()


@router.get("/{patient_id}/alerts/summary")
async def get_alert_summary(
    patient_id: str = Path(..., description="The patient ID"),
):
    """
    Get summary counts of active alerts for a patient.

    Returns counts by severity level (critical, high, medium) and total.
    Useful for displaying badge counts in the UI.
    """
    # Verify patient exists
    patient_repo = dependencies.get_patient_repo()
    patient = await patient_repo.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get summary
    alert_service = dependencies.get_clinical_alert_service()
    summary = await alert_service.get_alert_summary(patient_id)

    return summary.to_dict()


@router.post("/{patient_id}/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    request: AcknowledgeRequest,
    patient_id: str = Path(..., description="The patient ID"),
    alert_id: str = Path(..., description="The alert ID"),
):
    """
    Acknowledge a clinical alert.

    Marks the alert as reviewed. The alert will no longer appear in the
    active alerts list but can still be retrieved with status=acknowledged.
    """
    # Verify patient exists
    patient_repo = dependencies.get_patient_repo()
    patient = await patient_repo.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Acknowledge alert
    alert_service = dependencies.get_clinical_alert_service()
    result = await alert_service.acknowledge_alert(
        patient_id=patient_id,
        alert_id=alert_id,
        by=request.by,
        note=request.note,
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    return result.to_dict()


@router.post("/{patient_id}/alerts/{alert_id}/dismiss")
async def dismiss_alert(
    request: DismissRequest,
    patient_id: str = Path(..., description="The patient ID"),
    alert_id: str = Path(..., description="The alert ID"),
):
    """
    Dismiss a clinical alert.

    Marks the alert as dismissed (e.g., false positive, not clinically relevant).
    The alert will no longer appear in the active alerts list but can still be
    retrieved with status=dismissed.
    """
    # Verify patient exists
    patient_repo = dependencies.get_patient_repo()
    patient = await patient_repo.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Dismiss alert
    alert_service = dependencies.get_clinical_alert_service()
    result = await alert_service.dismiss_alert(
        patient_id=patient_id,
        alert_id=alert_id,
        by=request.by,
        reason=request.reason,
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    return result.to_dict()
