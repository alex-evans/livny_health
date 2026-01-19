"""
LabResult resource package.
"""

from .model import LabResult, LabResultHistory, LabResultStatus, TrendAnalysis
from .repository import LabResultRepository

__all__ = [
    "LabResult",
    "LabResultHistory",
    "LabResultStatus",
    "TrendAnalysis",
    "LabResultRepository",
]
