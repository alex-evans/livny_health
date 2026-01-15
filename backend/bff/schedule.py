'''
API endpoints for managing scheduling
'''

from fastapi import APIRouter, HTTPException, Path, Query, Depends
from pydantic import BaseModel

from bff.dependencies import get_scheduling_service, get_patient_repo
from services import ProviderNotFoundError


router = APIRouter(prefix='/schedule', tags=['schedule'])


@router.get("/")
async def get_schedule(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    provider_id: str = Query("provider-001", description="The provider ID"),
):
    """Get the daily schedule for a provider."""
    service = get_scheduling_service()

    try:
        result = await service.get_daily_schedule(date, provider_id)
    except ProviderNotFoundError:
        raise HTTPException(status_code=404, detail="Provider not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "date": result.date,
        "provider": {
            "id": result.provider_id,
            "name": result.provider_name,
        },
        "appointments": result.appointments,
    }


class AppointmentRequest(BaseModel):
    date: str
    patient_id: str
    time: str
    duration_minutes: int = 30
    visit_type: str = "Office Visit"
    chief_complaint: str | None = None


@router.post("/appointments")
async def create_appointment(request: AppointmentRequest):
    """Add a new appointment."""
    service = get_scheduling_service()

    try:
        appointment = await service.create_appointment(
            date_str=request.date,
            time=request.time,
            patient_id=request.patient_id,
            provider_id="provider-001",  # Default provider for now
            duration_minutes=request.duration_minutes,
            visit_type=request.visit_type,
            chief_complaint=request.chief_complaint,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ProviderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Get patient data for the response
    patient_repo = get_patient_repo()
    patient = await patient_repo.get(request.patient_id)
    patient_data = patient.to_bff_dict() if patient else None

    return {"success": True, "appointment": appointment.to_bff_dict(patient_data)}


@router.delete("/schedule/appointments")
async def clear_appointments():
    """Clear all appointments (for test reset)."""
    service = get_scheduling_service()
    await service.clear_dynamic_appointments()
    return {"success": True, "message": "All appointments cleared"}
