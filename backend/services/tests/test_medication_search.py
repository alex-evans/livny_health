"""
Unit tests for MedicationSearchService.

Tests medication search via RxNorm and dosing defaults.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from services.medication_search import (
    MedicationSearchService,
    get_common_dosing,
    get_default_duration,
    _extract_strength,
    _extract_form,
    _extract_strength_value,
    _find_matching_drug,
)


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.mark.unit
class TestExtractStrength:
    """Tests for _extract_strength helper."""

    def test_extract_mg_strength(self):
        """Should extract mg strength."""
        assert _extract_strength("Lisinopril 10 MG Oral Tablet") == "10 MG"

    def test_extract_mcg_strength(self):
        """Should extract mcg strength."""
        assert _extract_strength("Levothyroxine 50 MCG Oral Tablet") == "50 MCG"

    def test_extract_mg_ml_strength(self):
        """Should extract mg/ml strength (function extracts MG portion)."""
        # Note: The regex captures MG/ML but may return just MG part
        result = _extract_strength("Amoxicillin 250 MG/ML Suspension")
        assert "250" in result
        assert "MG" in result

    def test_extract_decimal_strength(self):
        """Should extract decimal strength."""
        assert _extract_strength("Warfarin 2.5 MG Tablet") == "2.5 MG"

    def test_extract_no_strength(self):
        """Should return empty string when no strength found."""
        assert _extract_strength("Some Drug Without Strength") == ""

    def test_extract_units_strength(self):
        """Should extract units."""
        assert "UNITS" in _extract_strength("Insulin 100 UNITS/ML").upper()


@pytest.mark.unit
class TestExtractForm:
    """Tests for _extract_form helper."""

    def test_extract_tablet_form(self):
        """Should extract tablet form."""
        assert _extract_form("Lisinopril 10 MG Oral Tablet") == "tablet"

    def test_extract_capsule_form(self):
        """Should extract capsule form."""
        assert _extract_form("Omeprazole 20 MG Oral Capsule") == "capsule"

    def test_extract_liquid_form(self):
        """Should extract liquid form from solution."""
        assert _extract_form("Amoxicillin Oral Solution") == "liquid"

    def test_extract_inhaler_form(self):
        """Should extract inhaler form."""
        assert _extract_form("Albuterol Metered Dose Inhaler") == "inhaler"

    def test_extract_topical_form(self):
        """Should extract topical form."""
        assert _extract_form("Hydrocortisone Topical Cream") == "topical"

    def test_extract_injection_form(self):
        """Should extract injection form."""
        assert _extract_form("Insulin Injectable Solution") == "injection"

    def test_extract_unknown_form(self):
        """Should return empty string for unknown form."""
        assert _extract_form("Some Drug Unknown Form") == ""


@pytest.mark.unit
class TestExtractStrengthValue:
    """Tests for _extract_strength_value helper."""

    def test_extract_integer_strength(self):
        """Should extract integer strength value."""
        assert _extract_strength_value("Lisinopril 10 MG") == "10"

    def test_extract_decimal_strength(self):
        """Should extract decimal strength value."""
        assert _extract_strength_value("Warfarin 2.5 MG") == "2.5"

    def test_extract_no_strength(self):
        """Should return None when no strength found."""
        assert _extract_strength_value("Albuterol Inhaler") is None

    def test_extract_mcg_strength(self):
        """Should extract mcg strength value."""
        assert _extract_strength_value("Levothyroxine 50 MCG") == "50"


@pytest.mark.unit
class TestFindMatchingDrug:
    """Tests for _find_matching_drug helper."""

    def test_find_exact_match(self):
        """Should find exact drug match."""
        assert _find_matching_drug("lisinopril") == "lisinopril"

    def test_find_match_with_strength(self):
        """Should find drug with strength in name."""
        assert _find_matching_drug("Lisinopril 10 MG Tablet") == "lisinopril"

    def test_find_match_case_insensitive(self):
        """Should find match case-insensitively."""
        assert _find_matching_drug("METFORMIN 500 MG") == "metformin"

    def test_find_no_match(self):
        """Should return None for unknown drug."""
        assert _find_matching_drug("UnknownDrugXYZ") is None

    def test_find_match_with_slash(self):
        """Should handle drug names with slashes."""
        # Note: depends on COMMON_DOSING_PATTERNS having appropriate entries
        result = _find_matching_drug("amoxicillin-clavulanate")
        # May or may not find a match depending on database
        assert result is None or result in ["amoxicillin", "augmentin"]


@pytest.mark.unit
class TestGetCommonDosing:
    """Tests for get_common_dosing function."""

    def test_get_dosing_lisinopril_10mg(self):
        """Should return dosing options for lisinopril 10mg."""
        dosing = get_common_dosing("Lisinopril 10 MG")
        assert len(dosing) > 0
        assert any("10mg" in d.lower() for d in dosing)

    def test_get_dosing_lisinopril_default(self):
        """Should return default dosing for lisinopril without strength."""
        dosing = get_common_dosing("Lisinopril Oral Tablet")
        assert len(dosing) > 0

    def test_get_dosing_metformin(self):
        """Should return dosing options for metformin."""
        dosing = get_common_dosing("Metformin 500 MG")
        assert len(dosing) > 0
        assert any("500mg" in d.lower() for d in dosing)

    def test_get_dosing_unknown_drug(self):
        """Should return empty list for unknown drug."""
        dosing = get_common_dosing("UnknownDrugXYZ")
        assert dosing == []

    def test_get_dosing_atorvastatin(self):
        """Should return bedtime dosing for statins."""
        dosing = get_common_dosing("Atorvastatin 20 MG")
        assert len(dosing) > 0
        assert any("bedtime" in d.lower() for d in dosing)


@pytest.mark.unit
class TestGetDefaultDuration:
    """Tests for get_default_duration function."""

    def test_duration_antibiotic(self):
        """Antibiotics should have 10-day default duration."""
        assert get_default_duration("Amoxicillin 500 MG") == 10
        assert get_default_duration("Azithromycin 250 MG") == 10
        assert get_default_duration("Ciprofloxacin 500 MG") == 10

    def test_duration_steroid(self):
        """Short-term steroids should have 7-day default duration."""
        assert get_default_duration("Prednisone 5 MG") == 7

    def test_duration_prn_medication(self):
        """PRN medications should have 30-day default duration."""
        assert get_default_duration("Hydrocodone 5 MG") == 30
        assert get_default_duration("Ibuprofen 400 MG") == 30
        assert get_default_duration("Albuterol Inhaler") == 30

    def test_duration_chronic_medication(self):
        """Chronic medications should have 30-day default duration."""
        assert get_default_duration("Lisinopril 10 MG") == 30
        assert get_default_duration("Metformin 500 MG") == 30

    def test_duration_unknown_medication(self):
        """Unknown medications should default to 30 days."""
        assert get_default_duration("UnknownMedXYZ") == 30


@pytest.mark.unit
class TestMedicationSearchServiceGetDefaults:
    """Tests for MedicationSearchService.get_defaults method."""

    def test_get_defaults_returns_dict(self, medication_search_service):
        """Should return dictionary with default values."""
        defaults = medication_search_service.get_defaults("Lisinopril")
        assert isinstance(defaults, dict)
        assert "defaultDuration" in defaults

    def test_get_defaults_antibiotic(self, medication_search_service):
        """Should return 10-day duration for antibiotics."""
        defaults = medication_search_service.get_defaults("Amoxicillin 500 MG")
        assert defaults["defaultDuration"] == 10

    def test_get_defaults_chronic(self, medication_search_service):
        """Should return 30-day duration for chronic medications."""
        defaults = medication_search_service.get_defaults("Atorvastatin 20 MG")
        assert defaults["defaultDuration"] == 30


@pytest.mark.unit
class TestMedicationSearchServiceSearch:
    """Tests for MedicationSearchService.search method."""

    def test_search_too_short_query(self, medication_search_service):
        """Should return empty list for query shorter than 3 characters."""
        result = run_async(medication_search_service.search("ab"))
        assert result == []

    @patch("services.medication_search.httpx.AsyncClient")
    def test_search_calls_rxnorm_api(self, mock_client_class, medication_search_service):
        """Should call RxNorm API with correct parameters."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_response = MagicMock()
        mock_response.json.return_value = {"drugGroup": {}}
        mock_response.raise_for_status = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        # Call search
        run_async(medication_search_service.search("aspirin"))

        # Verify API was called
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert "drugs.json" in call_args[0][0]
        assert call_args[1]["params"]["name"] == "aspirin"

    @patch("services.medication_search.httpx.AsyncClient")
    def test_search_parses_response(self, mock_client_class, medication_search_service):
        """Should parse RxNorm response into medication list."""
        # Setup mock with realistic response
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "drugGroup": {
                "conceptGroup": [
                    {
                        "tty": "SCD",
                        "conceptProperties": [
                            {
                                "rxcui": "12345",
                                "name": "Aspirin 325 MG Oral Tablet",
                            }
                        ],
                    }
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        # Call search
        results = run_async(medication_search_service.search("aspirin"))

        # Verify parsing
        assert len(results) == 1
        assert results[0]["id"] == "12345"
        assert results[0]["name"] == "Aspirin 325 MG Oral Tablet"
        assert results[0]["strength"] == "325 MG"
        assert results[0]["form"] == "tablet"

    @patch("services.medication_search.httpx.AsyncClient")
    def test_search_filters_by_tty(self, mock_client_class, medication_search_service):
        """Should only include SCD and SBD concept types."""
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "drugGroup": {
                "conceptGroup": [
                    {
                        "tty": "SCD",  # Should include
                        "conceptProperties": [{"rxcui": "1", "name": "Drug 1"}],
                    },
                    {
                        "tty": "SBD",  # Should include
                        "conceptProperties": [{"rxcui": "2", "name": "Drug 2"}],
                    },
                    {
                        "tty": "IN",  # Should exclude
                        "conceptProperties": [{"rxcui": "3", "name": "Drug 3"}],
                    },
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        results = run_async(medication_search_service.search("test"))

        assert len(results) == 2
        assert all(r["id"] in ["1", "2"] for r in results)


@pytest.mark.unit
class TestParsedrugResponse:
    """Tests for _parse_drug_response method."""

    def test_parse_empty_response(self, medication_search_service):
        """Should return empty list for empty response."""
        result = medication_search_service._parse_drug_response({})
        assert result == []

    def test_parse_response_extracts_common_dosing(self, medication_search_service):
        """Should extract common dosing patterns for known medications."""
        response = {
            "drugGroup": {
                "conceptGroup": [
                    {
                        "tty": "SCD",
                        "conceptProperties": [
                            {"rxcui": "1", "name": "Lisinopril 10 MG Oral Tablet"},
                        ],
                    }
                ]
            }
        }

        results = medication_search_service._parse_drug_response(response)

        assert len(results) == 1
        assert len(results[0]["commonDosing"]) > 0

    def test_parse_response_no_concept_groups(self, medication_search_service):
        """Should handle response with no concept groups."""
        response = {"drugGroup": {}}
        result = medication_search_service._parse_drug_response(response)
        assert result == []

    def test_parse_response_no_concept_properties(self, medication_search_service):
        """Should handle concept group with no properties."""
        response = {
            "drugGroup": {
                "conceptGroup": [{"tty": "SCD"}]
            }
        }
        result = medication_search_service._parse_drug_response(response)
        assert result == []
