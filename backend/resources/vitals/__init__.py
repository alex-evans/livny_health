"""
Vital Signs resource module.

Contains models and repository for vital sign tracking.
"""

from .model import (
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
from .repository import VitalSignRepository

__all__ = [
    "VitalSign",
    "VitalSignHistory",
    "VitalTrendAnalysis",
    "VitalType",
    "VitalStatus",
    "TrendDirection",
    "ClinicalSignificance",
    "VITAL_REFERENCE_RANGES",
    "LOWER_IS_BETTER_VITALS",
    "HIGHER_IS_BETTER_VITALS",
    "VitalSignRepository",
]
