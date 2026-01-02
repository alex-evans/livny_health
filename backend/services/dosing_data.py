"""
Common dosing patterns database for medications.
Maps medication names to typical dosing regimens.
"""

import re

# Dosing patterns keyed by generic drug name (lowercase)
# Each entry maps strength patterns to common dosing options
COMMON_DOSING_PATTERNS: dict[str, dict[str, list[str]]] = {
    "amoxicillin": {
        "250": ["250mg TID", "250mg BID"],
        "500": ["500mg TID", "500mg BID"],
        "875": ["875mg BID"],
        "_default": ["500mg TID", "500mg BID"],
    },
    "lisinopril": {
        "5": ["5mg daily"],
        "10": ["10mg daily"],
        "20": ["20mg daily"],
        "40": ["40mg daily"],
        "_default": ["10mg daily"],
    },
    "metformin": {
        "500": ["500mg BID", "500mg daily"],
        "850": ["850mg BID"],
        "1000": ["1000mg BID"],
        "_default": ["500mg BID"],
    },
    "atorvastatin": {
        "10": ["10mg daily at bedtime"],
        "20": ["20mg daily at bedtime"],
        "40": ["40mg daily at bedtime"],
        "80": ["80mg daily at bedtime"],
        "_default": ["20mg daily at bedtime"],
    },
    "omeprazole": {
        "20": ["20mg daily before breakfast"],
        "40": ["40mg daily before breakfast"],
        "_default": ["20mg daily before breakfast"],
    },
    "amlodipine": {
        "5": ["5mg daily"],
        "10": ["10mg daily"],
        "_default": ["5mg daily"],
    },
    "gabapentin": {
        "100": ["100mg TID"],
        "300": ["300mg TID"],
        "400": ["400mg TID"],
        "_default": ["300mg TID"],
    },
    "prednisone": {
        "_default": ["5mg daily", "Taper per instructions"],
    },
    "azithromycin": {
        "250": ["500mg day 1, then 250mg days 2-5"],
        "_default": ["500mg day 1, then 250mg days 2-5"],
    },
    "ciprofloxacin": {
        "250": ["250mg BID"],
        "500": ["500mg BID"],
        "750": ["750mg BID"],
        "_default": ["500mg BID"],
    },
    "albuterol": {
        "_default": ["2 puffs every 4-6 hours PRN"],
    },
    "hydrocodone": {
        "_default": ["1-2 tablets every 4-6 hours PRN"],
    },
    "oxycodone": {
        "5": ["5mg every 4-6 hours PRN"],
        "10": ["10mg every 4-6 hours PRN"],
        "_default": ["5mg every 4-6 hours PRN"],
    },
    "levothyroxine": {
        "_default": ["Take daily on empty stomach"],
    },
    "losartan": {
        "25": ["25mg daily"],
        "50": ["50mg daily"],
        "100": ["100mg daily"],
        "_default": ["50mg daily"],
    },
    "furosemide": {
        "20": ["20mg daily", "20mg BID"],
        "40": ["40mg daily", "40mg BID"],
        "_default": ["40mg daily"],
    },
    "sertraline": {
        "25": ["25mg daily"],
        "50": ["50mg daily"],
        "100": ["100mg daily"],
        "_default": ["50mg daily"],
    },
    "escitalopram": {
        "5": ["5mg daily"],
        "10": ["10mg daily"],
        "20": ["20mg daily"],
        "_default": ["10mg daily"],
    },
    "montelukast": {
        "10": ["10mg daily at bedtime"],
        "_default": ["10mg daily at bedtime"],
    },
    "pantoprazole": {
        "20": ["20mg daily before breakfast"],
        "40": ["40mg daily before breakfast"],
        "_default": ["40mg daily before breakfast"],
    },
    "ibuprofen": {
        "200": ["200-400mg every 4-6 hours PRN"],
        "400": ["400mg every 4-6 hours PRN"],
        "600": ["600mg TID with food"],
        "800": ["800mg TID with food"],
        "_default": ["400mg every 4-6 hours PRN"],
    },
    "acetaminophen": {
        "325": ["325-650mg every 4-6 hours PRN"],
        "500": ["500-1000mg every 4-6 hours PRN"],
        "_default": ["500-1000mg every 4-6 hours PRN"],
    },
    "metoprolol": {
        "25": ["25mg BID"],
        "50": ["50mg BID"],
        "100": ["100mg BID"],
        "_default": ["50mg BID"],
    },
    "carvedilol": {
        "3.125": ["3.125mg BID"],
        "6.25": ["6.25mg BID"],
        "12.5": ["12.5mg BID"],
        "25": ["25mg BID"],
        "_default": ["6.25mg BID"],
    },
    "warfarin": {
        "_default": ["Per INR monitoring"],
    },
    "apixaban": {
        "2.5": ["2.5mg BID"],
        "5": ["5mg BID"],
        "_default": ["5mg BID"],
    },
    "clopidogrel": {
        "75": ["75mg daily"],
        "_default": ["75mg daily"],
    },
    "simvastatin": {
        "10": ["10mg daily at bedtime"],
        "20": ["20mg daily at bedtime"],
        "40": ["40mg daily at bedtime"],
        "_default": ["20mg daily at bedtime"],
    },
    "pravastatin": {
        "10": ["10mg daily at bedtime"],
        "20": ["20mg daily at bedtime"],
        "40": ["40mg daily at bedtime"],
        "_default": ["40mg daily at bedtime"],
    },
    "rosuvastatin": {
        "5": ["5mg daily"],
        "10": ["10mg daily"],
        "20": ["20mg daily"],
        "_default": ["10mg daily"],
    },
    "tramadol": {
        "50": ["50mg every 4-6 hours PRN"],
        "_default": ["50mg every 4-6 hours PRN"],
    },
    "cyclobenzaprine": {
        "5": ["5mg TID"],
        "10": ["10mg TID"],
        "_default": ["10mg TID"],
    },
    "meloxicam": {
        "7.5": ["7.5mg daily"],
        "15": ["15mg daily"],
        "_default": ["15mg daily"],
    },
    "naproxen": {
        "250": ["250mg BID"],
        "500": ["500mg BID"],
        "_default": ["500mg BID"],
    },
    "doxycycline": {
        "100": ["100mg BID", "100mg daily"],
        "_default": ["100mg BID"],
    },
    "cephalexin": {
        "250": ["250mg QID"],
        "500": ["500mg QID", "500mg BID"],
        "_default": ["500mg QID"],
    },
    "augmentin": {
        "500": ["500/125mg BID"],
        "875": ["875/125mg BID"],
        "_default": ["875/125mg BID"],
    },
    "amoxicillin/clavulanate": {
        "500": ["500/125mg BID"],
        "875": ["875/125mg BID"],
        "_default": ["875/125mg BID"],
    },
    "fluticasone": {
        "_default": ["1-2 sprays each nostril daily"],
    },
    "cetirizine": {
        "10": ["10mg daily"],
        "_default": ["10mg daily"],
    },
    "loratadine": {
        "10": ["10mg daily"],
        "_default": ["10mg daily"],
    },
    "diphenhydramine": {
        "25": ["25-50mg at bedtime PRN"],
        "50": ["50mg at bedtime PRN"],
        "_default": ["25-50mg at bedtime PRN"],
    },
}


def _extract_strength_value(medication_name: str) -> str | None:
    """Extract the numeric strength value from a medication name."""
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:MG|MCG|MG/ML)?", medication_name, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def _find_matching_drug(medication_name: str) -> str | None:
    """Find a matching drug name in our database."""
    name_lower = medication_name.lower()
    for drug in COMMON_DOSING_PATTERNS:
        if drug in name_lower:
            return drug
    return None


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


# Medication categories for default duration
ANTIBIOTICS = {
    "amoxicillin",
    "azithromycin",
    "ciprofloxacin",
    "doxycycline",
    "cephalexin",
    "augmentin",
    "amoxicillin/clavulanate",
}

SHORT_TERM_STEROIDS = {
    "prednisone",
}

PRN_MEDICATIONS = {
    "hydrocodone",
    "oxycodone",
    "ibuprofen",
    "acetaminophen",
    "albuterol",
    "tramadol",
}


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
