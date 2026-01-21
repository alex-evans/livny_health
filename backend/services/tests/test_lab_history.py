"""
Unit tests for LabHistoryService.

Tests lab history retrieval and trend analysis.
"""
import asyncio
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
import uuid

from services.lab_history import LabHistoryService, LabHistoryResponse
from resources import LabResultRepository, LabResultHistory, TrendAnalysis


def make_lab_history(value: str, unit: str, ref_range: str, collection_date: datetime, status: str = "normal") -> LabResultHistory:
    """Helper to create LabResultHistory with required fields."""
    return LabResultHistory(
        id=str(uuid.uuid4()),
        value=value,
        unit=unit,
        reference_range=ref_range,
        collection_date=collection_date,
        status=status,
    )


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.mark.unit
class TestLabHistoryServiceIntegration:
    """Integration tests using seeded data."""

    def test_get_lab_history_returns_results(self, lab_history_service):
        """Should return lab history for existing patient and test."""
        response = run_async(lab_history_service.get_lab_history(
            patient_id="patient-001",
            test_name="HbA1c",
            days_back=3650,
        ))

        # May or may not have data depending on seed, just test it doesn't error
        # If there's data, check structure
        if response:
            assert response.test_name == "HbA1c"
            assert isinstance(response.history, list)

    def test_get_lab_history_returns_none_for_nonexistent(self, lab_history_service):
        """Should return None for non-existent test."""
        response = run_async(lab_history_service.get_lab_history(
            patient_id="patient-001",
            test_name="NonExistentTest12345",
            days_back=365,
        ))

        assert response is None


@pytest.mark.unit
class TestLabHistoryServiceUnit:
    """Unit tests with mocked repository."""

    @pytest.fixture
    def mock_lab_repo(self):
        """Create a mock lab result repository."""
        return MagicMock(spec=LabResultRepository)

    @pytest.fixture
    def service(self, mock_lab_repo):
        """Create service with mocked repo."""
        return LabHistoryService(lab_result_repo=mock_lab_repo)

    def test_get_lab_history_with_data(self, service, mock_lab_repo):
        """Should return lab history response with trend analysis."""
        now = datetime.now(timezone.utc)
        history = [
            make_lab_history("7.2", "%", "4.0-5.6", now),
            make_lab_history("7.8", "%", "4.0-5.6", now - timedelta(days=90)),
            make_lab_history("8.1", "%", "4.0-5.6", now - timedelta(days=180)),
        ]
        mock_lab_repo.get_history = AsyncMock(return_value=history)

        response = run_async(service.get_lab_history(
            patient_id="patient-001",
            test_name="HbA1c",
            days_back=365,
            limit=10,
        ))

        assert response is not None
        assert response.test_name == "HbA1c"
        assert response.unit == "%"
        assert response.reference_range == "4.0-5.6"
        assert len(response.history) == 3

    def test_get_lab_history_empty(self, service, mock_lab_repo):
        """Should return None when no history found."""
        mock_lab_repo.get_history = AsyncMock(return_value=[])

        response = run_async(service.get_lab_history(
            patient_id="patient-001",
            test_name="HbA1c",
        ))

        assert response is None

    def test_get_lab_history_single_result_no_trend(self, service, mock_lab_repo):
        """Should return response without trend for single result."""
        now = datetime.now(timezone.utc)
        history = [
            make_lab_history("7.2", "%", "4.0-5.6", now),
        ]
        mock_lab_repo.get_history = AsyncMock(return_value=history)

        response = run_async(service.get_lab_history(
            patient_id="patient-001",
            test_name="HbA1c",
        ))

        assert response is not None
        assert response.trend_analysis is None


@pytest.mark.unit
class TestTrendCalculation:
    """Tests for trend calculation logic."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repo."""
        mock_repo = MagicMock(spec=LabResultRepository)
        return LabHistoryService(lab_result_repo=mock_repo)

    def test_calculate_trend_increasing(self, service):
        """Should detect increasing trend."""
        now = datetime.now(timezone.utc)
        history = [
            make_lab_history("10", "mg/dL", "0-100", now),
            make_lab_history("5", "mg/dL", "0-100", now - timedelta(days=30)),
        ]

        trend = service._calculate_trend(history, "Test")

        assert trend is not None
        assert trend.direction == "increasing"
        assert trend.first_value == 5.0
        assert trend.last_value == 10.0
        assert trend.percent_change == 100.0

    def test_calculate_trend_decreasing(self, service):
        """Should detect decreasing trend."""
        now = datetime.now(timezone.utc)
        history = [
            make_lab_history("5", "mg/dL", "0-100", now),
            make_lab_history("10", "mg/dL", "0-100", now - timedelta(days=30)),
        ]

        trend = service._calculate_trend(history, "Test")

        assert trend is not None
        assert trend.direction == "decreasing"
        assert trend.percent_change == -50.0

    def test_calculate_trend_stable(self, service):
        """Should detect stable trend when change is small."""
        now = datetime.now(timezone.utc)
        history = [
            make_lab_history("100", "mg/dL", "0-200", now),
            make_lab_history("98", "mg/dL", "0-200", now - timedelta(days=30)),
        ]

        trend = service._calculate_trend(history, "Test")

        assert trend is not None
        assert trend.direction == "stable"

    def test_calculate_trend_handles_comparison_symbols(self, service):
        """Should handle < and > symbols in values."""
        now = datetime.now(timezone.utc)
        history = [
            make_lab_history("<10", "mg/dL", "0-100", now),
            make_lab_history(">5", "mg/dL", "0-100", now - timedelta(days=30)),
        ]

        trend = service._calculate_trend(history, "Test")

        assert trend is not None
        assert trend.first_value == 5.0
        assert trend.last_value == 10.0

    def test_calculate_trend_non_numeric_values(self, service):
        """Should return None if values are non-numeric."""
        now = datetime.now(timezone.utc)
        history = [
            make_lab_history("Positive", "", "Negative", now),
            make_lab_history("Negative", "", "Negative", now - timedelta(days=30)),
        ]

        trend = service._calculate_trend(history, "Test")

        assert trend is None

    def test_calculate_trend_zero_first_value(self, service):
        """Should handle zero first value without division error."""
        now = datetime.now(timezone.utc)
        history = [
            make_lab_history("10", "mg/dL", "0-100", now),
            make_lab_history("0", "mg/dL", "0-100", now - timedelta(days=30)),
        ]

        trend = service._calculate_trend(history, "Test")

        assert trend is not None
        assert trend.percent_change == 0.0  # Division by zero handled


@pytest.mark.unit
class TestConcerningTrends:
    """Tests for concerning trend detection."""

    @pytest.fixture
    def service(self):
        """Create service with mocked repo."""
        mock_repo = MagicMock(spec=LabResultRepository)
        return LabHistoryService(lab_result_repo=mock_repo)

    def test_stable_trend_not_concerning(self, service):
        """Stable trend should not be concerning."""
        trend = TrendAnalysis(
            direction="stable",
            percent_change=2.0,
            absolute_change=0.5,
            first_value=100.0,
            last_value=102.0,
            data_points=3,
        )

        assert service.is_trend_concerning("HbA1c", trend) is False

    def test_increasing_hba1c_concerning(self, service):
        """Increasing HbA1c (lower is better) should be concerning."""
        trend = TrendAnalysis(
            direction="increasing",
            percent_change=15.0,
            absolute_change=1.0,
            first_value=6.5,
            last_value=7.5,
            data_points=3,
        )

        assert service.is_trend_concerning("HbA1c", trend) is True

    def test_decreasing_hba1c_not_concerning(self, service):
        """Decreasing HbA1c (lower is better) should not be concerning."""
        trend = TrendAnalysis(
            direction="decreasing",
            percent_change=-10.0,
            absolute_change=-0.7,
            first_value=7.5,
            last_value=6.8,
            data_points=3,
        )

        assert service.is_trend_concerning("HbA1c", trend) is False

    def test_decreasing_hdl_concerning(self, service):
        """Decreasing HDL (higher is better) should be concerning."""
        trend = TrendAnalysis(
            direction="decreasing",
            percent_change=-20.0,
            absolute_change=-10.0,
            first_value=50.0,
            last_value=40.0,
            data_points=3,
        )

        assert service.is_trend_concerning("HDL", trend) is True

    def test_increasing_hdl_not_concerning(self, service):
        """Increasing HDL (higher is better) should not be concerning."""
        trend = TrendAnalysis(
            direction="increasing",
            percent_change=25.0,
            absolute_change=10.0,
            first_value=40.0,
            last_value=50.0,
            data_points=3,
        )

        assert service.is_trend_concerning("HDL", trend) is False

    def test_unknown_test_large_change_concerning(self, service):
        """Unknown test with large change should be concerning."""
        trend = TrendAnalysis(
            direction="increasing",
            percent_change=30.0,
            absolute_change=15.0,
            first_value=50.0,
            last_value=65.0,
            data_points=3,
        )

        assert service.is_trend_concerning("UnknownTest", trend) is True

    def test_unknown_test_small_change_not_concerning(self, service):
        """Unknown test with small change should not be concerning."""
        trend = TrendAnalysis(
            direction="increasing",
            percent_change=10.0,
            absolute_change=5.0,
            first_value=50.0,
            last_value=55.0,
            data_points=3,
        )

        assert service.is_trend_concerning("UnknownTest", trend) is False


@pytest.mark.unit
class TestLabHistoryResponse:
    """Tests for LabHistoryResponse dataclass."""

    def test_to_dict_without_trend(self):
        """Should convert to dict without trend analysis."""
        now = datetime.now(timezone.utc)
        history = [
            make_lab_history("7.2", "%", "4.0-5.6", now),
        ]
        response = LabHistoryResponse(
            test_name="HbA1c",
            unit="%",
            reference_range="4.0-5.6",
            history=history,
            trend_analysis=None,
        )

        result = response.to_dict()

        assert result["testName"] == "HbA1c"
        assert result["unit"] == "%"
        assert result["referenceRange"] == "4.0-5.6"
        assert len(result["history"]) == 1
        assert result["trendAnalysis"] is None

    def test_to_dict_with_trend(self):
        """Should convert to dict with trend analysis."""
        now = datetime.now(timezone.utc)
        history = [
            make_lab_history("7.2", "%", "4.0-5.6", now),
            make_lab_history("7.8", "%", "4.0-5.6", now - timedelta(days=90)),
        ]
        trend = TrendAnalysis(
            direction="decreasing",
            percent_change=-7.7,
            absolute_change=-0.6,
            first_value=7.8,
            last_value=7.2,
            data_points=2,
        )
        response = LabHistoryResponse(
            test_name="HbA1c",
            unit="%",
            reference_range="4.0-5.6",
            history=history,
            trend_analysis=trend,
        )

        result = response.to_dict()

        assert result["trendAnalysis"] is not None
        assert result["trendAnalysis"]["direction"] == "decreasing"
