"""
Unit tests for medication-related endpoints.

These tests verify search functionality and response structure.
"""

import pytest
from fastapi import status


@pytest.mark.unit
class TestSearchMedications:
    """Tests for GET /medications/search endpoint"""
    
    def test_search_medications_returns_200(self, client, sample_search_term):
        """Should return 200 OK for valid search"""
        response = client.get(f"/medications/search?q={sample_search_term}")
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_medications_returns_list(self, client):
        """Should return a list of medications"""
        response = client.get("/medications/search?q=statin")
        data = response.json()
        
        assert isinstance(data, list)
    
    def test_search_medications_with_results(self, client):
        """Should return matching medications for valid search"""
        response = client.get("/medications/search?q=amox")
        medications = response.json()
        
        assert len(medications) > 0
        # All results should contain search term
        for med in medications:
            assert "amoxicillin" in med["name"].lower()
    
    def test_search_medications_case_insensitive(self, client):
        """Search should be case-insensitive"""
        response_lower = client.get("/medications/search?q=simvastatin")
        response_upper = client.get("/medications/search?q=SIMVASTATIN")
        response_mixed = client.get("/medications/search?q=SimVaStAtIn")
        
        assert response_lower.json() == response_upper.json()
        assert response_lower.json() == response_mixed.json()
    
    def test_search_medications_no_results(self, client):
        """Should return empty list when no matches found"""
        response = client.get("/medications/search?q=nonexistentmedication123")
        medications = response.json()
        
        assert medications == []
    
    def test_search_medications_partial_match(self, client):
        """Should find medications with partial name match"""
        response = client.get("/medications/search?q=amox")
        medications = response.json()
        
        # Should find medications containing "amox" 
        assert len(medications) > 0
        for med in medications:
            assert "amox" in med["name"].lower()
    
    def test_search_medications_structure(self, client):
        """Each medication should have required fields"""
        response = client.get("/medications/search?q=amox")
        medications = response.json()
        
        assert len(medications) > 0
        first_med = medications[0]
        
        # Check expected fields exist
        assert "rxcui" in first_med
        assert "tty" in first_med
        assert "name" in first_med
    
    def test_search_medications_data_types(self, client):
        """Medication fields should have correct types"""
        response = client.get("/medications/search?q=amox")
        first_med = response.json()[0]
        
        assert isinstance(first_med["rxcui"], str)
        assert isinstance(first_med["tty"], str)
        assert isinstance(first_med["name"], str)


@pytest.mark.unit
class TestSearchMedicationsValidation:
    """Tests for search parameter validation"""
    
    def test_search_medications_missing_query_param(self, client):
        """Should return 422 when query parameter is missing"""
        response = client.get("/medications/search")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_search_medications_query_too_short(self, client):
        """Should return 422 when query is less than 3 characters"""
        response = client.get("/medications/search?q=ab")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_search_medications_query_exactly_3_chars(self, client):
        """Should accept query with exactly 3 characters"""
        response = client.get("/medications/search?q=abc")
        # Should not return validation error
        assert response.status_code in [status.HTTP_200_OK]
    
    def test_search_medications_empty_query(self, client):
        """Should return 422 for empty query string"""
        response = client.get("/medications/search?q=")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_search_medications_whitespace_only(self, client):
        """Should handle whitespace-only query appropriately"""
        response = client.get("/medications/search?q=   ")
        # Could either reject or return empty results
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST
        ]


@pytest.mark.unit
class TestSearchMedicationsEdgeCases:
    """Tests for edge cases and special scenarios"""
    
    def test_search_medications_special_characters(self, client):
        """Should handle special characters in search"""
        response = client.get("/medications/search?q=test-med")
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_medications_numbers(self, client):
        """Should handle numeric search terms"""
        response = client.get("/medications/search?q=20mg")
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_medications_unicode(self, client):
        """Should handle unicode characters gracefully"""
        response = client.get("/medications/search?q=café")
        # Should not crash, either return results or empty list
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_medications_very_long_query(self, client):
        """Should handle very long search terms"""
        long_query = "a" * 100
        response = client.get(f"/medications/search?q={long_query}")
        assert response.status_code == status.HTTP_200_OK


# Future tests when you add more medication endpoints
@pytest.mark.unit
class TestGetMedicationDetails:
    """Tests for GET /medications/{rxcui} endpoint (not implemented yet)"""
    
    @pytest.mark.skip(reason="Endpoint not implemented yet")
    def test_get_medication_by_rxcui(self, client):
        """Should return medication details for valid RxCUI"""
        response = client.get("/medications/197361")
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.skip(reason="Endpoint not implemented yet")
    def test_get_medication_not_found(self, client):
        """Should return 404 for non-existent RxCUI"""
        response = client.get("/medications/invalid")
        assert response.status_code == status.HTTP_404_NOT_FOUND
