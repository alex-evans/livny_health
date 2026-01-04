"""
Drug interaction checking service.

Business logic for checking if a medication interacts with patient's current medications.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Literal

from .database import DRUG_INTERACTIONS


# In-memory storage for interaction override logs
INTERACTION_OVERRIDE_LOGS: list[dict] = []


class InteractionCheckRequest(BaseModel):
    medication_name: str


class InteractionOverrideLog(BaseModel):
    patient_id: str
    medication_name: str
    interacting_drugs: list[str]
    severities: list[str]
    justification: str
    acknowledged_at: str
    prescribed_at: str


InteractionSeverity = Literal["minor", "moderate", "major"]


class DrugInteraction:
    """Represents a drug interaction warning."""

    def __init__(
        self,
        interacting_drug: str,
        severity: InteractionSeverity,
        description: str,
    ):
        self.interacting_drug = interacting_drug
        self.severity = severity
        self.description = description

    def to_dict(self) -> dict:
        return {
            "interactingDrug": self.interacting_drug,
            "severity": self.severity,
            "description": self.description,
        }


def _find_interaction(drug1: str, drug2: str) -> dict | None:
    """
    Look up an interaction between two drugs in the database.
    Checks both directions since interactions are bidirectional.
    """
    for interaction in DRUG_INTERACTIONS:
        drugs = [d.lower() for d in interaction["drugs"]]

        # Check if both drugs are involved in this interaction
        drug1_match = any(drug1 in d or d in drug1 for d in drugs)
        drug2_match = any(drug2 in d or d in drug2 for d in drugs)

        if drug1_match and drug2_match:
            return interaction

    return None


def check_interactions(medication_name: str, active_medications: list[dict]) -> list[DrugInteraction]:
    """
    Check if a medication interacts with any of the patient's current medications.

    Args:
        medication_name: The name of the medication being prescribed
        active_medications: List of patient's current active medications

    Returns:
        List of DrugInteraction objects for any found interactions
    """
    interactions = []
    medication_lower = medication_name.lower()

    for active_med in active_medications:
        active_name = active_med.get("name", "").lower()

        # Check both directions in the interaction database
        interaction = _find_interaction(medication_lower, active_name)
        if interaction:
            interactions.append(
                DrugInteraction(
                    interacting_drug=active_med.get("name", "Unknown"),
                    severity=interaction["severity"],
                    description=interaction["description"],
                )
            )

    return interactions


def log_interaction_override(override: InteractionOverrideLog) -> dict:
    """
    Log an interaction override when a physician prescribes despite drug interactions.

    Args:
        override: The override data to log

    Returns:
        The created log entry with ID and timestamp
    """
    log_entry = {
        "id": str(uuid.uuid4()),
        "patient_id": override.patient_id,
        "medication_name": override.medication_name,
        "interacting_drugs": override.interacting_drugs,
        "severities": override.severities,
        "justification": override.justification,
        "acknowledged_at": override.acknowledged_at,
        "prescribed_at": override.prescribed_at,
        "logged_at": datetime.now().isoformat(),
    }

    INTERACTION_OVERRIDE_LOGS.append(log_entry)
    print(f"[INTERACTION OVERRIDE] Logged override: {log_entry}")

    return log_entry

