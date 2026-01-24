"""Tests for social and family history repository."""

import asyncio
import pytest

from resources.social_family_history.model import (
    SocialFamilyHistory,
    SocialHistory,
    FamilyHistory,
    SmokingHistory,
)
from resources.social_family_history.repository import SocialFamilyHistoryRepository
from resources.core import Reference


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.fixture
def repo():
    """Create a fresh repository for each test."""
    return SocialFamilyHistoryRepository()


@pytest.fixture
def sample_histories():
    """Create sample social/family histories for testing."""
    histories = [
        SocialFamilyHistory(
            id="sfh-001",
            subject=Reference.to("Patient", "patient-001", "Patient One"),
            social_history=SocialHistory(
                smoking=SmokingHistory(status="former"),
                occupation="Teacher",
            ),
        ),
        SocialFamilyHistory(
            id="sfh-002",
            subject=Reference.to("Patient", "patient-002", "Patient Two"),
            social_history=SocialHistory(
                smoking=SmokingHistory(status="never"),
                occupation="Engineer",
            ),
        ),
        SocialFamilyHistory(
            id="sfh-003",
            subject=Reference.to("Patient", "patient-003", "Patient Three"),
            social_history=SocialHistory(
                smoking=SmokingHistory(status="current_daily"),
                occupation="Nurse",
            ),
        ),
    ]

    return histories


@pytest.mark.unit
class TestSocialFamilyHistoryRepository:
    """Tests for SocialFamilyHistoryRepository."""

    def test_create_and_get(self, repo):
        """Test creating and retrieving a social/family history."""
        history = SocialFamilyHistory(
            id="sfh-1",
            subject=Reference.to("Patient", "patient-001", "Test Patient"),
            social_history=SocialHistory(occupation="Doctor"),
        )

        run_async(repo.create(history))
        retrieved = run_async(repo.get("sfh-1"))

        assert retrieved is not None
        assert retrieved.id == "sfh-1"
        assert retrieved.social_history.occupation == "Doctor"

    def test_get_nonexistent(self, repo):
        """Test getting a nonexistent record."""
        retrieved = run_async(repo.get("sfh-999"))

        assert retrieved is None

    def test_list_all(self, repo, sample_histories):
        """Test listing all histories."""
        for history in sample_histories:
            repo._store[history.id] = history

        results = run_async(repo.list())

        assert len(results) == 3

    def test_list_by_patient_id(self, repo, sample_histories):
        """Test filtering by patient ID."""
        for history in sample_histories:
            repo._store[history.id] = history

        results = run_async(repo.list(patient_id="patient-001"))

        assert len(results) == 1
        assert results[0].patient_id == "patient-001"

    def test_list_by_nonexistent_patient(self, repo, sample_histories):
        """Test filtering by nonexistent patient ID."""
        for history in sample_histories:
            repo._store[history.id] = history

        results = run_async(repo.list(patient_id="patient-999"))

        assert len(results) == 0

    def test_get_by_patient(self, repo, sample_histories):
        """Test getting history for a specific patient."""
        for history in sample_histories:
            repo._store[history.id] = history

        result = run_async(repo.get_by_patient("patient-002"))

        assert result is not None
        assert result.id == "sfh-002"
        assert result.social_history.occupation == "Engineer"

    def test_get_by_patient_not_found(self, repo, sample_histories):
        """Test getting history for nonexistent patient."""
        for history in sample_histories:
            repo._store[history.id] = history

        result = run_async(repo.get_by_patient("patient-999"))

        assert result is None

    def test_get_by_patient_empty_repo(self, repo):
        """Test getting history from empty repository."""
        result = run_async(repo.get_by_patient("patient-001"))

        assert result is None

    def test_update(self, repo, sample_histories):
        """Test updating a history record."""
        for history in sample_histories:
            repo._store[history.id] = history

        # Get the record and modify it
        history = run_async(repo.get("sfh-001"))
        history.social_history.occupation = "Principal"

        updated = run_async(repo.update("sfh-001", history))

        assert updated is not None
        assert updated.social_history.occupation == "Principal"

        # Verify it's persisted
        retrieved = run_async(repo.get("sfh-001"))
        assert retrieved.social_history.occupation == "Principal"

    def test_update_nonexistent(self, repo):
        """Test updating a nonexistent record."""
        history = SocialFamilyHistory(
            id="sfh-999",
            subject=Reference.to("Patient", "patient-999", "Test"),
        )

        result = run_async(repo.update("sfh-999", history))

        assert result is None

    def test_delete(self, repo, sample_histories):
        """Test deleting a history record."""
        for history in sample_histories:
            repo._store[history.id] = history

        result = run_async(repo.delete("sfh-001"))
        assert result is True

        # Verify it's deleted
        retrieved = run_async(repo.get("sfh-001"))
        assert retrieved is None

    def test_delete_nonexistent(self, repo):
        """Test deleting a nonexistent record."""
        result = run_async(repo.delete("sfh-999"))

        assert result is False

    def test_seed_helper(self, repo):
        """Test the _seed helper method."""
        histories = [
            SocialFamilyHistory(
                id="sfh-1",
                subject=Reference.to("Patient", "patient-001", "Test"),
            ),
            SocialFamilyHistory(
                id="sfh-2",
                subject=Reference.to("Patient", "patient-002", "Test"),
            ),
        ]

        repo._seed(histories)

        assert len(repo._store) == 2
        assert "sfh-1" in repo._store
        assert "sfh-2" in repo._store
