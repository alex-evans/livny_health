"""
Livny Health BFF - Backend for Frontend.

This is the main API that the frontend talks to.
It orchestrates calls to services and shapes responses for the frontend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import get_settings
from bff.dependencies import (
    ensure_data_seeded,
    ensure_data_seeded_async,
    set_session_factory,
)
from bff.allergies import router as allergies_router
from bff.patients import router as patients_router
from bff.medications import router as medications_router
from bff.schedule import router as schedule_router
from bff.imaging import router as imaging_router
from bff.vitals import router as vitals_router
from bff.social_family_history import router as social_family_history_router
from bff.chart_sections import router as chart_sections_router
from bff.alerts import router as alerts_router
from bff.encounters import router as encounters_router, appointment_router, patient_router as patient_encounters_router
from bff.encounter_prompts import router as encounter_prompts_router
from bff.patient_context import router as patient_context_router
from bff.soap_mapping import router as soap_mapping_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    settings = get_settings()

    if settings.storage_backend == "postgres":
        # Initialize postgres connection
        from db import init_db, close_db, get_session_factory

        await init_db()
        session_factory = await get_session_factory()
        set_session_factory(session_factory)

        # Seed data asynchronously
        await ensure_data_seeded_async()

        yield

        # Cleanup postgres connection
        await close_db()
    else:
        # In-memory mode - synchronous seeding
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
app.include_router(encounters_router)
app.include_router(encounter_prompts_router)
app.include_router(appointment_router)
app.include_router(patient_encounters_router)
app.include_router(patient_context_router)
app.include_router(soap_mapping_router)


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker."""
    return {"status": "healthy"}
