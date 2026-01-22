"""Tests for vital signs model."""

import pytest
from datetime import datetime

from resources.vitals.model import (
    VitalSign,
    VitalSignHistory,
    VitalTrendAnalysis,
    VitalStatus,
    VITAL_REFERENCE_RANGES,
)
from resources.core import Reference


class TestVitalSign:
    """Tests for VitalSign model."""

    def test_create_vital_sign(self):
        """Test creating a basic vital sign."""
        vital = VitalSign(
            id="vital-1",
            vital_type="heart_rate",
            value=72.0,
            unit="bpm",
            status="normal",
            subject=Reference.to("Patient", "patient-001", "Test Patient"),
            recorded_at=datetime(2025, 1, 15, 10, 30),
            recorded_by="Dr. Smith",
            location="Main Clinic",
        )

        assert vital.id == "vital-1"
        assert vital.vital_type == "heart_rate"
        assert vital.value == 72.0
        assert vital.unit == "bpm"
        assert vital.status == "normal"
        assert vital.patient_id == "patient-001"
        assert vital.recorded_by == "Dr. Smith"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        vital = VitalSign(
            id="vital-1",
            vital_type="blood_pressure_systolic",
            value=120.0,
            unit="mmHg",
            status="normal",
            subject=Reference.to("Patient", "patient-001", "Test Patient"),
            recorded_at=datetime(2025, 1, 15, 10, 30),
        )

        d = vital.to_dict()

        assert d["id"] == "vital-1"
        assert d["vitalType"] == "blood_pressure_systolic"
        assert d["value"] == 120.0
        assert d["unit"] == "mmHg"
        assert d["status"] == "normal"
        assert "referenceRange" in d

    def test_to_bff_dict(self):
        """Test conversion to BFF format."""
        vital = VitalSign(
            id="vital-1",
            vital_type="heart_rate",
            value=80.0,
            unit="bpm",
            status="normal",
            subject=Reference.to("Patient", "patient-001", "Test Patient"),
            recorded_at=datetime(2025, 1, 15, 10, 30),
        )

        d = vital.to_bff_dict()

        assert "id" in d
        assert "vitalType" in d
        assert "value" in d
        assert "referenceRange" in d
        # BFF dict doesn't include subject
        assert "subject" not in d

    def test_reference_range_property(self):
        """Test reference range generation."""
        vital = VitalSign(
            id="vital-1",
            vital_type="heart_rate",
            value=72.0,
            unit="bpm",
            status="normal",
            subject=Reference.to("Patient", "patient-001", "Test Patient"),
        )

        ref_range = vital.reference_range
        assert "60" in ref_range
        assert "100" in ref_range
        assert "bpm" in ref_range

    def test_to_history_entry(self):
        """Test conversion to history entry."""
        vital = VitalSign(
            id="vital-1",
            vital_type="weight",
            value=156.0,
            unit="lbs",
            status="normal",
            subject=Reference.to("Patient", "patient-001", "Test Patient"),
            recorded_at=datetime(2025, 1, 15, 10, 30),
            recorded_by="MA Thompson",
            location="Main Clinic",
        )

        history = vital.to_history_entry()

        assert isinstance(history, VitalSignHistory)
        assert history.id == "vital-1"
        assert history.value == 156.0
        assert history.unit == "lbs"
        assert history.recorded_by == "MA Thompson"


class TestVitalSignDetermineStatus:
    """Tests for status determination."""

    def test_normal_heart_rate(self):
        """Test normal heart rate status."""
        status = VitalSign.determine_status("heart_rate", 72)
        assert status == "normal"

    def test_abnormal_heart_rate_high(self):
        """Test abnormal high heart rate."""
        status = VitalSign.determine_status("heart_rate", 110)
        assert status == "abnormal"

    def test_abnormal_heart_rate_low(self):
        """Test abnormal low heart rate."""
        status = VitalSign.determine_status("heart_rate", 55)
        assert status == "abnormal"

    def test_critical_heart_rate(self):
        """Test critical heart rate."""
        status = VitalSign.determine_status("heart_rate", 160)
        assert status == "critical"

    def test_normal_blood_pressure(self):
        """Test normal blood pressure."""
        status = VitalSign.determine_status("blood_pressure_systolic", 115)
        assert status == "normal"

    def test_abnormal_blood_pressure(self):
        """Test abnormal blood pressure."""
        status = VitalSign.determine_status("blood_pressure_systolic", 140)
        assert status == "abnormal"

    def test_critical_blood_pressure(self):
        """Test critical blood pressure."""
        status = VitalSign.determine_status("blood_pressure_systolic", 185)
        assert status == "critical"

    def test_low_oxygen_saturation(self):
        """Test low oxygen saturation is critical."""
        status = VitalSign.determine_status("oxygen_saturation", 88)
        assert status == "critical"

    def test_normal_oxygen_saturation(self):
        """Test normal oxygen saturation."""
        status = VitalSign.determine_status("oxygen_saturation", 98)
        assert status == "normal"


class TestVitalSignHistory:
    """Tests for VitalSignHistory model."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        history = VitalSignHistory(
            id="vital-1",
            value=72.0,
            unit="bpm",
            status="normal",
            recorded_at=datetime(2025, 1, 15, 10, 30),
            reference_range="60-100 bpm",
            recorded_by="Dr. Smith",
            location="Main Clinic",
        )

        d = history.to_dict()

        assert d["id"] == "vital-1"
        assert d["value"] == 72.0
        assert d["unit"] == "bpm"
        assert d["status"] == "normal"
        assert d["recordedBy"] == "Dr. Smith"
        assert d["location"] == "Main Clinic"
        assert "recordedAt" in d


class TestVitalTrendAnalysis:
    """Tests for VitalTrendAnalysis model."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        trend = VitalTrendAnalysis(
            direction="decreasing",
            percent_change=-5.5,
            absolute_change=-4.0,
            previous_value=76.0,
            current_value=72.0,
            previous_date=datetime(2025, 1, 1),
            data_points=5,
            clinical_significance="good",
        )

        d = trend.to_dict()

        assert d["direction"] == "decreasing"
        assert d["percentChange"] == -5.5
        assert d["absoluteChange"] == -4.0
        assert d["previousValue"] == 76.0
        assert d["currentValue"] == 72.0
        assert d["dataPoints"] == 5
        assert d["clinicalSignificance"] == "good"
        assert "previousDate" in d


class TestVitalReferenceRanges:
    """Tests for vital reference ranges configuration."""

    def test_all_vital_types_have_ranges(self):
        """Test that all vital types have reference ranges defined."""
        expected_types = [
            "blood_pressure_systolic",
            "blood_pressure_diastolic",
            "heart_rate",
            "temperature",
            "weight",
            "oxygen_saturation",
            "respiratory_rate",
            "height",
        ]

        for vital_type in expected_types:
            assert vital_type in VITAL_REFERENCE_RANGES

    def test_ranges_have_required_fields(self):
        """Test that each range has required fields."""
        for vital_type, ranges in VITAL_REFERENCE_RANGES.items():
            assert "unit" in ranges
            assert "min" in ranges
            assert "max" in ranges
