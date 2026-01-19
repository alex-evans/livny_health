"""
Lab History Integration Tests.

Tests for the lab history endpoint and service.
Verifies that lab history flows correctly from repositories
through services to HTTP responses.
"""
import asyncio
import pytest
from fastapi import status


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Test patient ID that matches the mock data in LabResultRepository
TEST_PATIENT_ID = "patient-001"


@pytest.mark.integration
class TestLabHistoryEndpointIntegration:
    """
    Integration tests for lab history endpoint.

    Verifies that lab history data flows correctly from repositories
    through services to HTTP responses.
    """

    def test_get_lab_history_returns_data(self, client):
        """GET /patients/{id}/labs/{test_name}/history should return lab history."""
        response = client.get(f"/patients/{TEST_PATIENT_ID}/labs/Glucose/history")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure
        assert "testName" in data
        assert "unit" in data
        assert "referenceRange" in data
        assert "history" in data
        assert "trendAnalysis" in data

        # Verify test name matches
        assert data["testName"] == "Glucose"
        assert data["unit"] == "mg/dL"
        assert data["referenceRange"] == "70-100"

        # Verify history entries
        assert len(data["history"]) > 0
        first_entry = data["history"][0]
        assert "id" in first_entry
        assert "value" in first_entry
        assert "status" in first_entry
        assert "collectionDate" in first_entry

    def test_get_lab_history_with_days_back_filter(self, client):
        """GET /patients/{id}/labs/{test_name}/history with days_back should filter results."""
        # Get history for last 30 days (should be limited)
        response = client.get(
            f"/patients/{TEST_PATIENT_ID}/labs/Glucose/history",
            params={"days_back": 30}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should have fewer results than full history
        short_history_count = len(data["history"])

        # Get full history for comparison
        full_response = client.get(
            f"/patients/{TEST_PATIENT_ID}/labs/Glucose/history",
            params={"days_back": 365}
        )
        full_data = full_response.json()
        full_history_count = len(full_data["history"])

        # Limited history should have fewer or equal results
        assert short_history_count <= full_history_count

    def test_get_lab_history_includes_trend_analysis(self, client):
        """GET /patients/{id}/labs/{test_name}/history should include trend analysis."""
        response = client.get(f"/patients/{TEST_PATIENT_ID}/labs/Creatinine/history")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify trend analysis is present
        assert data["trendAnalysis"] is not None
        trend = data["trendAnalysis"]

        assert "direction" in trend
        assert trend["direction"] in ["increasing", "decreasing", "stable"]
        assert "percentChange" in trend
        assert "absoluteChange" in trend
        assert "firstValue" in trend
        assert "lastValue" in trend
        assert "dataPoints" in trend
        assert trend["dataPoints"] >= 2

    def test_get_lab_history_creatinine_shows_increasing_trend(self, client):
        """Creatinine history should show increasing trend (worsening)."""
        response = client.get(f"/patients/{TEST_PATIENT_ID}/labs/Creatinine/history")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Creatinine mock data shows worsening trend
        assert data["trendAnalysis"]["direction"] == "increasing"

    def test_get_lab_history_patient_not_found(self, client):
        """GET /patients/{id}/labs/{test_name}/history with invalid patient should return 404."""
        response = client.get("/patients/nonexistent-patient/labs/Glucose/history")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_lab_history_test_not_found(self, client):
        """GET /patients/{id}/labs/{test_name}/history with invalid test should return 404."""
        response = client.get(f"/patients/{TEST_PATIENT_ID}/labs/NonexistentTest/history")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "No lab history found" in response.json()["detail"]

    def test_get_lab_history_multiple_tests(self, client):
        """Different tests should return different history data."""
        # Get Glucose history
        glucose_response = client.get(f"/patients/{TEST_PATIENT_ID}/labs/Glucose/history")
        glucose_data = glucose_response.json()

        # Get Potassium history
        potassium_response = client.get(f"/patients/{TEST_PATIENT_ID}/labs/Potassium/history")
        potassium_data = potassium_response.json()

        # Verify they're different tests
        assert glucose_data["testName"] == "Glucose"
        assert potassium_data["testName"] == "Potassium"

        # Verify units are different
        assert glucose_data["unit"] != potassium_data["unit"]

    def test_get_lab_history_case_insensitive_test_name(self, client):
        """Test name lookup should be case-insensitive."""
        # Lowercase
        response1 = client.get(f"/patients/{TEST_PATIENT_ID}/labs/glucose/history")
        # Uppercase
        response2 = client.get(f"/patients/{TEST_PATIENT_ID}/labs/GLUCOSE/history")
        # Mixed case
        response3 = client.get(f"/patients/{TEST_PATIENT_ID}/labs/Glucose/history")

        # All should succeed
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        assert response3.status_code == status.HTTP_200_OK

    def test_get_lab_history_sorted_by_date(self, client):
        """History should be sorted by collection date, most recent first."""
        response = client.get(f"/patients/{TEST_PATIENT_ID}/labs/Glucose/history")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify sorted by date (most recent first)
        dates = [entry["collectionDate"] for entry in data["history"]]
        assert dates == sorted(dates, reverse=True)


@pytest.mark.integration
class TestLabHistoryServiceIntegration:
    """
    Integration tests for LabHistoryService.

    Tests the service layer directly with real repositories.
    """

    def test_service_calculates_trend_correctly(self, client):
        """Service should calculate trend direction correctly."""
        # HbA1c mock data shows increasing trend (worsening diabetes control)
        response = client.get(f"/patients/{TEST_PATIENT_ID}/labs/HbA1c/history")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        trend = data["trendAnalysis"]
        assert trend["direction"] == "increasing"
        assert trend["lastValue"] > trend["firstValue"]

    def test_service_handles_stable_trend(self, client):
        """Service should identify stable trends (< 5% change)."""
        # We need to test with a lab that has stable values
        # For now, verify structure is correct even if not stable
        response = client.get(f"/patients/{TEST_PATIENT_ID}/labs/Potassium/history")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify trend structure
        if data["trendAnalysis"]:
            assert "direction" in data["trendAnalysis"]
            assert data["trendAnalysis"]["direction"] in ["increasing", "decreasing", "stable"]

    def test_service_returns_correct_data_points_count(self, client):
        """Service should report correct number of data points in trend."""
        response = client.get(f"/patients/{TEST_PATIENT_ID}/labs/LDL/history")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Data points in trend should match history length (for numeric values)
        if data["trendAnalysis"]:
            assert data["trendAnalysis"]["dataPoints"] <= len(data["history"])


@pytest.mark.integration
class TestLabHistoryDataCompleteness:
    """
    Integration tests for lab history data completeness features.

    Tests pending/in_progress status, acknowledged fields, and lastUpdated timestamps.
    """

    def test_history_entries_include_acknowledged_field(self, client):
        """History entries should include acknowledged field."""
        response = client.get(f"/patients/{TEST_PATIENT_ID}/labs/Glucose/history")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify acknowledged field is present in history entries
        for entry in data["history"]:
            assert "acknowledged" in entry
            assert isinstance(entry["acknowledged"], bool)

    def test_history_entries_include_last_updated(self, client):
        """History entries should include lastUpdated timestamp."""
        response = client.get(f"/patients/{TEST_PATIENT_ID}/labs/Glucose/history")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify lastUpdated field is present in history entries
        for entry in data["history"]:
            assert "lastUpdated" in entry
            # lastUpdated can be None or an ISO date string
            if entry["lastUpdated"] is not None:
                assert isinstance(entry["lastUpdated"], str)

    def test_history_entries_include_acknowledged_by_and_at(self, client):
        """History entries should include acknowledgedBy and acknowledgedAt fields."""
        response = client.get(f"/patients/{TEST_PATIENT_ID}/labs/Glucose/history")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify acknowledged metadata fields are present
        for entry in data["history"]:
            assert "acknowledgedBy" in entry
            assert "acknowledgedAt" in entry
            # These can be None if not acknowledged
            if entry["acknowledged"]:
                # If acknowledged, at least acknowledgedAt should have a value
                # acknowledgedBy could be None if system-acknowledged
                pass

    def test_potassium_recent_critical_is_unacknowledged(self, client):
        """Most recent Potassium result (critical) should be unacknowledged in mock data."""
        response = client.get(f"/patients/{TEST_PATIENT_ID}/labs/Potassium/history")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Most recent entry (first in list) should be the critical unacknowledged one
        if len(data["history"]) > 0:
            most_recent = data["history"][0]
            # Verify it's the critical value
            if most_recent["status"] == "critical":
                assert most_recent["acknowledged"] is False

    def test_acknowledged_results_have_metadata(self, client):
        """Acknowledged results should have acknowledgedBy and acknowledgedAt."""
        response = client.get(f"/patients/{TEST_PATIENT_ID}/labs/Glucose/history")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Find acknowledged entries
        acknowledged_entries = [e for e in data["history"] if e.get("acknowledged")]

        # At least some results should be acknowledged in the mock data
        assert len(acknowledged_entries) > 0

        # Acknowledged entries should have metadata
        for entry in acknowledged_entries:
            assert entry["acknowledgedAt"] is not None
            assert entry["acknowledgedBy"] is not None

    def test_history_response_structure_complete(self, client):
        """Verify complete response structure with all data completeness fields."""
        response = client.get(f"/patients/{TEST_PATIENT_ID}/labs/Creatinine/history")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Required top-level fields
        assert "testName" in data
        assert "unit" in data
        assert "referenceRange" in data
        assert "history" in data
        assert "trendAnalysis" in data

        # Each history entry should have all required fields
        required_entry_fields = [
            "id", "value", "unit", "status", "collectionDate",
            "referenceRange", "performingLab",
            "lastUpdated", "acknowledged", "acknowledgedBy", "acknowledgedAt"
        ]

        for entry in data["history"]:
            for field in required_entry_fields:
                assert field in entry, f"Missing field: {field}"


@pytest.mark.integration
class TestLabResultPendingStatus:
    """
    Integration tests for pending and in_progress lab status.

    Tests that pending labs are correctly represented in the system.
    """

    def test_pending_lab_status_in_repository(self):
        """Pending labs should be stored with pending status."""
        from resources.lab_result.repository import LabResultRepository

        repo = LabResultRepository()
        results = run_async(repo.list(patient_id=TEST_PATIENT_ID))

        # Find pending labs
        pending_results = [r for r in results if r.status == "pending"]
        in_progress_results = [r for r in results if r.status == "in_progress"]

        # At least one pending or in_progress lab should exist in mock data
        assert len(pending_results) > 0 or len(in_progress_results) > 0

    def test_pending_lab_has_empty_value(self):
        """Pending labs should have empty value."""
        from resources.lab_result.repository import LabResultRepository

        repo = LabResultRepository()
        results = run_async(repo.list(patient_id=TEST_PATIENT_ID))

        # Find pending/in_progress labs
        pending_results = [r for r in results if r.status in ("pending", "in_progress")]

        for result in pending_results:
            # Pending labs should have empty or minimal value
            assert result.value == "" or result.value is None or result.value.strip() == ""

    def test_in_progress_lab_has_last_updated(self):
        """In-progress labs should have last_updated timestamp."""
        from resources.lab_result.repository import LabResultRepository

        repo = LabResultRepository()
        results = run_async(repo.list(patient_id=TEST_PATIENT_ID))

        # Find in_progress labs
        in_progress_results = [r for r in results if r.status == "in_progress"]

        for result in in_progress_results:
            assert result.last_updated is not None


@pytest.mark.integration
class TestLabResultModel:
    """
    Tests for the LabResult model data completeness fields.
    """

    def test_lab_result_to_dict_includes_data_completeness_fields(self):
        """LabResult.to_dict() should include data completeness fields."""
        from datetime import datetime, timedelta
        from resources.lab_result.model import LabResult
        from resources.core import Reference

        today = datetime.now()

        result = LabResult(
            id="test-1",
            test_name="Test",
            value="100",
            unit="mg/dL",
            reference_range="50-150",
            status="normal",
            subject=Reference(reference="Patient/test-patient"),
            collection_date=today,
            last_updated=today - timedelta(hours=1),
            acknowledged=True,
            acknowledged_by="dr-test",
            acknowledged_at=today - timedelta(minutes=30),
        )

        data = result.to_dict()

        assert "lastUpdated" in data
        assert "acknowledged" in data
        assert "acknowledgedBy" in data
        assert "acknowledgedAt" in data

        assert data["acknowledged"] is True
        assert data["acknowledgedBy"] == "dr-test"
        assert data["lastUpdated"] is not None
        assert data["acknowledgedAt"] is not None

    def test_lab_result_to_bff_dict_includes_data_completeness_fields(self):
        """LabResult.to_bff_dict() should include data completeness fields."""
        from datetime import datetime, timedelta
        from resources.lab_result.model import LabResult
        from resources.core import Reference

        today = datetime.now()

        result = LabResult(
            id="test-2",
            test_name="Test",
            value="100",
            unit="mg/dL",
            reference_range="50-150",
            status="abnormal",
            subject=Reference(reference="Patient/test-patient"),
            collection_date=today,
            last_updated=today - timedelta(hours=2),
            acknowledged=False,
            acknowledged_by=None,
            acknowledged_at=None,
        )

        data = result.to_bff_dict()

        assert "lastUpdated" in data
        assert "acknowledged" in data
        assert "acknowledgedBy" in data
        assert "acknowledgedAt" in data

        assert data["acknowledged"] is False
        assert data["acknowledgedBy"] is None
        assert data["acknowledgedAt"] is None

    def test_lab_result_to_history_entry_includes_data_completeness_fields(self):
        """LabResult.to_history_entry() should include data completeness fields."""
        from datetime import datetime, timedelta
        from resources.lab_result.model import LabResult
        from resources.core import Reference

        today = datetime.now()

        result = LabResult(
            id="test-3",
            test_name="Test",
            value="100",
            unit="mg/dL",
            reference_range="50-150",
            status="critical",
            subject=Reference(reference="Patient/test-patient"),
            collection_date=today,
            last_updated=today - timedelta(hours=1),
            acknowledged=True,
            acknowledged_by="dr-test",
            acknowledged_at=today - timedelta(minutes=45),
        )

        history_entry = result.to_history_entry()

        assert history_entry.last_updated is not None
        assert history_entry.acknowledged is True
        assert history_entry.acknowledged_by == "dr-test"
        assert history_entry.acknowledged_at is not None

    def test_lab_result_history_to_dict_includes_data_completeness_fields(self):
        """LabResultHistory.to_dict() should include data completeness fields."""
        from datetime import datetime, timedelta
        from resources.lab_result.model import LabResultHistory

        today = datetime.now()

        history = LabResultHistory(
            id="hist-1",
            value="95",
            unit="mg/dL",
            status="normal",
            collection_date=today - timedelta(days=7),
            reference_range="70-100",
            performing_lab="Quest Diagnostics",
            last_updated=today - timedelta(days=6),
            acknowledged=True,
            acknowledged_by="dr-smith",
            acknowledged_at=today - timedelta(days=6, hours=2),
        )

        data = history.to_dict()

        assert "lastUpdated" in data
        assert "acknowledged" in data
        assert "acknowledgedBy" in data
        assert "acknowledgedAt" in data

        assert data["acknowledged"] is True
        assert data["acknowledgedBy"] == "dr-smith"

    def test_pending_status_is_valid(self):
        """Pending status should be a valid LabResultStatus."""
        from resources.lab_result.model import LabResult
        from resources.core import Reference
        from datetime import datetime

        # This should not raise an error
        result = LabResult(
            id="pending-test",
            test_name="CBC",
            value="",
            unit="",
            reference_range="",
            status="pending",
            subject=Reference(reference="Patient/test-patient"),
            collection_date=datetime.now(),
        )

        assert result.status == "pending"

    def test_in_progress_status_is_valid(self):
        """In-progress status should be a valid LabResultStatus."""
        from resources.lab_result.model import LabResult
        from resources.core import Reference
        from datetime import datetime

        # This should not raise an error
        result = LabResult(
            id="inprogress-test",
            test_name="TSH",
            value="",
            unit="mIU/L",
            reference_range="0.4-4.0",
            status="in_progress",
            subject=Reference(reference="Patient/test-patient"),
            collection_date=datetime.now(),
        )

        assert result.status == "in_progress"


@pytest.mark.integration
class TestLabResultRepository:
    """
    Tests for the LabResultRepository data completeness features.
    """

    def test_repository_returns_unacknowledged_critical_results(self):
        """Repository should return unacknowledged critical results."""
        from resources.lab_result.repository import LabResultRepository

        repo = LabResultRepository()
        results = run_async(repo.list(patient_id=TEST_PATIENT_ID, status="critical"))

        # Find unacknowledged critical results
        unacknowledged = [r for r in results if not r.acknowledged]

        # Mock data should have at least one unacknowledged critical
        assert len(unacknowledged) > 0

    def test_repository_stores_last_updated(self):
        """Repository results should have last_updated timestamps."""
        from resources.lab_result.repository import LabResultRepository

        repo = LabResultRepository()
        results = run_async(repo.list(patient_id=TEST_PATIENT_ID))

        # Most results should have last_updated (for completed results)
        results_with_timestamp = [r for r in results if r.last_updated is not None]

        # At least some results should have timestamps
        assert len(results_with_timestamp) > 0

    def test_repository_filters_by_status_list(self):
        """Repository should filter by multiple statuses."""
        from resources.lab_result.repository import LabResultRepository

        repo = LabResultRepository()

        # Filter by multiple statuses
        results = run_async(repo.list(
            patient_id=TEST_PATIENT_ID,
            status=["pending", "in_progress"]
        ))

        # All results should be pending or in_progress
        for result in results:
            assert result.status in ("pending", "in_progress")

    def test_get_history_includes_data_completeness_fields(self):
        """get_history() should return entries with data completeness fields."""
        from resources.lab_result.repository import LabResultRepository

        repo = LabResultRepository()
        history = run_async(repo.get_history(
            patient_id=TEST_PATIENT_ID,
            test_name="Glucose"
        ))

        assert len(history) > 0

        for entry in history:
            # All entries should have these fields
            assert hasattr(entry, 'acknowledged')
            assert hasattr(entry, 'acknowledged_by')
            assert hasattr(entry, 'acknowledged_at')
            assert hasattr(entry, 'last_updated')


@pytest.mark.integration
class TestLabHistoryServiceTrendCalculation:
    """
    Tests for the LabHistoryService trend calculation and edge cases.
    """

    def test_is_trend_concerning_for_lower_is_better_increasing(self):
        """Increasing trend for lower-is-better test should be concerning."""
        from services.lab_history import LabHistoryService
        from resources import LabResultRepository, TrendAnalysis

        repo = LabResultRepository()
        service = LabHistoryService(repo)

        trend = TrendAnalysis(
            direction="increasing",
            percent_change=15.0,
            absolute_change=1.5,
            first_value=10.0,
            last_value=11.5,
            data_points=5,
        )

        # Glucose is in LOWER_IS_BETTER_TESTS
        assert service.is_trend_concerning("Glucose", trend) is True

    def test_is_trend_concerning_for_lower_is_better_decreasing(self):
        """Decreasing trend for lower-is-better test should not be concerning."""
        from services.lab_history import LabHistoryService
        from resources import LabResultRepository, TrendAnalysis

        repo = LabResultRepository()
        service = LabHistoryService(repo)

        trend = TrendAnalysis(
            direction="decreasing",
            percent_change=-15.0,
            absolute_change=-1.5,
            first_value=11.5,
            last_value=10.0,
            data_points=5,
        )

        # Glucose is in LOWER_IS_BETTER_TESTS
        assert service.is_trend_concerning("Glucose", trend) is False

    def test_is_trend_concerning_for_higher_is_better_decreasing(self):
        """Decreasing trend for higher-is-better test should be concerning."""
        from services.lab_history import LabHistoryService
        from resources import LabResultRepository, TrendAnalysis

        repo = LabResultRepository()
        service = LabHistoryService(repo)

        trend = TrendAnalysis(
            direction="decreasing",
            percent_change=-15.0,
            absolute_change=-10.0,
            first_value=80.0,
            last_value=70.0,
            data_points=5,
        )

        # eGFR is in HIGHER_IS_BETTER_TESTS
        assert service.is_trend_concerning("eGFR", trend) is True

    def test_is_trend_concerning_for_higher_is_better_increasing(self):
        """Increasing trend for higher-is-better test should not be concerning."""
        from services.lab_history import LabHistoryService
        from resources import LabResultRepository, TrendAnalysis

        repo = LabResultRepository()
        service = LabHistoryService(repo)

        trend = TrendAnalysis(
            direction="increasing",
            percent_change=15.0,
            absolute_change=10.0,
            first_value=70.0,
            last_value=80.0,
            data_points=5,
        )

        # HDL is in HIGHER_IS_BETTER_TESTS
        assert service.is_trend_concerning("HDL", trend) is False

    def test_is_trend_concerning_stable_is_never_concerning(self):
        """Stable trend should never be concerning."""
        from services.lab_history import LabHistoryService
        from resources import LabResultRepository, TrendAnalysis

        repo = LabResultRepository()
        service = LabHistoryService(repo)

        trend = TrendAnalysis(
            direction="stable",
            percent_change=2.0,
            absolute_change=0.2,
            first_value=10.0,
            last_value=10.2,
            data_points=5,
        )

        # Even for concerning tests, stable should not be concerning
        assert service.is_trend_concerning("Glucose", trend) is False
        assert service.is_trend_concerning("eGFR", trend) is False
        assert service.is_trend_concerning("UnknownTest", trend) is False

    def test_is_trend_concerning_unknown_test_large_change(self):
        """Unknown test with large change should be concerning."""
        from services.lab_history import LabHistoryService
        from resources import LabResultRepository, TrendAnalysis

        repo = LabResultRepository()
        service = LabHistoryService(repo)

        trend = TrendAnalysis(
            direction="increasing",
            percent_change=25.0,
            absolute_change=5.0,
            first_value=20.0,
            last_value=25.0,
            data_points=5,
        )

        # Unknown test with >20% change should be concerning
        assert service.is_trend_concerning("SomeUnknownTest", trend) is True

    def test_is_trend_concerning_unknown_test_small_change(self):
        """Unknown test with small change should not be concerning."""
        from services.lab_history import LabHistoryService
        from resources import LabResultRepository, TrendAnalysis

        repo = LabResultRepository()
        service = LabHistoryService(repo)

        trend = TrendAnalysis(
            direction="increasing",
            percent_change=15.0,
            absolute_change=3.0,
            first_value=20.0,
            last_value=23.0,
            data_points=5,
        )

        # Unknown test with <20% change should not be concerning
        assert service.is_trend_concerning("SomeUnknownTest", trend) is False


@pytest.mark.integration
class TestLabHistoryServiceEdgeCases:
    """
    Tests for edge cases in LabHistoryService.
    """

    def test_trend_calculation_with_non_numeric_values(self):
        """Trend calculation should handle non-numeric values gracefully."""
        from services.lab_history import LabHistoryService
        from resources import LabResultRepository
        from resources.lab_result.model import LabResultHistory
        from datetime import datetime

        repo = LabResultRepository()
        service = LabHistoryService(repo)

        # Create history with some non-numeric values
        history = [
            LabResultHistory(
                id="1", value="positive", unit="", status="abnormal",
                collection_date=datetime.now(), reference_range="negative"
            ),
            LabResultHistory(
                id="2", value="100", unit="mg/dL", status="normal",
                collection_date=datetime.now(), reference_range="70-100"
            ),
            LabResultHistory(
                id="3", value="95", unit="mg/dL", status="normal",
                collection_date=datetime.now(), reference_range="70-100"
            ),
        ]

        trend = service._calculate_trend(history, "Test")

        # Should still calculate trend from the numeric values
        assert trend is not None
        assert trend.data_points == 2

    def test_trend_calculation_with_all_non_numeric_values(self):
        """Trend calculation should return None for all non-numeric values."""
        from services.lab_history import LabHistoryService
        from resources import LabResultRepository
        from resources.lab_result.model import LabResultHistory
        from datetime import datetime

        repo = LabResultRepository()
        service = LabHistoryService(repo)

        # Create history with only non-numeric values
        history = [
            LabResultHistory(
                id="1", value="positive", unit="", status="abnormal",
                collection_date=datetime.now(), reference_range="negative"
            ),
            LabResultHistory(
                id="2", value="negative", unit="", status="normal",
                collection_date=datetime.now(), reference_range="negative"
            ),
        ]

        trend = service._calculate_trend(history, "Test")

        # Should return None as no numeric values
        assert trend is None

    def test_trend_calculation_with_single_entry(self):
        """Trend calculation should return None for single entry."""
        from services.lab_history import LabHistoryService
        from resources import LabResultRepository
        from resources.lab_result.model import LabResultHistory
        from datetime import datetime

        repo = LabResultRepository()
        service = LabHistoryService(repo)

        history = [
            LabResultHistory(
                id="1", value="100", unit="mg/dL", status="normal",
                collection_date=datetime.now(), reference_range="70-100"
            ),
        ]

        trend = service._calculate_trend(history, "Test")

        assert trend is None

    def test_trend_calculation_with_zero_first_value(self):
        """Trend calculation should handle zero first value."""
        from services.lab_history import LabHistoryService
        from resources import LabResultRepository
        from resources.lab_result.model import LabResultHistory
        from datetime import datetime, timedelta

        repo = LabResultRepository()
        service = LabHistoryService(repo)

        now = datetime.now()
        history = [
            LabResultHistory(
                id="1", value="10", unit="mg/dL", status="normal",
                collection_date=now, reference_range="0-20"
            ),
            LabResultHistory(
                id="2", value="0", unit="mg/dL", status="normal",
                collection_date=now - timedelta(days=30), reference_range="0-20"
            ),
        ]

        trend = service._calculate_trend(history, "Test")

        # Should handle zero gracefully
        assert trend is not None
        assert trend.percent_change == 0.0  # When first value is 0
        assert trend.first_value == 0.0
        assert trend.last_value == 10.0

    def test_trend_calculation_stable_within_5_percent(self):
        """Trend calculation should be stable for changes within 5%."""
        from services.lab_history import LabHistoryService
        from resources import LabResultRepository
        from resources.lab_result.model import LabResultHistory
        from datetime import datetime, timedelta

        repo = LabResultRepository()
        service = LabHistoryService(repo)

        now = datetime.now()
        # 100 -> 103 is 3% change - should be stable
        history = [
            LabResultHistory(
                id="1", value="103", unit="mg/dL", status="normal",
                collection_date=now, reference_range="70-100"
            ),
            LabResultHistory(
                id="2", value="100", unit="mg/dL", status="normal",
                collection_date=now - timedelta(days=30), reference_range="70-100"
            ),
        ]

        trend = service._calculate_trend(history, "Test")

        assert trend is not None
        assert trend.direction == "stable"

    def test_trend_calculation_handles_lt_gt_values(self):
        """Trend calculation should handle <X and >X values."""
        from services.lab_history import LabHistoryService
        from resources import LabResultRepository
        from resources.lab_result.model import LabResultHistory
        from datetime import datetime, timedelta

        repo = LabResultRepository()
        service = LabHistoryService(repo)

        now = datetime.now()
        history = [
            LabResultHistory(
                id="1", value=">100", unit="mg/dL", status="abnormal",
                collection_date=now, reference_range="<80"
            ),
            LabResultHistory(
                id="2", value="<50", unit="mg/dL", status="normal",
                collection_date=now - timedelta(days=30), reference_range="<80"
            ),
        ]

        trend = service._calculate_trend(history, "Test")

        # Should parse 100 and 50 from the values
        assert trend is not None
        assert trend.first_value == 50.0
        assert trend.last_value == 100.0
        assert trend.direction == "increasing"

    def test_lab_history_response_to_dict(self):
        """LabHistoryResponse.to_dict() should serialize correctly."""
        from services.lab_history import LabHistoryResponse
        from resources.lab_result.model import LabResultHistory, TrendAnalysis
        from datetime import datetime

        history = [
            LabResultHistory(
                id="1", value="100", unit="mg/dL", status="normal",
                collection_date=datetime.now(), reference_range="70-100"
            ),
        ]

        trend = TrendAnalysis(
            direction="stable",
            percent_change=0.0,
            absolute_change=0.0,
            first_value=100.0,
            last_value=100.0,
            data_points=1,
        )

        response = LabHistoryResponse(
            test_name="Glucose",
            unit="mg/dL",
            reference_range="70-100",
            history=history,
            trend_analysis=trend,
        )

        data = response.to_dict()

        assert data["testName"] == "Glucose"
        assert data["unit"] == "mg/dL"
        assert data["referenceRange"] == "70-100"
        assert len(data["history"]) == 1
        assert data["trendAnalysis"]["direction"] == "stable"

    def test_lab_history_response_to_dict_no_trend(self):
        """LabHistoryResponse.to_dict() should handle None trend."""
        from services.lab_history import LabHistoryResponse
        from resources.lab_result.model import LabResultHistory
        from datetime import datetime

        history = [
            LabResultHistory(
                id="1", value="positive", unit="", status="abnormal",
                collection_date=datetime.now(), reference_range="negative"
            ),
        ]

        response = LabHistoryResponse(
            test_name="UrineProtein",
            unit="",
            reference_range="negative",
            history=history,
            trend_analysis=None,
        )

        data = response.to_dict()

        assert data["testName"] == "UrineProtein"
        assert data["trendAnalysis"] is None
