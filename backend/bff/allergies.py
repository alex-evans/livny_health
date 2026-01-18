'''
API endpoints for managing allergies
'''

from datetime import datetime
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel

from bff.dependencies import get_patient_repo, get_clinical_decision_service


router = APIRouter(prefix='/allergies', tags=['allergies'])


###############
# Allergy Review Status Endpoints
###############

class MarkAllergiesReviewedRequest(BaseModel):
    reviewer_id: str | None = None
    reviewer_name: str | None = None


@router.post("/{patient_id}/mark-reviewed")
async def mark_allergies_reviewed(
    patient_id: str = Path(..., description="The patient ID"),
    request: MarkAllergiesReviewedRequest = MarkAllergiesReviewedRequest(),
):
    """
    Mark a patient's allergy history as reviewed.

    This creates or updates the allergy review timestamp, indicating that
    a clinician has confirmed the allergy list is complete and current.
    """
    patient_repo = get_patient_repo()
    patient = await patient_repo.mark_allergies_reviewed(
        patient_id=patient_id,
        reviewer_id=request.reviewer_id,
        reviewer_name=request.reviewer_name,
    )

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    review_status = patient.allergy_review_status
    return {
        "success": True,
        "allergyReviewStatus": {
            "reviewedAt": review_status.reviewed_at.isoformat(),
            "reviewedBy": review_status.reviewer_name,
            "isStale": review_status.is_stale,
        },
    }


###############
# Allergy Check Endpoints
###############

class AllergyCheckRequest(BaseModel):
    medication_name: str


@router.post("/{patient_id}/check-allergy")
async def check_patient_allergy(
    patient_id: str = Path(..., description="The patient ID"),
    request: AllergyCheckRequest = ...,
):
    """Check if a medication conflicts with patient allergies."""
    patient_repo = get_patient_repo()
    patient = await patient_repo.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    service = get_clinical_decision_service()
    alert = await service.check_allergy_conflicts(patient_id, request.medication_name)

    if alert:
        return {"hasConflict": True, "alert": alert.to_dict()}
    return {"hasConflict": False, "alert": None}


###############
# Drug and Allergy Interaction Check Endpoints
###############

class InteractionCheckRequest(BaseModel):
    medication_name: str


@router.post("/{patient_id}/check-interactions")
async def check_drug_interactions(
    patient_id: str = Path(..., description="The patient ID"),
    request: InteractionCheckRequest = ...,
):
    """Check if a medication interacts with patient's current medications."""
    patient_repo = get_patient_repo()
    patient = await patient_repo.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    service = get_clinical_decision_service()
    interactions = await service.check_drug_interactions(patient_id, request.medication_name)

    if interactions:
        return {
            "hasInteractions": True,
            "interactions": [i.to_dict() for i in interactions],
        }
    return {"hasInteractions": False, "interactions": []}


################
# Override Logging Endpoints
################

class AllergyOverrideRequest(BaseModel):
    patient_id: str
    medication_name: str
    allergen: str
    severity: str
    justification: str
    acknowledged_at: str
    prescribed_at: str


@router.post("/allergy-overrides")
async def log_allergy_override(request: AllergyOverrideRequest):
    """Log an allergy override when prescribing despite allergy."""
    service = get_clinical_decision_service()
    log_entry = service.log_allergy_override(
        patient_id=request.patient_id,
        medication_name=request.medication_name,
        allergen=request.allergen,
        severity=request.severity,
        justification=request.justification,
        acknowledged_at=request.acknowledged_at,
        prescribed_at=request.prescribed_at,
    )
    return {"success": True, "logId": log_entry.id}


class InteractionOverrideRequest(BaseModel):
    patient_id: str
    medication_name: str
    interacting_drugs: list[str]
    severities: list[str]
    justification: str
    acknowledged_at: str
    prescribed_at: str


@router.post("/interaction-overrides")
async def log_interaction_override(request: InteractionOverrideRequest):
    """Log an interaction override when prescribing despite drug interactions."""
    service = get_clinical_decision_service()
    log_entry = service.log_interaction_override(
        patient_id=request.patient_id,
        medication_name=request.medication_name,
        interacting_drugs=request.interacting_drugs,
        severities=request.severities,
        justification=request.justification,
        acknowledged_at=request.acknowledged_at,
        prescribed_at=request.prescribed_at,
    )
    return {"success": True, "logId": log_entry.id}

