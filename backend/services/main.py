
from fastapi import FastAPI, HTTPException, Query

from fake_data import FAKE_PATIENTS
from rxnorm import search_medications as rxnorm_search


app = FastAPI(title="Livny Health Services", version="0.1.0")


@app.get("/patients")
async def get_patients():
    return FAKE_PATIENTS


@app.get("/medications/search")
async def search_medications(q: str = Query(..., min_length=3)):
    query = q.strip()
    if len(query) < 3:
        raise HTTPException(status_code=400, detail="Query must be at least 3 characters")
    return await rxnorm_search(query)
