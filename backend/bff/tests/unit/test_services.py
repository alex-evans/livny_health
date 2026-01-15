"""
Unit tests for services layer.

Tests the business logic in services without going through the HTTP layer.
"""
import asyncio
from datetime import date, timedelta
import pytest

from bff.dependencies import (
    get_scheduling_service,
    get_clinical_decision_service,
    get_prescribing_service,
    get_medication_search_service,
)
from services import ProviderNotFoundError, PatientNotFoundError


def run_async(coro):
    """Helper to run async code in sync tests."""
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture
def services(mock_services):
    """Get initialized services."""
    return {
        "scheduling": get_scheduling_service(),
        "clinical_decision": get_clinical_decision_service(),
        "prescribing": get_prescribing_service(),
        "medication_search": get_medication_search_service(),
    }


@pytest.mark.unit
class TestSchedulingService:
    """Tests for SchedulingService"""

    def test_get_daily_schedule(self, services):
        """Should return schedule for a date"""
        result = run_async(services["scheduling"].get_daily_schedule(
            date.today().isoformat(),
            "provider-001",
        ))
        assert result.provider_id == "provider-001"
        assert result.date == date.today().isoformat()
        assert isinstance(result.appointments, list)

    def test_get_daily_schedule_invalid_date(self, services):
        """Should raise ValueError for invalid date"""
        with pytest.raises(ValueError, match="Invalid date format"):
            run_async(services["scheduling"].get_daily_schedule(
                "not-a-date",
                "provider-001",
            ))

    def test_get_daily_schedule_unknown_provider(self, services):
        """Should raise ProviderNotFoundError for unknown provider"""
        with pytest.raises(ProviderNotFoundError):
            run_async(services["scheduling"].get_daily_schedule(
                date.today().isoformat(),
                "unknown-provider",
            ))

    def test_create_appointment(self, services):
        """Should create a new appointment"""
        appointment = run_async(services["scheduling"].create_appointment(
            date_str=date.today().isoformat(),
            time="15:30",
            patient_id="patient-001",
            provider_id="provider-001",
            duration_minutes=30,
            visit_type="Follow-up",
            chief_complaint="Test appointment",
        ))
        assert appointment.id is not None
        assert appointment.duration_minutes == 30

    def test_create_appointment_unknown_patient(self, services):
        """Should raise ValueError for unknown patient"""
        with pytest.raises(ValueError, match="not found"):
            run_async(services["scheduling"].create_appointment(
                date_str=date.today().isoformat(),
                time="15:30",
                patient_id="unknown-patient",
                provider_id="provider-001",
            ))

    def test_create_appointment_unknown_provider(self, services):
        """Should raise ProviderNotFoundError for unknown provider"""
        with pytest.raises(ProviderNotFoundError):
            run_async(services["scheduling"].create_appointment(
                date_str=date.today().isoformat(),
                time="15:30",
                patient_id="patient-001",
                provider_id="unknown-provider",
            ))

    def test_create_appointment_future_date(self, services):
        """Should create appointment with BOOKED status for future date"""
        future_date = (date.today() + timedelta(days=7)).isoformat()
        appointment = run_async(services["scheduling"].create_appointment(
            date_str=future_date,
            time="10:00",
            patient_id="patient-001",
            provider_id="provider-001",
        ))
        from resources import AppointmentStatus
        assert appointment.status == AppointmentStatus.BOOKED

    def test_create_appointment_past_date(self, services):
        """Should create appointment with FULFILLED status for past date"""
        past_date = (date.today() - timedelta(days=7)).isoformat()
        appointment = run_async(services["scheduling"].create_appointment(
            date_str=past_date,
            time="10:00",
            patient_id="patient-001",
            provider_id="provider-001",
        ))
        from resources import AppointmentStatus
        assert appointment.status == AppointmentStatus.FULFILLED

    def test_clear_dynamic_appointments(self, services):
        """Should clear all appointments"""
        run_async(services["scheduling"].clear_dynamic_appointments())

    def test_check_in_patient(self, services):
        """Should check in a patient for their appointment"""
        # First create an appointment
        appointment = run_async(services["scheduling"].create_appointment(
            date_str=date.today().isoformat(),
            time="11:00",
            patient_id="patient-002",
            provider_id="provider-001",
        ))
        # Then check them in
        updated = run_async(services["scheduling"].check_in_patient(appointment.id))
        from resources import AppointmentStatus
        assert updated.status == AppointmentStatus.CHECKED_IN

    def test_check_in_patient_not_found(self, services):
        """Should raise error for unknown appointment"""
        from services import AppointmentNotFoundError
        with pytest.raises(AppointmentNotFoundError):
            run_async(services["scheduling"].check_in_patient("unknown-appt"))

    def test_start_encounter(self, services):
        """Should start an encounter from an appointment"""
        # First create an appointment
        appointment = run_async(services["scheduling"].create_appointment(
            date_str=date.today().isoformat(),
            time="12:00",
            patient_id="patient-003",
            provider_id="provider-001",
        ))
        # Then start the encounter
        encounter = run_async(services["scheduling"].start_encounter(appointment.id))
        from resources import EncounterStatus
        assert encounter.status == EncounterStatus.IN_PROGRESS
        assert encounter.id is not None

    def test_start_encounter_not_found(self, services):
        """Should raise error for unknown appointment"""
        from services import AppointmentNotFoundError
        with pytest.raises(AppointmentNotFoundError):
            run_async(services["scheduling"].start_encounter("unknown-appt"))

    def test_end_encounter(self, services):
        """Should end an encounter"""
        # Create appointment and start encounter
        appointment = run_async(services["scheduling"].create_appointment(
            date_str=date.today().isoformat(),
            time="13:00",
            patient_id="patient-004",
            provider_id="provider-001",
        ))
        encounter = run_async(services["scheduling"].start_encounter(appointment.id))
        # End the encounter
        ended = run_async(services["scheduling"].end_encounter(encounter.id))
        from resources import EncounterStatus
        assert ended.status == EncounterStatus.FINISHED

    def test_end_encounter_not_found(self, services):
        """Should raise error for unknown encounter"""
        with pytest.raises(ValueError, match="not found"):
            run_async(services["scheduling"].end_encounter("unknown-enc"))


@pytest.mark.unit
class TestClinicalDecisionService:
    """Tests for ClinicalDecisionService"""

    def test_check_allergy_no_conflict(self, services):
        """Should return None for safe medication"""
        alert = run_async(services["clinical_decision"].check_allergy_conflicts(
            "patient-001",
            "Acetaminophen",
        ))
        assert alert is None

    def test_check_allergy_direct_match(self, services):
        """Should detect direct allergy match"""
        # Patient 001 is allergic to Penicillin
        alert = run_async(services["clinical_decision"].check_allergy_conflicts(
            "patient-001",
            "Penicillin",
        ))
        assert alert is not None
        assert alert.is_cross_reactive is False

    def test_check_allergy_cross_reactive(self, services):
        """Should detect cross-reactive medication"""
        # Patient 001 is allergic to Penicillin, Amoxicillin is cross-reactive
        alert = run_async(services["clinical_decision"].check_allergy_conflicts(
            "patient-001",
            "Amoxicillin",
        ))
        assert alert is not None
        assert alert.is_cross_reactive is True

    def test_check_drug_interactions_none(self, services):
        """Should return empty list for no interactions"""
        interactions = run_async(services["clinical_decision"].check_drug_interactions(
            "patient-003",  # Has minimal medications
            "Acetaminophen",
        ))
        assert interactions == []

    def test_check_drug_interactions_warfarin(self, services):
        """Should detect warfarin interactions"""
        # Patient 006 is on Warfarin
        interactions = run_async(services["clinical_decision"].check_drug_interactions(
            "patient-006",
            "Aspirin",
        ))
        assert len(interactions) > 0
        assert any(i.severity == "major" for i in interactions)

    def test_log_allergy_override(self, services):
        """Should log allergy override"""
        log_entry = services["clinical_decision"].log_allergy_override(
            patient_id="patient-001",
            medication_name="Amoxicillin",
            allergen="Penicillin",
            severity="severe",
            justification="No alternatives",
            acknowledged_at="2024-01-15T10:00:00Z",
            prescribed_at="2024-01-15T10:05:00Z",
        )
        assert log_entry.id is not None
        assert log_entry.patient_id == "patient-001"

    def test_log_interaction_override(self, services):
        """Should log interaction override"""
        log_entry = services["clinical_decision"].log_interaction_override(
            patient_id="patient-006",
            medication_name="Aspirin",
            interacting_drugs=["Warfarin"],
            severities=["major"],
            justification="Benefits outweigh risks",
            acknowledged_at="2024-01-15T10:00:00Z",
            prescribed_at="2024-01-15T10:05:00Z",
        )
        assert log_entry.id is not None


@pytest.mark.unit
class TestMedicationSearchService:
    """Tests for MedicationSearchService"""

    def test_search_medications(self, services):
        """Should return search results"""
        results = run_async(services["medication_search"].search("aspirin"))
        assert isinstance(results, list)

    def test_get_defaults(self, services):
        """Should return default prescription values"""
        defaults = services["medication_search"].get_defaults("Lisinopril")
        assert isinstance(defaults, dict)


@pytest.mark.unit
class TestPrescribingService:
    """Tests for PrescribingService"""

    def test_create_prescription(self, services):
        """Should create a prescription"""
        results = run_async(services["prescribing"].create_batch_prescription(
            patient_id="patient-001",
            medications=[
                {
                    "name": "TestMed",
                    "dosage": "10mg",
                    "frequency": "daily",
                    "duration_days": 30,
                    "instructions": "Take with food",
                }
            ],
        ))
        assert len(results) == 1
        assert results[0].medication_request is not None

    def test_create_prescription_unknown_patient(self, services):
        """Should raise error for unknown patient"""
        with pytest.raises(PatientNotFoundError):
            run_async(services["prescribing"].create_batch_prescription(
                patient_id="unknown-patient",
                medications=[
                    {
                        "name": "TestMed",
                        "dosage": "10mg",
                        "frequency": "daily",
                        "duration_days": 30,
                    }
                ],
            ))

    def test_create_multiple_prescriptions(self, services):
        """Should create multiple prescriptions at once"""
        results = run_async(services["prescribing"].create_batch_prescription(
            patient_id="patient-002",
            medications=[
                {
                    "name": "MedA",
                    "dosage": "5mg",
                    "frequency": "daily",
                    "duration_days": 14,
                },
                {
                    "name": "MedB",
                    "dosage": "10mg",
                    "frequency": "twice daily",
                    "duration_days": 7,
                },
            ],
        ))
        assert len(results) == 2
