"""
This will likely go away in the future when we have a real database.
For now, it contains constants and in-memory data structures for allergy overrides.
"""


# In-memory store for allergy override logs (fake database)
ALLERGY_OVERRIDE_LOGS: list[dict] = []

# Cross-reactivity mapping: allergen -> list of medication names that could trigger reaction
CROSS_REACTIVITY = {
    "penicillin": [
        "amoxicillin",
        "ampicillin",
        "penicillin",
        "piperacillin",
        "nafcillin",
        "oxacillin",
        "dicloxacillin",
        "augmentin",
        "amoxicillin/clavulanate",
    ],
    "sulfa": [
        "sulfamethoxazole",
        "sulfasalazine",
        "bactrim",
        "septra",
        "trimethoprim/sulfamethoxazole",
    ],
    "aspirin": [
        "aspirin",
        "acetylsalicylic acid",
    ],
    "codeine": [
        "codeine",
        "hydrocodone",
        "oxycodone",
        "morphine",
        "tramadol",
    ],
}


