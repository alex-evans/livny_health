"""
Vitals Service.

Provides vital signs retrieval, trend analysis, and clinical significance calculation.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from resources import (
    VitalSignRepository,
    VitalSign,
    VitalSignHistory,
    VitalTrendAnalysis,
    VitalType,
    VitalStatus,
    TrendDirection,
    ClinicalSignificance,
    VITAL_REFERENCE_RANGES,
    LOWER_IS_BETTER_VITALS,
    HIGHER_IS_BETTER_VITALS,
)


@dataclass
class SparklinePoint:
    """A single point in the sparkline data."""
    value: float
    status: VitalStatus
    date: datetime

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "status": self.status,
            "date": self.date.isoformat(),
        }


@dataclass
class CurrentVitalResponse:
    """Response for a single current vital with trend and sparkline data."""
    vital_type: VitalType
    value: float
    unit: str
    status: VitalStatus
    recorded_at: datetime
    reference_range: str
    recorded_by: str | None
    location: str | None
    trend: VitalTrendAnalysis | None
    sparkline_data: list[SparklinePoint]

    def to_dict(self) -> dict:
        return {
            "vitalType": self.vital_type,
            "value": self.value,
            "unit": self.unit,
            "status": self.status,
            "recordedAt": self.recorded_at.isoformat(),
            "referenceRange": self.reference_range,
            "recordedBy": self.recorded_by,
            "location": self.location,
            "trend": self.trend.to_dict() if self.trend else None,
            "sparklineData": [p.to_dict() for p in self.sparkline_data],
        }


@dataclass
class BMIResponse:
    """Response for BMI calculation."""
    value: float
    category: str
    height_value: float
    height_unit: str
    weight_value: float
    weight_unit: str
    calculated_at: datetime

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "category": self.category,
            "heightValue": self.height_value,
            "heightUnit": self.height_unit,
            "weightValue": self.weight_value,
            "weightUnit": self.weight_unit,
            "calculatedAt": self.calculated_at.isoformat(),
        }


@dataclass
class VitalsResponse:
    """Response containing all current vitals with trends."""
    vitals: list[CurrentVitalResponse]
    bmi: BMIResponse | None
    most_recent_date: datetime | None

    def to_dict(self) -> dict:
        return {
            "vitals": [v.to_dict() for v in self.vitals],
            "bmi": self.bmi.to_dict() if self.bmi else None,
            "mostRecentDate": self.most_recent_date.isoformat() if self.most_recent_date else None,
        }


@dataclass
class VitalHistoryResponse:
    """Response containing vital history and trend analysis."""
    vital_type: VitalType
    unit: str
    reference_range: str
    history: list[VitalSignHistory]
    trend_analysis: VitalTrendAnalysis | None

    def to_dict(self) -> dict:
        return {
            "vitalType": self.vital_type,
            "unit": self.unit,
            "referenceRange": self.reference_range,
            "history": [h.to_dict() for h in self.history],
            "trendAnalysis": self.trend_analysis.to_dict() if self.trend_analysis else None,
        }


class VitalsService:
    """
    Service for retrieving vitals and calculating trends.
    """

    def __init__(self, vitals_repo: VitalSignRepository):
        self.vitals_repo = vitals_repo

    async def get_current_vitals(
        self,
        patient_id: str,
        months: int = 12,
        include_trends: bool = True,
    ) -> VitalsResponse:
        """
        Get current vitals with optional trend analysis.

        Args:
            patient_id: The patient ID
            months: How many months of history to use for trend analysis
            include_trends: Whether to include trend data

        Returns:
            VitalsResponse with current vitals and optional BMI
        """
        # Get most recent vital for each type
        current_vitals = await self.vitals_repo.get_current_vitals(patient_id)

        if not current_vitals:
            return VitalsResponse(vitals=[], bmi=None, most_recent_date=None)

        vitals_responses: list[CurrentVitalResponse] = []
        most_recent_date: datetime | None = None

        for vital_type, vital in current_vitals.items():
            # Track most recent date
            if most_recent_date is None or vital.recorded_at > most_recent_date:
                most_recent_date = vital.recorded_at

            # Get history for sparkline and trend
            sparkline_data: list[SparklinePoint] = []
            trend: VitalTrendAnalysis | None = None

            if include_trends:
                days_back = months * 30  # Approximate days
                history = await self.vitals_repo.get_history(
                    patient_id=patient_id,
                    vital_type=vital_type,
                    days_back=days_back,
                    limit=20,
                )

                # Create sparkline data (reverse to chronological order)
                sparkline_data = [
                    SparklinePoint(
                        value=h.value,
                        status=h.status,
                        date=h.recorded_at,
                    )
                    for h in reversed(history)
                ]

                # Calculate trend
                if len(history) >= 2:
                    trend = self._calculate_trend(history, vital_type)

            vitals_responses.append(
                CurrentVitalResponse(
                    vital_type=vital_type,
                    value=vital.value,
                    unit=vital.unit,
                    status=vital.status,
                    recorded_at=vital.recorded_at,
                    reference_range=vital.reference_range,
                    recorded_by=vital.recorded_by,
                    location=vital.location,
                    trend=trend,
                    sparkline_data=sparkline_data,
                )
            )

        # Calculate BMI if height and weight are available
        bmi = self._calculate_bmi(current_vitals)

        return VitalsResponse(
            vitals=vitals_responses,
            bmi=bmi,
            most_recent_date=most_recent_date,
        )

    async def get_vital_history(
        self,
        patient_id: str,
        vital_type: VitalType,
        days_back: int = 365,
    ) -> VitalHistoryResponse | None:
        """
        Get vital history for a specific vital type.

        Args:
            patient_id: The patient ID
            vital_type: The vital type to look up
            days_back: How many days of history to include

        Returns:
            VitalHistoryResponse with history and trend analysis, or None if no results
        """
        history = await self.vitals_repo.get_history(
            patient_id=patient_id,
            vital_type=vital_type,
            limit=50,
            days_back=days_back,
        )

        if not history:
            return None

        # Get reference range and unit from most recent result
        most_recent = history[0]
        unit = most_recent.unit
        reference_range = most_recent.reference_range

        # Calculate trend analysis
        trend_analysis = self._calculate_trend(history, vital_type) if len(history) >= 2 else None

        return VitalHistoryResponse(
            vital_type=vital_type,
            unit=unit,
            reference_range=reference_range,
            history=history,
            trend_analysis=trend_analysis,
        )

    def _calculate_trend(
        self,
        history: list[VitalSignHistory],
        vital_type: VitalType,
    ) -> VitalTrendAnalysis | None:
        """
        Calculate trend analysis from historical data.

        Args:
            history: List of history entries (sorted most recent first)
            vital_type: The type of vital for clinical significance calculation

        Returns:
            VitalTrendAnalysis or None if insufficient data
        """
        if len(history) < 2:
            return None

        # History is sorted most recent first
        current_value = history[0].value
        previous_value = history[1].value
        previous_date = history[1].recorded_at

        # Calculate changes
        absolute_change = current_value - previous_value
        if previous_value != 0:
            percent_change = ((current_value - previous_value) / abs(previous_value)) * 100
        else:
            percent_change = 0.0

        # Determine direction (stable if within 5%)
        direction: TrendDirection
        if abs(percent_change) <= 5:
            direction = "stable"
        elif absolute_change > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        # Calculate clinical significance
        clinical_significance = self._calculate_clinical_significance(
            vital_type, direction
        )

        return VitalTrendAnalysis(
            direction=direction,
            percent_change=round(percent_change, 1),
            absolute_change=round(absolute_change, 2),
            previous_value=previous_value,
            current_value=current_value,
            previous_date=previous_date,
            data_points=len(history),
            clinical_significance=clinical_significance,
        )

    def _calculate_clinical_significance(
        self,
        vital_type: VitalType,
        direction: TrendDirection,
    ) -> ClinicalSignificance:
        """
        Determine if a trend is clinically significant.

        - For BP, weight, heart rate, respiratory rate: lower is better
        - For oxygen saturation: higher is better
        - For temperature, height: depends on context (neutral)
        """
        if direction == "stable":
            return "neutral"

        if vital_type in LOWER_IS_BETTER_VITALS:
            # Lower is better: increasing is concerning, decreasing is good
            return "concerning" if direction == "increasing" else "good"
        elif vital_type in HIGHER_IS_BETTER_VITALS:
            # Higher is better: decreasing is concerning, increasing is good
            return "concerning" if direction == "decreasing" else "good"
        else:
            # For temperature and height, significance depends on context
            return "neutral"

    def _calculate_bmi(
        self,
        current_vitals: dict[VitalType, VitalSign],
    ) -> BMIResponse | None:
        """
        Calculate BMI from height and weight.

        BMI = weight (kg) / height (m)^2

        Categories:
        - Underweight: < 18.5
        - Normal: 18.5 - 24.9
        - Overweight: 25 - 29.9
        - Obese: >= 30
        """
        height_vital = current_vitals.get("height")
        weight_vital = current_vitals.get("weight")

        if height_vital is None or weight_vital is None:
            return None

        height_value = height_vital.value
        weight_value = weight_vital.value

        # Convert to metric for calculation
        # Assume height is in inches and weight is in lbs
        height_unit = height_vital.unit
        weight_unit = weight_vital.unit

        # Convert height to meters
        if height_unit == "in" or height_unit == "inches":
            height_m = height_value * 0.0254
        elif height_unit == "cm":
            height_m = height_value / 100
        elif height_unit == "m":
            height_m = height_value
        else:
            # Assume inches if unknown
            height_m = height_value * 0.0254

        # Convert weight to kg
        if weight_unit == "lbs" or weight_unit == "lb":
            weight_kg = weight_value * 0.453592
        elif weight_unit == "kg":
            weight_kg = weight_value
        else:
            # Assume lbs if unknown
            weight_kg = weight_value * 0.453592

        # Calculate BMI
        if height_m <= 0:
            return None

        bmi_value = weight_kg / (height_m ** 2)

        # Determine category
        if bmi_value < 18.5:
            category = "Underweight"
        elif bmi_value < 25:
            category = "Normal"
        elif bmi_value < 30:
            category = "Overweight"
        else:
            category = "Obese"

        # Use the more recent date for calculated_at
        calculated_at = max(height_vital.recorded_at, weight_vital.recorded_at)

        return BMIResponse(
            value=round(bmi_value, 1),
            category=category,
            height_value=height_value,
            height_unit=height_unit,
            weight_value=weight_value,
            weight_unit=weight_unit,
            calculated_at=calculated_at,
        )
