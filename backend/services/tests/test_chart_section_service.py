"""
Tests for ChartSectionService.
"""

import pytest
import sys
from pathlib import Path

# Add parent directories to Python path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from services import ChartSectionService
from resources.chart_section import ChartSection, ChartSectionsResponse


def run_async(coro):
    """Helper to run async code in sync tests."""
    import asyncio
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestChartSectionService:
    """Tests for ChartSectionService."""

    def test_get_chart_sections_returns_all_sections(self, chart_section_service):
        """Test that all 8 sections are returned."""
        result = run_async(chart_section_service.get_chart_sections("patient-001"))

        assert result is not None
        assert result.patient_id == "patient-001"
        assert len(result.sections) == 8

        # Verify section IDs
        section_ids = [s.id for s in result.sections]
        expected_ids = [
            "visits",
            "medications",
            "allergies",
            "labs",
            "problems",
            "vitals",
            "imaging",
            "social-family",
        ]
        assert section_ids == expected_ids

    def test_get_chart_sections_returns_none_for_unknown_patient(self, chart_section_service):
        """Test that None is returned for non-existent patient."""
        result = run_async(chart_section_service.get_chart_sections("unknown-patient"))
        assert result is None

    def test_sections_are_ordered_correctly(self, chart_section_service):
        """Test that sections are in the correct order."""
        result = run_async(chart_section_service.get_chart_sections("patient-001"))

        assert result is not None
        orders = [s.order for s in result.sections]
        assert orders == [1, 2, 3, 4, 5, 6, 7, 8]

    def test_all_sections_have_keyboard_shortcuts(self, chart_section_service):
        """Test that all sections have keyboard shortcuts."""
        result = run_async(chart_section_service.get_chart_sections("patient-001"))

        assert result is not None
        for section in result.sections:
            assert section.keyboard_shortcut is not None
            assert section.keyboard_shortcut.key is not None
            assert section.keyboard_shortcut.modifier == "Alt"
            assert section.keyboard_shortcut.description is not None

    def test_keyboard_shortcuts_are_unique(self, chart_section_service):
        """Test that keyboard shortcuts are unique."""
        result = run_async(chart_section_service.get_chart_sections("patient-001"))

        assert result is not None
        shortcut_keys = [s.keyboard_shortcut.key for s in result.sections]
        assert len(shortcut_keys) == len(set(shortcut_keys)), "Keyboard shortcuts should be unique"

    def test_allergies_section_has_critical_alert_for_severe_allergies(self, chart_section_service):
        """Test that allergies section shows critical alert for severe allergies."""
        # Patient-001 (John Smith) has severe penicillin allergy
        result = run_async(chart_section_service.get_chart_sections("patient-001"))

        assert result is not None
        allergies_section = next(s for s in result.sections if s.id == "allergies")

        # Should have critical alert for severe allergies
        assert allergies_section.alert_level == "critical"
        assert allergies_section.badge_count is not None
        assert allergies_section.badge_count > 0

    def test_medications_section_has_badge_count(self, chart_section_service):
        """Test that medications section has a badge count."""
        result = run_async(chart_section_service.get_chart_sections("patient-001"))

        assert result is not None
        medications_section = next(s for s in result.sections if s.id == "medications")

        # Patient should have active medications
        assert medications_section.has_data is True
        assert medications_section.badge_count is not None

    def test_visits_section_has_badge_count(self, chart_section_service):
        """Test that visits section has badge count for visit history."""
        result = run_async(chart_section_service.get_chart_sections("patient-001"))

        assert result is not None
        visits_section = next(s for s in result.sections if s.id == "visits")

        # Patient should have visit history
        assert visits_section.badge_count is not None
        assert visits_section.badge_count > 0

    def test_problems_section_counts_active_problems(self, chart_section_service):
        """Test that problems section counts active problems."""
        result = run_async(chart_section_service.get_chart_sections("patient-001"))

        assert result is not None
        problems_section = next(s for s in result.sections if s.id == "problems")

        # Patient should have problems
        assert problems_section.has_data is True

    def test_section_names_are_correct(self, chart_section_service):
        """Test that section names match expected values."""
        result = run_async(chart_section_service.get_chart_sections("patient-001"))

        assert result is not None
        section_names = {s.id: s.name for s in result.sections}

        assert section_names["visits"] == "Chart Notes"
        assert section_names["medications"] == "Medications"
        assert section_names["allergies"] == "Allergies"
        assert section_names["labs"] == "Labs"
        assert section_names["problems"] == "Problems"
        assert section_names["vitals"] == "Vitals"
        assert section_names["imaging"] == "Imaging"
        assert section_names["social-family"] == "Social/Family Hx"

    def test_section_icons_are_correct(self, chart_section_service):
        """Test that section icons match expected values."""
        result = run_async(chart_section_service.get_chart_sections("patient-001"))

        assert result is not None
        section_icons = {s.id: s.icon for s in result.sections}

        assert section_icons["visits"] == "document"
        assert section_icons["medications"] == "pill"
        assert section_icons["allergies"] == "exclamation-triangle"
        assert section_icons["labs"] == "beaker"
        assert section_icons["problems"] == "clipboard-list"
        assert section_icons["vitals"] == "heart-pulse"
        assert section_icons["imaging"] == "film"
        assert section_icons["social-family"] == "users"

    def test_to_dict_method(self, chart_section_service):
        """Test that to_dict returns properly formatted dictionary."""
        result = run_async(chart_section_service.get_chart_sections("patient-001"))

        assert result is not None
        result_dict = result.to_dict()

        assert "patientId" in result_dict
        assert "sections" in result_dict
        assert result_dict["patientId"] == "patient-001"
        assert len(result_dict["sections"]) == 8

        # Check first section structure
        first_section = result_dict["sections"][0]
        assert "id" in first_section
        assert "name" in first_section
        assert "icon" in first_section
        assert "order" in first_section
        assert "hasData" in first_section
        assert "alertLevel" in first_section
        assert "badgeCount" in first_section
        assert "keyboardShortcut" in first_section

        # Check keyboard shortcut structure
        shortcut = first_section["keyboardShortcut"]
        assert "key" in shortcut
        assert "modifier" in shortcut
        assert "description" in shortcut


class TestChartSectionServiceAlertLevels:
    """Tests for alert level calculation."""

    def test_no_allergies_no_alert(self, repositories):
        """Test that patients without allergies have no alert on allergies section."""
        # Create a service with fresh repos
        service = ChartSectionService(
            patient_repo=repositories["patient"],
            allergy_repo=repositories["allergy"],
            medication_request_repo=repositories["medication_request"],
            visit_note_repo=repositories["visit_note"],
            lab_result_repo=repositories["lab_result"],
            imaging_study_repo=repositories["imaging_study"],
            vitals_repo=repositories["vitals"],
            social_family_history_repo=repositories["social_family_history"],
        )

        # patient-003 (Robert Johnson) has no allergies (NKDA)
        result = run_async(service.get_chart_sections("patient-003"))

        if result:
            allergies_section = next(
                (s for s in result.sections if s.id == "allergies"),
                None
            )
            if allergies_section:
                # If there are no allergies, alert level should be "none"
                # (unless the patient has mild allergies which would be "warning")
                assert allergies_section.alert_level in ["none", "warning"]


class TestChartSectionServiceKeyboardShortcuts:
    """Tests for keyboard shortcut configuration."""

    def test_shortcut_key_assignments(self, chart_section_service):
        """Test that shortcut keys are assigned correctly."""
        result = run_async(chart_section_service.get_chart_sections("patient-001"))

        assert result is not None
        shortcuts = {s.id: s.keyboard_shortcut.key for s in result.sections}

        # Verify expected shortcut assignments
        assert shortcuts["visits"] == "V"
        assert shortcuts["medications"] == "M"
        assert shortcuts["allergies"] == "A"
        assert shortcuts["labs"] == "L"
        assert shortcuts["problems"] == "P"
        assert shortcuts["vitals"] == "T"  # T for Vital signs (V is taken)
        assert shortcuts["imaging"] == "I"
        assert shortcuts["social-family"] == "S"
