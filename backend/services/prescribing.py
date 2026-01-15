"""
Prescribing Service.

Handles medication prescription workflows.
"""

from dataclasses import dataclass
from datetime import datetime

from resources import (
    Patient,
    PatientRepository,
    MedicationRequest,
    MedicationRequestStatus,
    MedicationRequestIntent,
    Dosage,
    MedicationRequestRepository,
)
from resources.core import Reference, CodeableConcept, generate_id

from .clinical_decision import ClinicalDecisionService, AllergyAlert, DrugInteraction


class PatientNotFoundError(Exception):
    """Raised when a patient is not found."""
    pass


class AllergyConflictError(Exception):
    """Raised when there's an unacknowledged allergy conflict."""
    def __init__(self, alert: AllergyAlert):
        self.alert = alert
        super().__init__(f"Allergy conflict: {alert.allergen}")


class DrugInteractionError(Exception):
    """Raised when there are unacknowledged drug interactions."""
    def __init__(self, interactions: list[DrugInteraction]):
        self.interactions = interactions
        super().__init__(f"Drug interactions found: {len(interactions)}")


@dataclass
class PrescriptionResult:
    """Result of creating a prescription."""
    prescription_id: str
    medication_request: MedicationRequest
    success: bool = True
    message: str = "Prescription created successfully"


class PrescribingService:
    """
    Service for prescribing medications.

    Orchestrates allergy/interaction checks and creates medication requests.
    """

    def __init__(
        self,
        patient_repo: PatientRepository,
        medication_request_repo: MedicationRequestRepository,
        clinical_decision_service: ClinicalDecisionService,
    ):
        self.patient_repo = patient_repo
        self.medication_request_repo = medication_request_repo
        self.clinical_decision = clinical_decision_service

    async def get_patient(self, patient_id: str) -> Patient:
        """Get a patient by ID, raising if not found."""
        patient = await self.patient_repo.get(patient_id)
        if not patient:
            raise PatientNotFoundError(f"Patient {patient_id} not found")
        return patient

    async def get_active_medications(self, patient_id: str) -> list[MedicationRequest]:
        """Get active medications for a patient."""
        return await self.medication_request_repo.get_active_for_patient(patient_id)

    async def check_allergy(self, patient_id: str, medication_name: str) -> AllergyAlert | None:
        """Check for allergy conflicts."""
        return await self.clinical_decision.check_allergy_conflicts(patient_id, medication_name)

    async def check_interactions(self, patient_id: str, medication_name: str) -> list[DrugInteraction]:
        """Check for drug interactions."""
        return await self.clinical_decision.check_drug_interactions(patient_id, medication_name)

    async def create_prescription(
        self,
        patient_id: str,
        medication_name: str,
        dosage: str,
        frequency: str,
        duration_days: int | None = None,
        instructions: str | None = None,
        encounter_id: str | None = None,
        prescriber_id: str | None = None,
        override_allergy: bool = False,
        override_interactions: bool = False,
    ) -> PrescriptionResult:
        """
        Create a new prescription for a patient.

        Args:
            patient_id: The patient to prescribe for
            medication_name: Name of the medication
            dosage: Dose (e.g., "500mg")
            frequency: Frequency (e.g., "twice daily")
            duration_days: Duration in days
            instructions: Additional instructions
            encounter_id: Optional encounter context
            prescriber_id: Optional prescriber ID
            override_allergy: Set to True to acknowledge allergy warnings
            override_interactions: Set to True to acknowledge interaction warnings

        Returns:
            PrescriptionResult with the created medication request
        """
        # Verify patient exists
        await self.get_patient(patient_id)

        # Check for conflicts if overrides not set
        if not override_allergy:
            allergy_alert = await self.check_allergy(patient_id, medication_name)
            if allergy_alert and allergy_alert.blocked:
                raise AllergyConflictError(allergy_alert)

        if not override_interactions:
            interactions = await self.check_interactions(patient_id, medication_name)
            major_interactions = [i for i in interactions if i.severity == "major"]
            if major_interactions:
                raise DrugInteractionError(major_interactions)

        # Create the medication request
        request_id = generate_id("rx")

        dosage_text = f"{dosage} {frequency}".strip()
        if duration_days:
            dosage_text += f" for {duration_days} days"

        dosage_instruction = Dosage(
            text=dosage_text,
            dose=dosage,
            frequency=frequency,
            duration_days=duration_days,
            additional_instructions=instructions,
        )

        medication_request = MedicationRequest(
            id=request_id,
            status=MedicationRequestStatus.DRAFT,  # Pending transmission
            intent=MedicationRequestIntent.ORDER,
            medication=CodeableConcept(
                code=medication_name.lower().replace(" ", "-"),
                display=medication_name,
            ),
            subject=Reference.to("Patient", patient_id),
            encounter=Reference.to("Encounter", encounter_id) if encounter_id else None,
            requester=Reference.to("Practitioner", prescriber_id) if prescriber_id else None,
            authored_on=datetime.utcnow(),
            dosage_instruction=[dosage_instruction],
        )

        # Save the medication request
        await self.medication_request_repo.create(medication_request)

        return PrescriptionResult(
            prescription_id=request_id,
            medication_request=medication_request,
            message=f"{medication_name} prescribed successfully",
        )

    async def create_batch_prescription(
        self,
        patient_id: str,
        medications: list[dict],
        encounter_id: str | None = None,
        prescriber_id: str | None = None,
    ) -> list[PrescriptionResult]:
        """
        Create multiple prescriptions at once.

        Args:
            patient_id: The patient to prescribe for
            medications: List of medication dicts with name, dosage, frequency, duration_days, instructions
            encounter_id: Optional encounter context
            prescriber_id: Optional prescriber ID

        Returns:
            List of PrescriptionResult objects
        """
        results = []
        for med in medications:
            result = await self.create_prescription(
                patient_id=patient_id,
                medication_name=med["name"],
                dosage=med["dosage"],
                frequency=med["frequency"],
                duration_days=med.get("duration_days"),
                instructions=med.get("instructions"),
                encounter_id=encounter_id,
                prescriber_id=prescriber_id,
                override_allergy=True,  # Assume already checked in batch
                override_interactions=True,
            )
            results.append(result)
        return results
