from fastapi import FastAPI, Query
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


@app.get("/api/medications/search")
async def search_medications(q: str = Query(..., min_length=3)):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICES_URL}/medications/search", params={"q": q})
        return response.json()
