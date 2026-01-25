"""Tests for clinical alert service."""

import asyncio
import pytest
from datetime import datetime, timedelta

from resources import (
    ClinicalAlert,
    ClinicalAlertRepository,
    LabResult,
    LabResultRepository,
    VitalSign,
    VitalSignRepository,
    Patient,
    PatientRepository,
    Problem,
)
from resources.core import Reference
from services.clinical_alert_service import (
    ClinicalAlertService,
    ClinicalAlertServiceBuilder,
    AlertsResponse,
)
from services.alert_generators import (
    LabAlertGenerator,
    VitalAlertGenerator,
)
from services.alert_thresholds import get_lab_severity, get_vital_severity


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.fixture
def alert_repo():
    """Create a fresh alert repository."""
    return ClinicalAlertRepository()


@pytest.fixture
def lab_repo():
    """Create a fresh lab repository without seeding."""
    repo = LabResultRepository()
    repo._store.clear()  # Clear seeded data
    return repo


@pytest.fixture
def vitals_repo():
    """Create a fresh vitals repository without seeding."""
    repo = VitalSignRepository()
    repo._store.clear()  # Clear seeded data
    return repo


@pytest.fixture
def patient_repo():
    """Create a fresh patient repository."""
    repo = PatientRepository()
    repo._store.clear()
    return repo


@pytest.fixture
def service(alert_repo, lab_repo, vitals_repo, patient_repo):
    """Create a clinical alert service with all generators."""
    return ClinicalAlertServiceBuilder.build(
        alert_repo=alert_repo,
        lab_result_repo=lab_repo,
        vitals_repo=vitals_repo,
        patient_repo=patient_repo,
    )


@pytest.mark.unit
class TestGetLabSeverity:
    """Tests for lab severity threshold checking."""

    def test_critical_high_potassium(self):
        """Test critical high potassium detection."""
        assert get_lab_severity("Potassium", 6.5) == "critical"

    def test_critical_low_potassium(self):
        """Test critical low potassium detection."""
        assert get_lab_severity("Potassium", 2.0) == "critical"

    def test_high_potassium(self):
        """Test high potassium detection."""
        assert get_lab_severity("Potassium", 5.6) == "high"

    def test_normal_potassium(self):
        """Test normal potassium returns None."""
        assert get_lab_severity("Potassium", 4.0) is None

    def test_critical_troponin(self):
        """Test any troponin elevation is critical."""
        assert get_lab_severity("Troponin I", 0.05) == "critical"

    def test_unknown_test(self):
        """Test unknown test returns None."""
        assert get_lab_severity("Unknown Test", 100) is None


@pytest.mark.unit
class TestGetVitalSeverity:
    """Tests for vital severity threshold checking."""

    def test_critical_high_bp(self):
        """Test critical high blood pressure."""
        assert get_vital_severity("blood_pressure_systolic", 185) == "critical"

    def test_critical_low_bp(self):
        """Test critical low blood pressure."""
        assert get_vital_severity("blood_pressure_systolic", 75) == "critical"

    def test_normal_bp(self):
        """Test normal blood pressure returns None."""
        assert get_vital_severity("blood_pressure_systolic", 120) is None

    def test_critical_low_o2(self):
        """Test critical low O2 saturation."""
        assert get_vital_severity("oxygen_saturation", 88) == "critical"

    def test_normal_o2(self):
        """Test normal O2 returns None."""
        assert get_vital_severity("oxygen_saturation", 98) is None


@pytest.mark.unit
class TestLabAlertGenerator:
    """Tests for lab alert generator."""

    def test_generates_critical_lab_alert(self, lab_repo):
        """Test generating alert for critical lab value."""
        # Add critical potassium result
        lab_result = LabResult(
            id="potassium-1",
            test_name="Potassium",
            test_code="2823-3",
            value="6.2",
            unit="mEq/L",
            reference_range="3.5-5.0",
            status="critical",
            subject=Reference.to("Patient", "patient-001", "Test Patient"),
            collection_date=datetime.now() - timedelta(hours=2),
        )
        lab_repo._store[lab_result.id] = lab_result

        generator = LabAlertGenerator(lab_repo)
        alerts = run_async(generator.generate_alerts("patient-001"))

        assert len(alerts) == 1
        assert alerts[0].alert_type == "critical_lab"
        assert alerts[0].severity == "critical"
        assert "Potassium" in alerts[0].title

    def test_generates_high_severity_alert(self, lab_repo):
        """Test generating alert for high but not critical lab value."""
        # Add high glucose result
        lab_result = LabResult(
            id="glucose-1",
            test_name="Glucose",
            test_code="2339-0",
            value="250",
            unit="mg/dL",
            reference_range="70-100",
            status="abnormal",
            subject=Reference.to("Patient", "patient-001", "Test Patient"),
            collection_date=datetime.now() - timedelta(hours=1),
        )
        lab_repo._store[lab_result.id] = lab_result

        generator = LabAlertGenerator(lab_repo)
        alerts = run_async(generator.generate_alerts("patient-001"))

        assert len(alerts) == 1
        assert alerts[0].severity == "high"

    def test_skips_pending_results(self, lab_repo):
        """Test that pending results don't generate alerts."""
        lab_result = LabResult(
            id="potassium-1",
            test_name="Potassium",
            value="",
            unit="mEq/L",
            status="pending",
            subject=Reference.to("Patient", "patient-001", "Test Patient"),
            collection_date=datetime.now(),
        )
        lab_repo._store[lab_result.id] = lab_result

        generator = LabAlertGenerator(lab_repo)
        alerts = run_async(generator.generate_alerts("patient-001"))

        assert len(alerts) == 0

    def test_includes_recommended_actions(self, lab_repo):
        """Test that alerts include recommended actions."""
        lab_result = LabResult(
            id="potassium-1",
            test_name="Potassium",
            value="6.2",
            unit="mEq/L",
            status="critical",
            subject=Reference.to("Patient", "patient-001", "Test Patient"),
            collection_date=datetime.now(),
        )
        lab_repo._store[lab_result.id] = lab_result

        generator = LabAlertGenerator(lab_repo)
        alerts = run_async(generator.generate_alerts("patient-001"))

        assert len(alerts[0].recommended_actions) > 0
        assert any("potassium" in action.lower() for action in alerts[0].recommended_actions)


@pytest.mark.unit
class TestVitalAlertGenerator:
    """Tests for vital alert generator."""

    def test_generates_critical_bp_alert(self, vitals_repo):
        """Test generating alert for critical blood pressure."""
        vital = VitalSign(
            id="bp-1",
            vital_type="blood_pressure_systolic",
            value=185.0,
            unit="mmHg",
            status="critical",
            subject=Reference.to("Patient", "patient-001", "Test Patient"),
            recorded_at=datetime.now() - timedelta(hours=1),
        )
        vitals_repo._store[vital.id] = vital

        generator = VitalAlertGenerator(vitals_repo)
        alerts = run_async(generator.generate_alerts("patient-001"))

        assert len(alerts) == 1
        assert alerts[0].alert_type == "critical_vital"
        assert alerts[0].severity == "critical"
        assert "Hypertensive" in alerts[0].title

    def test_generates_hypoxemia_alert(self, vitals_repo):
        """Test generating alert for low oxygen saturation."""
        vital = VitalSign(
            id="o2-1",
            vital_type="oxygen_saturation",
            value=88.0,
            unit="%",
            status="critical",
            subject=Reference.to("Patient", "patient-001", "Test Patient"),
            recorded_at=datetime.now() - timedelta(minutes=30),
        )
        vitals_repo._store[vital.id] = vital

        generator = VitalAlertGenerator(vitals_repo)
        alerts = run_async(generator.generate_alerts("patient-001"))

        assert len(alerts) == 1
        assert "Hypoxemia" in alerts[0].title

    def test_ignores_old_vitals(self, vitals_repo):
        """Test that vitals older than 24h don't generate alerts."""
        vital = VitalSign(
            id="bp-1",
            vital_type="blood_pressure_systolic",
            value=185.0,
            unit="mmHg",
            status="critical",
            subject=Reference.to("Patient", "patient-001", "Test Patient"),
            recorded_at=datetime.now() - timedelta(hours=48),
        )
        vitals_repo._store[vital.id] = vital

        generator = VitalAlertGenerator(vitals_repo)
        alerts = run_async(generator.generate_alerts("patient-001"))

        assert len(alerts) == 0


@pytest.mark.unit
class TestClinicalAlertService:
    """Tests for the clinical alert service."""

    def test_get_patient_alerts_generates_alerts(self, service, lab_repo):
        """Test that get_patient_alerts triggers alert generation."""
        lab_result = LabResult(
            id="potassium-1",
            test_name="Potassium",
            value="6.2",
            unit="mEq/L",
            status="critical",
            subject=Reference.to("Patient", "patient-001", "Test Patient"),
            collection_date=datetime.now(),
        )
        lab_repo._store[lab_result.id] = lab_result

        response = run_async(service.get_patient_alerts("patient-001"))

        assert len(response.alerts) == 1
        assert response.summary.critical_count == 1

    def test_get_patient_alerts_filters_by_status(self, service, alert_repo):
        """Test filtering alerts by status."""
        # Add alerts directly to repo
        active_alert = ClinicalAlert(
            id="alert-1",
            patient_id="patient-001",
            alert_type="critical_lab",
            severity="critical",
            status="active",
            title="Active Alert",
            description="An active alert",
            source="Test",
            source_id="test-1",
        )
        acknowledged_alert = ClinicalAlert(
            id="alert-2",
            patient_id="patient-001",
            alert_type="critical_lab",
            severity="high",
            status="acknowledged",
            title="Acknowledged Alert",
            description="An acknowledged alert",
            source="Test",
            source_id="test-2",
        )
        alert_repo._store[active_alert.id] = active_alert
        alert_repo._store[acknowledged_alert.id] = acknowledged_alert

        # Get only active
        response = run_async(service.get_patient_alerts(
            "patient-001",
            status="active",
            regenerate=False,
        ))
        assert len(response.alerts) == 1
        assert response.alerts[0].status == "active"

        # Get all
        response = run_async(service.get_patient_alerts(
            "patient-001",
            status=["active", "acknowledged"],
            regenerate=False,
        ))
        assert len(response.alerts) == 2

    def test_acknowledge_alert(self, service, alert_repo):
        """Test acknowledging an alert."""
        alert = ClinicalAlert(
            id="alert-1",
            patient_id="patient-001",
            alert_type="critical_lab",
            severity="critical",
            status="active",
            title="Test Alert",
            description="A test alert",
            source="Test",
            source_id="test-1",
        )
        alert_repo._store[alert.id] = alert

        result = run_async(service.acknowledge_alert(
            "patient-001",
            "alert-1",
            by="dr-smith",
            note="Reviewed and addressed",
        ))

        assert result is not None
        assert result.status == "acknowledged"
        assert result.acknowledgment.acknowledged_by == "dr-smith"
        assert result.acknowledgment.note == "Reviewed and addressed"

    def test_acknowledge_wrong_patient(self, service, alert_repo):
        """Test acknowledging alert for wrong patient returns None."""
        alert = ClinicalAlert(
            id="alert-1",
            patient_id="patient-001",
            alert_type="critical_lab",
            severity="critical",
            status="active",
            title="Test Alert",
            description="A test alert",
            source="Test",
            source_id="test-1",
        )
        alert_repo._store[alert.id] = alert

        result = run_async(service.acknowledge_alert(
            "patient-002",  # Wrong patient
            "alert-1",
            by="dr-smith",
        ))

        assert result is None

    def test_dismiss_alert(self, service, alert_repo):
        """Test dismissing an alert."""
        alert = ClinicalAlert(
            id="alert-1",
            patient_id="patient-001",
            alert_type="critical_lab",
            severity="critical",
            status="active",
            title="Test Alert",
            description="A test alert",
            source="Test",
            source_id="test-1",
        )
        alert_repo._store[alert.id] = alert

        result = run_async(service.dismiss_alert(
            "patient-001",
            "alert-1",
            by="dr-smith",
            reason="False positive - hemolyzed sample",
        ))

        assert result is not None
        assert result.status == "dismissed"
        assert result.dismissed_by == "dr-smith"
        assert result.dismissed_reason == "False positive - hemolyzed sample"

    def test_get_alert_summary(self, service, alert_repo):
        """Test getting alert summary."""
        alerts = [
            ClinicalAlert(
                id="alert-1",
                patient_id="patient-001",
                alert_type="critical_lab",
                severity="critical",
                status="active",
                title="Critical",
                description="Critical alert",
                source="Test",
                source_id="test-1",
            ),
            ClinicalAlert(
                id="alert-2",
                patient_id="patient-001",
                alert_type="critical_vital",
                severity="high",
                status="active",
                title="High",
                description="High alert",
                source="Test",
                source_id="test-2",
            ),
            ClinicalAlert(
                id="alert-3",
                patient_id="patient-001",
                alert_type="overdue_screening",
                severity="medium",
                status="active",
                title="Medium",
                description="Medium alert",
                source="Test",
                source_id="test-3",
            ),
        ]
        for alert in alerts:
            alert_repo._store[alert.id] = alert

        # Disable regeneration to use seeded alerts
        response = run_async(service.get_patient_alerts(
            "patient-001",
            regenerate=False,
        ))

        assert response.summary.critical_count == 1
        assert response.summary.high_count == 1
        assert response.summary.medium_count == 1
        assert response.summary.total_active == 3


@pytest.mark.unit
class TestAlertsResponse:
    """Tests for AlertsResponse."""

    def test_to_dict(self, alert_repo):
        """Test serialization of AlertsResponse."""
        from resources import AlertSummary

        alerts = [
            ClinicalAlert(
                id="alert-1",
                patient_id="patient-001",
                alert_type="critical_lab",
                severity="critical",
                status="active",
                title="Test Alert",
                description="A test alert",
                source="Test",
                source_id="test-1",
            )
        ]
        summary = AlertSummary(critical_count=1, high_count=0, medium_count=0)

        response = AlertsResponse(alerts=alerts, summary=summary)
        result = response.to_dict()

        assert "alerts" in result
        assert "summary" in result
        assert len(result["alerts"]) == 1
        assert result["summary"]["criticalCount"] == 1


@pytest.mark.unit
class TestServiceBuilder:
    """Tests for ClinicalAlertServiceBuilder."""

    def test_builds_with_all_repos(self, alert_repo, lab_repo, vitals_repo, patient_repo):
        """Test building service with all repositories."""
        service = ClinicalAlertServiceBuilder.build(
            alert_repo=alert_repo,
            lab_result_repo=lab_repo,
            vitals_repo=vitals_repo,
            patient_repo=patient_repo,
        )

        assert len(service.generators) == 4  # Lab, Vital, Screening, ChronicDisease

    def test_builds_with_minimal_repos(self, alert_repo, lab_repo):
        """Test building service with minimal repositories."""
        service = ClinicalAlertServiceBuilder.build(
            alert_repo=alert_repo,
            lab_result_repo=lab_repo,
        )

        assert len(service.generators) == 1  # Just Lab

    def test_builds_with_no_repos(self, alert_repo):
        """Test building service with no additional repositories."""
        service = ClinicalAlertServiceBuilder.build(alert_repo=alert_repo)

        assert len(service.generators) == 0
