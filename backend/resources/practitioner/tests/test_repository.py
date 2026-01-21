"""
Unit tests for PractitionerRepository.
"""
import asyncio
import pytest

from resources.practitioner import Practitioner, PractitionerRepository
from resources.core import HumanName, Identifier


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestPractitionerRepository:
    """Tests for PractitionerRepository."""

    @pytest.fixture
    def repo(self):
        """Create a repository."""
        return PractitionerRepository()

    @pytest.fixture
    def test_practitioners(self, repo):
        """Create test practitioners."""
        practitioners = [
            Practitioner(
                id="pract-001",
                name=HumanName(given=["John"], family="Smith"),
                active=True,
                identifiers=[Identifier(system="http://hl7.org/fhir/sid/us-npi", value="1234567890")],
            ),
            Practitioner(
                id="pract-002",
                name=HumanName(given=["Jane"], family="Doe"),
                active=True,
                identifiers=[Identifier(system="http://hl7.org/fhir/sid/us-npi", value="0987654321")],
            ),
            Practitioner(
                id="pract-003",
                name=HumanName(given=["Bob"], family="Johnson"),
                active=False,
                identifiers=[Identifier(system="http://hl7.org/fhir/sid/us-npi", value="5555555555")],
            ),
        ]
        for p in practitioners:
            repo._store[p.id] = p
        return practitioners

    def test_list_all(self, repo, test_practitioners):
        """list with no filters returns all practitioners."""
        result = run_async(repo.list())
        assert len(result) == 3

    def test_list_filter_by_active(self, repo, test_practitioners):
        """list filters by active status."""
        result = run_async(repo.list(active=True))
        assert len(result) == 2
        assert all(p.active for p in result)

    def test_list_filter_by_inactive(self, repo, test_practitioners):
        """list filters by inactive status."""
        result = run_async(repo.list(active=False))
        assert len(result) == 1
        assert result[0].id == "pract-003"

    def test_list_filter_by_name(self, repo, test_practitioners):
        """list filters by name partial match."""
        result = run_async(repo.list(name="smith"))
        assert len(result) == 1
        assert result[0].id == "pract-001"

    def test_list_filter_by_name_case_insensitive(self, repo, test_practitioners):
        """list name filter is case insensitive."""
        result = run_async(repo.list(name="JOHN"))
        assert len(result) == 2  # John Smith and Bob Johnson

    def test_list_multiple_filters(self, repo, test_practitioners):
        """list with multiple filters applies all."""
        result = run_async(repo.list(active=True, name="doe"))
        assert len(result) == 1
        assert result[0].id == "pract-002"

    def test_get_by_npi_found(self, repo, test_practitioners):
        """get_by_npi returns practitioner when NPI exists."""
        result = run_async(repo.get_by_npi("1234567890"))
        assert result is not None
        assert result.id == "pract-001"

    def test_get_by_npi_not_found(self, repo, test_practitioners):
        """get_by_npi returns None when NPI doesn't exist."""
        result = run_async(repo.get_by_npi("9999999999"))
        assert result is None

    def test_get_by_id(self, repo, test_practitioners):
        """get returns practitioner by ID."""
        result = run_async(repo.get("pract-002"))
        assert result is not None
        assert result.name.family == "Doe"

    def test_get_by_id_not_found(self, repo, test_practitioners):
        """get returns None when ID doesn't exist."""
        result = run_async(repo.get("nonexistent"))
        assert result is None

    def test_create(self, repo):
        """create adds a new practitioner."""
        new_pract = Practitioner(
            id="pract-new",
            name=HumanName(given=["New"], family="Doctor"),
            active=True,
        )
        result = run_async(repo.create(new_pract))
        assert result.id == "pract-new"

        # Verify it's stored
        stored = run_async(repo.get("pract-new"))
        assert stored is not None
        assert stored.name.family == "Doctor"

    def test_update(self, repo, test_practitioners):
        """update modifies an existing practitioner."""
        updated = Practitioner(
            id="pract-001",
            name=HumanName(given=["John", "Updated"], family="Smith"),
            active=False,
        )
        result = run_async(repo.update("pract-001", updated))
        assert result is not None
        assert result.active is False
        assert "Updated" in result.name.given

    def test_delete(self, repo, test_practitioners):
        """delete removes a practitioner."""
        result = run_async(repo.delete("pract-001"))
        assert result is True

        # Verify it's gone
        stored = run_async(repo.get("pract-001"))
        assert stored is None
