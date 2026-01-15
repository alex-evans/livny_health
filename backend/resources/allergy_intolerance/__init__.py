"""
AllergyIntolerance resource package.
"""

from .model import AllergyIntolerance, AllergyReaction, AllergyCategory, AllergyCriticality
from .repository import AllergyIntoleranceRepository

__all__ = [
    "AllergyIntolerance",
    "AllergyReaction",
    "AllergyCategory",
    "AllergyCriticality",
    "AllergyIntoleranceRepository",
]
