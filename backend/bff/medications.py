'''
Medication search and default retrieval endpoints.
'''

from fastapi import APIRouter, Query, Path, HTTPException
from pydantic import BaseModel

from bff import dependencies
from services import PatientNotFoundError


router = APIRouter(prefix='/medications', tags=['medications'])


@router.get("/search")
async def search_medications(q: str = Query(..., min_length=3)):
    """Search for medications via RxNorm."""
    service = dependencies.get_medication_search_service()
    return await service.search(q.strip())


@router.get("/defaults")
async def get_medication_defaults(name: str = Query(..., description="The medication name")):
    """Get default prescription values for a medication."""
    service = dependencies.get_medication_search_service()
    return service.get_defaults(name)


# =============================================================================
# Prescription Endpoints
# =============================================================================

class PrescribedMedication(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration_days: int
    instructions: str | None = None


class PrescriptionRequest(BaseModel):
    medications: list[PrescribedMedication]


@router.post("/{patient_id}/prescriptions")
async def create_prescription(
    patient_id: str = Path(..., description="The patient ID"),
    request: PrescriptionRequest = ...,
):
    """Create prescriptions and add medications to patient's active list."""
    service = dependencies.get_prescribing_service()

    try:
        results = await service.create_batch_prescription(
            patient_id=patient_id,
            medications=[
                {
                    "name": med.name,
                    "dosage": med.dosage,
                    "frequency": med.frequency,
                    "duration_days": med.duration_days,
                    "instructions": med.instructions,
                }
                for med in request.medications
            ],
        )
    except PatientNotFoundError:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {
        "success": True,
        "prescriptionId": results[0].prescription_id if results else None,
        "medications": [r.medication_request.to_bff_dict() for r in results],
    }


