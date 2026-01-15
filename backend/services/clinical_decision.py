"""
Clinical Decision Support Service.

Provides allergy checking, drug interaction checking, and other clinical decision support.
"""

from dataclasses import dataclass
from typing import Literal

from resources import (
    AllergyIntolerance,
    AllergyIntoleranceRepository,
    MedicationRequest,
    MedicationRequestRepository,
)


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

# Drug interactions database
DRUG_INTERACTIONS = [
    # Warfarin interactions
    {"drugs": ["warfarin", "amoxicillin"], "severity": "moderate", "description": "May increase warfarin effects - monitor INR"},
    {"drugs": ["warfarin", "aspirin"], "severity": "major", "description": "Increased risk of bleeding - avoid combination or use with extreme caution"},
    {"drugs": ["warfarin", "ibuprofen"], "severity": "major", "description": "Increased risk of bleeding and GI ulceration - avoid NSAIDs with warfarin"},
    {"drugs": ["warfarin", "metronidazole"], "severity": "major", "description": "Significantly increases warfarin effect - reduce warfarin dose and monitor INR closely"},
    {"drugs": ["warfarin", "fluconazole"], "severity": "major", "description": "Significantly increases warfarin effect - monitor INR closely"},
    # Metformin interactions
    {"drugs": ["metformin", "alcohol"], "severity": "moderate", "description": "Increased risk of lactic acidosis - limit alcohol consumption"},
    {"drugs": ["metformin", "contrast dye"], "severity": "major", "description": "Risk of lactic acidosis - hold metformin before and after contrast procedures"},
    # Statin interactions
    {"drugs": ["simvastatin", "amiodarone"], "severity": "major", "description": "Increased risk of myopathy - limit simvastatin to 20mg daily"},
    {"drugs": ["simvastatin", "erythromycin"], "severity": "major", "description": "Increased risk of myopathy/rhabdomyolysis - avoid combination"},
    {"drugs": ["atorvastatin", "clarithromycin"], "severity": "moderate", "description": "Increased statin levels - monitor for muscle pain/weakness"},
    # SSRI interactions
    {"drugs": ["sertraline", "tramadol"], "severity": "major", "description": "Risk of serotonin syndrome - monitor closely or avoid"},
    {"drugs": ["fluoxetine", "maoi"], "severity": "major", "description": "CONTRAINDICATED - severe serotonin syndrome risk"},
    # ACE inhibitor interactions
    {"drugs": ["lisinopril", "potassium"], "severity": "moderate", "description": "Risk of hyperkalemia - monitor potassium levels"},
    {"drugs": ["lisinopril", "spironolactone"], "severity": "moderate", "description": "Risk of hyperkalemia - monitor potassium levels closely"},
    {"drugs": ["lisinopril", "ibuprofen"], "severity": "moderate", "description": "May reduce antihypertensive effect and worsen kidney function"},
    # Antibiotic interactions
    {"drugs": ["ciprofloxacin", "tizanidine"], "severity": "major", "description": "CONTRAINDICATED - dramatically increases tizanidine levels"},
    {"drugs": ["metronidazole", "alcohol"], "severity": "major", "description": "Severe nausea/vomiting (disulfiram-like reaction) - avoid alcohol"},
    # Opioid interactions
    {"drugs": ["oxycodone", "benzodiazepine"], "severity": "major", "description": "Risk of profound sedation and respiratory depression - avoid if possible"},
    {"drugs": ["morphine", "benzodiazepine"], "severity": "major", "description": "Risk of profound sedation and respiratory depression - avoid if possible"},
    # OTC interactions
    {"drugs": ["methotrexate", "ibuprofen"], "severity": "major", "description": "Increased methotrexate toxicity - avoid combination"},
]


@dataclass
class AllergyAlert:
    """Represents an allergy alert for a medication."""
    blocked: bool
    allergen: str
    reaction: str
    severity: str
    medication_name: str
    is_cross_reactive: bool = False

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


@dataclass
class DrugInteraction:
    """Represents a drug interaction warning."""
    interacting_drug: str
    severity: Literal["minor", "moderate", "major"]
    description: str

    def to_dict(self) -> dict:
        return {
            "interactingDrug": self.interacting_drug,
            "severity": self.severity,
            "description": self.description,
        }


@dataclass
class AllergyOverrideLog:
    """Log entry for allergy override."""
    id: str
    patient_id: str
    medication_name: str
    allergen: str
    severity: str
    justification: str
    acknowledged_at: str
    prescribed_at: str


@dataclass
class InteractionOverrideLog:
    """Log entry for interaction override."""
    id: str
    patient_id: str
    medication_name: str
    interacting_drugs: list[str]
    severities: list[str]
    justification: str
    acknowledged_at: str
    prescribed_at: str


class ClinicalDecisionService:
    """
    Service for clinical decision support.

    Provides allergy checking, drug interaction checking, and override logging.
    """

    def __init__(
        self,
        allergy_repo: AllergyIntoleranceRepository,
        medication_request_repo: MedicationRequestRepository,
    ):
        self.allergy_repo = allergy_repo
        self.medication_request_repo = medication_request_repo
        self._allergy_override_logs: list[AllergyOverrideLog] = []
        self._interaction_override_logs: list[InteractionOverrideLog] = []

    async def check_allergy_conflicts(
        self,
        patient_id: str,
        medication_name: str,
    ) -> AllergyAlert | None:
        """
        Check if a medication conflicts with patient allergies.

        Args:
            patient_id: The patient ID
            medication_name: The medication to check

        Returns:
            AllergyAlert if there's a conflict, None otherwise
        """
        allergies = await self.allergy_repo.get_by_patient(patient_id)
        return self._check_med_conflicts(medication_name, allergies)

    def _check_med_conflicts(
        self,
        medication_name: str,
        allergies: list[AllergyIntolerance],
    ) -> AllergyAlert | None:
        """Check medication against list of allergies."""
        medication_lower = medication_name.lower()

        for allergy in allergies:
            allergen = allergy.allergen.lower()
            reaction = allergy.reaction
            severity = allergy.severity
            is_blocked = severity == "severe"

            # Direct match check
            if allergen in medication_lower or medication_lower in allergen:
                return AllergyAlert(
                    blocked=is_blocked,
                    allergen=allergy.allergen,
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
                            allergen=allergy.allergen,
                            reaction=reaction,
                            severity=severity,
                            medication_name=medication_name,
                            is_cross_reactive=True,
                        )

        return None

    async def check_drug_interactions(
        self,
        patient_id: str,
        medication_name: str,
    ) -> list[DrugInteraction]:
        """
        Check if a medication interacts with patient's current medications.

        Args:
            patient_id: The patient ID
            medication_name: The medication to check

        Returns:
            List of DrugInteraction objects for any found interactions
        """
        active_meds = await self.medication_request_repo.get_active_for_patient(patient_id)
        return self._check_interactions(medication_name, active_meds)

    def _check_interactions(
        self,
        medication_name: str,
        active_medications: list[MedicationRequest],
    ) -> list[DrugInteraction]:
        """Check medication against list of active medications."""
        interactions = []
        medication_lower = medication_name.lower()

        for active_med in active_medications:
            active_name = active_med.medication_name.lower()
            interaction = self._find_interaction(medication_lower, active_name)
            if interaction:
                interactions.append(
                    DrugInteraction(
                        interacting_drug=active_med.medication_name,
                        severity=interaction["severity"],
                        description=interaction["description"],
                    )
                )

        return interactions

    def _find_interaction(self, drug1: str, drug2: str) -> dict | None:
        """Look up an interaction between two drugs."""
        for interaction in DRUG_INTERACTIONS:
            drugs = [d.lower() for d in interaction["drugs"]]
            drug1_match = any(drug1 in d or d in drug1 for d in drugs)
            drug2_match = any(drug2 in d or d in drug2 for d in drugs)
            if drug1_match and drug2_match:
                return interaction
        return None

    def log_allergy_override(
        self,
        patient_id: str,
        medication_name: str,
        allergen: str,
        severity: str,
        justification: str,
        acknowledged_at: str,
        prescribed_at: str,
    ) -> AllergyOverrideLog:
        """Log an allergy override."""
        from resources.core import generate_id

        log_entry = AllergyOverrideLog(
            id=generate_id("override"),
            patient_id=patient_id,
            medication_name=medication_name,
            allergen=allergen,
            severity=severity,
            justification=justification,
            acknowledged_at=acknowledged_at,
            prescribed_at=prescribed_at,
        )
        self._allergy_override_logs.append(log_entry)
        print(f"[ALLERGY OVERRIDE LOGGED] {log_entry}")
        return log_entry

    def log_interaction_override(
        self,
        patient_id: str,
        medication_name: str,
        interacting_drugs: list[str],
        severities: list[str],
        justification: str,
        acknowledged_at: str,
        prescribed_at: str,
    ) -> InteractionOverrideLog:
        """Log an interaction override."""
        from resources.core import generate_id

        log_entry = InteractionOverrideLog(
            id=generate_id("override"),
            patient_id=patient_id,
            medication_name=medication_name,
            interacting_drugs=interacting_drugs,
            severities=severities,
            justification=justification,
            acknowledged_at=acknowledged_at,
            prescribed_at=prescribed_at,
        )
        self._interaction_override_logs.append(log_entry)
        print(f"[INTERACTION OVERRIDE LOGGED] {log_entry}")
        return log_entry
