import pytest
from allergy_checker import check_allergy, CROSS_REACTIVITY


class TestAllergyChecker:
    """Tests for the allergy checking service."""

    @pytest.fixture
    def penicillin_allergy_severe(self):
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
    def sulfa_allergy_moderate(self):
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
    def aspirin_allergy_mild(self):
        """Patient with mild aspirin allergy."""
        return [
            {
                "id": "allergy-3",
                "allergen": "Aspirin",
                "reaction": "Hives",
                "severity": "mild",
                "documented": "2018-04-10",
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

    def test_direct_match_penicillin_severe_is_blocked(self, penicillin_allergy_severe):
        """Direct match for severe penicillin allergy should be blocked."""
        result = check_allergy("Penicillin VK 500mg tablet", penicillin_allergy_severe)
        assert result is not None
        assert result.blocked is True
        assert result.allergen == "Penicillin"
        assert result.is_cross_reactive is False

    def test_cross_reactive_amoxicillin_with_severe_allergy_is_blocked(self, penicillin_allergy_severe):
        """Amoxicillin with severe penicillin allergy should be blocked."""
        result = check_allergy("Amoxicillin 500mg capsule", penicillin_allergy_severe)
        assert result is not None
        assert result.blocked is True
        assert result.allergen == "Penicillin"
        assert result.reaction == "Anaphylaxis"
        assert result.severity == "severe"
        assert result.is_cross_reactive is True

    def test_cross_reactive_ampicillin_with_severe_allergy_is_blocked(self, penicillin_allergy_severe):
        """Ampicillin with severe penicillin allergy should be blocked."""
        result = check_allergy("Ampicillin 250mg capsule", penicillin_allergy_severe)
        assert result is not None
        assert result.blocked is True
        assert result.is_cross_reactive is True

    def test_safe_medication_with_penicillin_allergy(self, penicillin_allergy_severe):
        """Non-penicillin medication should not trigger alert."""
        result = check_allergy("Lisinopril 10mg tablet", penicillin_allergy_severe)
        assert result is None

    def test_azithromycin_safe_with_penicillin_allergy(self, penicillin_allergy_severe):
        """Azithromycin (macrolide) should be safe for penicillin allergy."""
        result = check_allergy("Azithromycin 250mg tablet", penicillin_allergy_severe)
        assert result is None

    def test_moderate_allergy_shows_warning_not_blocked(self, sulfa_allergy_moderate):
        """Moderate allergy should trigger warning but NOT be blocked."""
        result = check_allergy("Bactrim DS tablet", sulfa_allergy_moderate)
        assert result is not None
        assert result.blocked is False  # Not blocked for moderate
        assert result.allergen == "Sulfa"
        assert result.severity == "moderate"
        assert result.is_cross_reactive is True

    def test_mild_allergy_shows_warning_not_blocked(self, aspirin_allergy_mild):
        """Mild allergy should trigger warning but NOT be blocked."""
        result = check_allergy("Aspirin 325mg tablet", aspirin_allergy_mild)
        assert result is not None
        assert result.blocked is False  # Not blocked for mild
        assert result.allergen == "Aspirin"
        assert result.severity == "mild"

    def test_multiple_allergies_first_match(self, multiple_allergies):
        """With multiple allergies, should match the first applicable allergy."""
        result = check_allergy("Amoxicillin 500mg capsule", multiple_allergies)
        assert result is not None
        assert result.allergen == "Penicillin"
        assert result.blocked is True  # Severe allergy

    def test_alert_dict_format_severe_shows_critical(self, penicillin_allergy_severe):
        """Severe allergy alert should show CRITICAL in title."""
        result = check_allergy("Amoxicillin 500mg capsule", penicillin_allergy_severe)
        assert result is not None

        alert_dict = result.to_dict()
        assert alert_dict["blocked"] is True
        assert alert_dict["severity"] == "severe"
        assert "CRITICAL" in alert_dict["title"]
        assert "Penicillin" in alert_dict["title"]
        assert alert_dict["allergen"] == "Penicillin"
        assert alert_dict["reaction"] == "Anaphylaxis"
        assert alert_dict["isCrossReactive"] is True

    def test_alert_dict_format_moderate_shows_warning(self, sulfa_allergy_moderate):
        """Moderate allergy alert should show Warning in title."""
        result = check_allergy("Bactrim DS tablet", sulfa_allergy_moderate)
        assert result is not None

        alert_dict = result.to_dict()
        assert alert_dict["blocked"] is False
        assert alert_dict["severity"] == "moderate"
        assert "Warning" in alert_dict["title"]
        assert "CRITICAL" not in alert_dict["title"]
        assert "Sulfa" in alert_dict["title"]

    def test_case_insensitive_matching(self, penicillin_allergy_severe):
        """Matching should be case-insensitive."""
        result = check_allergy("AMOXICILLIN 500MG CAPSULE", penicillin_allergy_severe)
        assert result is not None
        assert result.blocked is True

    def test_cross_reactivity_map_contains_expected_entries(self):
        """Verify cross-reactivity map has expected drug classes."""
        assert "penicillin" in CROSS_REACTIVITY
        assert "sulfa" in CROSS_REACTIVITY
        assert "amoxicillin" in CROSS_REACTIVITY["penicillin"]
        assert "ampicillin" in CROSS_REACTIVITY["penicillin"]
