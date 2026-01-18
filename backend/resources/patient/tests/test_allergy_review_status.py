"""
Unit tests for AllergyReviewStatus model and patient allergy review functionality.
"""
import asyncio
import pytest
from datetime import datetime, timedelta

from resources.patient import Patient, AllergyReviewStatus
from resources.patient.repository import PatientRepository
from resources.core import HumanName, Reference


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestAllergyReviewStatus:
    """Tests for the AllergyReviewStatus model."""

    def test_is_stale_false_when_reviewed_recently(self):
        """is_stale should return False when reviewed within the last year."""
        review_status = AllergyReviewStatus(
            reviewed_at=datetime.now() - timedelta(days=30),
        )
        assert review_status.is_stale is False

    def test_is_stale_false_at_exactly_one_year(self):
        """is_stale should return False at exactly 365 days."""
        review_status = AllergyReviewStatus(
            reviewed_at=datetime.now() - timedelta(days=365),
        )
        assert review_status.is_stale is False

    def test_is_stale_true_when_over_one_year(self):
        """is_stale should return True when reviewed over a year ago."""
        review_status = AllergyReviewStatus(
            reviewed_at=datetime.now() - timedelta(days=400),
        )
        assert review_status.is_stale is True

    def test_is_stale_true_when_much_older(self):
        """is_stale should return True for very old reviews."""
        review_status = AllergyReviewStatus(
            reviewed_at=datetime.now() - timedelta(days=1000),
        )
        assert review_status.is_stale is True

    def test_reviewer_name_from_reference(self):
        """reviewer_name should return display name from reference."""
        review_status = AllergyReviewStatus(
            reviewed_at=datetime.now(),
            reviewed_by=Reference(
                reference="Practitioner/provider-001",
                display="Dr. Elizabeth Frost",
            ),
        )
        assert review_status.reviewer_name == "Dr. Elizabeth Frost"

    def test_reviewer_name_none_when_no_reviewer(self):
        """reviewer_name should return None when no reviewer set."""
        review_status = AllergyReviewStatus(
            reviewed_at=datetime.now(),
        )
        assert review_status.reviewer_name is None

    def test_reviewer_name_none_when_no_display(self):
        """reviewer_name should return None when reference has no display."""
        review_status = AllergyReviewStatus(
            reviewed_at=datetime.now(),
            reviewed_by=Reference(reference="Practitioner/provider-001"),
        )
        assert review_status.reviewer_name is None


class TestPatientAllergyReviewStatusInBffDict:
    """Tests for allergy review status in Patient.to_bff_dict()."""

    def test_bff_dict_includes_allergy_review_status(self):
        """to_bff_dict should include allergyReviewStatus when set."""
        review_time = datetime(2024, 6, 15, 10, 30, 0)
        patient = Patient(
            id="patient-001",
            name=HumanName(family="Johnson", given=["Sarah"]),
            allergy_review_status=AllergyReviewStatus(
                reviewed_at=review_time,
                reviewed_by=Reference(
                    reference="Practitioner/provider-001",
                    display="Dr. Elizabeth Frost",
                ),
            ),
        )
        result = patient.to_bff_dict()

        assert "allergyReviewStatus" in result
        assert result["allergyReviewStatus"]["reviewedAt"] == review_time.isoformat()
        assert result["allergyReviewStatus"]["reviewedBy"] == "Dr. Elizabeth Frost"
        assert "isStale" in result["allergyReviewStatus"]

    def test_bff_dict_excludes_allergy_review_status_when_not_set(self):
        """to_bff_dict should not include allergyReviewStatus when not set."""
        patient = Patient(
            id="patient-001",
            name=HumanName(family="Johnson", given=["Sarah"]),
        )
        result = patient.to_bff_dict()

        assert "allergyReviewStatus" not in result

    def test_bff_dict_shows_stale_review(self):
        """to_bff_dict should show isStale: true for old reviews."""
        old_review_time = datetime.now() - timedelta(days=400)
        patient = Patient(
            id="patient-001",
            name=HumanName(family="Johnson", given=["Sarah"]),
            allergy_review_status=AllergyReviewStatus(
                reviewed_at=old_review_time,
            ),
        )
        result = patient.to_bff_dict()

        assert result["allergyReviewStatus"]["isStale"] is True

    def test_bff_dict_shows_fresh_review(self):
        """to_bff_dict should show isStale: false for recent reviews."""
        recent_review_time = datetime.now() - timedelta(days=30)
        patient = Patient(
            id="patient-001",
            name=HumanName(family="Johnson", given=["Sarah"]),
            allergy_review_status=AllergyReviewStatus(
                reviewed_at=recent_review_time,
            ),
        )
        result = patient.to_bff_dict()

        assert result["allergyReviewStatus"]["isStale"] is False


class TestPatientRepositoryMarkAllergiesReviewed:
    """Tests for PatientRepository.mark_allergies_reviewed()."""

    @pytest.fixture
    def repo(self):
        """Create a patient repository with test data."""
        repo = PatientRepository()
        return repo

    @pytest.fixture
    def patient(self, repo):
        """Create a test patient."""
        patient = Patient(
            id="patient-test",
            name=HumanName(family="Test", given=["Patient"]),
        )
        repo._store[patient.id] = patient
        return patient

    def test_mark_allergies_reviewed_updates_patient(self, repo, patient):
        """mark_allergies_reviewed should update patient's allergy review status."""
        result = run_async(repo.mark_allergies_reviewed(patient_id=patient.id))

        assert result is not None
        assert result.allergy_review_status is not None
        assert result.allergy_review_status.reviewed_at is not None
        assert result.allergy_review_status.is_stale is False

    def test_mark_allergies_reviewed_with_reviewer(self, repo, patient):
        """mark_allergies_reviewed should include reviewer info when provided."""
        result = run_async(repo.mark_allergies_reviewed(
            patient_id=patient.id,
            reviewer_id="provider-001",
            reviewer_name="Dr. Test Provider",
        ))

        assert result is not None
        assert result.allergy_review_status.reviewed_by is not None
        assert result.allergy_review_status.reviewer_name == "Dr. Test Provider"

    def test_mark_allergies_reviewed_returns_none_for_missing_patient(self, repo):
        """mark_allergies_reviewed should return None for non-existent patient."""
        result = run_async(repo.mark_allergies_reviewed(patient_id="nonexistent"))

        assert result is None

    def test_mark_allergies_reviewed_overwrites_existing(self, repo, patient):
        """mark_allergies_reviewed should overwrite existing review status."""
        # First review
        patient.allergy_review_status = AllergyReviewStatus(
            reviewed_at=datetime.now() - timedelta(days=400),
        )

        # Mark as reviewed again
        result = run_async(repo.mark_allergies_reviewed(
            patient_id=patient.id,
            reviewer_id="provider-002",
            reviewer_name="Dr. New Provider",
        ))

        assert result is not None
        assert result.allergy_review_status.is_stale is False
        assert result.allergy_review_status.reviewer_name == "Dr. New Provider"
