import httpx

RXNORM_BASE_URL = "https://rxnav.nlm.nih.gov/REST"


async def search_medications(query: str) -> list[dict]:
    """
    Search RxNorm for medications matching the query.
    Returns a list of medications with rxcui, name, and tty.
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
            medications.append({
                "rxcui": concept.get("rxcui", ""),
                "name": concept.get("name", ""),
                "tty": tty,
            })

    return medications
