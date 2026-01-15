"""
Patient resource package.
"""

from .model import Patient
from .repository import PatientRepository

__all__ = ["Patient", "PatientRepository"]
