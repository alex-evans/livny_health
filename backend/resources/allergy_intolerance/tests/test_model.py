"""
Unit tests for AllergyIntolerance model.

Tests the is_anaphylaxis property, allergy_type property, and BFF dict serialization.
"""
import pytest
from datetime import datetime

from resources.allergy_intolerance import (
    AllergyIntolerance,
    AllergyReaction,
    AllergyCategory,
    AllergyCriticality,
)
from resources.core import Reference, CodeableConcept


class TestIsAnaphylaxis:
    """Tests for the is_anaphylaxis property."""

    def test_anaphylaxis_detected_exact_match(self):
        """Should detect anaphylaxis when reaction manifestation is exactly 'Anaphylaxis'."""
        allergy = AllergyIntolerance(
            id="test-1",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            reactions=[AllergyReaction(manifestation="Anaphylaxis", severity="severe")],
        )
        assert allergy.is_anaphylaxis is True

    def test_anaphylaxis_detected_case_insensitive(self):
        """Should detect anaphylaxis case-insensitively."""
        allergy = AllergyIntolerance(
            id="test-2",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="peanuts", display="Peanuts"),
            reactions=[AllergyReaction(manifestation="ANAPHYLAXIS", severity="severe")],
        )
        assert allergy.is_anaphylaxis is True

    def test_anaphylaxis_detected_partial_match(self):
        """Should detect anaphylaxis when manifestation contains the term."""
        allergy = AllergyIntolerance(
            id="test-3",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="shellfish", display="Shellfish"),
            reactions=[AllergyReaction(manifestation="Severe anaphylaxis with throat swelling", severity="severe")],
        )
        assert allergy.is_anaphylaxis is True

    def test_anaphylactic_detected(self):
        """Should detect anaphylactic reaction variant."""
        allergy = AllergyIntolerance(
            id="test-4",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="bee-sting", display="Bee Sting"),
            reactions=[AllergyReaction(manifestation="Anaphylactic shock", severity="severe")],
        )
        assert allergy.is_anaphylaxis is True

    def test_anaphylaxis_false_for_rash(self):
        """Should return False when reaction is not anaphylaxis."""
        allergy = AllergyIntolerance(
            id="test-5",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="sulfa", display="Sulfa"),
            reactions=[AllergyReaction(manifestation="Rash", severity="moderate")],
        )
        assert allergy.is_anaphylaxis is False

    def test_anaphylaxis_false_for_hives(self):
        """Should return False for non-anaphylaxis reaction."""
        allergy = AllergyIntolerance(
            id="test-6",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="aspirin", display="Aspirin"),
            reactions=[AllergyReaction(manifestation="Hives", severity="mild")],
        )
        assert allergy.is_anaphylaxis is False

    def test_anaphylaxis_false_when_no_reactions(self):
        """Should return False when no reactions are documented."""
        allergy = AllergyIntolerance(
            id="test-7",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="unknown", display="Unknown"),
            reactions=[],
        )
        assert allergy.is_anaphylaxis is False

    def test_anaphylaxis_detected_in_multiple_reactions(self):
        """Should detect anaphylaxis when it appears in one of multiple reactions."""
        allergy = AllergyIntolerance(
            id="test-8",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            reactions=[
                AllergyReaction(manifestation="Mild rash", severity="mild"),
                AllergyReaction(manifestation="Anaphylaxis on second exposure", severity="severe"),
            ],
        )
        assert allergy.is_anaphylaxis is True


class TestAllergyType:
    """Tests for the allergy_type property."""

    def test_medication_category_returns_drug(self):
        """Medication category should map to 'drug' type."""
        allergy = AllergyIntolerance(
            id="test-1",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            category=AllergyCategory.MEDICATION,
        )
        assert allergy.allergy_type == "drug"

    def test_food_category_returns_food(self):
        """Food category should map to 'food' type."""
        allergy = AllergyIntolerance(
            id="test-2",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="peanuts", display="Peanuts"),
            category=AllergyCategory.FOOD,
        )
        assert allergy.allergy_type == "food"

    def test_environment_category_returns_environmental(self):
        """Environment category should map to 'environmental' type."""
        allergy = AllergyIntolerance(
            id="test-3",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="dust-mites", display="Dust Mites"),
            category=AllergyCategory.ENVIRONMENT,
        )
        assert allergy.allergy_type == "environmental"

    def test_biologic_category_returns_other(self):
        """Biologic category should map to 'other' type."""
        allergy = AllergyIntolerance(
            id="test-4",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="vaccine", display="Vaccine"),
            category=AllergyCategory.BIOLOGIC,
        )
        assert allergy.allergy_type == "other"

    def test_default_category_is_medication(self):
        """Default category should be MEDICATION, returning 'drug' type."""
        allergy = AllergyIntolerance(
            id="test-5",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="unknown", display="Unknown"),
        )
        assert allergy.category == AllergyCategory.MEDICATION
        assert allergy.allergy_type == "drug"


class TestToBffDict:
    """Tests for the to_bff_dict method."""

    def test_bff_dict_contains_required_fields(self):
        """BFF dict should contain all required fields."""
        allergy = AllergyIntolerance(
            id="test-1",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            reactions=[AllergyReaction(manifestation="Anaphylaxis", severity="severe")],
            recorded_date=datetime(2020, 1, 15),
        )
        result = allergy.to_bff_dict()

        assert "id" in result
        assert "allergen" in result
        assert "type" in result
        assert "reaction" in result
        assert "severity" in result
        assert "isAnaphylaxis" in result
        assert "documented" in result

    def test_bff_dict_values_are_correct(self):
        """BFF dict should have correct values."""
        allergy = AllergyIntolerance(
            id="allergy-123",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            category=AllergyCategory.MEDICATION,
            reactions=[AllergyReaction(manifestation="Anaphylaxis", severity="severe")],
            recorded_date=datetime(2020, 1, 15),
        )
        result = allergy.to_bff_dict()

        assert result["id"] == "allergy-123"
        assert result["allergen"] == "Penicillin"
        assert result["type"] == "drug"
        assert result["reaction"] == "Anaphylaxis"
        assert result["severity"] == "severe"
        assert result["isAnaphylaxis"] is True
        assert result["documented"] == "2020-01-15"

    def test_bff_dict_with_food_allergy(self):
        """BFF dict should correctly represent food allergy."""
        allergy = AllergyIntolerance(
            id="allergy-456",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="peanuts", display="Peanuts"),
            category=AllergyCategory.FOOD,
            reactions=[AllergyReaction(manifestation="Hives", severity="moderate")],
            recorded_date=datetime(2019, 6, 20),
        )
        result = allergy.to_bff_dict()

        assert result["allergen"] == "Peanuts"
        assert result["type"] == "food"
        assert result["reaction"] == "Hives"
        assert result["severity"] == "moderate"
        assert result["isAnaphylaxis"] is False

    def test_bff_dict_with_environmental_allergy(self):
        """BFF dict should correctly represent environmental allergy."""
        allergy = AllergyIntolerance(
            id="allergy-789",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="dust-mites", display="Dust Mites"),
            category=AllergyCategory.ENVIRONMENT,
            reactions=[AllergyReaction(manifestation="Rhinitis, sneezing", severity="mild")],
            recorded_date=datetime(2018, 3, 10),
        )
        result = allergy.to_bff_dict()

        assert result["allergen"] == "Dust Mites"
        assert result["type"] == "environmental"
        assert result["severity"] == "mild"
        assert result["isAnaphylaxis"] is False

    def test_bff_dict_with_no_recorded_date(self):
        """BFF dict should handle missing recorded_date."""
        allergy = AllergyIntolerance(
            id="allergy-no-date",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="unknown", display="Unknown Allergen"),
            reactions=[AllergyReaction(manifestation="Unknown", severity="moderate")],
            recorded_date=None,
        )
        result = allergy.to_bff_dict()

        assert result["documented"] is None

    def test_bff_dict_with_no_reactions(self):
        """BFF dict should handle missing reactions with defaults."""
        allergy = AllergyIntolerance(
            id="allergy-no-reaction",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="unknown", display="Unknown Allergen"),
            reactions=[],
        )
        result = allergy.to_bff_dict()

        assert result["reaction"] == "Unknown"
        assert result["severity"] == "moderate"  # default severity
        assert result["isAnaphylaxis"] is False


class TestSeverityProperty:
    """Tests for the severity property."""

    def test_severity_from_first_reaction(self):
        """Should return severity from first reaction."""
        allergy = AllergyIntolerance(
            id="test-1",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            reactions=[
                AllergyReaction(manifestation="Anaphylaxis", severity="severe"),
                AllergyReaction(manifestation="Rash", severity="mild"),
            ],
        )
        assert allergy.severity == "severe"

    def test_severity_default_when_no_reactions(self):
        """Should return 'moderate' when no reactions."""
        allergy = AllergyIntolerance(
            id="test-2",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="unknown", display="Unknown"),
            reactions=[],
        )
        assert allergy.severity == "moderate"


class TestReactionProperty:
    """Tests for the reaction property."""

    def test_reaction_from_first_reaction(self):
        """Should return manifestation from first reaction."""
        allergy = AllergyIntolerance(
            id="test-1",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            reactions=[
                AllergyReaction(manifestation="Anaphylaxis", severity="severe"),
                AllergyReaction(manifestation="Rash", severity="mild"),
            ],
        )
        assert allergy.reaction == "Anaphylaxis"

    def test_reaction_default_when_no_reactions(self):
        """Should return 'Unknown' when no reactions."""
        allergy = AllergyIntolerance(
            id="test-2",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="unknown", display="Unknown"),
            reactions=[],
        )
        assert allergy.reaction == "Unknown"


class TestDocumentingProviderProperty:
    """Tests for the documenting_provider property."""

    def test_documenting_provider_from_recorder(self):
        """Should return provider name from recorder reference display."""
        allergy = AllergyIntolerance(
            id="test-1",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            recorder=Reference(reference="Practitioner/provider-001", display="Dr. Elizabeth Frost"),
        )
        assert allergy.documenting_provider == "Dr. Elizabeth Frost"

    def test_documenting_provider_none_when_no_recorder(self):
        """Should return None when no recorder is set."""
        allergy = AllergyIntolerance(
            id="test-2",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
        )
        assert allergy.documenting_provider is None

    def test_documenting_provider_none_when_recorder_has_no_display(self):
        """Should return None when recorder has no display name."""
        allergy = AllergyIntolerance(
            id="test-3",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            recorder=Reference(reference="Practitioner/provider-001"),
        )
        assert allergy.documenting_provider is None


class TestNotesField:
    """Tests for the notes field."""

    def test_notes_stored_correctly(self):
        """Should store and retrieve notes correctly."""
        allergy = AllergyIntolerance(
            id="test-1",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            notes="Patient carries EpiPen. Avoid all penicillin-class antibiotics.",
        )
        assert allergy.notes == "Patient carries EpiPen. Avoid all penicillin-class antibiotics."

    def test_notes_default_is_none(self):
        """Should default to None when not provided."""
        allergy = AllergyIntolerance(
            id="test-2",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
        )
        assert allergy.notes is None


class TestLastUpdatedField:
    """Tests for the last_updated field."""

    def test_last_updated_stored_correctly(self):
        """Should store and retrieve last_updated correctly."""
        last_updated = datetime(2024, 6, 10)
        allergy = AllergyIntolerance(
            id="test-1",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            last_updated=last_updated,
        )
        assert allergy.last_updated == last_updated

    def test_last_updated_default_is_none(self):
        """Should default to None when not provided."""
        allergy = AllergyIntolerance(
            id="test-2",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
        )
        assert allergy.last_updated is None


class TestClinicalStatusInBffDict:
    """Tests for clinical_status in to_bff_dict method."""

    def test_bff_dict_contains_clinical_status(self):
        """BFF dict should contain clinicalStatus."""
        allergy = AllergyIntolerance(
            id="test-1",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
        )
        result = allergy.to_bff_dict()
        assert "clinicalStatus" in result
        assert result["clinicalStatus"] == "active"  # default status

    def test_bff_dict_clinical_status_inactive(self):
        """BFF dict should correctly serialize inactive status."""
        allergy = AllergyIntolerance(
            id="test-2",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            clinical_status="inactive",
        )
        result = allergy.to_bff_dict()
        assert result["clinicalStatus"] == "inactive"

    def test_bff_dict_clinical_status_resolved(self):
        """BFF dict should correctly serialize resolved status."""
        allergy = AllergyIntolerance(
            id="test-3",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="egg", display="Egg"),
            clinical_status="resolved",
        )
        result = allergy.to_bff_dict()
        assert result["clinicalStatus"] == "resolved"


class TestToBffDictNewFields:
    """Tests for the new fields in to_bff_dict method."""

    def test_bff_dict_contains_verification_status(self):
        """BFF dict should contain verificationStatus."""
        allergy = AllergyIntolerance(
            id="test-1",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
        )
        result = allergy.to_bff_dict()
        assert "verificationStatus" in result
        assert result["verificationStatus"] == "confirmed"  # default status

    def test_bff_dict_contains_last_updated(self):
        """BFF dict should contain lastUpdated."""
        allergy = AllergyIntolerance(
            id="test-1",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            last_updated=datetime(2024, 6, 10),
        )
        result = allergy.to_bff_dict()
        assert "lastUpdated" in result
        assert result["lastUpdated"] == "2024-06-10"

    def test_bff_dict_last_updated_none_when_not_set(self):
        """BFF dict lastUpdated should be None when not set."""
        allergy = AllergyIntolerance(
            id="test-1",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
        )
        result = allergy.to_bff_dict()
        assert result["lastUpdated"] is None

    def test_bff_dict_contains_documenting_provider(self):
        """BFF dict should contain documentingProvider."""
        allergy = AllergyIntolerance(
            id="test-1",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            recorder=Reference(reference="Practitioner/provider-001", display="Dr. Elizabeth Frost"),
        )
        result = allergy.to_bff_dict()
        assert "documentingProvider" in result
        assert result["documentingProvider"] == "Dr. Elizabeth Frost"

    def test_bff_dict_documenting_provider_none_when_no_recorder(self):
        """BFF dict documentingProvider should be None when no recorder."""
        allergy = AllergyIntolerance(
            id="test-1",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
        )
        result = allergy.to_bff_dict()
        assert result["documentingProvider"] is None

    def test_bff_dict_contains_notes(self):
        """BFF dict should contain notes."""
        allergy = AllergyIntolerance(
            id="test-1",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            notes="Patient carries EpiPen.",
        )
        result = allergy.to_bff_dict()
        assert "notes" in result
        assert result["notes"] == "Patient carries EpiPen."

    def test_bff_dict_notes_none_when_not_set(self):
        """BFF dict notes should be None when not set."""
        allergy = AllergyIntolerance(
            id="test-1",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
        )
        result = allergy.to_bff_dict()
        assert result["notes"] is None

    def test_bff_dict_contains_reactions_array(self):
        """BFF dict should contain reactions array."""
        allergy = AllergyIntolerance(
            id="test-1",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            reactions=[
                AllergyReaction(manifestation="Anaphylaxis", severity="severe", description="Immediate onset"),
                AllergyReaction(manifestation="Hives", severity="moderate"),
            ],
        )
        result = allergy.to_bff_dict()
        assert "reactions" in result
        assert len(result["reactions"]) == 2
        assert result["reactions"][0]["manifestation"] == "Anaphylaxis"
        assert result["reactions"][0]["severity"] == "severe"
        assert result["reactions"][0]["description"] == "Immediate onset"
        assert result["reactions"][1]["manifestation"] == "Hives"
        assert result["reactions"][1]["severity"] == "moderate"
        assert result["reactions"][1]["description"] is None

    def test_bff_dict_reactions_empty_when_no_reactions(self):
        """BFF dict reactions should be empty array when no reactions."""
        allergy = AllergyIntolerance(
            id="test-1",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            reactions=[],
        )
        result = allergy.to_bff_dict()
        assert result["reactions"] == []

    def test_bff_dict_complete_with_all_new_fields(self):
        """BFF dict should correctly serialize all new fields together."""
        from resources.allergy_intolerance import AllergyVerificationStatus

        allergy = AllergyIntolerance(
            id="allergy-complete",
            patient=Reference(reference="Patient/patient-001"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            category=AllergyCategory.MEDICATION,
            verification_status=AllergyVerificationStatus.CONFIRMED,
            reactions=[
                AllergyReaction(manifestation="Anaphylaxis", severity="severe", description="Throat swelling"),
                AllergyReaction(manifestation="Hives", severity="moderate"),
            ],
            recorded_date=datetime(2020, 1, 15),
            last_updated=datetime(2024, 6, 10),
            recorder=Reference(reference="Practitioner/provider-001", display="Dr. Elizabeth Frost"),
            notes="Patient carries EpiPen. Avoid all penicillin-class antibiotics.",
        )
        result = allergy.to_bff_dict()

        assert result["id"] == "allergy-complete"
        assert result["allergen"] == "Penicillin"
        assert result["type"] == "drug"
        assert result["reaction"] == "Anaphylaxis"
        assert result["severity"] == "severe"
        assert result["isAnaphylaxis"] is True
        assert result["documented"] == "2020-01-15"
        assert result["verificationStatus"] == "confirmed"
        assert result["lastUpdated"] == "2024-06-10"
        assert result["documentingProvider"] == "Dr. Elizabeth Frost"
        assert result["notes"] == "Patient carries EpiPen. Avoid all penicillin-class antibiotics."
        assert len(result["reactions"]) == 2
