"""
Allergy checking service with cross-reactivity logic.

Business logic for checking if a medication conflicts with patient allergies.
"""

from pydantic import BaseModel
from typing import Optional

from .constants import CROSS_REACTIVITY, ALLERGY_OVERRIDE_LOGS


class AllergyCheckRequest(BaseModel):
    medication_name: str


class AllergyOverrideLog(BaseModel):
    patient_id: str
    medication_name: str
    allergen: str
    severity: str
    justification: str
    acknowledged_at: str
    prescribed_at: str


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
        if self.blocked:
            title = f"CRITICAL: Patient allergic to {self.allergen}"
        else:
            title = f"Warning: Patient allergic to {self.allergen}"

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


def get_patient_allergies(patient: dict) -> list[dict]:
    """Retrieve the list of allergies for a patient."""
    return patient.get("allergies", [])


def check_med_conflicts(medication_name: str, allergies: list[dict]) -> Optional[AllergyAlert]:
    """
    Check if a medication conflicts with any patient allergies.

    Args:
        medication_name: The name of the medication to check
        allergies: List of patient allergy records

    Returns:
        AllergyAlert if there's a conflict, None otherwise
    """
    medication_lower = medication_name.lower()

    for allergy in allergies:
        allergen = allergy.get("allergen", "").lower()
        reaction = allergy.get("reaction", "Unknown")
        severity = allergy.get("severity", "unknown")
        # Only severe allergies require override
        is_blocked = severity == "severe"

        # Direct match check
        if allergen in medication_lower or medication_lower in allergen:
            return AllergyAlert(
                blocked=is_blocked,
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
                        blocked=is_blocked,
                        allergen=allergy.get("allergen", "Unknown"),
                        reaction=reaction,
                        severity=severity,
                        medication_name=medication_name,
                        is_cross_reactive=True,
                    )

    return None


def log_allergy_override(override: AllergyOverrideLog) -> dict:
    """Log an allergy override when a prescription is completed despite an allergy."""
    log_entry = {
        "id": f"override-{len(ALLERGY_OVERRIDE_LOGS) + 1}",
        "patientId": override.patient_id,
        "medicationName": override.medication_name,
        "allergen": override.allergen,
        "severity": override.severity,
        "justification": override.justification,
        "acknowledgedAt": override.acknowledged_at,
        "prescribedAt": override.prescribed_at,
    }
    ALLERGY_OVERRIDE_LOGS.append(log_entry)

    # In production, you would persist this to a database
    print(f'[ALLERGY OVERRIDE LOGGED] {log_entry}')

    return log_entry

