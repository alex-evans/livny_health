"""Tests for clinical alert repository."""

import asyncio
import pytest
from datetime import datetime, timedelta

from resources.clinical_alert.model import ClinicalAlert, AlertSummary
from resources.clinical_alert.repository import ClinicalAlertRepository


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
    return ClinicalAlertRepository()


@pytest.fixture
def sample_alerts():
    """Create sample alerts for testing."""
    now = datetime.now()
    patient_id = "patient-001"

    alerts = [
        ClinicalAlert(
            id="alert-1",
            patient_id=patient_id,
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
            patient_id=patient_id,
            alert_type="critical_vital",
            severity="high",
            status="active",
            title="Hypertensive Urgency",
            description="Blood pressure 185/120 mmHg",
            generated_at=now - timedelta(hours=1),
            source="Vital Signs",
            source_id="vital-10",
            recommended_actions=["Assess for symptoms", "Consider oral antihypertensive"],
        ),
        ClinicalAlert(
            id="alert-3",
            patient_id=patient_id,
            alert_type="overdue_screening",
            severity="medium",
            status="active",
            title="Overdue Colonoscopy",
            description="Patient is 62 years old and has no documented colonoscopy",
            generated_at=now - timedelta(days=1),
            source="Preventive Care",
            source_id="screening-colon",
            recommended_actions=["Discuss colonoscopy screening"],
        ),
        ClinicalAlert(
            id="alert-4",
            patient_id=patient_id,
            alert_type="critical_lab",
            severity="critical",
            status="acknowledged",
            title="Critical Troponin",
            description="Troponin I 0.85 ng/mL is elevated",
            generated_at=now - timedelta(hours=4),
            source="Lab Result",
            source_id="troponin-1",
        ),
        # Different patient
        ClinicalAlert(
            id="alert-5",
            patient_id="patient-002",
            alert_type="drug_interaction",
            severity="high",
            status="active",
            title="Drug Interaction",
            description="Warfarin and aspirin interaction",
            generated_at=now,
            source="Medication",
            source_id="med-interaction-1",
        ),
    ]

    return alerts


@pytest.mark.unit
class TestClinicalAlertRepository:
    """Tests for ClinicalAlertRepository."""

    def test_create_and_get(self, repo):
        """Test creating and retrieving an alert."""
        alert = ClinicalAlert(
            id="alert-1",
            patient_id="patient-001",
            alert_type="critical_lab",
            severity="critical",
            status="active",
            title="Critical Potassium",
            description="Potassium level is critically high",
            source="Lab Result",
            source_id="potassium-5",
        )

        run_async(repo.create(alert))
        retrieved = run_async(repo.get("alert-1"))

        assert retrieved is not None
        assert retrieved.id == "alert-1"
        assert retrieved.severity == "critical"
        assert retrieved.status == "active"

    def test_list_by_patient_id(self, repo, sample_alerts):
        """Test filtering by patient ID."""
        for alert in sample_alerts:
            repo._store[alert.id] = alert

        results = run_async(repo.list(patient_id="patient-001"))

        assert len(results) == 4  # All except patient-002's alert
        for r in results:
            assert r.patient_id == "patient-001"

    def test_list_by_status(self, repo, sample_alerts):
        """Test filtering by status."""
        for alert in sample_alerts:
            repo._store[alert.id] = alert

        results = run_async(repo.list(status="active"))

        assert len(results) == 4  # 3 patient-001 active + 1 patient-002 active
        for r in results:
            assert r.status == "active"

    def test_list_by_severity(self, repo, sample_alerts):
        """Test filtering by severity."""
        for alert in sample_alerts:
            repo._store[alert.id] = alert

        results = run_async(repo.list(severity="critical"))

        assert len(results) == 2
        for r in results:
            assert r.severity == "critical"

    def test_list_by_alert_type(self, repo, sample_alerts):
        """Test filtering by alert type."""
        for alert in sample_alerts:
            repo._store[alert.id] = alert

        results = run_async(repo.list(alert_type="critical_lab"))

        assert len(results) == 2
        for r in results:
            assert r.alert_type == "critical_lab"

    def test_list_combined_filters(self, repo, sample_alerts):
        """Test combining multiple filters."""
        for alert in sample_alerts:
            repo._store[alert.id] = alert

        results = run_async(repo.list(
            patient_id="patient-001",
            status="active",
            severity="critical",
        ))

        assert len(results) == 1
        assert results[0].id == "alert-1"

    def test_get_by_patient(self, repo, sample_alerts):
        """Test getting alerts for a patient."""
        for alert in sample_alerts:
            repo._store[alert.id] = alert

        results = run_async(repo.get_by_patient("patient-001"))

        assert len(results) == 4
        # Should be sorted by severity (critical first) then by date
        assert results[0].severity == "critical"

    def test_get_by_patient_with_status_filter(self, repo, sample_alerts):
        """Test getting active alerts for a patient."""
        for alert in sample_alerts:
            repo._store[alert.id] = alert

        results = run_async(repo.get_by_patient("patient-001", status="active"))

        assert len(results) == 3  # Excludes acknowledged alert
        for r in results:
            assert r.status == "active"

    def test_acknowledge(self, repo, sample_alerts):
        """Test acknowledging an alert."""
        for alert in sample_alerts:
            repo._store[alert.id] = alert

        result = run_async(repo.acknowledge("alert-1", by="dr-smith", note="Reviewed"))

        assert result is not None
        assert result.status == "acknowledged"
        assert result.acknowledgment is not None
        assert result.acknowledgment.acknowledged_by == "dr-smith"
        assert result.acknowledgment.note == "Reviewed"

    def test_acknowledge_nonexistent(self, repo):
        """Test acknowledging a nonexistent alert."""
        result = run_async(repo.acknowledge("alert-999", by="dr-smith"))

        assert result is None

    def test_dismiss(self, repo, sample_alerts):
        """Test dismissing an alert."""
        for alert in sample_alerts:
            repo._store[alert.id] = alert

        result = run_async(repo.dismiss(
            "alert-1",
            by="dr-smith",
            reason="False positive - hemolyzed sample",
        ))

        assert result is not None
        assert result.status == "dismissed"
        assert result.dismissed_by == "dr-smith"
        assert result.dismissed_reason == "False positive - hemolyzed sample"
        assert result.dismissed_at is not None

    def test_dismiss_nonexistent(self, repo):
        """Test dismissing a nonexistent alert."""
        result = run_async(repo.dismiss("alert-999", by="dr-smith"))

        assert result is None

    def test_get_alert_summary(self, repo, sample_alerts):
        """Test getting alert summary counts."""
        for alert in sample_alerts:
            repo._store[alert.id] = alert

        summary = run_async(repo.get_alert_summary("patient-001"))

        assert summary.critical_count == 1  # Only 1 active critical
        assert summary.high_count == 1
        assert summary.medium_count == 1
        assert summary.total_active == 3

    def test_get_alert_summary_empty(self, repo):
        """Test summary for patient with no alerts."""
        summary = run_async(repo.get_alert_summary("patient-999"))

        assert summary.critical_count == 0
        assert summary.high_count == 0
        assert summary.medium_count == 0
        assert summary.total_active == 0

    def test_upsert_alert_new(self, repo):
        """Test upserting a new alert."""
        alert = ClinicalAlert(
            id="alert-new",
            patient_id="patient-001",
            alert_type="critical_lab",
            severity="critical",
            status="active",
            title="New Alert",
            description="A new alert",
            source="Lab Result",
            source_id="lab-123",
        )

        result = run_async(repo.upsert_alert(alert))

        assert result.id == "alert-new"
        retrieved = run_async(repo.get("alert-new"))
        assert retrieved is not None

    def test_upsert_alert_existing_active(self, repo, sample_alerts):
        """Test upserting updates existing active alert."""
        for alert in sample_alerts:
            repo._store[alert.id] = alert

        # Create an alert with same source_id
        updated_alert = ClinicalAlert(
            id="alert-new-id",
            patient_id="patient-001",
            alert_type="critical_lab",
            severity="critical",
            status="active",
            title="Updated Title",
            description="Updated description",
            source="Lab Result",
            source_id="potassium-5",  # Same as alert-1
        )

        result = run_async(repo.upsert_alert(updated_alert))

        # Should update existing alert
        assert result.id == "alert-1"
        assert result.title == "Updated Title"

    def test_upsert_alert_existing_acknowledged(self, repo, sample_alerts):
        """Test upserting preserves acknowledged alert."""
        for alert in sample_alerts:
            repo._store[alert.id] = alert

        # Try to upsert an alert matching an acknowledged one
        new_alert = ClinicalAlert(
            id="alert-new-id",
            patient_id="patient-001",
            alert_type="critical_lab",
            severity="critical",
            status="active",
            title="New Alert",
            description="A new alert",
            source="Lab Result",
            source_id="troponin-1",  # Same as acknowledged alert-4
        )

        result = run_async(repo.upsert_alert(new_alert))

        # Should return existing acknowledged alert unchanged
        assert result.id == "alert-4"
        assert result.status == "acknowledged"

    def test_clear_patient_alerts(self, repo, sample_alerts):
        """Test clearing active alerts for a patient."""
        for alert in sample_alerts:
            repo._store[alert.id] = alert

        count = run_async(repo.clear_patient_alerts("patient-001"))

        assert count == 3  # Only active alerts cleared

        # Acknowledged alert should remain
        remaining = run_async(repo.get_by_patient("patient-001"))
        assert len(remaining) == 1
        assert remaining[0].status == "acknowledged"

    def test_delete(self, repo, sample_alerts):
        """Test deleting an alert."""
        for alert in sample_alerts:
            repo._store[alert.id] = alert

        result = run_async(repo.delete("alert-1"))
        assert result is True

        alert = run_async(repo.get("alert-1"))
        assert alert is None

    def test_delete_nonexistent(self, repo):
        """Test deleting a nonexistent alert."""
        result = run_async(repo.delete("alert-999"))
        assert result is False


@pytest.mark.unit
class TestAlertSummary:
    """Tests for AlertSummary model."""

    def test_total_active(self):
        """Test total_active calculation."""
        summary = AlertSummary(critical_count=2, high_count=3, medium_count=5)

        assert summary.total_active == 10

    def test_to_dict(self):
        """Test serialization."""
        summary = AlertSummary(critical_count=1, high_count=2, medium_count=3)

        result = summary.to_dict()

        assert result["criticalCount"] == 1
        assert result["highCount"] == 2
        assert result["mediumCount"] == 3
        assert result["totalActive"] == 6
