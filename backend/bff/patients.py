'''
API endpoints for managing patients
'''

from fastapi import APIRouter, HTTPException, Path, Depends
from pydantic import BaseModel

from bff import dependencies


router = APIRouter(prefix='/patients', tags=['patients'])


@router.get("/")
async def get_patients():
    """Get all patients."""
    patient_repo = dependencies.get_patient_repo()
    patients = await patient_repo.list()
    return [p.to_bff_dict() for p in patients]


@router.get("/{patient_id}")
async def get_patient(patient_id: str = Path(..., description="The patient ID")):
    """Get a single patient with their allergies, active medications, and next appointment."""
    patient_repo = dependencies.get_patient_repo()
    allergy_repo = dependencies.get_allergy_repo()
    medication_request_repo = dependencies.get_medication_request_repo()
    appointment_repo = dependencies.get_appointment_repo()

    patient = await patient_repo.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get all allergies (including inactive) for the toggle view
    all_allergies = await allergy_repo.get_all_by_patient(patient_id)
    medications = await medication_request_repo.get_active_for_patient(patient_id)
    upcoming_appointments = await appointment_repo.get_upcoming_for_patient(patient_id)

    result = patient.to_bff_dict()
    result["allergies"] = [a.to_bff_dict() for a in all_allergies]
    result["activeMedications"] = [m.to_bff_dict() for m in medications]

    # Add next appointment if available
    if upcoming_appointments:
        next_appt = upcoming_appointments[0]
        result["nextAppointment"] = {
            "date": next_appt.start.strftime("%m/%d/%Y"),
            "time": next_appt.start.strftime("%I:%M %p").lstrip("0"),
            "reason": next_appt.reason or next_appt.visit_type,
        }

    return result


