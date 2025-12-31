
from fastapi import FastAPI, Query

from fake_data import FAKE_PATIENTS, FAKE_MEDICATIONS


app = FastAPI(title="Livny Health Services", version="0.1.0")


@app.get("/patients")
async def get_patients():
    return FAKE_PATIENTS


@app.get("/medications/search")
async def search_medications(q: str = Query(..., min_length=3)):
    query_lower = q.lower()
    return [
        med for med in FAKE_MEDICATIONS
        if query_lower in med["name"].lower()
    ]
