"""Tests for clinical alerts BFF endpoints."""

import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timedelta

from main import app
from bff import dependencies
from resources import (
    ClinicalAlert,
    ClinicalAlertRepository,
    LabResult,
    LabResultRepository,
)
from resources.core import Reference
from services.clinical_alert_service import ClinicalAlertService, ClinicalAlertServiceBuilder


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Ensure data is seeded before running tests
dependencies.ensure_data_seeded()


def create_seeded_alert_repo():
    """Create an alert repository with sample data."""
    repo = ClinicalAlertRepository()
    now = datetime.now()

    alerts = [
        ClinicalAlert(
            id="alert-1",
            patient_id="patient-001",
            alert_type="critical_lab",
            severity="critical",
            status="active",
            title="Critical Potassium",
            description="Potassium level 6.2 mEq/L is critically high",
            generated_at=now - timedelta(hours=2),
            source="Lab Result",
            source_id="potassium-5",
            recommended_actions=["Repeat stat potassium", "Consider kayexalate"],
        ),
        ClinicalAlert(
            id="alert-2",
            patient_id="patient-001",
            alert_type="critical_vital",
            severity="high",
            status="active",
            title="Hypertensive Urgency",
            description="Blood pressure 185/120 mmHg",
            generated_at=now - timedelta(hours=1),
            source="Vital Signs",
            source_id="vital-10",
            recommended_actions=["Assess for symptoms"],
        ),
        ClinicalAlert(
            id="alert-3",
            patient_id="patient-001",
            alert_type="overdue_screening",
            severity="medium",
            status="acknowledged",
            title="Overdue Colonoscopy",
            description="Patient is 62 years old with no colonoscopy",
            generated_at=now - timedelta(days=1),
            source="Preventive Care",
            source_id="screening-colon",
        ),
    ]

    for alert in alerts:
        repo._store[alert.id] = alert

    return repo


def create_mock_service(alert_repo):
    """Create a mock service with the given alert repo."""
    # Create minimal repos for the service
    lab_repo = LabResultRepository()
    lab_repo._store.clear()

    return ClinicalAlertService(
        alert_repo=alert_repo,
        generators=[],  # No generators for testing - use seeded data
    )


@pytest.mark.integration
class TestGetPatientAlerts:
    """Tests for GET /patients/{patient_id}/alerts endpoint."""

    def test_get_alerts_success(self):
        """Test successfully getting patient alerts."""
        alert_repo = create_seeded_alert_repo()
        mock_service = create_mock_service(alert_repo)

        original_get_repo = dependencies.get_clinical_alert_repo
        original_get_service = dependencies.get_clinical_alert_service

        dependencies.get_clinical_alert_repo = lambda: alert_repo
        dependencies.get_clinical_alert_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-001/alerts")

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            assert "alerts" in data
            assert "summary" in data
            assert isinstance(data["alerts"], list)
        finally:
            dependencies.get_clinical_alert_repo = original_get_repo
            dependencies.get_clinical_alert_service = original_get_service

    def test_get_alerts_filters_by_status(self):
        """Test that alerts are filtered by status."""
        alert_repo = create_seeded_alert_repo()
        mock_service = create_mock_service(alert_repo)

        original_get_repo = dependencies.get_clinical_alert_repo
        original_get_service = dependencies.get_clinical_alert_service

        dependencies.get_clinical_alert_repo = lambda: alert_repo
        dependencies.get_clinical_alert_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-001/alerts?status=active")

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            # Should only have active alerts
            assert len(data["alerts"]) == 2
            for alert in data["alerts"]:
                assert alert["status"] == "active"
        finally:
            dependencies.get_clinical_alert_repo = original_get_repo
            dependencies.get_clinical_alert_service = original_get_service

    def test_get_alerts_all_statuses(self):
        """Test getting alerts with all statuses."""
        alert_repo = create_seeded_alert_repo()
        mock_service = create_mock_service(alert_repo)

        original_get_repo = dependencies.get_clinical_alert_repo
        original_get_service = dependencies.get_clinical_alert_service

        dependencies.get_clinical_alert_repo = lambda: alert_repo
        dependencies.get_clinical_alert_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-001/alerts?status=all")

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            # Should have all 3 alerts
            assert len(data["alerts"]) == 3
        finally:
            dependencies.get_clinical_alert_repo = original_get_repo
            dependencies.get_clinical_alert_service = original_get_service

    def test_get_alerts_patient_not_found(self):
        """Test 404 for unknown patient."""
        alert_repo = create_seeded_alert_repo()
        mock_service = create_mock_service(alert_repo)

        original_get_repo = dependencies.get_clinical_alert_repo
        original_get_service = dependencies.get_clinical_alert_service

        dependencies.get_clinical_alert_repo = lambda: alert_repo
        dependencies.get_clinical_alert_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-999/alerts")

            response = run_async(do_test())

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
        finally:
            dependencies.get_clinical_alert_repo = original_get_repo
            dependencies.get_clinical_alert_service = original_get_service

    def test_get_alerts_invalid_status(self):
        """Test 400 for invalid status filter."""
        alert_repo = create_seeded_alert_repo()
        mock_service = create_mock_service(alert_repo)

        original_get_repo = dependencies.get_clinical_alert_repo
        original_get_service = dependencies.get_clinical_alert_service

        dependencies.get_clinical_alert_repo = lambda: alert_repo
        dependencies.get_clinical_alert_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-001/alerts?status=invalid")

            response = run_async(do_test())

            assert response.status_code == 400
            assert "Invalid status" in response.json()["detail"]
        finally:
            dependencies.get_clinical_alert_repo = original_get_repo
            dependencies.get_clinical_alert_service = original_get_service

    def test_get_alerts_includes_summary(self):
        """Test that summary counts are included."""
        alert_repo = create_seeded_alert_repo()
        mock_service = create_mock_service(alert_repo)

        original_get_repo = dependencies.get_clinical_alert_repo
        original_get_service = dependencies.get_clinical_alert_service

        dependencies.get_clinical_alert_repo = lambda: alert_repo
        dependencies.get_clinical_alert_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-001/alerts")

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            assert "summary" in data
            assert "criticalCount" in data["summary"]
            assert "highCount" in data["summary"]
            assert "mediumCount" in data["summary"]
            assert "totalActive" in data["summary"]

            # Only counting active alerts
            assert data["summary"]["criticalCount"] == 1
            assert data["summary"]["highCount"] == 1
            assert data["summary"]["mediumCount"] == 0  # The medium one is acknowledged
        finally:
            dependencies.get_clinical_alert_repo = original_get_repo
            dependencies.get_clinical_alert_service = original_get_service


@pytest.mark.integration
class TestGetAlertSummary:
    """Tests for GET /patients/{patient_id}/alerts/summary endpoint."""

    def test_get_summary_success(self):
        """Test successfully getting alert summary."""
        alert_repo = create_seeded_alert_repo()
        mock_service = create_mock_service(alert_repo)

        original_get_repo = dependencies.get_clinical_alert_repo
        original_get_service = dependencies.get_clinical_alert_service

        dependencies.get_clinical_alert_repo = lambda: alert_repo
        dependencies.get_clinical_alert_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-001/alerts/summary")

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            assert "criticalCount" in data
            assert "highCount" in data
            assert "mediumCount" in data
            assert "totalActive" in data
        finally:
            dependencies.get_clinical_alert_repo = original_get_repo
            dependencies.get_clinical_alert_service = original_get_service

    def test_get_summary_patient_not_found(self):
        """Test 404 for unknown patient."""
        alert_repo = create_seeded_alert_repo()
        mock_service = create_mock_service(alert_repo)

        original_get_repo = dependencies.get_clinical_alert_repo
        original_get_service = dependencies.get_clinical_alert_service

        dependencies.get_clinical_alert_repo = lambda: alert_repo
        dependencies.get_clinical_alert_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.get("/patients/patient-999/alerts/summary")

            response = run_async(do_test())

            assert response.status_code == 404
        finally:
            dependencies.get_clinical_alert_repo = original_get_repo
            dependencies.get_clinical_alert_service = original_get_service


@pytest.mark.integration
class TestAcknowledgeAlert:
    """Tests for POST /patients/{patient_id}/alerts/{alert_id}/acknowledge endpoint."""

    def test_acknowledge_success(self):
        """Test successfully acknowledging an alert."""
        alert_repo = create_seeded_alert_repo()
        mock_service = create_mock_service(alert_repo)

        original_get_repo = dependencies.get_clinical_alert_repo
        original_get_service = dependencies.get_clinical_alert_service

        dependencies.get_clinical_alert_repo = lambda: alert_repo
        dependencies.get_clinical_alert_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.post(
                        "/patients/patient-001/alerts/alert-1/acknowledge",
                        json={"by": "dr-smith", "note": "Reviewed and addressed"}
                    )

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "acknowledged"
            assert data["acknowledgment"]["acknowledgedBy"] == "dr-smith"
            assert data["acknowledgment"]["note"] == "Reviewed and addressed"
        finally:
            dependencies.get_clinical_alert_repo = original_get_repo
            dependencies.get_clinical_alert_service = original_get_service

    def test_acknowledge_alert_not_found(self):
        """Test 404 for unknown alert."""
        alert_repo = create_seeded_alert_repo()
        mock_service = create_mock_service(alert_repo)

        original_get_repo = dependencies.get_clinical_alert_repo
        original_get_service = dependencies.get_clinical_alert_service

        dependencies.get_clinical_alert_repo = lambda: alert_repo
        dependencies.get_clinical_alert_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.post(
                        "/patients/patient-001/alerts/alert-999/acknowledge",
                        json={"by": "dr-smith"}
                    )

            response = run_async(do_test())

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
        finally:
            dependencies.get_clinical_alert_repo = original_get_repo
            dependencies.get_clinical_alert_service = original_get_service

    def test_acknowledge_patient_not_found(self):
        """Test 404 for unknown patient."""
        alert_repo = create_seeded_alert_repo()
        mock_service = create_mock_service(alert_repo)

        original_get_repo = dependencies.get_clinical_alert_repo
        original_get_service = dependencies.get_clinical_alert_service

        dependencies.get_clinical_alert_repo = lambda: alert_repo
        dependencies.get_clinical_alert_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.post(
                        "/patients/patient-999/alerts/alert-1/acknowledge",
                        json={"by": "dr-smith"}
                    )

            response = run_async(do_test())

            assert response.status_code == 404
        finally:
            dependencies.get_clinical_alert_repo = original_get_repo
            dependencies.get_clinical_alert_service = original_get_service


@pytest.mark.integration
class TestDismissAlert:
    """Tests for POST /patients/{patient_id}/alerts/{alert_id}/dismiss endpoint."""

    def test_dismiss_success(self):
        """Test successfully dismissing an alert."""
        alert_repo = create_seeded_alert_repo()
        mock_service = create_mock_service(alert_repo)

        original_get_repo = dependencies.get_clinical_alert_repo
        original_get_service = dependencies.get_clinical_alert_service

        dependencies.get_clinical_alert_repo = lambda: alert_repo
        dependencies.get_clinical_alert_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.post(
                        "/patients/patient-001/alerts/alert-1/dismiss",
                        json={"by": "dr-smith", "reason": "False positive - hemolyzed sample"}
                    )

            response = run_async(do_test())

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "dismissed"
            assert data["dismissedBy"] == "dr-smith"
            assert data["dismissedReason"] == "False positive - hemolyzed sample"
        finally:
            dependencies.get_clinical_alert_repo = original_get_repo
            dependencies.get_clinical_alert_service = original_get_service

    def test_dismiss_alert_not_found(self):
        """Test 404 for unknown alert."""
        alert_repo = create_seeded_alert_repo()
        mock_service = create_mock_service(alert_repo)

        original_get_repo = dependencies.get_clinical_alert_repo
        original_get_service = dependencies.get_clinical_alert_service

        dependencies.get_clinical_alert_repo = lambda: alert_repo
        dependencies.get_clinical_alert_service = lambda: mock_service

        try:
            async def do_test():
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://test"
                ) as client:
                    return await client.post(
                        "/patients/patient-001/alerts/alert-999/dismiss",
                        json={"by": "dr-smith", "reason": "Not relevant"}
                    )

            response = run_async(do_test())

            assert response.status_code == 404
        finally:
            dependencies.get_clinical_alert_repo = original_get_repo
            dependencies.get_clinical_alert_service = original_get_service
