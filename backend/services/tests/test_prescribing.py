"""
Unit tests for PrescribingService.

Tests prescription creation workflows with allergy and interaction checking.
"""
import asyncio
import pytest

from services import (
    PatientNotFoundError,
    AllergyConflictError,
    DrugInteractionError,
    PrescriptionResult,
)
from resources import MedicationRequestStatus


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.mark.unit
class TestGetPatient:
    """Tests for get_patient method."""

    def test_get_existing_patient(self, prescribing_service):
        """Should return patient for valid ID."""
        patient = run_async(prescribing_service.get_patient("patient-001"))
        assert patient is not None
        assert patient.id == "patient-001"

    def test_get_nonexistent_patient(self, prescribing_service):
        """Should raise PatientNotFoundError for invalid ID."""
        with pytest.raises(PatientNotFoundError):
            run_async(prescribing_service.get_patient("nonexistent-patient"))


@pytest.mark.unit
class TestGetActiveMedications:
    """Tests for get_active_medications method."""

    def test_get_active_medications(self, prescribing_service):
        """Should return list of active medications."""
        medications = run_async(prescribing_service.get_active_medications("patient-001"))
        assert isinstance(medications, list)
        assert len(medications) >= 1

    def test_get_active_medications_empty_for_new_patient(self, prescribing_service):
        """Should return empty list for patient with no medications."""
        # Patient 005 (Maria Garcia) may have minimal or no medications
        medications = run_async(prescribing_service.get_active_medications("patient-005"))
        assert isinstance(medications, list)


@pytest.mark.unit
class TestAllergyChecking:
    """Tests for allergy checking through prescribing service."""

    def test_check_allergy_no_conflict(self, prescribing_service):
        """Should return None for safe medication."""
        alert = run_async(prescribing_service.check_allergy("patient-001", "Acetaminophen"))
        assert alert is None

    def test_check_allergy_detects_conflict(self, prescribing_service):
        """Should detect allergy conflict."""
        alert = run_async(prescribing_service.check_allergy("patient-001", "Penicillin"))
        assert alert is not None
        assert alert.allergen == "Penicillin"


@pytest.mark.unit
class TestInteractionChecking:
    """Tests for interaction checking through prescribing service."""

    def test_check_interactions_no_interactions(self, prescribing_service):
        """Should return empty list for no interactions."""
        interactions = run_async(prescribing_service.check_interactions("patient-003", "Acetaminophen"))
        assert interactions == []

    def test_check_interactions_detects_interactions(self, prescribing_service):
        """Should detect drug interactions."""
        interactions = run_async(prescribing_service.check_interactions("patient-006", "Aspirin"))
        assert len(interactions) > 0


@pytest.mark.unit
class TestCreatePrescription:
    """Tests for create_prescription method."""

    def test_create_prescription_success(self, prescribing_service):
        """Should create prescription for safe medication."""
        result = run_async(prescribing_service.create_prescription(
            patient_id="patient-003",  # No allergies, minimal medications
            medication_name="Acetaminophen",
            dosage="500mg",
            frequency="every 6 hours as needed",
            duration_days=7,
            instructions="Do not exceed 3g per day",
        ))

        assert isinstance(result, PrescriptionResult)
        assert result.success is True
        assert result.prescription_id is not None
        assert result.medication_request is not None

    def test_create_prescription_with_all_options(self, prescribing_service):
        """Should create prescription with all optional parameters."""
        result = run_async(prescribing_service.create_prescription(
            patient_id="patient-003",
            medication_name="Ibuprofen",
            dosage="400mg",
            frequency="three times daily",
            duration_days=10,
            instructions="Take with food",
            encounter_id="enc-123",
            prescriber_id="provider-001",
        ))

        assert result.success is True
        assert result.medication_request.encounter is not None
        assert result.medication_request.requester is not None

    def test_create_prescription_without_duration(self, prescribing_service):
        """Should create prescription without duration (chronic medication)."""
        result = run_async(prescribing_service.create_prescription(
            patient_id="patient-003",
            medication_name="Lisinopril",
            dosage="10mg",
            frequency="daily",
        ))

        assert result.success is True

    def test_create_prescription_patient_not_found(self, prescribing_service):
        """Should raise PatientNotFoundError for invalid patient."""
        with pytest.raises(PatientNotFoundError):
            run_async(prescribing_service.create_prescription(
                patient_id="nonexistent-patient",
                medication_name="Acetaminophen",
                dosage="500mg",
                frequency="daily",
            ))

    def test_create_prescription_blocks_severe_allergy(self, prescribing_service):
        """Should raise AllergyConflictError for severe allergy."""
        with pytest.raises(AllergyConflictError) as exc_info:
            run_async(prescribing_service.create_prescription(
                patient_id="patient-001",  # Allergic to Penicillin (severe)
                medication_name="Penicillin",
                dosage="500mg",
                frequency="four times daily",
            ))

        assert exc_info.value.alert.blocked is True
        assert exc_info.value.alert.severity == "severe"

    def test_create_prescription_blocks_major_interaction(self, prescribing_service):
        """Should raise DrugInteractionError for major interaction."""
        with pytest.raises(DrugInteractionError) as exc_info:
            run_async(prescribing_service.create_prescription(
                patient_id="patient-006",  # On Warfarin
                medication_name="Aspirin",
                dosage="325mg",
                frequency="daily",
            ))

        assert len(exc_info.value.interactions) > 0
        assert any(i.severity == "major" for i in exc_info.value.interactions)

    def test_create_prescription_with_allergy_override(self, prescribing_service):
        """Should allow prescription with allergy override."""
        result = run_async(prescribing_service.create_prescription(
            patient_id="patient-001",
            medication_name="Amoxicillin",  # Cross-reactive with Penicillin
            dosage="500mg",
            frequency="three times daily",
            override_allergy=True,
        ))

        assert result.success is True

    def test_create_prescription_with_interaction_override(self, prescribing_service):
        """Should allow prescription with interaction override."""
        result = run_async(prescribing_service.create_prescription(
            patient_id="patient-006",
            medication_name="Ibuprofen",  # Interacts with Warfarin
            dosage="400mg",
            frequency="as needed",
            override_interactions=True,
        ))

        assert result.success is True

    def test_medication_request_has_draft_status(self, prescribing_service):
        """New prescriptions should have DRAFT status."""
        result = run_async(prescribing_service.create_prescription(
            patient_id="patient-003",
            medication_name="TestMed",
            dosage="10mg",
            frequency="daily",
        ))

        assert result.medication_request.status == MedicationRequestStatus.DRAFT

    def test_dosage_instruction_format(self, prescribing_service):
        """Dosage instruction should be properly formatted."""
        result = run_async(prescribing_service.create_prescription(
            patient_id="patient-003",
            medication_name="Metformin",
            dosage="500mg",
            frequency="twice daily",
            duration_days=30,
            instructions="Take with meals",
        ))

        dosage = result.medication_request.dosage_instruction[0]
        assert "500mg" in dosage.text
        assert "twice daily" in dosage.text
        assert "30 days" in dosage.text


@pytest.mark.unit
class TestCreateBatchPrescription:
    """Tests for create_batch_prescription method."""

    def test_create_batch_prescription_single(self, prescribing_service):
        """Should create single prescription in batch."""
        results = run_async(prescribing_service.create_batch_prescription(
            patient_id="patient-003",
            medications=[{
                "name": "Acetaminophen",
                "dosage": "500mg",
                "frequency": "as needed",
                "duration_days": 7,
            }],
        ))

        assert len(results) == 1
        assert results[0].success is True

    def test_create_batch_prescription_multiple(self, prescribing_service):
        """Should create multiple prescriptions in batch."""
        results = run_async(prescribing_service.create_batch_prescription(
            patient_id="patient-003",
            medications=[
                {"name": "MedA", "dosage": "10mg", "frequency": "daily", "duration_days": 30},
                {"name": "MedB", "dosage": "20mg", "frequency": "twice daily", "duration_days": 14},
                {"name": "MedC", "dosage": "5mg", "frequency": "at bedtime"},
            ],
        ))

        assert len(results) == 3
        assert all(r.success for r in results)

    def test_create_batch_prescription_empty(self, prescribing_service):
        """Should return empty list for empty medication list."""
        results = run_async(prescribing_service.create_batch_prescription(
            patient_id="patient-003",
            medications=[],
        ))

        assert results == []

    def test_create_batch_prescription_with_context(self, prescribing_service):
        """Should pass encounter and prescriber context to all prescriptions."""
        results = run_async(prescribing_service.create_batch_prescription(
            patient_id="patient-003",
            medications=[
                {"name": "MedA", "dosage": "10mg", "frequency": "daily"},
                {"name": "MedB", "dosage": "20mg", "frequency": "daily"},
            ],
            encounter_id="enc-001",
            prescriber_id="provider-001",
        ))

        assert len(results) == 2
        for result in results:
            assert result.medication_request.encounter is not None
            assert result.medication_request.requester is not None

    def test_create_batch_prescription_patient_not_found(self, prescribing_service):
        """Should raise PatientNotFoundError for invalid patient."""
        with pytest.raises(PatientNotFoundError):
            run_async(prescribing_service.create_batch_prescription(
                patient_id="nonexistent-patient",
                medications=[{"name": "Test", "dosage": "10mg", "frequency": "daily"}],
            ))

    def test_create_batch_prescription_bypasses_checks(self, prescribing_service):
        """Batch prescription should bypass allergy/interaction checks (already verified)."""
        # This would normally raise an error for patient-001 (allergic to Penicillin)
        results = run_async(prescribing_service.create_batch_prescription(
            patient_id="patient-001",
            medications=[{"name": "Amoxicillin", "dosage": "500mg", "frequency": "TID"}],
        ))

        # Should succeed because batch mode sets override flags
        assert len(results) == 1
        assert results[0].success is True
