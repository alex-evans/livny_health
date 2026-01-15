"""
Medication Search Service.

Handles medication search via RxNorm and dosing defaults.
"""

import re
import httpx

from resources import Medication, MedicationRepository


RXNORM_BASE_URL = "https://rxnav.nlm.nih.gov/REST"

# Form patterns for extracting dosage forms
FORM_PATTERNS = {
    "Oral Tablet": "tablet",
    "Oral Capsule": "capsule",
    "Oral Solution": "liquid",
    "Oral Suspension": "liquid",
    "Injectable Solution": "injection",
    "Injection": "injection",
    "Topical Cream": "topical",
    "Topical Ointment": "topical",
    "Topical Gel": "topical",
    "Metered Dose Inhaler": "inhaler",
    "Inhalation Powder": "inhaler",
}

# Medication categories for default duration
ANTIBIOTICS = {
    "amoxicillin", "azithromycin", "ciprofloxacin", "doxycycline",
    "cephalexin", "augmentin", "amoxicillin/clavulanate",
}

SHORT_TERM_STEROIDS = {"prednisone"}

PRN_MEDICATIONS = {
    "hydrocodone", "oxycodone", "ibuprofen", "acetaminophen", "albuterol", "tramadol",
}

# Common dosing patterns
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
    "prednisone": {"_default": ["5mg daily", "Taper per instructions"]},
    "azithromycin": {"250": ["500mg day 1, then 250mg days 2-5"], "_default": ["500mg day 1, then 250mg days 2-5"]},
    "ciprofloxacin": {"250": ["250mg BID"], "500": ["500mg BID"], "750": ["750mg BID"], "_default": ["500mg BID"]},
    "albuterol": {"_default": ["2 puffs every 4-6 hours PRN"]},
    "hydrocodone": {"_default": ["1-2 tablets every 4-6 hours PRN"]},
    "oxycodone": {"5": ["5mg every 4-6 hours PRN"], "10": ["10mg every 4-6 hours PRN"], "_default": ["5mg every 4-6 hours PRN"]},
    "sertraline": {"25": ["25mg daily"], "50": ["50mg daily"], "100": ["100mg daily"], "_default": ["50mg daily"]},
    "warfarin": {"_default": ["Per INR monitoring"]},
    "simvastatin": {"10": ["10mg daily at bedtime"], "20": ["20mg daily at bedtime"], "40": ["40mg daily at bedtime"], "_default": ["20mg daily at bedtime"]},
    "tramadol": {"50": ["50mg every 4-6 hours PRN"], "_default": ["50mg every 4-6 hours PRN"]},
    "ibuprofen": {"400": ["400mg every 4-6 hours PRN"], "600": ["600mg TID with food"], "800": ["800mg TID with food"], "_default": ["400mg every 4-6 hours PRN"]},
}


def _extract_strength(name: str) -> str:
    """Extract strength from RxNorm drug name."""
    match = re.search(r"(\d+(?:\.\d+)?(?:/\d+(?:\.\d+)?)?\s*(?:MG|MCG|MG/ML|UNITS?|%|MEQ))", name, re.IGNORECASE)
    return match.group(1) if match else ""


def _extract_form(name: str) -> str:
    """Extract dosage form from RxNorm drug name."""
    name_upper = name.upper()
    for pattern, form in FORM_PATTERNS.items():
        if pattern.upper() in name_upper:
            return form
    return ""


def _extract_strength_value(medication_name: str) -> str | None:
    """Extract the numeric strength value from a medication name."""
    name_normalized = medication_name.replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)(?:/\d+)?[\s-]*(?:MG|MCG|MG/ML)\b", name_normalized, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def _find_matching_drug(medication_name: str) -> str | None:
    """Find a matching drug name in our database."""
    name_lower = medication_name.lower()
    name_normalized = name_lower.replace("-", "/")

    matches = []
    for drug in COMMON_DOSING_PATTERNS:
        pos = name_normalized.find(drug)
        if pos != -1:
            matches.append((pos, len(drug), drug))

    if not matches:
        return None

    matches.sort(key=lambda x: (x[0], -x[1]))
    return matches[0][2]


def get_common_dosing(medication_name: str) -> list[str]:
    """Get common dosing patterns for a medication."""
    drug = _find_matching_drug(medication_name)
    if not drug:
        return []

    dosing_options = COMMON_DOSING_PATTERNS[drug]
    strength = _extract_strength_value(medication_name)
    if strength and strength in dosing_options:
        return dosing_options[strength]

    return dosing_options.get("_default", [])


def get_default_duration(medication_name: str) -> int:
    """Get default duration in days based on medication type."""
    drug = _find_matching_drug(medication_name)

    if drug in ANTIBIOTICS:
        return 10
    if drug in SHORT_TERM_STEROIDS:
        return 7
    if drug in PRN_MEDICATIONS:
        return 30

    return 30


class MedicationSearchService:
    """
    Service for searching medications and getting dosing defaults.
    """

    def __init__(self, medication_repo: MedicationRepository | None = None):
        self.medication_repo = medication_repo

    async def search(self, query: str) -> list[dict]:
        """
        Search RxNorm for medications matching the query.

        Args:
            query: Search query (minimum 3 characters)

        Returns:
            List of medications in frontend-compatible format
        """
        if len(query) < 3:
            return []

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{RXNORM_BASE_URL}/drugs.json",
                params={"name": query},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

        return self._parse_drug_response(data)

    def _parse_drug_response(self, data: dict) -> list[dict]:
        """Parse RxNorm getDrugs response into medication list."""
        medications = []
        drug_group = data.get("drugGroup", {})
        concept_groups = drug_group.get("conceptGroup", [])

        for group in concept_groups:
            tty = group.get("tty", "")
            if tty not in ("SCD", "SBD"):
                continue

            for concept in group.get("conceptProperties", []):
                name = concept.get("name", "")
                medications.append({
                    "id": concept.get("rxcui", ""),
                    "name": name,
                    "strength": _extract_strength(name),
                    "form": _extract_form(name),
                    "commonDosing": get_common_dosing(name),
                    "isControlled": False,
                })

        return medications

    def get_defaults(self, medication_name: str) -> dict:
        """
        Get default prescription values for a medication.

        Args:
            medication_name: The medication name

        Returns:
            Dict with defaultDuration
        """
        return {
            "defaultDuration": get_default_duration(medication_name),
        }
