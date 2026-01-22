"""Tests for vital signs repository."""

import asyncio
import pytest
from datetime import datetime, timedelta

from resources.vitals.model import VitalSign
from resources.vitals.repository import VitalSignRepository
from resources.core import Reference


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.fixture
def repo():
    """Create a fresh repository for each test."""
    return VitalSignRepository()


@pytest.fixture
def sample_vitals():
    """Create sample vital signs for testing."""
    today = datetime.now()
    patient_id = "patient-001"

    vitals = [
        VitalSign(
            id="vital-1",
            vital_type="heart_rate",
            value=72.0,
            unit="bpm",
            status="normal",
            subject=Reference.to("Patient", patient_id, "Test Patient"),
            recorded_at=today - timedelta(days=30),
        ),
        VitalSign(
            id="vital-2",
            vital_type="heart_rate",
            value=78.0,
            unit="bpm",
            status="normal",
            subject=Reference.to("Patient", patient_id, "Test Patient"),
            recorded_at=today - timedelta(days=15),
        ),
        VitalSign(
            id="vital-3",
            vital_type="heart_rate",
            value=68.0,
            unit="bpm",
            status="normal",
            subject=Reference.to("Patient", patient_id, "Test Patient"),
            recorded_at=today,
        ),
        VitalSign(
            id="vital-4",
            vital_type="blood_pressure_systolic",
            value=120.0,
            unit="mmHg",
            status="normal",
            subject=Reference.to("Patient", patient_id, "Test Patient"),
            recorded_at=today - timedelta(days=30),
        ),
        VitalSign(
            id="vital-5",
            vital_type="blood_pressure_systolic",
            value=135.0,
            unit="mmHg",
            status="abnormal",
            subject=Reference.to("Patient", patient_id, "Test Patient"),
            recorded_at=today,
        ),
        # Different patient
        VitalSign(
            id="vital-6",
            vital_type="heart_rate",
            value=80.0,
            unit="bpm",
            status="normal",
            subject=Reference.to("Patient", "patient-002", "Other Patient"),
            recorded_at=today,
        ),
    ]

    return vitals


@pytest.mark.unit
class TestVitalSignRepository:
    """Tests for VitalSignRepository."""

    def test_create_and_get(self, repo):
        """Test creating and retrieving a vital sign."""
        vital = VitalSign(
            id="vital-1",
            vital_type="heart_rate",
            value=72.0,
            unit="bpm",
            status="normal",
            subject=Reference.to("Patient", "patient-001", "Test Patient"),
        )

        run_async(repo.create(vital))
        retrieved = run_async(repo.get("vital-1"))

        assert retrieved is not None
        assert retrieved.id == "vital-1"
        assert retrieved.value == 72.0

    def test_list_by_patient_id(self, repo, sample_vitals):
        """Test filtering by patient ID."""
        for vital in sample_vitals:
            repo._store[vital.id] = vital

        results = run_async(repo.list(patient_id="patient-001"))

        assert len(results) == 5  # All except patient-002's vital
        for r in results:
            assert r.patient_id == "patient-001"

    def test_list_by_vital_type(self, repo, sample_vitals):
        """Test filtering by vital type."""
        for vital in sample_vitals:
            repo._store[vital.id] = vital

        results = run_async(repo.list(vital_type="heart_rate"))

        assert len(results) == 4  # All heart rate readings
        for r in results:
            assert r.vital_type == "heart_rate"

    def test_list_by_status(self, repo, sample_vitals):
        """Test filtering by status."""
        for vital in sample_vitals:
            repo._store[vital.id] = vital

        results = run_async(repo.list(status="abnormal"))

        assert len(results) == 1
        assert results[0].status == "abnormal"

    def test_list_by_days_back(self, repo, sample_vitals):
        """Test filtering by days back."""
        for vital in sample_vitals:
            repo._store[vital.id] = vital

        results = run_async(repo.list(days_back=20))

        assert len(results) == 4  # Only recent vitals

    def test_list_combined_filters(self, repo, sample_vitals):
        """Test combining multiple filters."""
        for vital in sample_vitals:
            repo._store[vital.id] = vital

        results = run_async(repo.list(
            patient_id="patient-001",
            vital_type="heart_rate",
            days_back=20,
        ))

        assert len(results) == 2  # Recent heart rate for patient-001

    def test_get_history(self, repo, sample_vitals):
        """Test getting history for a specific vital type."""
        for vital in sample_vitals:
            repo._store[vital.id] = vital

        history = run_async(repo.get_history(
            patient_id="patient-001",
            vital_type="heart_rate",
        ))

        assert len(history) == 3
        # Should be sorted most recent first
        assert history[0].value == 68.0  # Most recent
        assert history[1].value == 78.0
        assert history[2].value == 72.0  # Oldest

    def test_get_history_with_limit(self, repo, sample_vitals):
        """Test history with limit."""
        for vital in sample_vitals:
            repo._store[vital.id] = vital

        history = run_async(repo.get_history(
            patient_id="patient-001",
            vital_type="heart_rate",
            limit=2,
        ))

        assert len(history) == 2
        # Should be the 2 most recent
        assert history[0].value == 68.0
        assert history[1].value == 78.0

    def test_get_history_with_days_back(self, repo, sample_vitals):
        """Test history with days_back filter."""
        for vital in sample_vitals:
            repo._store[vital.id] = vital

        history = run_async(repo.get_history(
            patient_id="patient-001",
            vital_type="heart_rate",
            days_back=20,
        ))

        assert len(history) == 2  # Only recent readings

    def test_get_current_vitals(self, repo, sample_vitals):
        """Test getting most recent vital for each type."""
        for vital in sample_vitals:
            repo._store[vital.id] = vital

        current = run_async(repo.get_current_vitals("patient-001"))

        assert "heart_rate" in current
        assert "blood_pressure_systolic" in current

        # Should be the most recent for each type
        assert current["heart_rate"].value == 68.0
        assert current["blood_pressure_systolic"].value == 135.0

    def test_get_current_vitals_empty(self, repo):
        """Test getting current vitals for patient with no data."""
        current = run_async(repo.get_current_vitals("patient-999"))

        assert current == {}

    def test_get_by_patient(self, repo, sample_vitals):
        """Test getting all vitals for a patient."""
        for vital in sample_vitals:
            repo._store[vital.id] = vital

        results = run_async(repo.get_by_patient("patient-001"))

        assert len(results) == 5

    def test_get_available_vital_types(self, repo, sample_vitals):
        """Test getting available vital types for a patient."""
        for vital in sample_vitals:
            repo._store[vital.id] = vital

        types = run_async(repo.get_available_vital_types("patient-001"))

        assert "heart_rate" in types
        assert "blood_pressure_systolic" in types
        assert len(types) == 2

    def test_delete(self, repo, sample_vitals):
        """Test deleting a vital sign."""
        for vital in sample_vitals:
            repo._store[vital.id] = vital

        result = run_async(repo.delete("vital-1"))
        assert result is True

        vital = run_async(repo.get("vital-1"))
        assert vital is None

    def test_delete_nonexistent(self, repo):
        """Test deleting a nonexistent vital sign."""
        result = run_async(repo.delete("vital-999"))
        assert result is False
