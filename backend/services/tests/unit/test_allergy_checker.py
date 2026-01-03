import pytest
from allergy_checker import check_allergy, CROSS_REACTIVITY


class TestAllergyChecker:
    """Tests for the allergy checking service."""

    @pytest.fixture
    def penicillin_allergy(self):
        """Patient with severe penicillin allergy."""
        return [
            {
                "id": "allergy-1",
                "allergen": "Penicillin",
                "reaction": "Anaphylaxis",
                "severity": "severe",
                "documented": "2020-01-15",
            }
        ]

    @pytest.fixture
    def sulfa_allergy(self):
        """Patient with moderate sulfa allergy."""
        return [
            {
                "id": "allergy-2",
                "allergen": "Sulfa",
                "reaction": "Rash",
                "severity": "moderate",
                "documented": "2019-06-20",
            }
        ]

    @pytest.fixture
    def multiple_allergies(self):
        """Patient with multiple allergies."""
        return [
            {
                "id": "allergy-1",
                "allergen": "Penicillin",
                "reaction": "Anaphylaxis",
                "severity": "severe",
                "documented": "2020-01-15",
            },
            {
                "id": "allergy-2",
                "allergen": "Sulfa",
                "reaction": "Rash",
                "severity": "moderate",
                "documented": "2019-06-20",
            },
        ]

    def test_no_allergies_returns_none(self):
        """When patient has no allergies, should return None."""
        result = check_allergy("Amoxicillin 500mg capsule", [])
        assert result is None

    def test_direct_match_penicillin(self, penicillin_allergy):
        """Direct match for penicillin allergy."""
        result = check_allergy("Penicillin VK 500mg tablet", penicillin_allergy)
        assert result is not None
        assert result.blocked is True
        assert result.allergen == "Penicillin"
        assert result.is_cross_reactive is False

    def test_cross_reactive_amoxicillin_with_penicillin_allergy(self, penicillin_allergy):
        """Amoxicillin should trigger alert for penicillin allergy (cross-reactivity)."""
        result = check_allergy("Amoxicillin 500mg capsule", penicillin_allergy)
        assert result is not None
        assert result.blocked is True
        assert result.allergen == "Penicillin"
        assert result.reaction == "Anaphylaxis"
        assert result.severity == "severe"
        assert result.is_cross_reactive is True

    def test_cross_reactive_ampicillin_with_penicillin_allergy(self, penicillin_allergy):
        """Ampicillin should trigger alert for penicillin allergy (cross-reactivity)."""
        result = check_allergy("Ampicillin 250mg capsule", penicillin_allergy)
        assert result is not None
        assert result.blocked is True
        assert result.is_cross_reactive is True

    def test_safe_medication_with_penicillin_allergy(self, penicillin_allergy):
        """Non-penicillin medication should not trigger alert."""
        result = check_allergy("Lisinopril 10mg tablet", penicillin_allergy)
        assert result is None

    def test_azithromycin_safe_with_penicillin_allergy(self, penicillin_allergy):
        """Azithromycin (macrolide) should be safe for penicillin allergy."""
        result = check_allergy("Azithromycin 250mg tablet", penicillin_allergy)
        assert result is None

    def test_bactrim_with_sulfa_allergy(self, sulfa_allergy):
        """Bactrim should trigger alert for sulfa allergy (cross-reactivity)."""
        result = check_allergy("Bactrim DS tablet", sulfa_allergy)
        assert result is not None
        assert result.blocked is True
        assert result.allergen == "Sulfa"
        assert result.is_cross_reactive is True

    def test_multiple_allergies_first_match(self, multiple_allergies):
        """With multiple allergies, should match the first applicable allergy."""
        result = check_allergy("Amoxicillin 500mg capsule", multiple_allergies)
        assert result is not None
        assert result.allergen == "Penicillin"

    def test_alert_dict_format(self, penicillin_allergy):
        """Alert to_dict should return correct format."""
        result = check_allergy("Amoxicillin 500mg capsule", penicillin_allergy)
        assert result is not None

        alert_dict = result.to_dict()
        assert alert_dict["blocked"] is True
        assert alert_dict["severity"] == "severe"
        assert "CRITICAL" in alert_dict["title"]
        assert "Penicillin" in alert_dict["title"]
        assert alert_dict["allergen"] == "Penicillin"
        assert alert_dict["reaction"] == "Anaphylaxis"
        assert alert_dict["isCrossReactive"] is True

    def test_case_insensitive_matching(self, penicillin_allergy):
        """Matching should be case-insensitive."""
        result = check_allergy("AMOXICILLIN 500MG CAPSULE", penicillin_allergy)
        assert result is not None
        assert result.blocked is True

    def test_cross_reactivity_map_contains_expected_entries(self):
        """Verify cross-reactivity map has expected drug classes."""
        assert "penicillin" in CROSS_REACTIVITY
        assert "sulfa" in CROSS_REACTIVITY
        assert "amoxicillin" in CROSS_REACTIVITY["penicillin"]
        assert "ampicillin" in CROSS_REACTIVITY["penicillin"]
