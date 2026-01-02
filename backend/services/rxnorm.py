import re

import httpx

from dosing_data import get_common_dosing

RXNORM_BASE_URL = "https://rxnav.nlm.nih.gov/REST"

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


async def search_medications(query: str) -> list[dict]:
    """
    Search RxNorm for medications matching the query.
    Returns medications in frontend-compatible format.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{RXNORM_BASE_URL}/drugs.json",
            params={"name": query},
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()

    return _parse_drug_response(data)


def _parse_drug_response(data: dict) -> list[dict]:
    """Parse RxNorm getDrugs response into medication list."""
    medications = []
    drug_group = data.get("drugGroup", {})
    concept_groups = drug_group.get("conceptGroup", [])

    for group in concept_groups:
        tty = group.get("tty", "")
        # Only include clinical drugs (SCD) and branded drugs (SBD)
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


def _extract_strength(name: str) -> str:
    """Extract strength from RxNorm drug name (e.g., '500 MG' from 'Amoxicillin 500 MG Oral Tablet')."""
    match = re.search(r"(\d+(?:\.\d+)?(?:/\d+(?:\.\d+)?)?\s*(?:MG|MCG|MG/ML|UNITS?|%|MEQ))", name, re.IGNORECASE)
    return match.group(1) if match else ""


def _extract_form(name: str) -> str:
    """Extract dosage form from RxNorm drug name."""
    name_upper = name.upper()
    for pattern, form in FORM_PATTERNS.items():
        if pattern.upper() in name_upper:
            return form
    return ""
