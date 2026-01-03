"""
Allergy checking service with cross-reactivity logic.

Business logic for checking if a medication conflicts with patient allergies.
"""

from typing import Optional

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


class AllergyAlert:
    """Represents an allergy alert for a medication."""

    def __init__(
        self,
        blocked: bool,
        allergen: str,
        reaction: str,
        severity: str,
        medication_name: str,
        is_cross_reactive: bool = False,
    ):
        self.blocked = blocked
        self.allergen = allergen
        self.reaction = reaction
        self.severity = severity
        self.medication_name = medication_name
        self.is_cross_reactive = is_cross_reactive

    def to_dict(self) -> dict:
        title = f"CRITICAL: Patient allergic to {self.allergen}"
        if self.is_cross_reactive:
            message = (
                f"{self.medication_name} is cross-reactive with {self.allergen}. "
                f"Patient has documented {self.severity} allergy with reaction: {self.reaction}."
            )
        else:
            message = (
                f"Patient has documented {self.severity} allergy to {self.allergen} "
                f"with reaction: {self.reaction}."
            )

        return {
            "blocked": self.blocked,
            "severity": self.severity,
            "title": title,
            "message": message,
            "allergen": self.allergen,
            "reaction": self.reaction,
            "medicationName": self.medication_name,
            "isCrossReactive": self.is_cross_reactive,
        }


def check_allergy(
    medication_name: str, allergies: list[dict]
) -> Optional[AllergyAlert]:
    """
    Check if a medication conflicts with any patient allergies.

    Args:
        medication_name: The name of the medication to check
        allergies: List of patient allergy records

    Returns:
        AllergyAlert if there's a conflict, None otherwise
    """
    if not allergies:
        return None

    medication_lower = medication_name.lower()

    for allergy in allergies:
        allergen = allergy.get("allergen", "").lower()
        reaction = allergy.get("reaction", "Unknown")
        severity = allergy.get("severity", "unknown")

        # Direct match check
        if allergen in medication_lower or medication_lower in allergen:
            return AllergyAlert(
                blocked=True,
                allergen=allergy.get("allergen", "Unknown"),
                reaction=reaction,
                severity=severity,
                medication_name=medication_name,
                is_cross_reactive=False,
            )

        # Cross-reactivity check
        if allergen in CROSS_REACTIVITY:
            cross_reactive_meds = CROSS_REACTIVITY[allergen]
            for reactive_med in cross_reactive_meds:
                if reactive_med in medication_lower:
                    return AllergyAlert(
                        blocked=True,
                        allergen=allergy.get("allergen", "Unknown"),
                        reaction=reaction,
                        severity=severity,
                        medication_name=medication_name,
                        is_cross_reactive=True,
                    )

    return None
