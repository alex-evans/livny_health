import asyncio

from fastapi import FastAPI, Query, Path, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="Livny Health BFF", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICES_URL = "http://localhost:8001"


@app.get("/api/patients")
async def get_patients():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICES_URL}/patients")
        return response.json()


@app.get("/api/patients/{patient_id}")
async def get_patient(patient_id: str = Path(..., description="The patient ID")):
    async with httpx.AsyncClient() as client:
        patient_task = client.get(f"{SERVICES_URL}/patients/{patient_id}")
        allergies_task = client.get(f"{SERVICES_URL}/patients/{patient_id}/allergies")
        medications_task = client.get(f"{SERVICES_URL}/patients/{patient_id}/medications")

        patient_res, allergies_res, medications_res = await asyncio.gather(
            patient_task, allergies_task, medications_task
        )

        if patient_res.status_code == 404:
            raise HTTPException(status_code=404, detail="Patient not found")

        patient = patient_res.json()
        patient["allergies"] = allergies_res.json()
        patient["activeMedications"] = medications_res.json()

        return patient


@app.get("/api/medications/search")
async def search_medications(q: str = Query(..., min_length=3)):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICES_URL}/medications/search", params={"q": q})
        return response.json()
