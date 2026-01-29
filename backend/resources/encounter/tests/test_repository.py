"""
Unit tests for EncounterRepository.
"""
import asyncio
import pytest
from datetime import datetime, date

from resources.encounter import (
    Encounter,
    EncounterRepository,
    EncounterStatus,
    EncounterClass,
    EncounterParticipant,
)
from resources.core import Reference, Period, CodeableConcept


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestEncounterRepository:
    """Tests for EncounterRepository."""

    @pytest.fixture
    def repo(self):
        """Create a repository."""
        return EncounterRepository()

    @pytest.fixture
    def test_encounters(self, repo):
        """Create test encounters."""
        base_date = datetime(2024, 1, 15, 9, 0, 0)
        encounters = [
            # In-progress encounter for patient-001
            Encounter(
                id="enc-001",
                status=EncounterStatus.IN_PROGRESS,
                encounter_class=EncounterClass.AMBULATORY,
                subject=Reference(reference="Patient/patient-001"),
                participants=[
                    EncounterParticipant(
                        individual=Reference(reference="Practitioner/pract-001"),
                        type="primary",
                    )
                ],
                period=Period(start=base_date),
                appointment=Reference(reference="Appointment/appt-001"),
            ),
            # Completed encounter for patient-001
            Encounter(
                id="enc-002",
                status=EncounterStatus.COMPLETED,
                encounter_class=EncounterClass.AMBULATORY,
                subject=Reference(reference="Patient/patient-001"),
                participants=[
                    EncounterParticipant(
                        individual=Reference(reference="Practitioner/pract-002"),
                        type="primary",
                    )
                ],
                period=Period(start=datetime(2024, 1, 10, 10, 0, 0), end=datetime(2024, 1, 10, 10, 30, 0)),
                appointment=Reference(reference="Appointment/appt-002"),
            ),
            # Scheduled encounter for patient-002
            Encounter(
                id="enc-003",
                status=EncounterStatus.SCHEDULED,
                encounter_class=EncounterClass.AMBULATORY,
                subject=Reference(reference="Patient/patient-002"),
                participants=[
                    EncounterParticipant(
                        individual=Reference(reference="Practitioner/pract-001"),
                        type="primary",
                    )
                ],
                period=Period(start=base_date),
            ),
            # Signed encounter
            Encounter(
                id="enc-004",
                status=EncounterStatus.SIGNED,
                encounter_class=EncounterClass.AMBULATORY,
                subject=Reference(reference="Patient/patient-001"),
                period=Period(start=datetime(2024, 1, 20, 14, 0, 0)),
            ),
        ]
        for e in encounters:
            repo._store[e.id] = e
        return encounters

    def test_list_all(self, repo, test_encounters):
        """list with no filters returns all encounters."""
        result = run_async(repo.list())
        assert len(result) == 4

    def test_list_filter_by_patient_id(self, repo, test_encounters):
        """list filters by patient ID."""
        result = run_async(repo.list(patient_id="patient-001"))
        assert len(result) == 3
        assert all("patient-001" in e.subject.reference for e in result)

    def test_list_filter_by_status_string(self, repo, test_encounters):
        """list filters by single status string."""
        result = run_async(repo.list(status="completed"))
        assert len(result) == 1
        assert result[0].id == "enc-002"

    def test_list_filter_by_status_list(self, repo, test_encounters):
        """list filters by multiple statuses."""
        result = run_async(repo.list(status=["in_progress", "scheduled"]))
        assert len(result) == 2
        ids = {e.id for e in result}
        assert ids == {"enc-001", "enc-003"}

    def test_list_filter_by_provider_id(self, repo, test_encounters):
        """list filters by provider ID."""
        result = run_async(repo.list(provider_id="pract-001"))
        assert len(result) == 2
        ids = {e.id for e in result}
        assert ids == {"enc-001", "enc-003"}

    def test_list_filter_by_date_object(self, repo, test_encounters):
        """list filters by date object."""
        result = run_async(repo.list(date=date(2024, 1, 15)))
        assert len(result) == 2  # enc-001 and enc-003

    def test_list_filter_by_date_string(self, repo, test_encounters):
        """list filters by date string."""
        result = run_async(repo.list(date="2024-01-10"))
        assert len(result) == 1
        assert result[0].id == "enc-002"

    def test_list_filter_by_appointment_id(self, repo, test_encounters):
        """list filters by appointment ID."""
        result = run_async(repo.list(appointment_id="appt-001"))
        assert len(result) == 1
        assert result[0].id == "enc-001"

    def test_list_multiple_filters(self, repo, test_encounters):
        """list with multiple filters applies all."""
        result = run_async(repo.list(patient_id="patient-001", status="completed"))
        assert len(result) == 1
        assert result[0].id == "enc-002"

    def test_get_active_for_patient_in_progress(self, repo, test_encounters):
        """get_active_for_patient returns in-progress encounter."""
        result = run_async(repo.get_active_for_patient("patient-001"))
        assert result is not None
        assert result.id == "enc-001"

    def test_get_active_for_patient_no_active(self, repo, test_encounters):
        """get_active_for_patient returns None for patient with only scheduled encounter."""
        result = run_async(repo.get_active_for_patient("patient-002"))
        assert result is None

    def test_get_active_for_patient_none(self, repo, test_encounters):
        """get_active_for_patient returns None when no active encounter."""
        result = run_async(repo.get_active_for_patient("patient-999"))
        assert result is None

    def test_get_by_patient(self, repo, test_encounters):
        """get_by_patient returns all encounters for patient."""
        result = run_async(repo.get_by_patient("patient-001"))
        assert len(result) == 3

    def test_get_by_patient_empty(self, repo, test_encounters):
        """get_by_patient returns empty list for unknown patient."""
        result = run_async(repo.get_by_patient("patient-999"))
        assert result == []

    def test_get_by_appointment_found(self, repo, test_encounters):
        """get_by_appointment returns encounter when found."""
        result = run_async(repo.get_by_appointment("appt-002"))
        assert result is not None
        assert result.id == "enc-002"

    def test_get_by_appointment_not_found(self, repo, test_encounters):
        """get_by_appointment returns None when not found."""
        result = run_async(repo.get_by_appointment("appt-999"))
        assert result is None

    def test_get_by_id(self, repo, test_encounters):
        """get returns encounter by ID."""
        result = run_async(repo.get("enc-001"))
        assert result is not None
        assert result.status == EncounterStatus.IN_PROGRESS

    def test_get_by_id_not_found(self, repo, test_encounters):
        """get returns None when ID doesn't exist."""
        result = run_async(repo.get("nonexistent"))
        assert result is None

    def test_create(self, repo):
        """create adds a new encounter."""
        new_enc = Encounter(
            id="enc-new",
            status=EncounterStatus.SCHEDULED,
            subject=Reference(reference="Patient/patient-new"),
        )
        result = run_async(repo.create(new_enc))
        assert result.id == "enc-new"

        stored = run_async(repo.get("enc-new"))
        assert stored is not None

    def test_update(self, repo, test_encounters):
        """update modifies an existing encounter."""
        updated = Encounter(
            id="enc-001",
            status=EncounterStatus.COMPLETED,
            subject=Reference(reference="Patient/patient-001"),
            period=Period(start=datetime(2024, 1, 15, 9, 0, 0), end=datetime(2024, 1, 15, 9, 30, 0)),
        )
        result = run_async(repo.update("enc-001", updated))
        assert result is not None
        assert result.status == EncounterStatus.COMPLETED
        assert result.period.end is not None

    def test_delete(self, repo, test_encounters):
        """delete removes an encounter."""
        result = run_async(repo.delete("enc-001"))
        assert result is True

        stored = run_async(repo.get("enc-001"))
        assert stored is None
