#!/usr/bin/env python3
"""
Standalone script to seed the PostgreSQL database with initial data.

Usage:
    # First, ensure the database is created and migrations are run:
    # docker-compose up -d  (or ensure postgres is running)
    # alembic upgrade head

    # Then run this script:
    python seed_postgres.py

This script will:
1. Initialize the database connection
2. Seed all repositories with initial data (using upsert/merge)
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from config import get_settings
from db.engine import get_session_factory, init_db
from services.data_seeder import seed_all_async

# Import all Postgres repositories
from resources.patient.postgres_repository import PostgresPatientRepository
from resources.practitioner.postgres_repository import PostgresPractitionerRepository
from resources.allergy_intolerance.postgres_repository import PostgresAllergyIntoleranceRepository
from resources.medication_request.postgres_repository import PostgresMedicationRequestRepository
from resources.appointment.postgres_repository import PostgresAppointmentRepository
from resources.encounter.postgres_repository import PostgresEncounterRepository
from resources.visit_note.postgres_repository import PostgresVisitNoteRepository
from resources.imaging_study.postgres_repository import PostgresImagingStudyRepository
from resources.vitals.postgres_repository import PostgresVitalSignRepository
from resources.social_family_history.postgres_repository import PostgresSocialFamilyHistoryRepository
from resources.lab_result.postgres_repository import PostgresLabResultRepository


async def seed_database():
    """Main function to seed the PostgreSQL database."""
    settings = get_settings()

    if settings.storage_backend != "postgres":
        print("ERROR: STORAGE_BACKEND is not set to 'postgres'")
        print(f"Current value: {settings.storage_backend}")
        print("Set STORAGE_BACKEND=postgres in your environment or .env file")
        sys.exit(1)

    # Mask password in database URL for display
    db_url = settings.database_url
    if "@" in db_url:
        # Hide password in output
        parts = db_url.split("@")
        prefix = parts[0].rsplit(":", 1)[0] + ":***"
        db_url_display = f"{prefix}@{parts[1]}"
    else:
        db_url_display = db_url[:50] + "..."

    print(f"Connecting to database: {db_url_display}")

    # Initialize the database connection
    print("Initializing database connection...")
    await init_db()

    # Get session factory (this is async)
    session_factory = await get_session_factory()

    # Create repository instances
    print("Creating repository instances...")
    patient_repo = PostgresPatientRepository(session_factory)
    practitioner_repo = PostgresPractitionerRepository(session_factory)
    allergy_repo = PostgresAllergyIntoleranceRepository(session_factory)
    medication_request_repo = PostgresMedicationRequestRepository(session_factory)
    appointment_repo = PostgresAppointmentRepository(session_factory)
    encounter_repo = PostgresEncounterRepository(session_factory)
    visit_note_repo = PostgresVisitNoteRepository(session_factory)
    imaging_study_repo = PostgresImagingStudyRepository(session_factory)
    vitals_repo = PostgresVitalSignRepository(session_factory)
    social_family_history_repo = PostgresSocialFamilyHistoryRepository(session_factory)
    lab_result_repo = PostgresLabResultRepository(session_factory)

    # Seed all repositories
    print("Seeding repositories with initial data...")
    print("(This uses merge/upsert, so it's safe to run multiple times)")
    print()

    await seed_all_async(
        patient_repo=patient_repo,
        practitioner_repo=practitioner_repo,
        allergy_repo=allergy_repo,
        medication_request_repo=medication_request_repo,
        appointment_repo=appointment_repo,
        encounter_repo=encounter_repo,
        visit_note_repo=visit_note_repo,
        imaging_study_repo=imaging_study_repo,
        vitals_repo=vitals_repo,
        social_family_history_repo=social_family_history_repo,
        lab_result_repo=lab_result_repo,
    )

    print("\n" + "=" * 60)
    print("Database seeding completed successfully!")
    print("=" * 60)
    print("\nSeeded data includes:")
    print("  - Patients (patient-001, patient-002, ...)")
    print("  - Practitioners (provider-001, provider-002, ...)")
    print("  - Allergies")
    print("  - Medication Requests")
    print("  - Appointments")
    print("  - Visit Notes")
    print("  - Imaging Studies")
    print("  - Vital Signs")
    print("  - Social/Family History")
    print("  - Lab Results")


if __name__ == "__main__":
    print("=" * 60)
    print("PostgreSQL Database Seeder")
    print("=" * 60)
    print()
    asyncio.run(seed_database())
