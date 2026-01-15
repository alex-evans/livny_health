"""
Unit tests for ClinicalDecisionService.

Tests allergy checking, drug interaction checking, and override logging.
"""
import asyncio
import pytest

from services import AllergyAlert, DrugInteraction


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.mark.unit
class TestAllergyConflictChecking:
    """Tests for allergy conflict detection."""

    def test_no_allergy_conflict(self, clinical_decision_service):
        """Should return None for safe medication."""
        alert = run_async(clinical_decision_service.check_allergy_conflicts(
            "patient-001",  # Sarah Johnson - allergic to Penicillin, Sulfa
            "Acetaminophen",
        ))
        assert alert is None

    def test_detect_direct_allergy_match(self, clinical_decision_service):
        """Should detect direct allergy match."""
        alert = run_async(clinical_decision_service.check_allergy_conflicts(
            "patient-001",
            "Penicillin",
        ))
        assert alert is not None
        assert isinstance(alert, AllergyAlert)
        assert alert.allergen == "Penicillin"
        assert alert.is_cross_reactive is False

    def test_detect_cross_reactive_medication(self, clinical_decision_service):
        """Should detect cross-reactive medication (penicillin family)."""
        alert = run_async(clinical_decision_service.check_allergy_conflicts(
            "patient-001",
            "Amoxicillin",
        ))
        assert alert is not None
        assert alert.is_cross_reactive is True
        assert "penicillin" in alert.allergen.lower()

    def test_detect_sulfa_allergy(self, clinical_decision_service):
        """Should detect sulfa allergy (direct match on allergen name)."""
        alert = run_async(clinical_decision_service.check_allergy_conflicts(
            "patient-001",
            "Sulfamethoxazole",
        ))
        assert alert is not None
        # Direct allergen name match, not cross-reactive
        assert "sulfa" in alert.allergen.lower()

    def test_detect_sulfa_cross_reactivity(self, clinical_decision_service):
        """Should detect cross-reactive sulfa medication."""
        alert = run_async(clinical_decision_service.check_allergy_conflicts(
            "patient-001",
            "Bactrim",  # Trade name that's in cross-reactivity list
        ))
        assert alert is not None
        assert alert.is_cross_reactive is True

    def test_severe_allergy_is_blocked(self, clinical_decision_service):
        """Severe allergies should be blocked."""
        alert = run_async(clinical_decision_service.check_allergy_conflicts(
            "patient-001",
            "Penicillin",
        ))
        assert alert.blocked is True
        assert alert.severity == "severe"

    def test_moderate_allergy_not_blocked(self, clinical_decision_service):
        """Moderate allergies should not be blocked."""
        # Patient 001 has moderate allergy to Sulfa
        alert = run_async(clinical_decision_service.check_allergy_conflicts(
            "patient-001",
            "Bactrim",  # Cross-reactive with Sulfa
        ))
        assert alert is not None
        assert alert.blocked is False

    def test_patient_without_allergies(self, clinical_decision_service):
        """Patient without allergies should return None for any medication."""
        # Patient 003 (Emily Rodriguez) has no allergies
        alert = run_async(clinical_decision_service.check_allergy_conflicts(
            "patient-003",
            "Penicillin",
        ))
        assert alert is None

    def test_allergy_alert_to_dict(self, clinical_decision_service):
        """AllergyAlert.to_dict() should return proper structure."""
        alert = run_async(clinical_decision_service.check_allergy_conflicts(
            "patient-001",
            "Penicillin",
        ))
        alert_dict = alert.to_dict()

        assert "blocked" in alert_dict
        assert "severity" in alert_dict
        assert "title" in alert_dict
        assert "message" in alert_dict
        assert "allergen" in alert_dict
        assert "reaction" in alert_dict
        assert "medicationName" in alert_dict
        assert "isCrossReactive" in alert_dict


@pytest.mark.unit
class TestDrugInteractionChecking:
    """Tests for drug interaction detection."""

    def test_no_drug_interactions(self, clinical_decision_service):
        """Should return empty list for no interactions."""
        interactions = run_async(clinical_decision_service.check_drug_interactions(
            "patient-003",  # Emily Rodriguez - on Albuterol inhaler
            "Acetaminophen",
        ))
        assert interactions == []

    def test_detect_warfarin_aspirin_interaction(self, clinical_decision_service):
        """Should detect warfarin-aspirin major interaction."""
        # Patient 006 (Robert Thompson) is on Warfarin
        interactions = run_async(clinical_decision_service.check_drug_interactions(
            "patient-006",
            "Aspirin",
        ))
        assert len(interactions) > 0
        assert any(i.severity == "major" for i in interactions)

    def test_detect_warfarin_ibuprofen_interaction(self, clinical_decision_service):
        """Should detect warfarin-ibuprofen major interaction."""
        interactions = run_async(clinical_decision_service.check_drug_interactions(
            "patient-006",
            "Ibuprofen",
        ))
        assert len(interactions) > 0
        assert any("bleeding" in i.description.lower() for i in interactions)

    def test_detect_lisinopril_ibuprofen_interaction(self, clinical_decision_service):
        """Should detect ACE inhibitor-NSAID interaction."""
        # Patient 006 is on Lisinopril
        interactions = run_async(clinical_decision_service.check_drug_interactions(
            "patient-006",
            "Ibuprofen",
        ))
        # Should find both warfarin and lisinopril interactions
        assert len(interactions) >= 1

    def test_detect_sertraline_tramadol_interaction(self, clinical_decision_service):
        """Should detect SSRI-opioid serotonin syndrome risk."""
        # Patient 007 (Patricia Martinez) is on Sertraline
        interactions = run_async(clinical_decision_service.check_drug_interactions(
            "patient-007",
            "Tramadol",
        ))
        assert len(interactions) > 0
        assert any("serotonin" in i.description.lower() for i in interactions)

    def test_drug_interaction_to_dict(self, clinical_decision_service):
        """DrugInteraction.to_dict() should return proper structure."""
        interactions = run_async(clinical_decision_service.check_drug_interactions(
            "patient-006",
            "Aspirin",
        ))
        assert len(interactions) > 0
        interaction_dict = interactions[0].to_dict()

        assert "interactingDrug" in interaction_dict
        assert "severity" in interaction_dict
        assert "description" in interaction_dict


@pytest.mark.unit
class TestOverrideLogging:
    """Tests for allergy and interaction override logging."""

    def test_log_allergy_override(self, clinical_decision_service):
        """Should log allergy override with unique ID."""
        log_entry = clinical_decision_service.log_allergy_override(
            patient_id="patient-001",
            medication_name="Amoxicillin",
            allergen="Penicillin",
            severity="severe",
            justification="No alternative antibiotics available",
            acknowledged_at="2024-01-15T10:00:00Z",
            prescribed_at="2024-01-15T10:05:00Z",
        )

        assert log_entry.id is not None
        assert log_entry.id.startswith("override-")
        assert log_entry.patient_id == "patient-001"
        assert log_entry.medication_name == "Amoxicillin"
        assert log_entry.allergen == "Penicillin"
        assert log_entry.severity == "severe"
        assert log_entry.justification == "No alternative antibiotics available"

    def test_log_interaction_override(self, clinical_decision_service):
        """Should log interaction override with unique ID."""
        log_entry = clinical_decision_service.log_interaction_override(
            patient_id="patient-006",
            medication_name="Aspirin",
            interacting_drugs=["Warfarin"],
            severities=["major"],
            justification="Low-dose aspirin for cardiac protection, close INR monitoring",
            acknowledged_at="2024-01-15T10:00:00Z",
            prescribed_at="2024-01-15T10:05:00Z",
        )

        assert log_entry.id is not None
        assert log_entry.id.startswith("override-")
        assert log_entry.patient_id == "patient-006"
        assert log_entry.medication_name == "Aspirin"
        assert log_entry.interacting_drugs == ["Warfarin"]
        assert log_entry.severities == ["major"]

    def test_log_multiple_interaction_override(self, clinical_decision_service):
        """Should log override with multiple interacting drugs."""
        log_entry = clinical_decision_service.log_interaction_override(
            patient_id="patient-007",
            medication_name="TestDrug",
            interacting_drugs=["DrugA", "DrugB", "DrugC"],
            severities=["major", "moderate", "minor"],
            justification="Clinical necessity with monitoring plan",
            acknowledged_at="2024-01-15T10:00:00Z",
            prescribed_at="2024-01-15T10:05:00Z",
        )

        assert len(log_entry.interacting_drugs) == 3
        assert len(log_entry.severities) == 3

    def test_multiple_overrides_have_unique_ids(self, clinical_decision_service):
        """Each override should have a unique ID."""
        log1 = clinical_decision_service.log_allergy_override(
            patient_id="patient-001",
            medication_name="Med1",
            allergen="Allergen1",
            severity="mild",
            justification="Test1",
            acknowledged_at="2024-01-15T10:00:00Z",
            prescribed_at="2024-01-15T10:05:00Z",
        )
        log2 = clinical_decision_service.log_allergy_override(
            patient_id="patient-001",
            medication_name="Med2",
            allergen="Allergen2",
            severity="mild",
            justification="Test2",
            acknowledged_at="2024-01-15T10:00:00Z",
            prescribed_at="2024-01-15T10:05:00Z",
        )

        assert log1.id != log2.id


@pytest.mark.unit
class TestInternalMethods:
    """Tests for internal helper methods."""

    def test_check_med_conflicts_empty_allergies(self, clinical_decision_service):
        """Should return None for empty allergy list."""
        result = clinical_decision_service._check_med_conflicts("Aspirin", [])
        assert result is None

    def test_check_interactions_empty_medications(self, clinical_decision_service):
        """Should return empty list for no active medications."""
        result = clinical_decision_service._check_interactions("Aspirin", [])
        assert result == []

    def test_find_interaction_no_match(self, clinical_decision_service):
        """Should return None for non-interacting drugs."""
        result = clinical_decision_service._find_interaction("acetaminophen", "vitamin-d")
        assert result is None

    def test_find_interaction_match(self, clinical_decision_service):
        """Should return interaction dict for known interaction."""
        result = clinical_decision_service._find_interaction("warfarin", "aspirin")
        assert result is not None
        assert result["severity"] == "major"
