"""
Common dosing patterns database for medications.
Maps medication names to typical dosing regimens.
"""

import re

from .constants import (
    COMMON_DOSING_PATTERNS, 
    ANTIBIOTICS, 
    SHORT_TERM_STEROIDS, 
    PRN_MEDICATIONS
)


def _extract_strength_value(medication_name: str) -> str | None:
    """Extract the numeric strength value from a medication name.

    Only matches numbers followed by a unit (MG, MCG, etc.) to avoid
    matching non-strength numbers like "Take 2 tablets".

    For combination drugs like "500/125 MG", extracts the primary strength (500).
    Handles hyphens (500-MG) and commas (1,000 MG).
    """
    # Handle commas in numbers by removing them first
    name_normalized = medication_name.replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)(?:/\d+)?[\s-]*(?:MG|MCG|MG/ML)\b", name_normalized, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def _find_matching_drug(medication_name: str) -> str | None:
    """Find a matching drug name in our database.

    Returns the first matching drug that appears in the medication name.
    Among matches at the same position, prefers the longest (most specific).
    """
    name_lower = medication_name.lower()
    # Normalize common separators to match our keys
    name_normalized = name_lower.replace("-", "/")

    matches = []
    for drug in COMMON_DOSING_PATTERNS:
        pos = name_normalized.find(drug)
        if pos != -1:
            matches.append((pos, len(drug), drug))

    if not matches:
        return None

    # Sort by position (earliest first), then by length descending (longest first)
    matches.sort(key=lambda x: (x[0], -x[1]))
    return matches[0][2]


def get_common_dosing(medication_name: str) -> list[str]:
    """
    Get common dosing patterns for a medication.

    Args:
        medication_name: The full medication name (e.g., "Amoxicillin 500 MG Oral Tablet")

    Returns:
        List of common dosing patterns, or empty list if not found
    """
    drug = _find_matching_drug(medication_name)
    if not drug:
        return []

    dosing_options = COMMON_DOSING_PATTERNS[drug]

    # Try to match by strength first
    strength = _extract_strength_value(medication_name)
    if strength and strength in dosing_options:
        return dosing_options[strength]

    # Fall back to default dosing
    return dosing_options.get("_default", [])


def get_default_duration(medication_name: str) -> int:
    """
    Get default duration in days based on medication type/class.

    Antibiotics typically 7-10 days, short-term steroids 5-7 days,
    PRN medications 30 days, chronic meds 30 days default.

    Args:
        medication_name: The medication name to check

    Returns:
        Default duration in days
    """
    drug = _find_matching_drug(medication_name)

    if drug in ANTIBIOTICS:
        return 10

    if drug in SHORT_TERM_STEROIDS:
        return 7

    if drug in PRN_MEDICATIONS:
        return 30

    # Chronic medications: 30 days default
    return 30
