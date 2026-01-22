"""Tests for vitals BFF endpoints."""

import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timedelta

from main import app
from bff import dependencies
from resources.vitals import VitalSign, VitalSignRepository
from resources.core import Reference


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Ensure data is seeded before running tests
dependencies.ensure_data_seeded()


def create_seeded_vitals_repo():
    """Create a repository with sample vital data."""
    repo = VitalSignRepository()
    today = datetime.now()
    patient_id = "patient-001"

    # Heart rate history
    hr_values = [75, 74, 73, 72, 71, 70]
    for i, value in enumerate(hr_values):
        vital = VitalSign(
            id=f"hr-{i}",
            vital_type="heart_rate",
            value=float(value),
            unit="bpm",
            status="normal",
            subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
            recorded_at=today - timedelta(days=(len(hr_values) - i - 1) * 30),
            recorded_by="Dr. Smith",
            location="Main Clinic",
        )
        repo._store[vital.id] = vital

    # Blood pressure systolic
    bp_values = [130, 128, 126, 124, 122, 120]
    for i, value in enumerate(bp_values):
        vital = VitalSign(
            id=f"bp-{i}",
            vital_type="blood_pressure_systolic",
            value=float(value),
            unit="mmHg",
            status="normal" if value <= 120 else "abnormal",
            subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
            recorded_at=today - timedelta(days=(len(bp_values) - i - 1) * 30),
        )
        repo._store[vital.id] = vital

    # Weight
    for i, value in enumerate([160, 158, 156]):
        vital = VitalSign(
            id=f"weight-{i}",
            vital_type="weight",
            value=float(value),
            unit="lbs",
            status="normal",
            subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
            recorded_at=today - timedelta(days=(2 - i) * 30),
        )
        repo._store[vital.id] = vital

    # Height
    vital = VitalSign(
        id="height-1",
        vital_type="height",
        value=65.0,
        unit="in",
        status="normal",
        subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
        recorded_at=today - timedelta(days=365),
    )
    repo._store[vital.id] = vital

    return repo


@pytest.mark.integration
class TestGetPatientVitals:
    """Tests for GET /patients/{patient_id}/vitals endpoint."""

    def test_get_vitals_success(self):
        """Test successfully getting patient vitals."""
        # Create test repo and service
        seeded_repo = create_seeded_vitals_repo()
        from services.vitals_service import VitalsService
        mock_service = VitalsService(vitals_repo=seeded_repo)

        # Store original functions
        original_get_vitals_repo = dependencies.get_vitals_repo
        original_get_vitals_service = dependencies.get_vitals_service

        # Override
        dependencies.get_vitals_repo = lambda: seeded_repo
        dependencies.get_vitals_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    response = await client.get("/patients/patient-001/vitals")
                    return response

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            assert "vitals" in data
            assert "bmi" in data
            assert "mostRecentDate" in data
            assert isinstance(data["vitals"], list)
        finally:
            # Restore
            dependencies.get_vitals_repo = original_get_vitals_repo
            dependencies.get_vitals_service = original_get_vitals_service

    def test_get_vitals_includes_trend_by_default(self):
        """Test that trends are included by default."""
        seeded_repo = create_seeded_vitals_repo()
        from services.vitals_service import VitalsService
        mock_service = VitalsService(vitals_repo=seeded_repo)

        original_get_vitals_repo = dependencies.get_vitals_repo
        original_get_vitals_service = dependencies.get_vitals_service

        dependencies.get_vitals_repo = lambda: seeded_repo
        dependencies.get_vitals_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-001/vitals")

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            # Find heart rate vital
            hr_vital = next((v for v in data["vitals"] if v["vitalType"] == "heart_rate"), None)
            assert hr_vital is not None
            assert hr_vital["trend"] is not None
            assert hr_vital["sparklineData"] is not None
        finally:
            dependencies.get_vitals_repo = original_get_vitals_repo
            dependencies.get_vitals_service = original_get_vitals_service

    def test_get_vitals_without_trends(self):
        """Test getting vitals without trends."""
        seeded_repo = create_seeded_vitals_repo()
        from services.vitals_service import VitalsService
        mock_service = VitalsService(vitals_repo=seeded_repo)

        original_get_vitals_repo = dependencies.get_vitals_repo
        original_get_vitals_service = dependencies.get_vitals_service

        dependencies.get_vitals_repo = lambda: seeded_repo
        dependencies.get_vitals_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-001/vitals?include_trends=false")

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            for vital in data["vitals"]:
                assert vital["trend"] is None
                assert vital["sparklineData"] == []
        finally:
            dependencies.get_vitals_repo = original_get_vitals_repo
            dependencies.get_vitals_service = original_get_vitals_service

    def test_get_vitals_patient_not_found(self):
        """Test 404 for unknown patient."""
        seeded_repo = create_seeded_vitals_repo()
        from services.vitals_service import VitalsService
        mock_service = VitalsService(vitals_repo=seeded_repo)

        original_get_vitals_repo = dependencies.get_vitals_repo
        original_get_vitals_service = dependencies.get_vitals_service

        dependencies.get_vitals_repo = lambda: seeded_repo
        dependencies.get_vitals_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-999/vitals")

            response = run_async(do_test())

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
        finally:
            dependencies.get_vitals_repo = original_get_vitals_repo
            dependencies.get_vitals_service = original_get_vitals_service

    def test_get_vitals_includes_bmi(self):
        """Test that BMI is calculated when height and weight exist."""
        seeded_repo = create_seeded_vitals_repo()
        from services.vitals_service import VitalsService
        mock_service = VitalsService(vitals_repo=seeded_repo)

        original_get_vitals_repo = dependencies.get_vitals_repo
        original_get_vitals_service = dependencies.get_vitals_service

        dependencies.get_vitals_repo = lambda: seeded_repo
        dependencies.get_vitals_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-001/vitals")

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            assert data["bmi"] is not None
            assert "value" in data["bmi"]
            assert "category" in data["bmi"]
        finally:
            dependencies.get_vitals_repo = original_get_vitals_repo
            dependencies.get_vitals_service = original_get_vitals_service


@pytest.mark.integration
class TestGetVitalHistory:
    """Tests for GET /patients/{patient_id}/vitals/{vital_type}/history endpoint."""

    def test_get_history_success(self):
        """Test successfully getting vital history."""
        seeded_repo = create_seeded_vitals_repo()
        from services.vitals_service import VitalsService
        mock_service = VitalsService(vitals_repo=seeded_repo)

        original_get_vitals_repo = dependencies.get_vitals_repo
        original_get_vitals_service = dependencies.get_vitals_service

        dependencies.get_vitals_repo = lambda: seeded_repo
        dependencies.get_vitals_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-001/vitals/heart_rate/history")

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            assert "vitalType" in data
            assert "unit" in data
            assert "referenceRange" in data
            assert "history" in data
            assert "trendAnalysis" in data

            assert data["vitalType"] == "heart_rate"
            assert len(data["history"]) > 0
        finally:
            dependencies.get_vitals_repo = original_get_vitals_repo
            dependencies.get_vitals_service = original_get_vitals_service

    def test_get_history_patient_not_found(self):
        """Test 404 for unknown patient."""
        seeded_repo = create_seeded_vitals_repo()
        from services.vitals_service import VitalsService
        mock_service = VitalsService(vitals_repo=seeded_repo)

        original_get_vitals_repo = dependencies.get_vitals_repo
        original_get_vitals_service = dependencies.get_vitals_service

        dependencies.get_vitals_repo = lambda: seeded_repo
        dependencies.get_vitals_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-999/vitals/heart_rate/history")

            response = run_async(do_test())

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
        finally:
            dependencies.get_vitals_repo = original_get_vitals_repo
            dependencies.get_vitals_service = original_get_vitals_service

    def test_get_history_invalid_vital_type(self):
        """Test 400 for invalid vital type."""
        seeded_repo = create_seeded_vitals_repo()
        from services.vitals_service import VitalsService
        mock_service = VitalsService(vitals_repo=seeded_repo)

        original_get_vitals_repo = dependencies.get_vitals_repo
        original_get_vitals_service = dependencies.get_vitals_service

        dependencies.get_vitals_repo = lambda: seeded_repo
        dependencies.get_vitals_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-001/vitals/invalid_type/history")

            response = run_async(do_test())

            assert response.status_code == 400
            assert "Invalid vital type" in response.json()["detail"]
        finally:
            dependencies.get_vitals_repo = original_get_vitals_repo
            dependencies.get_vitals_service = original_get_vitals_service

    def test_get_history_no_data(self):
        """Test 404 when no history exists for vital type."""
        seeded_repo = create_seeded_vitals_repo()
        from services.vitals_service import VitalsService
        mock_service = VitalsService(vitals_repo=seeded_repo)

        original_get_vitals_repo = dependencies.get_vitals_repo
        original_get_vitals_service = dependencies.get_vitals_service

        dependencies.get_vitals_repo = lambda: seeded_repo
        dependencies.get_vitals_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-001/vitals/respiratory_rate/history")

            response = run_async(do_test())

            assert response.status_code == 404
            assert "No vital history found" in response.json()["detail"]
        finally:
            dependencies.get_vitals_repo = original_get_vitals_repo
            dependencies.get_vitals_service = original_get_vitals_service

    def test_get_history_includes_trend_analysis(self):
        """Test that trend analysis is included."""
        seeded_repo = create_seeded_vitals_repo()
        from services.vitals_service import VitalsService
        mock_service = VitalsService(vitals_repo=seeded_repo)

        original_get_vitals_repo = dependencies.get_vitals_repo
        original_get_vitals_service = dependencies.get_vitals_service

        dependencies.get_vitals_repo = lambda: seeded_repo
        dependencies.get_vitals_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-001/vitals/heart_rate/history")

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            assert data["trendAnalysis"] is not None
            assert "direction" in data["trendAnalysis"]
            assert "percentChange" in data["trendAnalysis"]
            assert "clinicalSignificance" in data["trendAnalysis"]
        finally:
            dependencies.get_vitals_repo = original_get_vitals_repo
            dependencies.get_vitals_service = original_get_vitals_service
