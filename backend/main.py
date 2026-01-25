"""
Livny Health BFF - Backend for Frontend.

This is the main API that the frontend talks to.
It orchestrates calls to services and shapes responses for the frontend.
"""

from fastapi import FastAPI, Query, Path, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

from bff.dependencies import ensure_data_seeded
from bff.allergies import router as allergies_router
from bff.patients import router as patients_router
from bff.medications import router as medications_router
from bff.schedule import router as schedule_router
from bff.imaging import router as imaging_router
from bff.vitals import router as vitals_router
from bff.social_family_history import router as social_family_history_router
from bff.chart_sections import router as chart_sections_router
from bff.alerts import router as alerts_router
from bff.chart_sections import router as chart_sections_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Seed data on startup
    ensure_data_seeded()
    yield


app = FastAPI(
    title="Livny Health BFF",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(allergies_router)
app.include_router(patients_router)
app.include_router(medications_router)
app.include_router(schedule_router)
app.include_router(imaging_router)
app.include_router(vitals_router)
app.include_router(social_family_history_router)
app.include_router(chart_sections_router)
app.include_router(alerts_router)
app.include_router(chart_sections_router)

