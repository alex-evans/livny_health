"""
Unit tests for drug interaction checking service.
"""

import pytest
from interactions.main import check_interactions, _find_interaction, DrugInteraction


class TestCheckInteractions:
    """Tests for the check_interactions function."""

    def test_no_active_medications_returns_empty(self):
        """When patient has no active medications, no interactions should be found."""
        result = check_interactions("Amoxicillin", [])
        assert result == []

    def test_warfarin_amoxicillin_interaction(self):
        """Amoxicillin interacts with Warfarin - moderate severity."""
        active_meds = [
            {"id": "med-1", "name": "Warfarin", "dosage": "5mg", "frequency": "daily"}
        ]
        result = check_interactions("Amoxicillin", active_meds)

        assert len(result) == 1
        assert result[0].interacting_drug == "Warfarin"
        assert result[0].severity == "moderate"
        assert "INR" in result[0].description

    def test_warfarin_aspirin_major_interaction(self):
        """Aspirin has a major interaction with Warfarin."""
        active_meds = [
            {"id": "med-1", "name": "Warfarin", "dosage": "5mg", "frequency": "daily"}
        ]
        result = check_interactions("Aspirin", active_meds)

        assert len(result) == 1
        assert result[0].severity == "major"
        assert "bleeding" in result[0].description.lower()

    def test_no_interaction_found(self):
        """When no interaction exists, returns empty list."""
        active_meds = [
            {"id": "med-1", "name": "Omeprazole", "dosage": "20mg", "frequency": "daily"}
        ]
        result = check_interactions("Amoxicillin", active_meds)

        assert result == []

    def test_multiple_interactions(self):
        """Patient on multiple medications may have multiple interactions."""
        active_meds = [
            {"id": "med-1", "name": "Warfarin", "dosage": "5mg", "frequency": "daily"},
            {"id": "med-2", "name": "Lisinopril", "dosage": "10mg", "frequency": "daily"},
        ]
        result = check_interactions("Ibuprofen", active_meds)

        # Ibuprofen interacts with both Warfarin and Lisinopril
        assert len(result) == 2
        drug_names = [r.interacting_drug for r in result]
        assert "Warfarin" in drug_names
        assert "Lisinopril" in drug_names

    def test_case_insensitive_matching(self):
        """Drug name matching should be case insensitive."""
        active_meds = [
            {"id": "med-1", "name": "WARFARIN", "dosage": "5mg", "frequency": "daily"}
        ]
        result = check_interactions("amoxicillin", active_meds)

        assert len(result) == 1
        assert result[0].interacting_drug == "WARFARIN"

    def test_partial_name_matching(self):
        """Should match when medication names contain the drug name."""
        active_meds = [
            {"id": "med-1", "name": "Warfarin Sodium 5mg", "dosage": "5mg", "frequency": "daily"}
        ]
        result = check_interactions("Amoxicillin 500mg capsule", active_meds)

        assert len(result) == 1


class TestFindInteraction:
    """Tests for the _find_interaction helper function."""

    def test_finds_direct_match(self):
        """Should find interaction when drugs match directly."""
        result = _find_interaction("warfarin", "amoxicillin")
        assert result is not None
        assert result["severity"] == "moderate"

    def test_bidirectional_lookup(self):
        """Should find interaction regardless of drug order."""
        result1 = _find_interaction("warfarin", "amoxicillin")
        result2 = _find_interaction("amoxicillin", "warfarin")

        assert result1 is not None
        assert result2 is not None
        assert result1["description"] == result2["description"]

    def test_returns_none_for_no_interaction(self):
        """Should return None when no interaction exists."""
        result = _find_interaction("amoxicillin", "omeprazole")
        assert result is None


class TestDrugInteractionModel:
    """Tests for DrugInteraction class."""

    def test_to_dict_format(self):
        """to_dict should return proper camelCase keys."""
        interaction = DrugInteraction(
            interacting_drug="Warfarin",
            severity="moderate",
            description="Test description",
        )
        result = interaction.to_dict()

        assert result["interactingDrug"] == "Warfarin"
        assert result["severity"] == "moderate"
        assert result["description"] == "Test description"


class TestInteractionDatabase:
    """Tests for the interaction database content."""

    def test_warfarin_interactions_exist(self):
        """Warfarin should have multiple documented interactions."""
        warfarin_meds = [
            {"id": "med-1", "name": "Warfarin", "dosage": "5mg", "frequency": "daily"}
        ]

        # Check known interactions exist
        amox_result = check_interactions("Amoxicillin", warfarin_meds)
        assert len(amox_result) == 1

        aspirin_result = check_interactions("Aspirin", warfarin_meds)
        assert len(aspirin_result) == 1

        ibuprofen_result = check_interactions("Ibuprofen", warfarin_meds)
        assert len(ibuprofen_result) == 1

    def test_ssri_tramadol_major_interaction(self):
        """SSRIs and tramadol have major interaction (serotonin syndrome risk)."""
        active_meds = [
            {"id": "med-1", "name": "Sertraline", "dosage": "50mg", "frequency": "daily"}
        ]
        result = check_interactions("Tramadol", active_meds)

        assert len(result) == 1
        assert result[0].severity == "major"
        assert "serotonin" in result[0].description.lower()
