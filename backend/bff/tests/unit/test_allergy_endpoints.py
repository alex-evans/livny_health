"""
Unit tests for allergy-related endpoints.

These tests verify the API contract and response structure
for allergy and drug interaction checking.
"""
from fastapi import status
import pytest


@pytest.mark.unit
class TestCheckAllergy:
    """Tests for POST /allergies/{patient_id}/check-allergy endpoint"""

    def test_check_allergy_returns_200(self, client, mock_services):
        """Should return 200 OK status for valid request"""
        response = client.post(
            "/allergies/patient-001/check-allergy",
            json={"medication_name": "Ibuprofen"},
        )
        assert response.status_code == status.HTTP_200_OK

    def test_check_allergy_no_conflict(self, client, mock_services):
        """Should return no conflict for safe medication"""
        response = client.post(
            "/allergies/patient-001/check-allergy",
            json={"medication_name": "Ibuprofen"},
        )
        data = response.json()

        assert "hasConflict" in data
        assert data["hasConflict"] is False
        assert data["alert"] is None

    def test_check_allergy_detects_conflict(self, client, mock_services):
        """Should detect allergy conflict for penicillin-allergic patient"""
        # Patient 001 is allergic to Penicillin
        response = client.post(
            "/allergies/patient-001/check-allergy",
            json={"medication_name": "Penicillin"},
        )
        data = response.json()

        assert data["hasConflict"] is True
        assert data["alert"] is not None
        assert "allergen" in data["alert"]

    def test_check_allergy_detects_cross_reactivity(self, client, mock_services):
        """Should detect cross-reactive medications"""
        # Patient 001 is allergic to Penicillin, Amoxicillin is cross-reactive
        response = client.post(
            "/allergies/patient-001/check-allergy",
            json={"medication_name": "Amoxicillin"},
        )
        data = response.json()

        assert data["hasConflict"] is True
        assert data["alert"]["isCrossReactive"] is True

    def test_check_allergy_patient_not_found(self, client, mock_services):
        """Should return 404 for unknown patient"""
        response = client.post(
            "/allergies/unknown-patient/check-allergy",
            json={"medication_name": "Ibuprofen"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_check_allergy_missing_medication_name(self, client, mock_services):
        """Should return 422 when medication_name is missing"""
        response = client.post(
            "/allergies/patient-001/check-allergy",
            json={},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_check_allergy_alert_structure(self, client, mock_services):
        """Alert should have expected structure"""
        response = client.post(
            "/allergies/patient-001/check-allergy",
            json={"medication_name": "Penicillin"},
        )
        data = response.json()

        alert = data["alert"]
        assert "blocked" in alert
        assert "severity" in alert
        assert "title" in alert
        assert "message" in alert
        assert "allergen" in alert
        assert "reaction" in alert
        assert "medicationName" in alert


@pytest.mark.unit
class TestCheckDrugInteractions:
    """Tests for POST /allergies/{patient_id}/check-interactions endpoint"""

    def test_check_interactions_returns_200(self, client, mock_services):
        """Should return 200 OK status for valid request"""
        response = client.post(
            "/allergies/patient-001/check-interactions",
            json={"medication_name": "Aspirin"},
        )
        assert response.status_code == status.HTTP_200_OK

    def test_check_interactions_no_interactions(self, client, mock_services):
        """Should return no interactions for safe combination"""
        # Patient 003 has minimal medications
        response = client.post(
            "/allergies/patient-003/check-interactions",
            json={"medication_name": "Acetaminophen"},
        )
        data = response.json()

        assert "hasInteractions" in data
        assert data["hasInteractions"] is False
        assert data["interactions"] == []

    def test_check_interactions_detects_warfarin_aspirin(self, client, mock_services):
        """Should detect warfarin-aspirin interaction"""
        # Patient 006 is on Warfarin
        response = client.post(
            "/allergies/patient-006/check-interactions",
            json={"medication_name": "Aspirin"},
        )
        data = response.json()

        assert data["hasInteractions"] is True
        assert len(data["interactions"]) > 0

    def test_check_interactions_patient_not_found(self, client, mock_services):
        """Should return 404 for unknown patient"""
        response = client.post(
            "/allergies/unknown-patient/check-interactions",
            json={"medication_name": "Aspirin"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_check_interactions_missing_medication_name(self, client, mock_services):
        """Should return 422 when medication_name is missing"""
        response = client.post(
            "/allergies/patient-001/check-interactions",
            json={},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_check_interactions_structure(self, client, mock_services):
        """Interaction should have expected structure"""
        response = client.post(
            "/allergies/patient-006/check-interactions",
            json={"medication_name": "Aspirin"},
        )
        data = response.json()

        if data["hasInteractions"]:
            interaction = data["interactions"][0]
            assert "interactingDrug" in interaction
            assert "severity" in interaction
            assert "description" in interaction


@pytest.mark.unit
class TestLogAllergyOverride:
    """Tests for POST /allergies/allergy-overrides endpoint"""

    def test_log_allergy_override_returns_200(self, client, mock_services):
        """Should return 200 OK status for valid request"""
        response = client.post(
            "/allergies/allergy-overrides",
            json={
                "patient_id": "patient-001",
                "medication_name": "Amoxicillin",
                "allergen": "Penicillin",
                "severity": "severe",
                "justification": "No alternatives available, patient consented",
                "acknowledged_at": "2024-01-15T10:00:00Z",
                "prescribed_at": "2024-01-15T10:05:00Z",
            },
        )
        assert response.status_code == status.HTTP_200_OK

    def test_log_allergy_override_structure(self, client, mock_services):
        """Response should have success and logId"""
        response = client.post(
            "/allergies/allergy-overrides",
            json={
                "patient_id": "patient-001",
                "medication_name": "Amoxicillin",
                "allergen": "Penicillin",
                "severity": "severe",
                "justification": "Clinical necessity",
                "acknowledged_at": "2024-01-15T10:00:00Z",
                "prescribed_at": "2024-01-15T10:05:00Z",
            },
        )
        data = response.json()

        assert "success" in data
        assert data["success"] is True
        assert "logId" in data
        assert data["logId"] is not None

    def test_log_allergy_override_missing_fields(self, client, mock_services):
        """Should return 422 for missing required fields"""
        response = client.post(
            "/allergies/allergy-overrides",
            json={
                "patient_id": "patient-001",
                # Missing other required fields
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.unit
class TestLogInteractionOverride:
    """Tests for POST /allergies/interaction-overrides endpoint"""

    def test_log_interaction_override_returns_200(self, client, mock_services):
        """Should return 200 OK status for valid request"""
        response = client.post(
            "/allergies/interaction-overrides",
            json={
                "patient_id": "patient-006",
                "medication_name": "Aspirin",
                "interacting_drugs": ["Warfarin"],
                "severities": ["major"],
                "justification": "Benefits outweigh risks, close monitoring planned",
                "acknowledged_at": "2024-01-15T10:00:00Z",
                "prescribed_at": "2024-01-15T10:05:00Z",
            },
        )
        assert response.status_code == status.HTTP_200_OK

    def test_log_interaction_override_structure(self, client, mock_services):
        """Response should have success and logId"""
        response = client.post(
            "/allergies/interaction-overrides",
            json={
                "patient_id": "patient-006",
                "medication_name": "Ibuprofen",
                "interacting_drugs": ["Warfarin"],
                "severities": ["major"],
                "justification": "Short-term use with monitoring",
                "acknowledged_at": "2024-01-15T10:00:00Z",
                "prescribed_at": "2024-01-15T10:05:00Z",
            },
        )
        data = response.json()

        assert "success" in data
        assert data["success"] is True
        assert "logId" in data
        assert data["logId"] is not None

    def test_log_interaction_override_missing_fields(self, client, mock_services):
        """Should return 422 for missing required fields"""
        response = client.post(
            "/allergies/interaction-overrides",
            json={
                "patient_id": "patient-006",
                "medication_name": "Aspirin",
                # Missing other required fields
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_log_interaction_override_multiple_drugs(self, client, mock_services):
        """Should handle multiple interacting drugs"""
        response = client.post(
            "/allergies/interaction-overrides",
            json={
                "patient_id": "patient-007",
                "medication_name": "NSAIDTest",
                "interacting_drugs": ["Warfarin", "Lisinopril"],
                "severities": ["major", "moderate"],
                "justification": "Comprehensive monitoring in place",
                "acknowledged_at": "2024-01-15T10:00:00Z",
                "prescribed_at": "2024-01-15T10:05:00Z",
            },
        )
        assert response.status_code == status.HTTP_200_OK
