
from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel

import allergies.main as allergy_services
import medications.main as medication_services
import patients.main as patient_services
import interactions.main as interaction_services


app = FastAPI(title="Livny Health Services", version="0.1.0")


@app.get("/patients")
async def get_patients():
    return [
        {
            "id": p["id"],
            "name": p["name"],
            "dateOfBirth": p["dateOfBirth"],
            "mrn": p["mrn"],
        }
        for p in patient_services.FAKE_PATIENTS
    ]


@app.get("/patients/{patient_id}")
async def get_patient(patient_id: str = Path(..., description="The patient ID")):
    patient = patient_services.find_patient(patient_id)
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
    patient = patient_services.find_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return allergy_services.get_patient_allergies(patient) 


@app.get("/patients/{patient_id}/medications")
async def get_patient_medications(patient_id: str = Path(..., description="The patient ID")):
    patient = patient_services.find_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return medication_services.get_patient_active_medications(patient)


@app.get("/medications/search")
async def search_medications(q: str = Query(..., min_length=3)):
    query = q.strip()
    if len(query) < 3:
        raise HTTPException(status_code=400, detail="Query must be at least 3 characters")
    return await medication_services.search(query)


@app.get("/medications/defaults")
async def get_medication_defaults(name: str = Query(..., description="The medication name")):
    """Get default prescription values for a medication."""
    default_duration = medication_services.get_default_duration(name)
    return {"defaultDuration": default_duration}


@app.post("/patients/{patient_id}/check-allergy")
async def check_patient_allergy(
    patient_id: str = Path(..., description="The patient ID"),
    request: allergy_services.AllergyCheckRequest = ...,
):
    """Check if a medication conflicts with patient allergies."""
    patient = patient_services.find_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient_allergies = allergies.get_patient_allergies(patient) 
    alert = allergies.check_med_conflicts(request.medication_name, patient_allergies)

    if alert:
        return {"hasConflict": True, "alert": alert.to_dict()}

    return {"hasConflict": False, "alert": None}


@app.post("/allergy-overrides")
async def log_allergy_override(override: allergy_services.AllergyOverrideLog):
    """Log an allergy override when a prescription is completed despite an allergy."""
    log_entry = allergy_services.log_allergy_override(override)

    return {"success": True, "logId": log_entry["id"]}


@app.post("/patients/{patient_id}/check-interactions")
async def check_drug_interactions(
    patient_id: str = Path(..., description="The patient ID"),
    request: interaction_services.InteractionCheckRequest = ...,
):
    """Check if a medication interacts with the patient's current medications."""
    patient = patient_services.find_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    active_medications = medication_services.get_patient_active_medications(patient)
    interactions = interaction_services.check_interactions(
        request.medication_name, active_medications
    )

    if interactions:
        return {
            "hasInteractions": True,
            "interactions": [i.to_dict() for i in interactions],
        }

    return {"hasInteractions": False, "interactions": []}


@app.post("/interaction-overrides")
async def log_interaction_override(override: interaction_services.InteractionOverrideLog):
    """Log an interaction override when a prescription is completed despite drug interactions."""
    log_entry = interaction_services.log_interaction_override(override)

    return {"success": True, "logId": log_entry["id"]}

