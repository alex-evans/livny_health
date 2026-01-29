"""
Service Layer Integration Tests.

These tests verify that services work correctly with real repositories.
Unlike unit tests that mock repository responses, these tests exercise
the actual service-repository interactions:

    Service Method -> Repository Query -> Data Transformation -> Result

What these tests verify:
- Services correctly query repositories
- Data transformations between layers work correctly
- Service business logic operates on real data
- State changes persist correctly across operations
"""
import asyncio
from datetime import date, timedelta
import pytest

from services import PatientNotFoundError, ProviderNotFoundError, AppointmentNotFoundError
from resources import AppointmentStatus, EncounterStatus, MedicationRequestStatus


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Test data constants - these match the seeded data
class TestPatients:
    """Known patient data from seed for test assertions."""
    SARAH_JOHNSON = {"id": "patient-001", "name": "Sarah Johnson"}
    MICHAEL_CHEN = {"id": "patient-002", "name": "Michael Chen"}
    EMILY_RODRIGUEZ = {"id": "patient-003", "name": "Emily Rodriguez"}
    ROBERT_THOMPSON = {"id": "patient-006", "name": "Robert Thompson"}
    PATRICIA_MARTINEZ = {"id": "patient-007", "name": "Patricia Martinez"}


class TestProviders:
    """Known provider data from seed."""
    DR_FROST = {"id": "provider-001", "name": "Dr. Elizabeth Frost"}


@pytest.mark.integration
class TestClinicalDecisionServiceIntegration:
    """
    Integration tests for ClinicalDecisionService.

    Verifies clinical decision logic works with real allergy
    and medication data from repositories.
    """

    def test_allergy_check_queries_allergy_repository(self, services, repositories):
        """Service should query allergy repository for patient allergies."""
        # Get allergies directly from repository
        repo_allergies = run_async(
            repositories["allergy"].get_by_patient(TestPatients.SARAH_JOHNSON["id"])
        )
        allergen_names = {a.allergen for a in repo_allergies}

        # Service should detect these allergies
        for allergen in allergen_names:
            alert = run_async(
                services["clinical_decision"].check_allergy_conflicts(
                    TestPatients.SARAH_JOHNSON["id"],
                    allergen,
                )
            )
            assert alert is not None

    def test_interaction_check_queries_medication_repository(self, services, repositories):
        """Service should query medication request repository for current meds."""
        # Get medications directly from repository
        repo_meds = run_async(
            repositories["medication_request"].get_active_for_patient(
                TestPatients.ROBERT_THOMPSON["id"]
            )
        )
        med_names = [m.medication_name for m in repo_meds]

        # Verify repository has Warfarin
        assert any("warfarin" in name.lower() for name in med_names)

        # Service should detect warfarin interaction with aspirin
        interactions = run_async(
            services["clinical_decision"].check_drug_interactions(
                TestPatients.ROBERT_THOMPSON["id"],
                "Aspirin",
            )
        )
        assert len(interactions) > 0

    def test_multiple_interactions_from_multiple_medications(self, services):
        """Should detect multiple interactions when patient is on multiple conflicting meds."""
        # Patricia Martinez is on Warfarin, Simvastatin, Sertraline, Lisinopril
        interactions = run_async(
            services["clinical_decision"].check_drug_interactions(
                TestPatients.PATRICIA_MARTINEZ["id"],
                "Ibuprofen",  # Interacts with both Warfarin and Lisinopril
            )
        )

        # Should find interactions with both Warfarin and Lisinopril
        interacting_drugs = [i.interacting_drug.lower() for i in interactions]
        assert any("warfarin" in d for d in interacting_drugs)
        assert any("lisinopril" in d for d in interacting_drugs)


@pytest.mark.integration
class TestPrescribingServiceIntegration:
    """
    Integration tests for PrescribingService.

    Verifies prescribing workflow integrates correctly with
    patient repository, medication repository, and clinical decision service.
    """

    def test_prescription_creates_medication_request_in_repo(self, services, repositories):
        """Creating a prescription should persist to medication request repository."""
        initial_count = len(run_async(
            repositories["medication_request"].list()
        ))

        # Create prescription
        result = run_async(services["prescribing"].create_prescription(
            patient_id=TestPatients.EMILY_RODRIGUEZ["id"],
            medication_name="IntegrationTestPrescription",
            dosage="50mg",
            frequency="daily",
            duration_days=30,
        ))

        # Verify it was persisted
        final_count = len(run_async(
            repositories["medication_request"].list()
        ))
        assert final_count == initial_count + 1

        # Verify we can retrieve it
        med = run_async(repositories["medication_request"].get(result.prescription_id))
        assert med is not None
        assert med.medication_name == "IntegrationTestPrescription"

    def test_prescription_blocked_by_severe_allergy(self, services):
        """Prescription should be blocked when patient has severe allergy."""
        from services import AllergyConflictError

        # Sarah Johnson has severe Penicillin allergy
        with pytest.raises(AllergyConflictError) as exc_info:
            run_async(services["prescribing"].create_prescription(
                patient_id=TestPatients.SARAH_JOHNSON["id"],
                medication_name="Penicillin",
                dosage="500mg",
                frequency="four times daily",
            ))

        assert exc_info.value.alert.severity == "severe"
        assert exc_info.value.alert.blocked is True

    def test_prescription_blocked_by_major_interaction(self, services):
        """Prescription should be blocked when major drug interaction exists."""
        from services import DrugInteractionError

        # Robert Thompson is on Warfarin
        with pytest.raises(DrugInteractionError) as exc_info:
            run_async(services["prescribing"].create_prescription(
                patient_id=TestPatients.ROBERT_THOMPSON["id"],
                medication_name="Aspirin",
                dosage="325mg",
                frequency="daily",
            ))

        assert any(i.severity == "major" for i in exc_info.value.interactions)

    def test_prescription_with_override_bypasses_allergy_check(self, services, repositories):
        """Prescription with override should succeed despite allergy."""
        # This should normally fail
        result = run_async(services["prescribing"].create_prescription(
            patient_id=TestPatients.SARAH_JOHNSON["id"],
            medication_name="Amoxicillin",  # Cross-reactive with Penicillin
            dosage="500mg",
            frequency="three times daily",
            override_allergy=True,
        ))

        assert result.success is True

        # Verify it was created
        med = run_async(repositories["medication_request"].get(result.prescription_id))
        assert med is not None

    def test_get_patient_verifies_patient_exists(self, services):
        """get_patient should verify patient exists in repository."""
        # Valid patient
        patient = run_async(services["prescribing"].get_patient(TestPatients.SARAH_JOHNSON["id"]))
        assert patient is not None
        assert patient.id == TestPatients.SARAH_JOHNSON["id"]

        # Invalid patient
        with pytest.raises(PatientNotFoundError):
            run_async(services["prescribing"].get_patient("nonexistent-patient"))


@pytest.mark.integration
class TestSchedulingServiceIntegration:
    """
    Integration tests for SchedulingService.

    Verifies scheduling workflow integrates correctly with
    patient, provider, appointment, and encounter repositories.
    """

    def test_get_schedule_queries_appointment_repository(self, services, repositories):
        """get_daily_schedule should return appointments from repository."""
        today = date.today()

        # Get directly from repository
        repo_appointments = run_async(
            repositories["appointment"].get_for_date(today, TestProviders.DR_FROST["id"])
        )

        # Get via service
        schedule = run_async(services["scheduling"].get_daily_schedule(
            today.isoformat(),
            TestProviders.DR_FROST["id"],
        ))

        # Should match
        assert len(schedule.appointments) == len(repo_appointments)

    def test_create_appointment_persists_to_repository(self, services, repositories):
        """create_appointment should persist to appointment repository."""
        future_date = (date.today() + timedelta(days=14)).isoformat()

        appointment = run_async(services["scheduling"].create_appointment(
            date_str=future_date,
            time="10:00",
            patient_id=TestPatients.EMILY_RODRIGUEZ["id"],
            provider_id=TestProviders.DR_FROST["id"],
            visit_type="Integration Test Visit",
        ))

        # Verify persisted
        repo_appt = run_async(repositories["appointment"].get(appointment.id))
        assert repo_appt is not None
        assert repo_appt.appointment_type.display == "Integration Test Visit"

    def test_check_in_updates_appointment_in_repository(self, services, repositories):
        """check_in_patient should update appointment status in repository."""
        # Create appointment
        appointment = run_async(services["scheduling"].create_appointment(
            date_str=date.today().isoformat(),
            time="08:30",
            patient_id=TestPatients.MICHAEL_CHEN["id"],
            provider_id=TestProviders.DR_FROST["id"],
        ))

        # Check in
        run_async(services["scheduling"].check_in_patient(appointment.id))

        # Verify status updated in repository
        repo_appt = run_async(repositories["appointment"].get(appointment.id))
        assert repo_appt.status == AppointmentStatus.CHECKED_IN

    def test_start_encounter_creates_encounter_in_repository(self, services, repositories):
        """start_encounter should create encounter in encounter repository."""
        initial_encounter_count = len(run_async(repositories["encounter"].list()))

        # Create and start encounter
        appointment = run_async(services["scheduling"].create_appointment(
            date_str=date.today().isoformat(),
            time="09:00",
            patient_id=TestPatients.SARAH_JOHNSON["id"],
            provider_id=TestProviders.DR_FROST["id"],
            chief_complaint="Service integration test",
        ))

        encounter = run_async(services["scheduling"].start_encounter(appointment.id))

        # Verify encounter created
        final_encounter_count = len(run_async(repositories["encounter"].list()))
        assert final_encounter_count == initial_encounter_count + 1

        # Verify encounter data
        repo_enc = run_async(repositories["encounter"].get(encounter.id))
        assert repo_enc is not None
        assert repo_enc.status == EncounterStatus.IN_PROGRESS
        assert repo_enc.chief_complaint == "Service integration test"

    def test_end_encounter_updates_both_encounter_and_appointment(self, services, repositories):
        """end_encounter should update both encounter and linked appointment."""
        # Create full workflow
        appointment = run_async(services["scheduling"].create_appointment(
            date_str=date.today().isoformat(),
            time="09:30",
            patient_id=TestPatients.MICHAEL_CHEN["id"],
            provider_id=TestProviders.DR_FROST["id"],
        ))
        encounter = run_async(services["scheduling"].start_encounter(appointment.id))

        # End encounter
        run_async(services["scheduling"].end_encounter(encounter.id))

        # Verify encounter updated
        repo_enc = run_async(repositories["encounter"].get(encounter.id))
        assert repo_enc.status == EncounterStatus.COMPLETED
        assert repo_enc.period.end is not None

        # Verify appointment updated
        repo_appt = run_async(repositories["appointment"].get(appointment.id))
        assert repo_appt.status == AppointmentStatus.FULFILLED

    def test_clear_appointments_removes_from_repository(self, services, repositories):
        """clear_dynamic_appointments should remove all appointments from repository."""
        # Create some appointments
        for i in range(3):
            run_async(services["scheduling"].create_appointment(
                date_str=date.today().isoformat(),
                time=f"10:{i:02d}",
                patient_id=TestPatients.EMILY_RODRIGUEZ["id"],
                provider_id=TestProviders.DR_FROST["id"],
            ))

        # Clear
        run_async(services["scheduling"].clear_dynamic_appointments())

        # Verify cleared
        remaining = run_async(repositories["appointment"].list())
        assert len(remaining) == 0


@pytest.mark.integration
class TestRepositoryDataConsistency:
    """
    Integration tests verifying data consistency across repositories.

    These tests ensure that related data across repositories
    stays consistent through operations.
    """

    def test_patient_allergies_reference_correct_patient(self, repositories):
        """All allergies for a patient should reference that patient."""
        allergies = run_async(
            repositories["allergy"].get_by_patient(TestPatients.SARAH_JOHNSON["id"])
        )

        for allergy in allergies:
            assert allergy.patient.id == TestPatients.SARAH_JOHNSON["id"]

    def test_patient_medications_reference_correct_patient(self, repositories):
        """All medication requests for a patient should reference that patient."""
        medications = run_async(
            repositories["medication_request"].get_active_for_patient(
                TestPatients.ROBERT_THOMPSON["id"]
            )
        )

        for med in medications:
            assert med.subject.id == TestPatients.ROBERT_THOMPSON["id"]

    def test_appointment_participants_reference_valid_entities(self, repositories):
        """Appointment participants should reference valid patients and providers."""
        appointments = run_async(repositories["appointment"].list())

        for appt in appointments:
            for participant in appt.participants:
                if participant.type == "patient":
                    patient = run_async(
                        repositories["patient"].get(participant.actor.id)
                    )
                    assert patient is not None
                elif participant.type == "practitioner":
                    provider = run_async(
                        repositories["practitioner"].get(participant.actor.id)
                    )
                    assert provider is not None
