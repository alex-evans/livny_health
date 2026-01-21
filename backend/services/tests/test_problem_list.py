"""
Unit tests for ProblemListService.

Tests problem list retrieval, sorting, and status management.
"""
import asyncio
import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock

from services.problem_list import ProblemListService, ProblemListResponse, ProblemGroup, CATEGORY_LABELS
from resources import (
    Patient,
    PatientRepository,
    Problem,
    ProblemStatus,
    ProblemPriority,
    ProblemSeverity,
    ClinicalCategory,
)


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.mark.unit
class TestProblemListServiceIntegration:
    """Integration tests using seeded data."""

    def test_get_problem_list_for_patient(self, problem_list_service):
        """Should retrieve problem list for existing patient."""
        response = run_async(problem_list_service.get_problem_list(
            patient_id="patient-001",
        ))

        assert response is not None
        assert response.total_count >= 0
        assert isinstance(response.problems, list)

    def test_get_problem_list_nonexistent_patient(self, problem_list_service):
        """Should return None for non-existent patient."""
        response = run_async(problem_list_service.get_problem_list(
            patient_id="nonexistent-patient",
        ))

        assert response is None


@pytest.mark.unit
class TestProblemListServiceUnit:
    """Unit tests with mocked repository."""

    @pytest.fixture
    def mock_patient_repo(self):
        """Create a mock patient repository."""
        return MagicMock(spec=PatientRepository)

    @pytest.fixture
    def service(self, mock_patient_repo):
        """Create service with mocked repo."""
        return ProblemListService(patient_repo=mock_patient_repo)

    @pytest.fixture
    def sample_problems(self):
        """Create sample problems for testing."""
        today = date.today()
        return [
            Problem(
                name="Type 2 Diabetes Mellitus",
                icd10_code="E11.9",
                onset_date=today - timedelta(days=365),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
                is_critical=False,
            ),
            Problem(
                name="Essential Hypertension",
                icd10_code="I10",
                onset_date=today - timedelta(days=180),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
                is_critical=False,
            ),
            Problem(
                name="Acute bronchitis",
                icd10_code="J20.9",
                onset_date=today - timedelta(days=7),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.ACUTE,
                is_critical=False,
            ),
            Problem(
                name="Heart Failure",
                icd10_code="I50.9",
                onset_date=today - timedelta(days=100),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
                is_critical=True,
            ),
            Problem(
                name="Resolved Pneumonia",
                icd10_code="J18.9",
                onset_date=today - timedelta(days=200),
                status=ProblemStatus.RESOLVED,
                priority=ProblemPriority.RESOLVED,
                is_critical=False,
                resolved_date=today - timedelta(days=170),
            ),
        ]

    def test_get_problem_list_with_problems(self, service, mock_patient_repo, sample_problems):
        """Should return sorted problem list."""
        patient = MagicMock(spec=Patient)
        patient.problem_list = sample_problems
        mock_patient_repo.get = AsyncMock(return_value=patient)

        response = run_async(service.get_problem_list(patient_id="patient-001"))

        assert response is not None
        assert response.total_count == 5
        assert response.active_count == 4
        assert response.critical_count == 1
        assert len(response.problems) == 5

    def test_get_problem_list_exclude_resolved(self, service, mock_patient_repo, sample_problems):
        """Should exclude resolved problems when requested."""
        patient = MagicMock(spec=Patient)
        patient.problem_list = sample_problems
        mock_patient_repo.get = AsyncMock(return_value=patient)

        response = run_async(service.get_problem_list(
            patient_id="patient-001",
            include_resolved=False,
        ))

        assert response is not None
        assert response.total_count == 4
        assert all(p.status != ProblemStatus.RESOLVED for p in response.problems)

    def test_get_problem_list_empty(self, service, mock_patient_repo):
        """Should handle patient with no problems."""
        patient = MagicMock(spec=Patient)
        patient.problem_list = []
        mock_patient_repo.get = AsyncMock(return_value=patient)

        response = run_async(service.get_problem_list(patient_id="patient-001"))

        assert response is not None
        assert response.total_count == 0
        assert response.active_count == 0
        assert response.problems == []

    def test_get_problem_list_patient_not_found(self, service, mock_patient_repo):
        """Should return None for non-existent patient."""
        mock_patient_repo.get = AsyncMock(return_value=None)

        response = run_async(service.get_problem_list(patient_id="nonexistent"))

        assert response is None


@pytest.mark.unit
class TestProblemSorting:
    """Tests for problem sorting logic."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repo."""
        mock_repo = MagicMock(spec=PatientRepository)
        return ProblemListService(patient_repo=mock_repo)

    def test_sort_critical_first(self, service):
        """Should sort critical problems first."""
        today = date.today()
        problems = [
            Problem(name="Non-critical", icd10_code="A00", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.ACUTE, is_critical=False),
            Problem(name="Critical", icd10_code="B00", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC, is_critical=True),
        ]

        sorted_problems = service.sort_by_priority(problems)

        assert sorted_problems[0].name == "Critical"
        assert sorted_problems[1].name == "Non-critical"

    def test_sort_acute_before_chronic(self, service):
        """Should sort acute problems before chronic."""
        today = date.today()
        problems = [
            Problem(name="Chronic", icd10_code="A00", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC),
            Problem(name="Acute", icd10_code="B00", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.ACUTE),
        ]

        sorted_problems = service.sort_by_priority(problems)

        assert sorted_problems[0].name == "Acute"
        assert sorted_problems[1].name == "Chronic"

    def test_sort_resolved_last(self, service):
        """Should sort resolved problems last."""
        today = date.today()
        problems = [
            Problem(name="Resolved", icd10_code="A00", onset_date=today, status=ProblemStatus.RESOLVED, priority=ProblemPriority.RESOLVED),
            Problem(name="Active", icd10_code="B00", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC),
        ]

        sorted_problems = service.sort_by_priority(problems)

        assert sorted_problems[0].name == "Active"
        assert sorted_problems[1].name == "Resolved"

    def test_sort_by_onset_within_priority(self, service):
        """Should sort by onset date within same priority."""
        today = date.today()
        problems = [
            Problem(name="Older", icd10_code="A00", onset_date=today - timedelta(days=30), status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC),
            Problem(name="Newer", icd10_code="B00", onset_date=today - timedelta(days=5), status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC),
        ]

        sorted_problems = service.sort_by_priority(problems)

        assert sorted_problems[0].name == "Newer"
        assert sorted_problems[1].name == "Older"


@pytest.mark.unit
class TestProblemFiltering:
    """Tests for problem filtering methods."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repo."""
        mock_repo = MagicMock(spec=PatientRepository)
        return ProblemListService(patient_repo=mock_repo)

    @pytest.fixture
    def mixed_problems(self):
        """Create problems with mixed statuses."""
        today = date.today()
        return [
            Problem(name="Active1", icd10_code="A00", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC),
            Problem(name="Active2", icd10_code="B00", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.ACUTE),
            Problem(name="Inactive", icd10_code="C00", onset_date=today, status=ProblemStatus.INACTIVE, priority=ProblemPriority.INACTIVE),
            Problem(name="Resolved", icd10_code="D00", onset_date=today, status=ProblemStatus.RESOLVED, priority=ProblemPriority.RESOLVED),
        ]

    def test_get_active_problems(self, service, mixed_problems):
        """Should return only active problems."""
        active = service.get_active_problems(mixed_problems)

        assert len(active) == 2
        assert all(p.status == ProblemStatus.ACTIVE for p in active)

    def test_get_problems_by_status_resolved(self, service, mixed_problems):
        """Should filter by resolved status."""
        resolved = service.get_problems_by_status(mixed_problems, ProblemStatus.RESOLVED)

        assert len(resolved) == 1
        assert resolved[0].name == "Resolved"

    def test_get_problems_by_status_inactive(self, service, mixed_problems):
        """Should filter by inactive status."""
        inactive = service.get_problems_by_status(mixed_problems, ProblemStatus.INACTIVE)

        assert len(inactive) == 1
        assert inactive[0].name == "Inactive"


@pytest.mark.unit
class TestProblemStatusUpdate:
    """Tests for problem status update methods."""

    @pytest.fixture
    def mock_patient_repo(self):
        """Create a mock patient repository."""
        return MagicMock(spec=PatientRepository)

    @pytest.fixture
    def service(self, mock_patient_repo):
        """Create service with mocked repo."""
        return ProblemListService(patient_repo=mock_patient_repo)

    @pytest.fixture
    def patient_with_problems(self):
        """Create patient with problems."""
        today = date.today()
        patient = MagicMock(spec=Patient)
        patient.problem_list = [
            Problem(
                name="Type 2 Diabetes",
                icd10_code="E11.9",
                onset_date=today - timedelta(days=365),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
            ),
            Problem(
                name="Hypertension",
                icd10_code="I10",
                onset_date=today - timedelta(days=180),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
            ),
        ]
        return patient

    def test_update_problem_status_to_resolved(self, service, mock_patient_repo, patient_with_problems):
        """Should update problem status to resolved."""
        mock_patient_repo.get = AsyncMock(return_value=patient_with_problems)
        mock_patient_repo.update = AsyncMock(return_value=patient_with_problems)

        result = run_async(service.update_problem_status(
            patient_id="patient-001",
            icd10_code="E11.9",
            new_status=ProblemStatus.RESOLVED,
            provider_name="Dr. Smith",
        ))

        assert result is not None
        assert result.status == ProblemStatus.RESOLVED
        assert result.resolved_date == date.today()
        assert result.resolved_by_provider == "Dr. Smith"

    def test_update_problem_status_reactivate(self, service, mock_patient_repo):
        """Should reactivate a resolved problem."""
        today = date.today()
        patient = MagicMock(spec=Patient)
        patient.problem_list = [
            Problem(
                name="Resolved Problem",
                icd10_code="A00",
                onset_date=today - timedelta(days=100),
                status=ProblemStatus.RESOLVED,
                priority=ProblemPriority.RESOLVED,
                resolved_date=today - timedelta(days=30),
                resolved_by_provider="Dr. Jones",
            ),
        ]
        mock_patient_repo.get = AsyncMock(return_value=patient)
        mock_patient_repo.update = AsyncMock(return_value=patient)

        result = run_async(service.update_problem_status(
            patient_id="patient-001",
            icd10_code="A00",
            new_status=ProblemStatus.ACTIVE,
            provider_name="Dr. Smith",
        ))

        assert result is not None
        assert result.status == ProblemStatus.ACTIVE
        assert result.resolved_date is None
        assert result.resolved_by_provider is None

    def test_update_problem_status_not_found(self, service, mock_patient_repo, patient_with_problems):
        """Should return None when problem not found."""
        mock_patient_repo.get = AsyncMock(return_value=patient_with_problems)

        result = run_async(service.update_problem_status(
            patient_id="patient-001",
            icd10_code="NONEXISTENT",
            new_status=ProblemStatus.RESOLVED,
            provider_name="Dr. Smith",
        ))

        assert result is None

    def test_update_problem_status_patient_not_found(self, service, mock_patient_repo):
        """Should return None when patient not found."""
        mock_patient_repo.get = AsyncMock(return_value=None)

        result = run_async(service.update_problem_status(
            patient_id="nonexistent",
            icd10_code="E11.9",
            new_status=ProblemStatus.RESOLVED,
            provider_name="Dr. Smith",
        ))

        assert result is None

    def test_resolve_problem_convenience_method(self, service, mock_patient_repo, patient_with_problems):
        """Should resolve problem using convenience method."""
        mock_patient_repo.get = AsyncMock(return_value=patient_with_problems)
        mock_patient_repo.update = AsyncMock(return_value=patient_with_problems)

        result = run_async(service.resolve_problem(
            patient_id="patient-001",
            icd10_code="I10",
            provider_name="Dr. Smith",
        ))

        assert result is not None
        assert result.status == ProblemStatus.RESOLVED

    def test_reactivate_problem_convenience_method(self, service, mock_patient_repo):
        """Should reactivate problem using convenience method."""
        today = date.today()
        patient = MagicMock(spec=Patient)
        patient.problem_list = [
            Problem(
                name="Resolved Problem",
                icd10_code="A00",
                onset_date=today - timedelta(days=100),
                status=ProblemStatus.RESOLVED,
                priority=ProblemPriority.RESOLVED,
            ),
        ]
        mock_patient_repo.get = AsyncMock(return_value=patient)
        mock_patient_repo.update = AsyncMock(return_value=patient)

        result = run_async(service.reactivate_problem(
            patient_id="patient-001",
            icd10_code="A00",
            provider_name="Dr. Smith",
        ))

        assert result is not None
        assert result.status == ProblemStatus.ACTIVE


@pytest.mark.unit
class TestGetResolvedProblems:
    """Tests for get_resolved_problems method."""

    @pytest.fixture
    def mock_patient_repo(self):
        """Create a mock patient repository."""
        return MagicMock(spec=PatientRepository)

    @pytest.fixture
    def service(self, mock_patient_repo):
        """Create service with mocked repo."""
        return ProblemListService(patient_repo=mock_patient_repo)

    def test_get_resolved_problems(self, service, mock_patient_repo):
        """Should return resolved problems sorted by date."""
        today = date.today()
        patient = MagicMock(spec=Patient)
        patient.problem_list = [
            Problem(name="Active", icd10_code="A00", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC),
            Problem(name="Resolved Old", icd10_code="B00", onset_date=today - timedelta(days=200), status=ProblemStatus.RESOLVED, priority=ProblemPriority.RESOLVED, resolved_date=today - timedelta(days=150)),
            Problem(name="Resolved New", icd10_code="C00", onset_date=today - timedelta(days=100), status=ProblemStatus.RESOLVED, priority=ProblemPriority.RESOLVED, resolved_date=today - timedelta(days=30)),
        ]
        mock_patient_repo.get = AsyncMock(return_value=patient)

        resolved = run_async(service.get_resolved_problems(patient_id="patient-001"))

        assert len(resolved) == 2
        # Most recently resolved first
        assert resolved[0].name == "Resolved New"
        assert resolved[1].name == "Resolved Old"

    def test_get_resolved_problems_none(self, service, mock_patient_repo):
        """Should return empty list when no resolved problems."""
        today = date.today()
        patient = MagicMock(spec=Patient)
        patient.problem_list = [
            Problem(name="Active", icd10_code="A00", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC),
        ]
        mock_patient_repo.get = AsyncMock(return_value=patient)

        resolved = run_async(service.get_resolved_problems(patient_id="patient-001"))

        assert resolved == []

    def test_get_resolved_problems_patient_not_found(self, service, mock_patient_repo):
        """Should return empty list when patient not found."""
        mock_patient_repo.get = AsyncMock(return_value=None)

        resolved = run_async(service.get_resolved_problems(patient_id="nonexistent"))

        assert resolved == []


@pytest.mark.unit
class TestProblemListResponse:
    """Tests for ProblemListResponse dataclass."""

    def test_to_dict_without_groups(self):
        """Should convert to dict without groups."""
        today = date.today()
        problems = [
            Problem(name="Test", icd10_code="A00", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC),
        ]
        response = ProblemListResponse(
            problems=problems,
            active_count=1,
            total_count=1,
            critical_count=0,
            new_count=0,
            groups=None,
        )

        result = response.to_dict()

        assert result["activeCount"] == 1
        assert result["totalCount"] == 1
        assert result["criticalCount"] == 0
        assert result["newCount"] == 0
        assert len(result["problems"]) == 1
        assert "groups" not in result

    def test_to_dict_with_groups(self):
        """Should convert to dict with groups."""
        today = date.today()
        problems = [
            Problem(name="Test", icd10_code="A00", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC),
        ]
        groups = [
            ProblemGroup(
                category=ClinicalCategory.CARDIOVASCULAR,
                category_label="Cardiovascular",
                problems=problems,
            ),
        ]
        response = ProblemListResponse(
            problems=problems,
            active_count=1,
            total_count=1,
            groups=groups,
        )

        result = response.to_dict()

        assert "groups" in result
        assert len(result["groups"]) == 1
        assert result["groups"][0]["category"] == "cardiovascular"
        assert result["groups"][0]["categoryLabel"] == "Cardiovascular"
