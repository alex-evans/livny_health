"""
Unit tests for dosing_data module.

Tests the common dosing pattern lookup functionality.
"""

import pytest

from dosing_data import get_common_dosing, _extract_strength_value, _find_matching_drug


@pytest.mark.unit
class TestGetCommonDosing:
    """Tests for get_common_dosing function"""

    def test_amoxicillin_500mg_returns_dosing(self):
        """Should return common dosing for Amoxicillin 500mg"""
        result = get_common_dosing("Amoxicillin 500 MG Oral Capsule")
        assert result == ["500mg TID", "500mg BID"]

    def test_amoxicillin_250mg_returns_dosing(self):
        """Should return strength-specific dosing for 250mg"""
        result = get_common_dosing("Amoxicillin 250 MG Oral Capsule")
        assert result == ["250mg TID", "250mg BID"]

    def test_amoxicillin_875mg_returns_dosing(self):
        """Should return correct dosing for 875mg strength"""
        result = get_common_dosing("Amoxicillin 875 MG Oral Tablet")
        assert result == ["875mg BID"]

    def test_lisinopril_returns_dosing(self):
        """Should return common dosing for Lisinopril"""
        result = get_common_dosing("Lisinopril 10 MG Oral Tablet")
        assert result == ["10mg daily"]

    def test_atorvastatin_returns_bedtime_dosing(self):
        """Should return at bedtime dosing for statins"""
        result = get_common_dosing("Atorvastatin 20 MG Oral Tablet")
        assert result == ["20mg daily at bedtime"]

    def test_albuterol_inhaler_returns_prn(self):
        """Should return PRN dosing for inhalers"""
        result = get_common_dosing("Albuterol 90 MCG Metered Dose Inhaler")
        assert result == ["2 puffs every 4-6 hours PRN"]

    def test_unknown_medication_returns_empty(self):
        """Should return empty list for unknown medications"""
        result = get_common_dosing("Unknown Medication 123 MG Tablet")
        assert result == []

    def test_case_insensitive_matching(self):
        """Should match medication names case-insensitively"""
        result1 = get_common_dosing("AMOXICILLIN 500 MG")
        result2 = get_common_dosing("amoxicillin 500 mg")
        result3 = get_common_dosing("Amoxicillin 500 MG")

        assert result1 == result2 == result3
        assert len(result1) > 0

    def test_metformin_500_returns_bid(self):
        """Should return BID dosing for Metformin 500"""
        result = get_common_dosing("Metformin 500 MG Oral Tablet")
        assert "500mg BID" in result

    def test_gabapentin_returns_tid(self):
        """Should return TID dosing for Gabapentin"""
        result = get_common_dosing("Gabapentin 300 MG Oral Capsule")
        assert result == ["300mg TID"]

    def test_opioid_returns_prn_dosing(self):
        """Should return PRN dosing for controlled substances"""
        result = get_common_dosing("Hydrocodone Bitartrate 5 MG / Acetaminophen 325 MG Oral Tablet")
        assert result == ["1-2 tablets every 4-6 hours PRN"]

    def test_azithromycin_returns_zpack_dosing(self):
        """Should return Z-pack dosing for azithromycin"""
        result = get_common_dosing("Azithromycin 250 MG Oral Tablet")
        assert result == ["500mg day 1, then 250mg days 2-5"]

    def test_prednisone_includes_taper(self):
        """Should include taper instructions for prednisone"""
        result = get_common_dosing("Prednisone 10 MG Oral Tablet")
        assert "Taper per instructions" in result

    def test_fallback_to_default_for_unknown_strength(self):
        """Should use default dosing when strength not in database"""
        result = get_common_dosing("Lisinopril 15 MG Oral Tablet")
        # 15mg is not in database, should use default
        assert result == ["10mg daily"]

    def test_omeprazole_before_breakfast(self):
        """Should return before breakfast instruction for PPIs"""
        result = get_common_dosing("Omeprazole 20 MG Oral Capsule")
        assert result == ["20mg daily before breakfast"]


@pytest.mark.unit
class TestExtractStrengthValue:
    """Tests for _extract_strength_value helper function"""

    def test_extracts_integer_mg(self):
        """Should extract integer mg strength"""
        result = _extract_strength_value("Amoxicillin 500 MG Oral Capsule")
        assert result == "500"

    def test_extracts_decimal_mg(self):
        """Should extract decimal mg strength"""
        result = _extract_strength_value("Levothyroxine 0.05 MG Oral Tablet")
        assert result == "0.05"

    def test_extracts_mcg(self):
        """Should extract mcg strength"""
        result = _extract_strength_value("Albuterol 90 MCG Inhaler")
        assert result == "90"

    def test_returns_none_for_no_strength(self):
        """Should return None when no strength found"""
        result = _extract_strength_value("Some Medication Without Strength")
        assert result is None


@pytest.mark.unit
class TestFindMatchingDrug:
    """Tests for _find_matching_drug helper function"""

    def test_finds_amoxicillin(self):
        """Should find amoxicillin in drug name"""
        result = _find_matching_drug("Amoxicillin 500 MG Oral Capsule")
        assert result == "amoxicillin"

    def test_finds_drug_case_insensitive(self):
        """Should find drug regardless of case"""
        result = _find_matching_drug("LISINOPRIL 10 MG ORAL TABLET")
        assert result == "lisinopril"

    def test_returns_none_for_unknown(self):
        """Should return None for unknown drugs"""
        result = _find_matching_drug("Unknown Drug 123 MG")
        assert result is None

    def test_finds_combination_drug(self):
        """Should find combination drugs"""
        result = _find_matching_drug("Hydrocodone Bitartrate 5 MG / Acetaminophen 325 MG")
        assert result == "hydrocodone"
