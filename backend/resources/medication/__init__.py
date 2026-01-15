"""
Medication resource package.
"""

from .model import Medication
from .repository import MedicationRepository

__all__ = ["Medication", "MedicationRepository"]
