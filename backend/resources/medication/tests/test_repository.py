"""
Unit tests for MedicationRepository.
"""
import asyncio
import pytest

from resources.medication import Medication, MedicationRepository
from resources.core import CodeableConcept


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestMedicationRepository:
    """Tests for MedicationRepository."""

    @pytest.fixture
    def repo(self):
        """Create a repository."""
        return MedicationRepository()

    @pytest.fixture
    def test_medications(self, repo):
        """Create test medications."""
        medications = [
            Medication(
                id="med-001",
                code=CodeableConcept(code="lisinopril", display="Lisinopril"),
                form="tablet",
                strength="10mg",
                is_controlled=False,
                status="active",
            ),
            Medication(
                id="med-002",
                code=CodeableConcept(code="metformin", display="Metformin"),
                form="tablet",
                strength="500mg",
                is_controlled=False,
                status="active",
            ),
            Medication(
                id="med-003",
                code=CodeableConcept(code="oxycodone", display="Oxycodone"),
                form="tablet",
                strength="5mg",
                is_controlled=True,
                status="active",
            ),
            Medication(
                id="med-004",
                code=CodeableConcept(code="amoxicillin", display="Amoxicillin"),
                form="capsule",
                strength="250mg",
                is_controlled=False,
                status="inactive",
            ),
        ]
        for m in medications:
            repo._store[m.id] = m
        return medications

    def test_list_all(self, repo, test_medications):
        """list with no filters returns all medications."""
        result = run_async(repo.list())
        assert len(result) == 4

    def test_list_filter_by_name(self, repo, test_medications):
        """list filters by name partial match."""
        result = run_async(repo.list(name="lisin"))
        assert len(result) == 1
        assert result[0].id == "med-001"

    def test_list_filter_by_name_case_insensitive(self, repo, test_medications):
        """list name filter is case insensitive."""
        result = run_async(repo.list(name="METFORMIN"))
        assert len(result) == 1
        assert result[0].id == "med-002"

    def test_list_filter_by_controlled(self, repo, test_medications):
        """list filters by controlled substance status."""
        result = run_async(repo.list(is_controlled=True))
        assert len(result) == 1
        assert result[0].id == "med-003"

    def test_list_filter_by_not_controlled(self, repo, test_medications):
        """list filters by non-controlled status."""
        result = run_async(repo.list(is_controlled=False))
        assert len(result) == 3

    def test_list_filter_by_status(self, repo, test_medications):
        """list filters by status."""
        result = run_async(repo.list(status="inactive"))
        assert len(result) == 1
        assert result[0].id == "med-004"

    def test_list_multiple_filters(self, repo, test_medications):
        """list with multiple filters applies all."""
        result = run_async(repo.list(is_controlled=False, status="active"))
        assert len(result) == 2
        ids = {m.id for m in result}
        assert ids == {"med-001", "med-002"}

    def test_search_by_name(self, repo, test_medications):
        """search returns medications matching query."""
        result = run_async(repo.search("oxy"))
        assert len(result) == 1
        assert result[0].id == "med-003"

    def test_search_case_insensitive(self, repo, test_medications):
        """search is case insensitive."""
        result = run_async(repo.search("AMOX"))
        assert len(result) == 1
        assert result[0].id == "med-004"

    def test_search_partial_match(self, repo, test_medications):
        """search matches partial names."""
        result = run_async(repo.search("in"))  # matches Lisinopril, Metformin, Amoxicillin
        assert len(result) == 3

    def test_search_no_results(self, repo, test_medications):
        """search returns empty list when no matches."""
        result = run_async(repo.search("xyz123"))
        assert result == []

    def test_get_by_id(self, repo, test_medications):
        """get returns medication by ID."""
        result = run_async(repo.get("med-002"))
        assert result is not None
        assert result.name == "Metformin"

    def test_get_by_id_not_found(self, repo, test_medications):
        """get returns None when ID doesn't exist."""
        result = run_async(repo.get("nonexistent"))
        assert result is None

    def test_create(self, repo):
        """create adds a new medication."""
        new_med = Medication(
            id="med-new",
            code=CodeableConcept(code="aspirin", display="Aspirin"),
            form="tablet",
            strength="81mg",
            is_controlled=False,
        )
        result = run_async(repo.create(new_med))
        assert result.id == "med-new"

        # Verify it's stored
        stored = run_async(repo.get("med-new"))
        assert stored is not None
        assert stored.name == "Aspirin"

    def test_update(self, repo, test_medications):
        """update modifies an existing medication."""
        updated = Medication(
            id="med-001",
            code=CodeableConcept(code="lisinopril", display="Lisinopril"),
            form="tablet",
            strength="20mg",  # Changed strength
            is_controlled=False,
        )
        result = run_async(repo.update("med-001", updated))
        assert result is not None
        assert result.strength == "20mg"

    def test_delete(self, repo, test_medications):
        """delete removes a medication."""
        result = run_async(repo.delete("med-001"))
        assert result is True

        # Verify it's gone
        stored = run_async(repo.get("med-001"))
        assert stored is None
