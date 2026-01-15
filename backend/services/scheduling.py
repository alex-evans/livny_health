"""
Scheduling Service.

Handles appointment and encounter workflows.
"""

from dataclasses import dataclass
from datetime import datetime, date, timedelta

from resources import (
    Patient,
    PatientRepository,
    Practitioner,
    PractitionerRepository,
    Appointment,
    AppointmentStatus,
    AppointmentParticipant,
    AppointmentFlag,
    AppointmentRepository,
    Encounter,
    EncounterStatus,
    EncounterClass,
    EncounterParticipant,
    EncounterRepository,
)
from resources.core import Reference, CodeableConcept, Period, generate_id


class ProviderNotFoundError(Exception):
    """Raised when a provider is not found."""
    pass


class AppointmentNotFoundError(Exception):
    """Raised when an appointment is not found."""
    pass


@dataclass
class ScheduleResult:
    """Result of getting a schedule."""
    date: str
    provider_id: str
    provider_name: str
    appointments: list[dict]


class SchedulingService:
    """
    Service for managing appointments and encounters.
    """

    def __init__(
        self,
        patient_repo: PatientRepository,
        practitioner_repo: PractitionerRepository,
        appointment_repo: AppointmentRepository,
        encounter_repo: EncounterRepository,
    ):
        self.patient_repo = patient_repo
        self.practitioner_repo = practitioner_repo
        self.appointment_repo = appointment_repo
        self.encounter_repo = encounter_repo

    async def get_daily_schedule(
        self,
        date_str: str,
        provider_id: str,
    ) -> ScheduleResult:
        """
        Get the daily schedule for a provider.

        Args:
            date_str: Date in YYYY-MM-DD format
            provider_id: The provider ID

        Returns:
            ScheduleResult with appointments for the day
        """
        # Validate date format
        try:
            schedule_date = date.fromisoformat(date_str)
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")

        # Get provider
        provider = await self.practitioner_repo.get(provider_id)
        if not provider:
            raise ProviderNotFoundError(f"Provider {provider_id} not found")

        # Get appointments for the date
        appointments = await self.appointment_repo.get_for_date(schedule_date, provider_id)

        # Convert to BFF format with patient data
        appointment_dicts = []
        for appt in appointments:
            # Get patient data if available
            patient_data = None
            if appt.patient_id:
                patient = await self.patient_repo.get(appt.patient_id)
                if patient:
                    patient_data = patient.to_bff_dict()

            appointment_dicts.append(appt.to_bff_dict(patient_data))

        return ScheduleResult(
            date=date_str,
            provider_id=provider_id,
            provider_name=provider.display_name,
            appointments=appointment_dicts,
        )

    async def create_appointment(
        self,
        date_str: str,
        time: str,
        patient_id: str,
        provider_id: str,
        duration_minutes: int = 30,
        visit_type: str = "Office Visit",
        chief_complaint: str | None = None,
    ) -> Appointment:
        """
        Create a new appointment.

        Args:
            date_str: Date in YYYY-MM-DD format
            time: Time in HH:MM format (24-hour)
            patient_id: Patient ID
            provider_id: Provider ID
            duration_minutes: Duration in minutes
            visit_type: Type of visit
            chief_complaint: Reason for visit

        Returns:
            The created Appointment
        """
        # Validate patient exists
        patient = await self.patient_repo.get(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")

        # Validate provider exists
        provider = await self.practitioner_repo.get(provider_id)
        if not provider:
            raise ProviderNotFoundError(f"Provider {provider_id} not found")

        # Parse datetime
        start = datetime.strptime(f"{date_str} {time}", "%Y-%m-%d %H:%M")
        end = start + timedelta(minutes=duration_minutes)

        # Determine initial status based on time
        now = datetime.now()
        if start.date() < now.date():
            status = AppointmentStatus.FULFILLED
        elif start.date() > now.date():
            status = AppointmentStatus.BOOKED
        else:
            if end < now:
                status = AppointmentStatus.FULFILLED
            elif start <= now < end:
                status = AppointmentStatus.ARRIVED
            else:
                status = AppointmentStatus.BOOKED
                if now >= start - timedelta(minutes=30):
                    status = AppointmentStatus.CHECKED_IN

        appointment = Appointment(
            id=generate_id("appt"),
            status=status,
            appointment_type=CodeableConcept(
                code=visit_type.lower().replace(" ", "-"),
                display=visit_type,
            ),
            start=start,
            end=end,
            duration_minutes=duration_minutes,
            reason=chief_complaint,
            participants=[
                AppointmentParticipant(
                    actor=Reference.to("Patient", patient_id, patient.display_name),
                    type="patient",
                ),
                AppointmentParticipant(
                    actor=Reference.to("Practitioner", provider_id, provider.display_name),
                    type="practitioner",
                ),
            ],
        )

        await self.appointment_repo.create(appointment)
        return appointment

    async def check_in_patient(self, appointment_id: str) -> Appointment:
        """Check in a patient for their appointment."""
        appointment = await self.appointment_repo.get(appointment_id)
        if not appointment:
            raise AppointmentNotFoundError(f"Appointment {appointment_id} not found")

        appointment.status = AppointmentStatus.CHECKED_IN
        await self.appointment_repo.update(appointment_id, appointment)
        return appointment

    async def start_encounter(self, appointment_id: str) -> Encounter:
        """
        Start an encounter from an appointment.

        Creates a new encounter linked to the appointment.
        """
        appointment = await self.appointment_repo.get(appointment_id)
        if not appointment:
            raise AppointmentNotFoundError(f"Appointment {appointment_id} not found")

        # Update appointment status
        appointment.status = AppointmentStatus.ARRIVED
        await self.appointment_repo.update(appointment_id, appointment)

        # Create encounter
        encounter = Encounter(
            id=generate_id("enc"),
            status=EncounterStatus.IN_PROGRESS,
            encounter_class=EncounterClass.AMBULATORY,
            type=appointment.appointment_type,
            subject=appointment.patient,
            participants=[
                EncounterParticipant(
                    individual=p.actor,
                    type=p.type,
                )
                for p in appointment.participants
                if p.type == "practitioner"
            ],
            period=Period(start=datetime.utcnow()),
            chief_complaint=appointment.reason,
            appointment=Reference.to("Appointment", appointment_id),
        )

        await self.encounter_repo.create(encounter)
        return encounter

    async def end_encounter(self, encounter_id: str) -> Encounter:
        """End an encounter."""
        encounter = await self.encounter_repo.get(encounter_id)
        if not encounter:
            raise ValueError(f"Encounter {encounter_id} not found")

        encounter.status = EncounterStatus.FINISHED
        if encounter.period:
            encounter.period.end = datetime.utcnow()

        await self.encounter_repo.update(encounter_id, encounter)

        # Update linked appointment
        if encounter.appointment:
            appointment = await self.appointment_repo.get(encounter.appointment.id)
            if appointment:
                appointment.status = AppointmentStatus.FULFILLED
                await self.appointment_repo.update(appointment.id, appointment)

        return encounter

    async def clear_dynamic_appointments(self) -> None:
        """Clear all appointments (for testing)."""
        # Get all appointments and delete them
        all_appointments = await self.appointment_repo.list()
        for appt in all_appointments:
            await self.appointment_repo.delete(appt.id)
