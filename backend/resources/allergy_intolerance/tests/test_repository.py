"""
Unit tests for AllergyIntoleranceRepository.

Tests filtering by clinical_status and the new get_all_by_patient method.
"""
import asyncio
import pytest
from datetime import datetime

from resources.allergy_intolerance import (
    AllergyIntolerance,
    AllergyReaction,
    AllergyCategory,
    AllergyIntoleranceRepository,
)
from resources.core import Reference, CodeableConcept


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestAllergyIntoleranceRepository:
    """Tests for AllergyIntoleranceRepository."""

    @pytest.fixture
    def repo(self):
        """Create a repository with test data."""
        repo = AllergyIntoleranceRepository()
        return repo

    @pytest.fixture
    def test_allergies(self, repo):
        """Create test allergies with various clinical statuses."""
        allergies = [
            # Active allergies for patient-001
            AllergyIntolerance(
                id="allergy-1",
                patient=Reference(reference="Patient/patient-001"),
                code=CodeableConcept(code="penicillin", display="Penicillin"),
                clinical_status="active",
                reactions=[AllergyReaction(manifestation="Anaphylaxis", severity="severe")],
            ),
            AllergyIntolerance(
                id="allergy-2",
                patient=Reference(reference="Patient/patient-001"),
                code=CodeableConcept(code="sulfa", display="Sulfa"),
                clinical_status="active",
                reactions=[AllergyReaction(manifestation="Rash", severity="moderate")],
            ),
            # Inactive allergy for patient-001
            AllergyIntolerance(
                id="allergy-3",
                patient=Reference(reference="Patient/patient-001"),
                code=CodeableConcept(code="aspirin", display="Aspirin"),
                clinical_status="inactive",
                reactions=[AllergyReaction(manifestation="GI upset", severity="mild")],
            ),
            # Resolved allergy for patient-001
            AllergyIntolerance(
                id="allergy-4",
                patient=Reference(reference="Patient/patient-001"),
                code=CodeableConcept(code="egg", display="Egg"),
                category=AllergyCategory.FOOD,
                clinical_status="resolved",
                reactions=[AllergyReaction(manifestation="Hives", severity="mild")],
            ),
            # Active allergy for patient-002
            AllergyIntolerance(
                id="allergy-5",
                patient=Reference(reference="Patient/patient-002"),
                code=CodeableConcept(code="latex", display="Latex"),
                category=AllergyCategory.ENVIRONMENT,
                clinical_status="active",
                reactions=[AllergyReaction(manifestation="Contact dermatitis", severity="mild")],
            ),
        ]
        for allergy in allergies:
            repo._store[allergy.id] = allergy
        return allergies

    def test_get_by_patient_returns_only_active_by_default(self, repo, test_allergies):
        """get_by_patient should return only active allergies by default."""
        result = run_async(repo.get_by_patient("patient-001"))

        assert len(result) == 2
        assert all(a.clinical_status == "active" for a in result)
        allergen_names = {a.allergen for a in result}
        assert allergen_names == {"Penicillin", "Sulfa"}

    def test_get_by_patient_with_include_inactive(self, repo, test_allergies):
        """get_by_patient with include_inactive=True should return all allergies."""
        result = run_async(repo.get_by_patient("patient-001", include_inactive=True))

        assert len(result) == 4
        statuses = {a.clinical_status for a in result}
        assert statuses == {"active", "inactive", "resolved"}

    def test_get_all_by_patient_returns_all_statuses(self, repo, test_allergies):
        """get_all_by_patient should return all allergies regardless of status."""
        result = run_async(repo.get_all_by_patient("patient-001"))

        assert len(result) == 4
        allergen_names = {a.allergen for a in result}
        assert allergen_names == {"Penicillin", "Sulfa", "Aspirin", "Egg"}

    def test_get_by_patient_filters_by_patient(self, repo, test_allergies):
        """get_by_patient should only return allergies for the specified patient."""
        result = run_async(repo.get_by_patient("patient-002"))

        assert len(result) == 1
        assert result[0].allergen == "Latex"

    def test_get_by_patient_empty_for_unknown_patient(self, repo, test_allergies):
        """get_by_patient should return empty list for unknown patient."""
        result = run_async(repo.get_by_patient("patient-999"))

        assert result == []

    def test_list_with_clinical_status_filter(self, repo, test_allergies):
        """list should filter by clinical_status when provided."""
        result = run_async(repo.list(patient_id="patient-001", clinical_status="inactive"))

        assert len(result) == 1
        assert result[0].allergen == "Aspirin"

    def test_list_with_resolved_status(self, repo, test_allergies):
        """list should find resolved allergies."""
        result = run_async(repo.list(patient_id="patient-001", clinical_status="resolved"))

        assert len(result) == 1
        assert result[0].allergen == "Egg"
