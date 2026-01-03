
from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel

from fake_data import FAKE_PATIENTS
from rxnorm import search_medications as rxnorm_search
from dosing_data import get_default_duration
from allergy_checker import check_allergy


class AllergyCheckRequest(BaseModel):
    medication_name: str


app = FastAPI(title="Livny Health Services", version="0.1.0")


def find_patient(patient_id: str):
    for patient in FAKE_PATIENTS:
        if patient["id"] == patient_id:
            return patient
    return None


@app.get("/patients")
async def get_patients():
    return [
        {
            "id": p["id"],
            "name": p["name"],
            "dateOfBirth": p["dateOfBirth"],
            "mrn": p["mrn"],
        }
        for p in FAKE_PATIENTS
    ]


@app.get("/patients/{patient_id}")
async def get_patient(patient_id: str = Path(..., description="The patient ID")):
    patient = find_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {
        "id": patient["id"],
        "name": patient["name"],
        "dateOfBirth": patient["dateOfBirth"],
        "mrn": patient["mrn"],
    }


@app.get("/patients/{patient_id}/allergies")
async def get_patient_allergies(patient_id: str = Path(..., description="The patient ID")):
    patient = find_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient.get("allergies", [])


@app.get("/patients/{patient_id}/medications")
async def get_patient_medications(patient_id: str = Path(..., description="The patient ID")):
    patient = find_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient.get("activeMedications", [])


@app.get("/medications/search")
async def search_medications(q: str = Query(..., min_length=3)):
    query = q.strip()
    if len(query) < 3:
        raise HTTPException(status_code=400, detail="Query must be at least 3 characters")
    return await rxnorm_search(query)


@app.get("/medications/defaults")
async def get_medication_defaults(name: str = Query(..., description="The medication name")):
    """Get default prescription values for a medication."""
    default_duration = get_default_duration(name)
    return {"defaultDuration": default_duration}


@app.post("/patients/{patient_id}/check-allergy")
async def check_patient_allergy(
    patient_id: str = Path(..., description="The patient ID"),
    request: AllergyCheckRequest = ...,
):
    """Check if a medication conflicts with patient allergies."""
    patient = find_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    allergies = patient.get("allergies", [])
    alert = check_allergy(request.medication_name, allergies)

    if alert:
        return {"hasConflict": True, "alert": alert.to_dict()}

    return {"hasConflict": False, "alert": None}
