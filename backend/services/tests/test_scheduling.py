"""
Unit tests for SchedulingService.

Tests appointment and encounter management workflows.
"""
import asyncio
from datetime import date, timedelta
import pytest

from services import (
    ProviderNotFoundError,
    AppointmentNotFoundError,
    ScheduleResult,
)
from resources import AppointmentStatus, EncounterStatus


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.mark.unit
class TestGetDailySchedule:
    """Tests for get_daily_schedule method."""

    def test_get_schedule_success(self, scheduling_service):
        """Should return schedule for valid date and provider."""
        result = run_async(scheduling_service.get_daily_schedule(
            date.today().isoformat(),
            "provider-001",
        ))

        assert isinstance(result, ScheduleResult)
        assert result.date == date.today().isoformat()
        assert result.provider_id == "provider-001"
        assert isinstance(result.appointments, list)

    def test_get_schedule_returns_appointments(self, scheduling_service):
        """Should return seeded appointments for today."""
        result = run_async(scheduling_service.get_daily_schedule(
            date.today().isoformat(),
            "provider-001",
        ))

        # Seeded data should have appointments for today
        assert len(result.appointments) > 0

    def test_get_schedule_empty_for_future_date(self, scheduling_service):
        """Should return empty schedule for future date with no appointments."""
        future_date = (date.today() + timedelta(days=30)).isoformat()
        result = run_async(scheduling_service.get_daily_schedule(
            future_date,
            "provider-001",
        ))

        assert result.appointments == []

    def test_get_schedule_invalid_date_format(self, scheduling_service):
        """Should raise ValueError for invalid date format."""
        with pytest.raises(ValueError, match="Invalid date format"):
            run_async(scheduling_service.get_daily_schedule(
                "not-a-date",
                "provider-001",
            ))

    def test_get_schedule_invalid_date_value(self, scheduling_service):
        """Should raise ValueError for invalid date value."""
        with pytest.raises(ValueError):
            run_async(scheduling_service.get_daily_schedule(
                "2024-13-45",  # Invalid month/day
                "provider-001",
            ))

    def test_get_schedule_unknown_provider(self, scheduling_service):
        """Should raise ProviderNotFoundError for unknown provider."""
        with pytest.raises(ProviderNotFoundError):
            run_async(scheduling_service.get_daily_schedule(
                date.today().isoformat(),
                "unknown-provider",
            ))

    def test_get_schedule_includes_provider_name(self, scheduling_service):
        """Should include provider name in result."""
        result = run_async(scheduling_service.get_daily_schedule(
            date.today().isoformat(),
            "provider-001",
        ))

        assert result.provider_name is not None
        assert len(result.provider_name) > 0


@pytest.mark.unit
class TestCreateAppointment:
    """Tests for create_appointment method."""

    def test_create_appointment_success(self, scheduling_service):
        """Should create appointment successfully."""
        appointment = run_async(scheduling_service.create_appointment(
            date_str=date.today().isoformat(),
            time="16:00",
            patient_id="patient-001",
            provider_id="provider-001",
            duration_minutes=30,
            visit_type="Follow-up",
            chief_complaint="Test appointment",
        ))

        assert appointment is not None
        assert appointment.id is not None
        assert appointment.duration_minutes == 30

    def test_create_appointment_with_defaults(self, scheduling_service):
        """Should use default values for optional parameters."""
        appointment = run_async(scheduling_service.create_appointment(
            date_str=date.today().isoformat(),
            time="17:00",
            patient_id="patient-002",
            provider_id="provider-001",
        ))

        assert appointment.duration_minutes == 30  # Default
        assert appointment.appointment_type.display == "Office Visit"  # Default

    def test_create_appointment_future_is_booked(self, scheduling_service):
        """Appointment for future date should have BOOKED status."""
        future_date = (date.today() + timedelta(days=7)).isoformat()
        appointment = run_async(scheduling_service.create_appointment(
            date_str=future_date,
            time="10:00",
            patient_id="patient-001",
            provider_id="provider-001",
        ))

        assert appointment.status == AppointmentStatus.BOOKED

    def test_create_appointment_past_is_fulfilled(self, scheduling_service):
        """Appointment for past date should have FULFILLED status."""
        past_date = (date.today() - timedelta(days=7)).isoformat()
        appointment = run_async(scheduling_service.create_appointment(
            date_str=past_date,
            time="10:00",
            patient_id="patient-001",
            provider_id="provider-001",
        ))

        assert appointment.status == AppointmentStatus.FULFILLED

    def test_create_appointment_unknown_patient(self, scheduling_service):
        """Should raise ValueError for unknown patient."""
        with pytest.raises(ValueError, match="not found"):
            run_async(scheduling_service.create_appointment(
                date_str=date.today().isoformat(),
                time="10:00",
                patient_id="unknown-patient",
                provider_id="provider-001",
            ))

    def test_create_appointment_unknown_provider(self, scheduling_service):
        """Should raise ProviderNotFoundError for unknown provider."""
        with pytest.raises(ProviderNotFoundError):
            run_async(scheduling_service.create_appointment(
                date_str=date.today().isoformat(),
                time="10:00",
                patient_id="patient-001",
                provider_id="unknown-provider",
            ))

    def test_create_appointment_has_participants(self, scheduling_service):
        """Created appointment should have patient and provider participants."""
        appointment = run_async(scheduling_service.create_appointment(
            date_str=date.today().isoformat(),
            time="18:00",
            patient_id="patient-003",
            provider_id="provider-001",
        ))

        assert len(appointment.participants) == 2
        types = [p.type for p in appointment.participants]
        assert "patient" in types
        assert "practitioner" in types


@pytest.mark.unit
class TestCheckInPatient:
    """Tests for check_in_patient method."""

    def test_check_in_patient_success(self, scheduling_service):
        """Should check in patient successfully."""
        # First create an appointment
        appointment = run_async(scheduling_service.create_appointment(
            date_str=date.today().isoformat(),
            time="09:00",
            patient_id="patient-002",
            provider_id="provider-001",
        ))

        # Then check them in
        updated = run_async(scheduling_service.check_in_patient(appointment.id))

        assert updated.status == AppointmentStatus.CHECKED_IN

    def test_check_in_patient_not_found(self, scheduling_service):
        """Should raise AppointmentNotFoundError for unknown appointment."""
        with pytest.raises(AppointmentNotFoundError):
            run_async(scheduling_service.check_in_patient("unknown-appointment"))


@pytest.mark.unit
class TestStartEncounter:
    """Tests for start_encounter method."""

    def test_start_encounter_success(self, scheduling_service):
        """Should start encounter from appointment."""
        # Create and check in appointment
        appointment = run_async(scheduling_service.create_appointment(
            date_str=date.today().isoformat(),
            time="09:30",
            patient_id="patient-003",
            provider_id="provider-001",
            chief_complaint="Test encounter",
        ))

        # Start encounter
        encounter = run_async(scheduling_service.start_encounter(appointment.id))

        assert encounter is not None
        assert encounter.id is not None
        assert encounter.status == EncounterStatus.IN_PROGRESS
        assert encounter.chief_complaint == "Test encounter"

    def test_start_encounter_updates_appointment_status(self, scheduling_service):
        """Starting encounter should update appointment to ARRIVED."""
        appointment = run_async(scheduling_service.create_appointment(
            date_str=date.today().isoformat(),
            time="10:00",
            patient_id="patient-004",
            provider_id="provider-001",
        ))

        run_async(scheduling_service.start_encounter(appointment.id))

        # Fetch updated appointment
        updated_appt = run_async(scheduling_service.appointment_repo.get(appointment.id))
        assert updated_appt.status == AppointmentStatus.ARRIVED

    def test_start_encounter_has_practitioner_participant(self, scheduling_service):
        """Encounter should have practitioner as participant."""
        appointment = run_async(scheduling_service.create_appointment(
            date_str=date.today().isoformat(),
            time="10:30",
            patient_id="patient-005",
            provider_id="provider-001",
        ))

        encounter = run_async(scheduling_service.start_encounter(appointment.id))

        assert len(encounter.participants) > 0
        assert any(p.type == "practitioner" for p in encounter.participants)

    def test_start_encounter_not_found(self, scheduling_service):
        """Should raise AppointmentNotFoundError for unknown appointment."""
        with pytest.raises(AppointmentNotFoundError):
            run_async(scheduling_service.start_encounter("unknown-appointment"))


@pytest.mark.unit
class TestEndEncounter:
    """Tests for end_encounter method."""

    def test_end_encounter_success(self, scheduling_service):
        """Should end encounter and update status."""
        # Create appointment and start encounter
        appointment = run_async(scheduling_service.create_appointment(
            date_str=date.today().isoformat(),
            time="11:00",
            patient_id="patient-001",
            provider_id="provider-001",
        ))
        encounter = run_async(scheduling_service.start_encounter(appointment.id))

        # End encounter
        ended = run_async(scheduling_service.end_encounter(encounter.id))

        assert ended.status == EncounterStatus.FINISHED
        assert ended.period.end is not None

    def test_end_encounter_updates_appointment(self, scheduling_service):
        """Ending encounter should update appointment to FULFILLED."""
        appointment = run_async(scheduling_service.create_appointment(
            date_str=date.today().isoformat(),
            time="11:30",
            patient_id="patient-002",
            provider_id="provider-001",
        ))
        encounter = run_async(scheduling_service.start_encounter(appointment.id))

        run_async(scheduling_service.end_encounter(encounter.id))

        # Fetch updated appointment
        updated_appt = run_async(scheduling_service.appointment_repo.get(appointment.id))
        assert updated_appt.status == AppointmentStatus.FULFILLED

    def test_end_encounter_not_found(self, scheduling_service):
        """Should raise ValueError for unknown encounter."""
        with pytest.raises(ValueError, match="not found"):
            run_async(scheduling_service.end_encounter("unknown-encounter"))


@pytest.mark.unit
class TestClearDynamicAppointments:
    """Tests for clear_dynamic_appointments method."""

    def test_clear_appointments(self, scheduling_service):
        """Should clear all appointments."""
        # Create some appointments
        run_async(scheduling_service.create_appointment(
            date_str=date.today().isoformat(),
            time="12:00",
            patient_id="patient-001",
            provider_id="provider-001",
        ))

        # Clear them
        run_async(scheduling_service.clear_dynamic_appointments())

        # Verify cleared (schedule should be empty for today after clearing)
        result = run_async(scheduling_service.get_daily_schedule(
            date.today().isoformat(),
            "provider-001",
        ))
        assert result.appointments == []
