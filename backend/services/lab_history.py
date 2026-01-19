"""
Lab History Service.

Provides lab result history retrieval and trend analysis.
"""

from dataclasses import dataclass
from typing import Literal

from resources import LabResultRepository, LabResultHistory, TrendAnalysis


@dataclass
class LabHistoryResponse:
    """Response containing lab history and trend analysis."""
    test_name: str
    unit: str
    reference_range: str
    history: list[LabResultHistory]
    trend_analysis: TrendAnalysis | None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "testName": self.test_name,
            "unit": self.unit,
            "referenceRange": self.reference_range,
            "history": [h.to_dict() for h in self.history],
            "trendAnalysis": self.trend_analysis.to_dict() if self.trend_analysis else None,
        }


class LabHistoryService:
    """
    Service for retrieving lab history and calculating trends.
    """

    # Tests where LOWER values are generally better
    LOWER_IS_BETTER_TESTS = {
        "HbA1c", "A1C", "HgbA1c", "Hemoglobin A1C",
        "LDL", "LDL-C", "Low-Density Lipoprotein Cholesterol",
        "TC", "Total Cholesterol",
        "TG", "Trig", "Triglycerides",
        "BUN", "Blood Urea Nitrogen",
        "Cr", "Creatinine",
        "ALT", "Alanine Aminotransferase",
        "AST", "Aspartate Aminotransferase",
        "ALP", "Alkaline Phosphatase",
        "GGT", "Gamma-Glutamyl Transferase",
        "T. Bili", "Total Bilirubin",
        "D. Bili", "Direct Bilirubin",
        "ESR", "Erythrocyte Sedimentation Rate",
        "CRP", "C-Reactive Protein",
        "hs-CRP", "High-Sensitivity C-Reactive Protein",
        "PSA", "Prostate-Specific Antigen",
        "FBG", "Fasting Blood Glucose", "FBS", "Fasting Blood Sugar",
        "RBS", "Random Blood Sugar", "Glucose",
        "Potassium",  # High potassium is dangerous
    }

    # Tests where HIGHER values are generally better
    HIGHER_IS_BETTER_TESTS = {
        "HDL", "HDL-C", "High-Density Lipoprotein Cholesterol",
        "eGFR", "GFR", "Estimated Glomerular Filtration Rate",
    }

    def __init__(self, lab_result_repo: LabResultRepository):
        self.lab_result_repo = lab_result_repo

    async def get_lab_history(
        self,
        patient_id: str,
        test_name: str,
        days_back: int = 365,
        limit: int = 10,
    ) -> LabHistoryResponse | None:
        """
        Get lab result history for a specific test.

        Args:
            patient_id: The patient ID
            test_name: The test name to look up
            days_back: How many days of history to include
            limit: Maximum number of results

        Returns:
            LabHistoryResponse with history and trend analysis, or None if no results
        """
        history = await self.lab_result_repo.get_history(
            patient_id=patient_id,
            test_name=test_name,
            limit=limit,
            days_back=days_back,
        )

        if not history:
            return None

        # Get reference range and unit from most recent result
        most_recent = history[0]
        unit = most_recent.unit
        reference_range = most_recent.reference_range

        # Calculate trend analysis
        trend_analysis = self._calculate_trend(history, test_name)

        return LabHistoryResponse(
            test_name=test_name,
            unit=unit,
            reference_range=reference_range,
            history=history,
            trend_analysis=trend_analysis,
        )

    def _calculate_trend(
        self,
        history: list[LabResultHistory],
        test_name: str,
    ) -> TrendAnalysis | None:
        """
        Calculate trend analysis from historical data.

        Uses linear regression-like approach to determine overall trend.
        """
        if len(history) < 2:
            return None

        # Extract numeric values (history is already sorted most recent first)
        numeric_values: list[tuple[float, LabResultHistory]] = []
        for entry in history:
            try:
                value = float(entry.value.replace("<", "").replace(">", "").strip())
                numeric_values.append((value, entry))
            except ValueError:
                continue

        if len(numeric_values) < 2:
            return None

        # Get first and last values (chronologically)
        # History is sorted most recent first, so reverse for chronological order
        numeric_values.reverse()
        first_value = numeric_values[0][0]
        last_value = numeric_values[-1][0]

        # Calculate changes
        absolute_change = last_value - first_value
        if first_value != 0:
            percent_change = ((last_value - first_value) / abs(first_value)) * 100
        else:
            percent_change = 0.0

        # Determine direction (stable if within 5%)
        direction: Literal["increasing", "decreasing", "stable"]
        if abs(percent_change) <= 5:
            direction = "stable"
        elif absolute_change > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        return TrendAnalysis(
            direction=direction,
            percent_change=round(percent_change, 1),
            absolute_change=round(absolute_change, 2),
            first_value=first_value,
            last_value=last_value,
            data_points=len(numeric_values),
        )

    def is_trend_concerning(
        self,
        test_name: str,
        trend: TrendAnalysis,
    ) -> bool:
        """
        Determine if a trend is clinically concerning.

        Returns True if the trend direction is unfavorable for the test type.
        """
        if trend.direction == "stable":
            return False

        if test_name in self.LOWER_IS_BETTER_TESTS:
            return trend.direction == "increasing"
        elif test_name in self.HIGHER_IS_BETTER_TESTS:
            return trend.direction == "decreasing"

        # For unknown tests, any significant change might be notable
        return abs(trend.percent_change) > 20
