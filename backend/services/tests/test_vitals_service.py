"""Tests for vitals service."""

import asyncio
import pytest
from datetime import datetime, timedelta

from resources.vitals import VitalSign, VitalSignRepository
from resources.core import Reference
from services.vitals_service import VitalsService


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
def service(repo):
    """Create a vitals service with the repository."""
    return VitalsService(vitals_repo=repo)


@pytest.fixture
def seeded_repo():
    """Create a repository with sample data."""
    repo = VitalSignRepository()
    today = datetime.now()
    patient_id = "patient-001"

    # Add heart rate history (showing decreasing trend - good)
    # Need >5% change between first two readings (most recent)
    hr_values = [95, 90, 85, 80, 75, 70]  # Oldest to newest, ~7% decrease between 75 and 70
    for i, value in enumerate(hr_values):
        vital = VitalSign(
            id=f"hr-{i}",
            vital_type="heart_rate",
            value=float(value),
            unit="bpm",
            status="normal",
            subject=Reference.to("Patient", patient_id, "Test Patient"),
            recorded_at=today - timedelta(days=(len(hr_values) - i - 1) * 30),
            recorded_by="Dr. Smith",
            location="Main Clinic",
        )
        repo._store[vital.id] = vital

    # Add blood pressure history (showing increasing trend - concerning)
    # Need >5% increase between last two readings
    bp_values = [110, 115, 120, 125, 130, 140]  # Oldest to newest, ~7.7% increase between 130 and 140
    for i, value in enumerate(bp_values):
        vital = VitalSign(
            id=f"bp-sys-{i}",
            vital_type="blood_pressure_systolic",
            value=float(value),
            unit="mmHg",
            status="normal" if value < 120 else "abnormal",
            subject=Reference.to("Patient", patient_id, "Test Patient"),
            recorded_at=today - timedelta(days=(len(bp_values) - i - 1) * 30),
        )
        repo._store[vital.id] = vital

    # Add weight history (decreasing - good)
    # Need >5% decrease between last two readings
    weight_values = [185, 180, 175, 170, 165, 155]  # Oldest to newest, ~6% decrease between 165 and 155
    for i, value in enumerate(weight_values):
        vital = VitalSign(
            id=f"weight-{i}",
            vital_type="weight",
            value=float(value),
            unit="lbs",
            status="normal",
            subject=Reference.to("Patient", patient_id, "Test Patient"),
            recorded_at=today - timedelta(days=(len(weight_values) - i - 1) * 30),
        )
        repo._store[vital.id] = vital

    # Add height (single measurement)
    vital = VitalSign(
        id="height-1",
        vital_type="height",
        value=65.0,
        unit="in",
        status="normal",
        subject=Reference.to("Patient", patient_id, "Test Patient"),
        recorded_at=today - timedelta(days=365),
    )
    repo._store[vital.id] = vital

    # Add O2 saturation (decreasing - concerning for this vital)
    # Need >5% decrease between last two readings
    o2_values = [99, 98, 97, 96, 90]  # Oldest to newest, ~6.3% decrease between 96 and 90
    for i, value in enumerate(o2_values):
        vital = VitalSign(
            id=f"o2-{i}",
            vital_type="oxygen_saturation",
            value=float(value),
            unit="%",
            status="normal" if value >= 95 else "abnormal",
            subject=Reference.to("Patient", patient_id, "Test Patient"),
            recorded_at=today - timedelta(days=(len(o2_values) - i - 1) * 30),
        )
        repo._store[vital.id] = vital

    return repo


@pytest.fixture
def seeded_service(seeded_repo):
    """Create a vitals service with seeded data."""
    return VitalsService(vitals_repo=seeded_repo)


@pytest.mark.unit
class TestVitalsServiceGetCurrentVitals:
    """Tests for get_current_vitals method."""

    def test_returns_all_vital_types(self, seeded_service):
        """Test that current vitals returns all available types."""
        response = run_async(seeded_service.get_current_vitals("patient-001"))

        assert len(response.vitals) == 5  # HR, BP, weight, height, O2

        vital_types = {v.vital_type for v in response.vitals}
        assert "heart_rate" in vital_types
        assert "blood_pressure_systolic" in vital_types
        assert "weight" in vital_types
        assert "height" in vital_types
        assert "oxygen_saturation" in vital_types

    def test_returns_most_recent_date(self, seeded_service):
        """Test that most recent date is returned."""
        response = run_async(seeded_service.get_current_vitals("patient-001"))

        assert response.most_recent_date is not None

    def test_calculates_bmi(self, seeded_service):
        """Test that BMI is calculated when height and weight available."""
        response = run_async(seeded_service.get_current_vitals("patient-001"))

        assert response.bmi is not None
        assert response.bmi.value > 0
        assert response.bmi.category in ["Underweight", "Normal", "Overweight", "Obese"]

    def test_includes_trend_data(self, seeded_service):
        """Test that trend data is included when requested."""
        response = run_async(seeded_service.get_current_vitals(
            "patient-001",
            include_trends=True,
        ))

        # Heart rate should have a trend
        hr_vital = next((v for v in response.vitals if v.vital_type == "heart_rate"), None)
        assert hr_vital is not None
        assert hr_vital.trend is not None
        assert len(hr_vital.sparkline_data) > 0

    def test_no_trends_when_disabled(self, seeded_service):
        """Test that trends are not included when disabled."""
        response = run_async(seeded_service.get_current_vitals(
            "patient-001",
            include_trends=False,
        ))

        for vital in response.vitals:
            assert vital.trend is None
            assert len(vital.sparkline_data) == 0

    def test_empty_for_unknown_patient(self, seeded_service):
        """Test empty response for unknown patient."""
        response = run_async(seeded_service.get_current_vitals("patient-999"))

        assert len(response.vitals) == 0
        assert response.bmi is None
        assert response.most_recent_date is None

    def test_to_dict(self, seeded_service):
        """Test conversion to dictionary."""
        response = run_async(seeded_service.get_current_vitals("patient-001"))

        d = response.to_dict()

        assert "vitals" in d
        assert "bmi" in d
        assert "mostRecentDate" in d
        assert isinstance(d["vitals"], list)


@pytest.mark.unit
class TestVitalsServiceGetVitalHistory:
    """Tests for get_vital_history method."""

    def test_returns_history(self, seeded_service):
        """Test that history is returned."""
        response = run_async(seeded_service.get_vital_history(
            "patient-001",
            "heart_rate",
        ))

        assert response is not None
        assert len(response.history) == 6
        assert response.vital_type == "heart_rate"

    def test_history_sorted_most_recent_first(self, seeded_service):
        """Test that history is sorted by date descending."""
        response = run_async(seeded_service.get_vital_history(
            "patient-001",
            "heart_rate",
        ))

        assert response.history[0].value == 70.0  # Most recent
        assert response.history[-1].value == 95.0  # Oldest

    def test_includes_trend_analysis(self, seeded_service):
        """Test that trend analysis is included."""
        response = run_async(seeded_service.get_vital_history(
            "patient-001",
            "heart_rate",
        ))

        assert response.trend_analysis is not None
        assert response.trend_analysis.direction == "decreasing"

    def test_returns_none_for_no_data(self, seeded_service):
        """Test None is returned when no data exists."""
        response = run_async(seeded_service.get_vital_history(
            "patient-001",
            "respiratory_rate",  # Not seeded
        ))

        assert response is None

    def test_days_back_filter(self, seeded_service):
        """Test filtering by days back."""
        response = run_async(seeded_service.get_vital_history(
            "patient-001",
            "heart_rate",
            days_back=45,
        ))

        assert response is not None
        assert len(response.history) < 6  # Should be filtered

    def test_to_dict(self, seeded_service):
        """Test conversion to dictionary."""
        response = run_async(seeded_service.get_vital_history(
            "patient-001",
            "heart_rate",
        ))

        d = response.to_dict()

        assert "vitalType" in d
        assert "unit" in d
        assert "referenceRange" in d
        assert "history" in d
        assert "trendAnalysis" in d


@pytest.mark.unit
class TestTrendCalculation:
    """Tests for trend calculation logic."""

    def test_decreasing_heart_rate_is_good(self, seeded_service):
        """Test that decreasing heart rate is marked as good."""
        response = run_async(seeded_service.get_vital_history(
            "patient-001",
            "heart_rate",
        ))

        assert response.trend_analysis.direction == "decreasing"
        assert response.trend_analysis.clinical_significance == "good"

    def test_increasing_bp_is_concerning(self, seeded_service):
        """Test that increasing blood pressure is concerning."""
        response = run_async(seeded_service.get_vital_history(
            "patient-001",
            "blood_pressure_systolic",
        ))

        assert response.trend_analysis.direction == "increasing"
        assert response.trend_analysis.clinical_significance == "concerning"

    def test_decreasing_weight_is_good(self, seeded_service):
        """Test that decreasing weight is good."""
        response = run_async(seeded_service.get_vital_history(
            "patient-001",
            "weight",
        ))

        assert response.trend_analysis.direction == "decreasing"
        assert response.trend_analysis.clinical_significance == "good"

    def test_decreasing_o2_is_concerning(self, seeded_service):
        """Test that decreasing oxygen saturation is concerning."""
        response = run_async(seeded_service.get_vital_history(
            "patient-001",
            "oxygen_saturation",
        ))

        assert response.trend_analysis.direction == "decreasing"
        assert response.trend_analysis.clinical_significance == "concerning"


@pytest.mark.unit
class TestBMICalculation:
    """Tests for BMI calculation."""

    def test_bmi_value(self, seeded_service):
        """Test BMI calculation value."""
        response = run_async(seeded_service.get_current_vitals("patient-001"))

        # Height: 65 in (1.651 m), Weight: 155 lbs (70.3 kg)
        # BMI = 70.3 / (1.651)^2 = 25.8 (Overweight)
        assert response.bmi is not None
        assert 25 < response.bmi.value < 27
        assert response.bmi.category == "Overweight"

    def test_bmi_categories(self):
        """Test all BMI categories."""
        repo = VitalSignRepository()
        service = VitalsService(vitals_repo=repo)
        today = datetime.now()

        # Test different weight/height combinations
        test_cases = [
            # (height_in, weight_lbs, expected_category)
            (70, 120, "Underweight"),  # BMI ~17.2
            (70, 150, "Normal"),  # BMI ~21.5
            (70, 190, "Overweight"),  # BMI ~27.3
            (70, 230, "Obese"),  # BMI ~33.0
        ]

        for height, weight, expected_category in test_cases:
            # Clear and reseed repo
            repo._store.clear()

            repo._store["height"] = VitalSign(
                id="height",
                vital_type="height",
                value=float(height),
                unit="in",
                status="normal",
                subject=Reference.to("Patient", "test-patient", "Test"),
                recorded_at=today,
            )
            repo._store["weight"] = VitalSign(
                id="weight",
                vital_type="weight",
                value=float(weight),
                unit="lbs",
                status="normal",
                subject=Reference.to("Patient", "test-patient", "Test"),
                recorded_at=today,
            )

            response = run_async(service.get_current_vitals("test-patient"))
            assert response.bmi is not None
            assert response.bmi.category == expected_category, (
                f"Expected {expected_category} for height={height}, weight={weight}, "
                f"got {response.bmi.category} (BMI={response.bmi.value})"
            )

    def test_no_bmi_without_height(self):
        """Test that BMI is not calculated without height."""
        repo = VitalSignRepository()
        service = VitalsService(vitals_repo=repo)
        today = datetime.now()

        repo._store["weight"] = VitalSign(
            id="weight",
            vital_type="weight",
            value=155.0,
            unit="lbs",
            status="normal",
            subject=Reference.to("Patient", "test-patient", "Test"),
            recorded_at=today,
        )

        response = run_async(service.get_current_vitals("test-patient"))
        assert response.bmi is None

    def test_no_bmi_without_weight(self):
        """Test that BMI is not calculated without weight."""
        repo = VitalSignRepository()
        service = VitalsService(vitals_repo=repo)
        today = datetime.now()

        repo._store["height"] = VitalSign(
            id="height",
            vital_type="height",
            value=65.0,
            unit="in",
            status="normal",
            subject=Reference.to("Patient", "test-patient", "Test"),
            recorded_at=today,
        )

        response = run_async(service.get_current_vitals("test-patient"))
        assert response.bmi is None


@pytest.mark.unit
class TestSparklineData:
    """Tests for sparkline data generation."""

    def test_sparkline_chronological_order(self, seeded_service):
        """Test that sparkline data is in chronological order."""
        response = run_async(seeded_service.get_current_vitals("patient-001"))

        hr_vital = next((v for v in response.vitals if v.vital_type == "heart_rate"), None)
        assert hr_vital is not None

        # Sparkline should be oldest to newest (chronological)
        values = [p.value for p in hr_vital.sparkline_data]
        assert values[0] == 95.0  # Oldest
        assert values[-1] == 70.0  # Newest

    def test_sparkline_includes_status(self, seeded_service):
        """Test that sparkline points include status."""
        response = run_async(seeded_service.get_current_vitals("patient-001"))

        hr_vital = next((v for v in response.vitals if v.vital_type == "heart_rate"), None)
        assert hr_vital is not None

        for point in hr_vital.sparkline_data:
            assert point.status in ["normal", "abnormal", "critical"]

    def test_sparkline_to_dict(self, seeded_service):
        """Test sparkline point to_dict conversion."""
        response = run_async(seeded_service.get_current_vitals("patient-001"))

        hr_vital = next((v for v in response.vitals if v.vital_type == "heart_rate"), None)
        assert hr_vital is not None

        point_dict = hr_vital.sparkline_data[0].to_dict()
        assert "value" in point_dict
        assert "status" in point_dict
        assert "date" in point_dict
