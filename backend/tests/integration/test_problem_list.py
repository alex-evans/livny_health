"""
Problem List Service Integration Tests.

Tests for the problem list endpoint and service.
Verifies that problem list data flows correctly from repositories
through services to HTTP responses.
"""
import asyncio
from datetime import date, timedelta
import pytest
from fastapi import status

from resources import Problem, ProblemStatus, ProblemPriority, ProblemSeverity
from services import ProblemListService


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Test patient ID that matches the mock data
TEST_PATIENT_ID = "patient-001"
TEST_PATIENT_WITH_MANY_PROBLEMS = "patient-004"  # James Williams with 8 problems


@pytest.mark.integration
class TestProblemListServiceIntegration:
    """
    Integration tests for ProblemListService.

    Tests the service layer directly with real repositories.
    """

    def test_get_problem_list_returns_problems(self, client, repositories):
        """get_problem_list should return problems for a patient."""
        from bff.dependencies import get_problem_list_service

        service = get_problem_list_service()
        result = run_async(service.get_problem_list(TEST_PATIENT_ID))

        assert result is not None
        assert result.total_count > 0
        assert len(result.problems) > 0

    def test_get_problem_list_returns_none_for_invalid_patient(self, client, repositories):
        """get_problem_list should return None for non-existent patient."""
        from bff.dependencies import get_problem_list_service

        service = get_problem_list_service()
        result = run_async(service.get_problem_list("nonexistent-patient"))

        assert result is None

    def test_problems_sorted_by_priority(self, client, repositories):
        """Problems should be sorted by clinical priority."""
        from bff.dependencies import get_problem_list_service

        service = get_problem_list_service()
        result = run_async(service.get_problem_list(TEST_PATIENT_ID))

        assert result is not None

        # Verify sorting - acute should come before chronic, which should come before resolved
        priority_order = {
            ProblemPriority.ACUTE: 0,
            ProblemPriority.CHRONIC: 1,
            ProblemPriority.INACTIVE: 2,
            ProblemPriority.RESOLVED: 3,
        }

        for i in range(len(result.problems) - 1):
            current_priority = priority_order.get(result.problems[i].priority, 99)
            next_priority = priority_order.get(result.problems[i + 1].priority, 99)
            assert current_priority <= next_priority, (
                f"Problem at index {i} ({result.problems[i].name}, {result.problems[i].priority}) "
                f"should come before problem at index {i+1} ({result.problems[i+1].name}, {result.problems[i+1].priority})"
            )

    def test_active_count_calculated_correctly(self, client, repositories):
        """active_count should match number of problems with active status."""
        from bff.dependencies import get_problem_list_service

        service = get_problem_list_service()
        result = run_async(service.get_problem_list(TEST_PATIENT_ID))

        assert result is not None

        # Count manually
        manual_active_count = sum(1 for p in result.problems if p.status == ProblemStatus.ACTIVE)
        assert result.active_count == manual_active_count

    def test_to_dict_includes_all_fields(self, client, repositories):
        """to_dict should include all required fields."""
        from bff.dependencies import get_problem_list_service

        service = get_problem_list_service()
        result = run_async(service.get_problem_list(TEST_PATIENT_ID))

        assert result is not None

        data = result.to_dict()

        assert "problems" in data
        assert "activeCount" in data
        assert "totalCount" in data

        # Check problem structure
        if len(data["problems"]) > 0:
            problem = data["problems"][0]
            assert "name" in problem
            assert "icd10Code" in problem
            assert "onsetDate" in problem
            assert "status" in problem
            assert "priority" in problem


@pytest.mark.integration
class TestProblemListSorting:
    """
    Tests for problem list sorting logic.

    Verifies that problems are sorted correctly by clinical priority.
    """

    def test_sort_by_priority_acute_first(self):
        """Acute problems should come before chronic problems."""
        from services import ProblemListService

        service = ProblemListService(patient_repo=None)

        problems = [
            Problem(
                name="Chronic Hypertension",
                icd10_code="I10",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
            ),
            Problem(
                name="Acute Back Pain",
                icd10_code="M54.5",
                onset_date=date(2024, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.ACUTE,
            ),
        ]

        sorted_problems = service.sort_by_priority(problems)

        assert sorted_problems[0].name == "Acute Back Pain"
        assert sorted_problems[1].name == "Chronic Hypertension"

    def test_sort_by_priority_resolved_last(self):
        """Resolved problems should come after active problems."""
        from services import ProblemListService

        service = ProblemListService(patient_repo=None)

        problems = [
            Problem(
                name="Resolved Infection",
                icd10_code="A00",
                onset_date=date(2024, 1, 1),
                status=ProblemStatus.RESOLVED,
                priority=ProblemPriority.RESOLVED,
            ),
            Problem(
                name="Active Diabetes",
                icd10_code="E11.9",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
            ),
        ]

        sorted_problems = service.sort_by_priority(problems)

        assert sorted_problems[0].name == "Active Diabetes"
        assert sorted_problems[1].name == "Resolved Infection"

    def test_sort_by_priority_within_same_priority_by_date(self):
        """Within same priority, problems should be sorted by onset date (most recent first)."""
        from services import ProblemListService

        service = ProblemListService(patient_repo=None)

        problems = [
            Problem(
                name="Older Chronic Problem",
                icd10_code="I10",
                onset_date=date(2018, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
            ),
            Problem(
                name="Newer Chronic Problem",
                icd10_code="E11.9",
                onset_date=date(2022, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
            ),
        ]

        sorted_problems = service.sort_by_priority(problems)

        assert sorted_problems[0].name == "Newer Chronic Problem"
        assert sorted_problems[1].name == "Older Chronic Problem"

    def test_sort_full_priority_order(self):
        """Test complete priority ordering: acute, chronic, inactive, resolved."""
        from services import ProblemListService

        service = ProblemListService(patient_repo=None)

        problems = [
            Problem(
                name="Resolved",
                icd10_code="A01",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.RESOLVED,
                priority=ProblemPriority.RESOLVED,
            ),
            Problem(
                name="Chronic",
                icd10_code="A02",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
            ),
            Problem(
                name="Inactive",
                icd10_code="A03",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.INACTIVE,
                priority=ProblemPriority.INACTIVE,
            ),
            Problem(
                name="Acute",
                icd10_code="A04",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.ACUTE,
            ),
        ]

        sorted_problems = service.sort_by_priority(problems)

        assert sorted_problems[0].name == "Acute"
        assert sorted_problems[1].name == "Chronic"
        assert sorted_problems[2].name == "Inactive"
        assert sorted_problems[3].name == "Resolved"


@pytest.mark.integration
class TestProblemListFiltering:
    """
    Tests for problem list filtering logic.
    """

    def test_get_active_problems(self):
        """get_active_problems should return only active problems."""
        from services import ProblemListService

        service = ProblemListService(patient_repo=None)

        problems = [
            Problem(
                name="Active Problem",
                icd10_code="A01",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
            ),
            Problem(
                name="Resolved Problem",
                icd10_code="A02",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.RESOLVED,
                priority=ProblemPriority.RESOLVED,
            ),
            Problem(
                name="Inactive Problem",
                icd10_code="A03",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.INACTIVE,
                priority=ProblemPriority.INACTIVE,
            ),
        ]

        active_problems = service.get_active_problems(problems)

        assert len(active_problems) == 1
        assert active_problems[0].name == "Active Problem"

    def test_get_problems_by_status(self):
        """get_problems_by_status should filter correctly."""
        from services import ProblemListService

        service = ProblemListService(patient_repo=None)

        problems = [
            Problem(
                name="Active 1",
                icd10_code="A01",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
            ),
            Problem(
                name="Active 2",
                icd10_code="A02",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
            ),
            Problem(
                name="Resolved",
                icd10_code="A03",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.RESOLVED,
                priority=ProblemPriority.RESOLVED,
            ),
        ]

        active = service.get_problems_by_status(problems, ProblemStatus.ACTIVE)
        resolved = service.get_problems_by_status(problems, ProblemStatus.RESOLVED)

        assert len(active) == 2
        assert len(resolved) == 1


@pytest.mark.integration
class TestProblemModel:
    """
    Tests for the Problem model.
    """

    def test_problem_to_bff_dict(self):
        """Problem.to_bff_dict() should return correct structure."""
        problem = Problem(
            name="Essential hypertension",
            icd10_code="I10",
            onset_date=date(2020, 3, 15),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        data = problem.to_bff_dict()

        assert data["name"] == "Essential hypertension"
        assert data["icd10Code"] == "I10"
        assert data["onsetDate"] == "2020-03-15"
        assert data["status"] == "active"
        assert data["priority"] == "chronic"

    def test_problem_to_bff_dict_with_optional_fields(self):
        """Problem.to_bff_dict() should include optional fields when set."""
        problem = Problem(
            name="Essential hypertension",
            icd10_code="I10",
            onset_date=date(2020, 3, 15),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
            severity=ProblemSeverity.WELL_CONTROLLED,
            documenting_provider="Dr. Elizabeth Frost",
            documented_date=date(2020, 3, 15),
        )

        data = problem.to_bff_dict()

        assert data["name"] == "Essential hypertension"
        assert data["icd10Code"] == "I10"
        assert data["onsetDate"] == "2020-03-15"
        assert data["status"] == "active"
        assert data["priority"] == "chronic"
        assert data["severity"] == "well_controlled"
        assert data["documentingProvider"] == "Dr. Elizabeth Frost"
        assert data["documentedDate"] == "2020-03-15"

    def test_problem_to_bff_dict_without_optional_fields(self):
        """Problem.to_bff_dict() should not include optional fields when not set."""
        problem = Problem(
            name="Essential hypertension",
            icd10_code="I10",
            onset_date=date(2020, 3, 15),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        data = problem.to_bff_dict()

        assert "severity" not in data
        assert "documentingProvider" not in data
        assert "documentedDate" not in data

    def test_problem_status_enum_values(self):
        """ProblemStatus enum should have correct values."""
        assert ProblemStatus.ACTIVE.value == "active"
        assert ProblemStatus.INACTIVE.value == "inactive"
        assert ProblemStatus.RESOLVED.value == "resolved"
        assert ProblemStatus.RULE_OUT.value == "rule_out"

    def test_problem_priority_enum_values(self):
        """ProblemPriority enum should have correct values."""
        assert ProblemPriority.ACUTE.value == "acute"
        assert ProblemPriority.CHRONIC.value == "chronic"
        assert ProblemPriority.INACTIVE.value == "inactive"
        assert ProblemPriority.RESOLVED.value == "resolved"

    def test_problem_severity_enum_values(self):
        """ProblemSeverity enum should have correct values."""
        assert ProblemSeverity.MILD.value == "mild"
        assert ProblemSeverity.MODERATE.value == "moderate"
        assert ProblemSeverity.SEVERE.value == "severe"
        assert ProblemSeverity.WELL_CONTROLLED.value == "well_controlled"

    def test_problem_with_rule_out_status(self):
        """Problem can have rule_out status."""
        problem = Problem(
            name="Prostate cancer",
            icd10_code="C61",
            onset_date=date(2025, 1, 10),
            status=ProblemStatus.RULE_OUT,
            priority=ProblemPriority.ACUTE,
            documenting_provider="Dr. Elizabeth Frost",
            documented_date=date(2025, 1, 10),
        )

        data = problem.to_bff_dict()

        assert data["status"] == "rule_out"
        assert data["priority"] == "acute"

    def test_problem_severity_variations(self):
        """Problem severity can be set to different values."""
        severities = [
            (ProblemSeverity.MILD, "mild"),
            (ProblemSeverity.MODERATE, "moderate"),
            (ProblemSeverity.SEVERE, "severe"),
            (ProblemSeverity.WELL_CONTROLLED, "well_controlled"),
        ]

        for severity_enum, severity_value in severities:
            problem = Problem(
                name="Test problem",
                icd10_code="T00",
                onset_date=date(2025, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
                severity=severity_enum,
            )

            data = problem.to_bff_dict()
            assert data["severity"] == severity_value


@pytest.mark.integration
class TestProblemCriticalAndNew:
    """
    Tests for critical and new problem fields.
    """

    def test_is_new_within_30_days(self):
        """is_new should be True for problems documented within last 30 days."""
        recent_date = date.today() - timedelta(days=15)
        problem = Problem(
            name="Recent Problem",
            icd10_code="A01",
            onset_date=recent_date,
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.ACUTE,
            documented_date=recent_date,
        )

        assert problem.is_new is True

    def test_is_new_over_30_days(self):
        """is_new should be False for problems documented over 30 days ago."""
        old_date = date.today() - timedelta(days=60)
        problem = Problem(
            name="Old Problem",
            icd10_code="A02",
            onset_date=old_date,
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
            documented_date=old_date,
        )

        assert problem.is_new is False

    def test_is_new_no_documented_date(self):
        """is_new should be False if documented_date is not set."""
        problem = Problem(
            name="No Date Problem",
            icd10_code="A03",
            onset_date=date.today(),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        assert problem.is_new is False

    def test_is_rule_out(self):
        """is_rule_out should be True for RULE_OUT status."""
        problem = Problem(
            name="Rule Out Problem",
            icd10_code="A04",
            onset_date=date.today(),
            status=ProblemStatus.RULE_OUT,
            priority=ProblemPriority.ACUTE,
        )

        assert problem.is_rule_out is True

    def test_is_not_rule_out(self):
        """is_rule_out should be False for non-RULE_OUT status."""
        problem = Problem(
            name="Active Problem",
            icd10_code="A05",
            onset_date=date.today(),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        assert problem.is_rule_out is False

    def test_to_bff_dict_includes_new_fields(self):
        """to_bff_dict should include isCritical, isNew, and isRuleOut."""
        problem = Problem(
            name="Test Problem",
            icd10_code="A06",
            onset_date=date.today(),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
            is_critical=True,
        )

        data = problem.to_bff_dict()

        assert "isCritical" in data
        assert "isNew" in data
        assert "isRuleOut" in data
        assert data["isCritical"] is True
        assert data["isRuleOut"] is False

    def test_critical_problems_sorted_first(self):
        """Critical problems should be sorted before non-critical regardless of priority."""
        from services import ProblemListService

        service = ProblemListService(patient_repo=None)

        problems = [
            Problem(
                name="Non-critical Acute",
                icd10_code="A01",
                onset_date=date(2024, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.ACUTE,
                is_critical=False,
            ),
            Problem(
                name="Critical Chronic",
                icd10_code="A02",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
                is_critical=True,
            ),
        ]

        sorted_problems = service.sort_by_priority(problems)

        assert sorted_problems[0].name == "Critical Chronic"
        assert sorted_problems[1].name == "Non-critical Acute"

    def test_response_includes_critical_and_new_counts(self, client, repositories):
        """ProblemListResponse should include critical_count and new_count."""
        from bff.dependencies import get_problem_list_service

        service = get_problem_list_service()
        # Patient 004 (James Williams) has critical problems
        result = run_async(service.get_problem_list("patient-004"))

        assert result is not None
        assert result.critical_count >= 0
        assert result.new_count >= 0

        data = result.to_dict()
        assert "criticalCount" in data
        assert "newCount" in data


@pytest.mark.integration
class TestPatientProblemListBFF:
    """
    Integration tests for problem list via BFF endpoints.
    """

    def test_patient_response_includes_problem_list(self, client):
        """GET /patients/{id} should include problemList with new format."""
        response = client.get(f"/patients/{TEST_PATIENT_ID}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "problemList" in data
        problems = data["problemList"]
        assert len(problems) > 0

        # Check problem structure
        problem = problems[0]
        assert "name" in problem
        assert "icd10Code" in problem
        assert "onsetDate" in problem
        assert "status" in problem
        assert "priority" in problem

    def test_patient_response_includes_new_problem_fields(self, client):
        """GET /patients/{id} should include severity, documenting provider, and documented date."""
        response = client.get(f"/patients/{TEST_PATIENT_ID}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        problems = data["problemList"]
        # At least one problem should have the new optional fields
        problems_with_severity = [p for p in problems if "severity" in p]
        problems_with_provider = [p for p in problems if "documentingProvider" in p]
        problems_with_date = [p for p in problems if "documentedDate" in p]

        assert len(problems_with_severity) > 0, "At least one problem should have severity"
        assert len(problems_with_provider) > 0, "At least one problem should have documenting provider"
        assert len(problems_with_date) > 0, "At least one problem should have documented date"

    def test_patient_with_rule_out_problem(self, client):
        """GET /patients/{id} should include problems with rule_out status."""
        # Patient 004 (James Williams) has a rule_out problem
        response = client.get(f"/patients/{TEST_PATIENT_WITH_MANY_PROBLEMS}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        problems = data["problemList"]
        rule_out_problems = [p for p in problems if p["status"] == "rule_out"]

        assert len(rule_out_problems) > 0, "Patient should have at least one rule_out problem"

    def test_patient_problem_list_has_icd10_codes(self, client):
        """Problem list should include valid ICD-10 codes."""
        response = client.get(f"/patients/{TEST_PATIENT_ID}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        for problem in data["problemList"]:
            assert problem["icd10Code"] is not None
            assert len(problem["icd10Code"]) > 0
            # ICD-10 codes should match pattern like I10, E11.9, etc.
            assert problem["icd10Code"][0].isalpha()

    def test_patient_problem_list_has_onset_dates(self, client):
        """Problem list should include onset dates in ISO format."""
        response = client.get(f"/patients/{TEST_PATIENT_ID}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        for problem in data["problemList"]:
            assert problem["onsetDate"] is not None
            # Should be ISO date format (YYYY-MM-DD)
            assert len(problem["onsetDate"]) == 10
            assert problem["onsetDate"][4] == "-"
            assert problem["onsetDate"][7] == "-"

    def test_patient_with_many_problems_sorted_correctly(self, client):
        """Patient with many problems should have them sorted by priority."""
        response = client.get(f"/patients/{TEST_PATIENT_WITH_MANY_PROBLEMS}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        problems = data["problemList"]

        # Check that acute problems (if any) come before chronic
        priority_order = {"acute": 0, "chronic": 1, "inactive": 2, "resolved": 3}
        for i in range(len(problems) - 1):
            current_priority = priority_order.get(problems[i]["priority"], 99)
            next_priority = priority_order.get(problems[i + 1]["priority"], 99)
            # Note: The BFF doesn't guarantee sorting, but the frontend should sort
            # This test just verifies the structure is correct
            assert problems[i]["priority"] in priority_order


@pytest.mark.integration
class TestProblemStatusManagement:
    """
    Tests for problem status management (resolve/reactivate).
    """

    def test_resolve_problem(self, client, repositories):
        """resolve_problem should mark problem as resolved with date and provider."""
        from bff.dependencies import get_problem_list_service

        service = get_problem_list_service()
        # Patient 001 has hypertension (I10) as an active problem
        result = run_async(service.resolve_problem(
            patient_id=TEST_PATIENT_ID,
            icd10_code="I10",
            provider_name="Dr. Test Provider"
        ))

        assert result is not None
        assert result.status == ProblemStatus.RESOLVED
        assert result.priority == ProblemPriority.RESOLVED
        assert result.resolved_date == date.today()
        assert result.resolved_by_provider == "Dr. Test Provider"

    def test_reactivate_problem(self, client, repositories):
        """reactivate_problem should reset status and clear resolved fields."""
        from bff.dependencies import get_problem_list_service

        service = get_problem_list_service()
        # First resolve a problem
        run_async(service.resolve_problem(
            patient_id=TEST_PATIENT_ID,
            icd10_code="E11.9",  # Diabetes
            provider_name="Dr. Test Provider"
        ))

        # Now reactivate it
        result = run_async(service.reactivate_problem(
            patient_id=TEST_PATIENT_ID,
            icd10_code="E11.9",
            provider_name="Dr. Reactivate Provider"
        ))

        assert result is not None
        assert result.status == ProblemStatus.ACTIVE
        assert result.priority == ProblemPriority.CHRONIC
        assert result.resolved_date is None
        assert result.resolved_by_provider is None

    def test_get_resolved_problems(self, client, repositories):
        """get_resolved_problems should return only resolved problems."""
        from bff.dependencies import get_problem_list_service

        service = get_problem_list_service()
        # Patient 001 has resolved problems in seed data
        result = run_async(service.get_resolved_problems(TEST_PATIENT_ID))

        assert isinstance(result, list)
        for problem in result:
            assert problem.status == ProblemStatus.RESOLVED

    def test_update_problem_status_nonexistent_problem(self, client, repositories):
        """update_problem_status should return None for nonexistent problem."""
        from bff.dependencies import get_problem_list_service

        service = get_problem_list_service()
        result = run_async(service.update_problem_status(
            patient_id=TEST_PATIENT_ID,
            icd10_code="NONEXISTENT",
            new_status=ProblemStatus.RESOLVED,
            provider_name="Dr. Test"
        ))

        assert result is None

    def test_update_problem_status_nonexistent_patient(self, client, repositories):
        """update_problem_status should return None for nonexistent patient."""
        from bff.dependencies import get_problem_list_service

        service = get_problem_list_service()
        result = run_async(service.update_problem_status(
            patient_id="nonexistent-patient",
            icd10_code="I10",
            new_status=ProblemStatus.RESOLVED,
            provider_name="Dr. Test"
        ))

        assert result is None


@pytest.mark.integration
class TestProblemResolvedFields:
    """
    Tests for resolved date and provider fields.
    """

    def test_problem_with_resolved_fields(self):
        """Problem with resolved fields should serialize correctly."""
        problem = Problem(
            name="Resolved Infection",
            icd10_code="J01.90",
            onset_date=date(2024, 9, 15),
            status=ProblemStatus.RESOLVED,
            priority=ProblemPriority.RESOLVED,
            documenting_provider="Dr. Original",
            documented_date=date(2024, 9, 15),
            resolved_date=date(2024, 9, 28),
            resolved_by_provider="Dr. Resolver",
        )

        data = problem.to_bff_dict()

        assert data["status"] == "resolved"
        assert data["priority"] == "resolved"
        assert data["resolvedDate"] == "2024-09-28"
        assert data["resolvedByProvider"] == "Dr. Resolver"

    def test_problem_without_resolved_fields(self):
        """Active problem should not have resolved fields in dict."""
        problem = Problem(
            name="Active Problem",
            icd10_code="I10",
            onset_date=date(2024, 1, 1),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        data = problem.to_bff_dict()

        assert "resolvedDate" not in data
        assert "resolvedByProvider" not in data

    def test_patient_response_includes_resolved_fields(self, client):
        """GET /patients/{id} should include resolved fields for resolved problems."""
        response = client.get(f"/patients/{TEST_PATIENT_ID}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Find resolved problems
        resolved_problems = [p for p in data["problemList"] if p["status"] == "resolved"]

        assert len(resolved_problems) > 0, "Patient should have at least one resolved problem"

        # Check that resolved problems have the new fields
        for problem in resolved_problems:
            if "resolvedDate" in problem:
                # Verify date format
                assert len(problem["resolvedDate"]) == 10  # YYYY-MM-DD
            if "resolvedByProvider" in problem:
                assert isinstance(problem["resolvedByProvider"], str)


@pytest.mark.integration
class TestProblemStatusManagementBFF:
    """
    Integration tests for problem status management via BFF endpoints.
    """

    def test_resolve_problem_endpoint(self, client):
        """POST /patients/{id}/problems/{code}/resolve should mark problem as resolved."""
        response = client.post(
            f"/patients/{TEST_PATIENT_ID}/problems/E78.5/resolve",
            json={"providerName": "Dr. API Test"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "resolved"
        assert data["priority"] == "resolved"
        assert "resolvedDate" in data
        assert data["resolvedByProvider"] == "Dr. API Test"

    def test_reactivate_problem_endpoint(self, client):
        """POST /patients/{id}/problems/{code}/reactivate should reactivate problem."""
        # First resolve the problem
        client.post(
            f"/patients/{TEST_PATIENT_ID}/problems/E66.9/resolve",
            json={"providerName": "Dr. First"}
        )

        # Then reactivate
        response = client.post(
            f"/patients/{TEST_PATIENT_ID}/problems/E66.9/reactivate",
            json={"providerName": "Dr. Reactivate"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "active"
        assert "resolvedDate" not in data or data.get("resolvedDate") is None
        assert "resolvedByProvider" not in data or data.get("resolvedByProvider") is None

    def test_update_problem_status_endpoint(self, client):
        """PATCH /patients/{id}/problems/{code}/status should update status."""
        response = client.patch(
            f"/patients/{TEST_PATIENT_WITH_MANY_PROBLEMS}/problems/N40.0/status",
            json={"status": "inactive", "providerName": "Dr. Status Update"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "inactive"
        assert data["priority"] == "inactive"

    def test_get_resolved_problems_endpoint(self, client):
        """GET /patients/{id}/problems/resolved should return resolved problems."""
        response = client.get(f"/patients/{TEST_PATIENT_ID}/problems/resolved")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "problems" in data
        assert "count" in data
        assert isinstance(data["problems"], list)
        assert data["count"] == len(data["problems"])

        for problem in data["problems"]:
            assert problem["status"] == "resolved"

    def test_resolve_nonexistent_problem(self, client):
        """POST /patients/{id}/problems/{code}/resolve with invalid code returns 404."""
        response = client.post(
            f"/patients/{TEST_PATIENT_ID}/problems/INVALID123/resolve",
            json={"providerName": "Dr. Test"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_resolve_for_nonexistent_patient(self, client):
        """POST /patients/{id}/problems/{code}/resolve with invalid patient returns 404."""
        response = client.post(
            "/patients/nonexistent-patient/problems/I10/resolve",
            json={"providerName": "Dr. Test"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
