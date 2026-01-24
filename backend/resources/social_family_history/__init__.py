"""
Social and Family History resource module.

Contains models and repository for social history (smoking, alcohol, occupation, etc.)
and family history (relatives with conditions, hereditary syndromes) tracking.
"""

from .model import (
    SocialFamilyHistory,
    SocialHistory,
    FamilyHistory,
    SmokingHistory,
    AlcoholHistory,
    SubstanceUseHistory,
    FamilyMember,
    FamilyMemberCondition,
    SignificantCondition,
    RiskAssessment,
    SmokingStatus,
    AlcoholUse,
    SubstanceUseLevel,
    ExerciseLevel,
    DietType,
    MaritalStatus,
    RelativeDegree,
    RelativeType,
    RiskLevel,
    AdoptionStatus,
    RELATIVE_DEGREE_MAP,
)
from .repository import SocialFamilyHistoryRepository

__all__ = [
    "SocialFamilyHistory",
    "SocialHistory",
    "FamilyHistory",
    "SmokingHistory",
    "AlcoholHistory",
    "SubstanceUseHistory",
    "FamilyMember",
    "FamilyMemberCondition",
    "SignificantCondition",
    "RiskAssessment",
    "SmokingStatus",
    "AlcoholUse",
    "SubstanceUseLevel",
    "ExerciseLevel",
    "DietType",
    "MaritalStatus",
    "RelativeDegree",
    "RelativeType",
    "RiskLevel",
    "AdoptionStatus",
    "RELATIVE_DEGREE_MAP",
    "SocialFamilyHistoryRepository",
]
