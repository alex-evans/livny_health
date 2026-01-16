"""
Data Seeder.

Initializes repositories with seed data for development.
"""

from datetime import date, datetime, timedelta

from resources import (
    Patient,
    PatientRepository,
    Problem,
    RecentVitals,
    Insurance,
    Practitioner,
    PractitionerRepository,
    AllergyIntolerance,
    AllergyReaction,
    AllergyIntoleranceRepository,
    MedicationRequest,
    MedicationRequestStatus,
    MedicationForm,
    Dosage,
    MedicationRequestRepository,
    Appointment,
    AppointmentStatus,
    AppointmentParticipant,
    AppointmentFlag,
    AppointmentRepository,
    EncounterRepository,
)
from resources.core import (
    HumanName,
    Gender,
    Identifier,
    Reference,
    CodeableConcept,
    ContactPoint,
)


def seed_patients(repo: PatientRepository) -> None:
    """Seed patient data."""
    patients = [
        Patient(
            id="patient-001",
            name=HumanName(family="Johnson", given=["Sarah"]),
            birth_date=date(1985, 3, 15),
            gender=Gender.FEMALE,
            identifiers=[Identifier.mrn("MRN-10001")],
            telecom=[ContactPoint(system="phone", value="(555) 234-5678", use="mobile")],
            insurance=Insurance(provider="Blue Cross Blue Shield", member_id="BCBS-12345678"),
            problem_list=[
                Problem(name="Hypertension", diagnosed_year=2020),
                Problem(name="Type 2 Diabetes", diagnosed_year=2021),
                Problem(name="Hyperlipidemia", diagnosed_year=2022),
            ],
            recent_vitals=RecentVitals(
                date="01/10/2025",
                blood_pressure="138/82",
                weight="156 lbs",
                temperature="98.4°F",
            ),
        ),
        Patient(
            id="patient-002",
            name=HumanName(family="Chen", given=["Michael"]),
            birth_date=date(1972, 8, 22),
            gender=Gender.MALE,
            identifiers=[Identifier.mrn("MRN-10002")],
            telecom=[ContactPoint(system="phone", value="(555) 345-6789", use="home")],
            insurance=Insurance(provider="Aetna", member_id="AET-98765432"),
            problem_list=[
                Problem(name="GERD", diagnosed_year=2019),
                Problem(name="Anxiety", diagnosed_year=2020),
            ],
            recent_vitals=RecentVitals(
                date="01/08/2025",
                blood_pressure="124/78",
                weight="185 lbs",
                temperature="98.6°F",
            ),
        ),
        Patient(
            id="patient-003",
            name=HumanName(family="Rodriguez", given=["Emily"]),
            birth_date=date(1990, 11, 8),
            gender=Gender.FEMALE,
            identifiers=[Identifier.mrn("MRN-10003")],
            telecom=[ContactPoint(system="phone", value="(555) 456-7890", use="mobile")],
            insurance=Insurance(provider="UnitedHealthcare", member_id="UHC-11223344"),
            problem_list=[
                Problem(name="Asthma", diagnosed_year=2015),
            ],
            recent_vitals=RecentVitals(
                date="12/20/2024",
                blood_pressure="118/72",
                weight="142 lbs",
                temperature="98.2°F",
            ),
        ),
        Patient(
            id="patient-004",
            name=HumanName(family="Williams", given=["James"]),
            birth_date=date(1968, 5, 30),
            gender=Gender.MALE,
            identifiers=[Identifier.mrn("MRN-10004")],
            telecom=[ContactPoint(system="phone", value="(555) 567-8901", use="home")],
            insurance=Insurance(provider="Cigna", member_id="CIG-55667788"),
            problem_list=[
                Problem(name="Hypertension", diagnosed_year=2010),
                Problem(name="Chronic Pain Syndrome", diagnosed_year=2018),
                Problem(name="Peripheral Neuropathy", diagnosed_year=2019),
            ],
            recent_vitals=RecentVitals(
                date="01/12/2025",
                blood_pressure="142/88",
                weight="210 lbs",
                temperature="98.6°F",
            ),
        ),
        Patient(
            id="patient-005",
            name=HumanName(family="Garcia", given=["Maria"]),
            birth_date=date(1995, 1, 17),
            gender=Gender.FEMALE,
            identifiers=[Identifier.mrn("MRN-10005")],
            telecom=[ContactPoint(system="phone", value="(555) 678-9012", use="mobile")],
            insurance=Insurance(provider="Kaiser Permanente", member_id="KP-44556677"),
            problem_list=[],
            recent_vitals=None,
        ),
        Patient(
            id="patient-006",
            name=HumanName(family="Thompson", given=["Robert"]),
            birth_date=date(1958, 7, 12),
            gender=Gender.MALE,
            identifiers=[Identifier.mrn("MRN-10006")],
            telecom=[ContactPoint(system="phone", value="(555) 789-0123", use="home")],
            insurance=Insurance(provider="Medicare", member_id="MED-99887766"),
            problem_list=[
                Problem(name="Atrial Fibrillation", diagnosed_year=2018),
                Problem(name="Hypertension", diagnosed_year=2012),
                Problem(name="Heart Failure", diagnosed_year=2020),
            ],
            recent_vitals=RecentVitals(
                date="01/14/2025",
                blood_pressure="128/76",
                weight="178 lbs",
                temperature="98.8°F",
            ),
        ),
        Patient(
            id="patient-007",
            name=HumanName(family="Martinez", given=["Patricia"]),
            birth_date=date(1965, 9, 23),
            gender=Gender.FEMALE,
            identifiers=[Identifier.mrn("MRN-10007")],
            telecom=[ContactPoint(system="phone", value="(555) 890-1234", use="mobile")],
            insurance=Insurance(provider="Humana", member_id="HUM-33445566"),
            problem_list=[
                Problem(name="Atrial Fibrillation", diagnosed_year=2019),
                Problem(name="Hypertension", diagnosed_year=2015),
                Problem(name="Depression", diagnosed_year=2020),
                Problem(name="Hyperlipidemia", diagnosed_year=2017),
            ],
            recent_vitals=RecentVitals(
                date="01/05/2025",
                blood_pressure="132/80",
                weight="165 lbs",
                temperature="98.4°F",
            ),
        ),
    ]
    repo._seed(patients)


def seed_practitioners(repo: PractitionerRepository) -> None:
    """Seed practitioner data."""
    practitioners = [
        Practitioner(
            id="provider-001",
            name=HumanName(family="Frost", given=["Elizabeth"], prefix=["Dr."]),
            gender=Gender.FEMALE,
        ),
    ]
    repo._seed(practitioners)


def seed_allergies(repo: AllergyIntoleranceRepository) -> None:
    """Seed allergy data."""
    allergies = [
        # Patient 001 - Sarah Johnson
        AllergyIntolerance(
            id="allergy-1",
            patient=Reference.to("Patient", "patient-001", "Sarah Johnson"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            reactions=[AllergyReaction(manifestation="Anaphylaxis", severity="severe")],
            recorded_date=datetime(2020, 1, 15),
        ),
        AllergyIntolerance(
            id="allergy-2",
            patient=Reference.to("Patient", "patient-001", "Sarah Johnson"),
            code=CodeableConcept(code="sulfa", display="Sulfa"),
            reactions=[AllergyReaction(manifestation="Rash", severity="moderate")],
            recorded_date=datetime(2019, 6, 20),
        ),
        # Patient 002 - Michael Chen
        AllergyIntolerance(
            id="allergy-3",
            patient=Reference.to("Patient", "patient-002", "Michael Chen"),
            code=CodeableConcept(code="aspirin", display="Aspirin"),
            reactions=[AllergyReaction(manifestation="Hives", severity="mild")],
            recorded_date=datetime(2018, 4, 10),
        ),
        # Patient 004 - James Williams
        AllergyIntolerance(
            id="allergy-4",
            patient=Reference.to("Patient", "patient-004", "James Williams"),
            code=CodeableConcept(code="codeine", display="Codeine"),
            reactions=[AllergyReaction(manifestation="Nausea and vomiting", severity="moderate")],
            recorded_date=datetime(2015, 8, 22),
        ),
        AllergyIntolerance(
            id="allergy-5",
            patient=Reference.to("Patient", "patient-004", "James Williams"),
            code=CodeableConcept(code="latex", display="Latex"),
            reactions=[AllergyReaction(manifestation="Contact dermatitis", severity="mild")],
            recorded_date=datetime(2010, 3, 15),
        ),
    ]
    repo._seed(allergies)


def seed_medication_requests(repo: MedicationRequestRepository) -> None:
    """Seed medication request (active medications) data."""
    # Reference to prescriber (Dr. Frost)
    prescriber = Reference.to("Practitioner", "provider-001", "Dr. Elizabeth Frost")

    medications = [
        # Patient 001 - Sarah Johnson
        MedicationRequest(
            id="med-1",
            status=MedicationRequestStatus.ACTIVE,
            medication=CodeableConcept(code="lisinopril", display="Lisinopril"),
            brand_name="Zestril",
            strength="10mg",
            form=MedicationForm.TABLET,
            subject=Reference.to("Patient", "patient-001"),
            requester=prescriber,
            authored_on=datetime(2023, 6, 15),
            dosage_instruction=[Dosage(text="10mg daily", dose="1 tablet", frequency="once daily", route="oral")],
        ),
        MedicationRequest(
            id="med-2",
            status=MedicationRequestStatus.ACTIVE,
            medication=CodeableConcept(code="metformin", display="Metformin"),
            brand_name="Glucophage",
            strength="500mg",
            form=MedicationForm.TABLET,
            subject=Reference.to("Patient", "patient-001"),
            requester=prescriber,
            authored_on=datetime(2022, 3, 10),
            dosage_instruction=[Dosage(text="500mg twice daily", dose="1 tablet", frequency="twice daily", route="oral")],
        ),
        MedicationRequest(
            id="med-3",
            status=MedicationRequestStatus.ACTIVE,
            medication=CodeableConcept(code="atorvastatin", display="Atorvastatin"),
            brand_name="Lipitor",
            strength="20mg",
            form=MedicationForm.TABLET,
            subject=Reference.to("Patient", "patient-001"),
            requester=prescriber,
            authored_on=datetime(2023, 1, 5),
            dosage_instruction=[Dosage(text="20mg at bedtime", dose="1 tablet", frequency="at bedtime", route="oral")],
        ),
        MedicationRequest(
            id="med-14",
            status=MedicationRequestStatus.ACTIVE,
            medication=CodeableConcept(code="metoprolol", display="Metoprolol"),
            brand_name="Lopressor",
            strength="50mg",
            form=MedicationForm.TABLET,
            subject=Reference.to("Patient", "patient-001"),
            requester=prescriber,
            authored_on=datetime(2024, 2, 10),
            dosage_instruction=[Dosage(text="50mg twice daily", dose="1 tablet", frequency="twice daily", route="oral")],
        ),
        MedicationRequest(
            id="med-15",
            status=MedicationRequestStatus.ACTIVE,
            medication=CodeableConcept(code="aspirin", display="Aspirin"),
            brand_name=None,  # Generic only
            strength="81mg",
            form=MedicationForm.TABLET,
            subject=Reference.to("Patient", "patient-001"),
            requester=prescriber,
            authored_on=datetime(2023, 12, 1),
            dosage_instruction=[Dosage(text="81mg daily", dose="1 tablet", frequency="once daily", route="oral")],
        ),
        MedicationRequest(
            id="med-16",
            status=MedicationRequestStatus.ACTIVE,
            medication=CodeableConcept(code="hydrochlorothiazide", display="Hydrochlorothiazide"),
            brand_name="Microzide",
            strength="25mg",
            form=MedicationForm.TABLET,
            subject=Reference.to("Patient", "patient-001"),
            requester=prescriber,
            authored_on=datetime(2022, 8, 20),
            dosage_instruction=[Dosage(text="25mg daily", dose="1 tablet", frequency="once daily", route="oral")],
        ),
        # Patient 002 - Michael Chen
        MedicationRequest(
            id="med-4",
            status=MedicationRequestStatus.ACTIVE,
            medication=CodeableConcept(code="omeprazole", display="Omeprazole"),
            brand_name="Prilosec",
            strength="20mg",
            form=MedicationForm.CAPSULE,
            subject=Reference.to("Patient", "patient-002"),
            requester=prescriber,
            authored_on=datetime(2024, 1, 20),
            dosage_instruction=[Dosage(text="20mg daily before breakfast", dose="1 capsule", frequency="once daily", route="oral")],
        ),
        # Patient 003 - Emily Rodriguez
        MedicationRequest(
            id="med-5",
            status=MedicationRequestStatus.ACTIVE,
            medication=CodeableConcept(code="albuterol", display="Albuterol"),
            brand_name="ProAir HFA",
            strength="90mcg/actuation",
            form=MedicationForm.INHALER,
            subject=Reference.to("Patient", "patient-003"),
            requester=prescriber,
            authored_on=datetime(2023, 9, 1),
            dosage_instruction=[Dosage(text="90mcg as needed", dose="2 puffs", frequency="as needed", route="inhalation", as_needed=True)],
        ),
        # Patient 004 - James Williams
        MedicationRequest(
            id="med-6",
            status=MedicationRequestStatus.ACTIVE,
            medication=CodeableConcept(code="amlodipine", display="Amlodipine"),
            brand_name="Norvasc",
            strength="5mg",
            form=MedicationForm.TABLET,
            subject=Reference.to("Patient", "patient-004"),
            requester=prescriber,
            authored_on=datetime(2021, 11, 30),
            dosage_instruction=[Dosage(text="5mg daily", dose="1 tablet", frequency="once daily", route="oral")],
        ),
        MedicationRequest(
            id="med-7",
            status=MedicationRequestStatus.ACTIVE,
            medication=CodeableConcept(code="gabapentin", display="Gabapentin"),
            brand_name="Neurontin",
            strength="300mg",
            form=MedicationForm.CAPSULE,
            subject=Reference.to("Patient", "patient-004"),
            requester=prescriber,
            authored_on=datetime(2023, 4, 15),
            dosage_instruction=[Dosage(text="300mg three times daily", dose="1 capsule", frequency="three times daily", route="oral")],
        ),
        # Patient 006 - Robert Thompson
        MedicationRequest(
            id="med-8",
            status=MedicationRequestStatus.ACTIVE,
            medication=CodeableConcept(code="warfarin", display="Warfarin"),
            brand_name="Coumadin",
            strength="5mg",
            form=MedicationForm.TABLET,
            subject=Reference.to("Patient", "patient-006"),
            requester=prescriber,
            authored_on=datetime(2022, 8, 15),
            dosage_instruction=[Dosage(text="5mg daily", dose="1 tablet", frequency="once daily", route="oral")],
        ),
        MedicationRequest(
            id="med-9",
            status=MedicationRequestStatus.ACTIVE,
            medication=CodeableConcept(code="lisinopril", display="Lisinopril"),
            brand_name="Zestril",
            strength="10mg",
            form=MedicationForm.TABLET,
            subject=Reference.to("Patient", "patient-006"),
            requester=prescriber,
            authored_on=datetime(2021, 3, 20),
            dosage_instruction=[Dosage(text="10mg daily", dose="1 tablet", frequency="once daily", route="oral")],
        ),
        # Patient 007 - Patricia Martinez
        MedicationRequest(
            id="med-10",
            status=MedicationRequestStatus.ACTIVE,
            medication=CodeableConcept(code="warfarin", display="Warfarin"),
            brand_name="Coumadin",
            strength="5mg",
            form=MedicationForm.TABLET,
            subject=Reference.to("Patient", "patient-007"),
            requester=prescriber,
            authored_on=datetime(2023, 2, 10),
            dosage_instruction=[Dosage(text="5mg daily", dose="1 tablet", frequency="once daily", route="oral")],
        ),
        MedicationRequest(
            id="med-11",
            status=MedicationRequestStatus.ACTIVE,
            medication=CodeableConcept(code="simvastatin", display="Simvastatin"),
            brand_name="Zocor",
            strength="40mg",
            form=MedicationForm.TABLET,
            subject=Reference.to("Patient", "patient-007"),
            requester=prescriber,
            authored_on=datetime(2022, 5, 15),
            dosage_instruction=[Dosage(text="40mg at bedtime", dose="1 tablet", frequency="at bedtime", route="oral")],
        ),
        MedicationRequest(
            id="med-12",
            status=MedicationRequestStatus.ACTIVE,
            medication=CodeableConcept(code="sertraline", display="Sertraline"),
            brand_name="Zoloft",
            strength="50mg",
            form=MedicationForm.TABLET,
            subject=Reference.to("Patient", "patient-007"),
            requester=prescriber,
            authored_on=datetime(2023, 8, 1),
            dosage_instruction=[Dosage(text="50mg daily", dose="1 tablet", frequency="once daily", route="oral")],
        ),
        MedicationRequest(
            id="med-13",
            status=MedicationRequestStatus.ACTIVE,
            medication=CodeableConcept(code="lisinopril", display="Lisinopril"),
            brand_name="Zestril",
            strength="20mg",
            form=MedicationForm.TABLET,
            subject=Reference.to("Patient", "patient-007"),
            requester=prescriber,
            authored_on=datetime(2021, 11, 20),
            dosage_instruction=[Dosage(text="20mg daily", dose="1 tablet", frequency="once daily", route="oral")],
        ),
    ]
    repo._seed(medications)


def seed_appointments(repo: AppointmentRepository, patient_repo: PatientRepository) -> None:
    """
    Seed appointment data for today's schedule.
    Creates appointments similar to the original fake_data.py.
    """
    today = date.today()
    base_time = datetime.combine(today, datetime.min.time()).replace(hour=8, minute=0)
    now = datetime.now()

    templates = [
        {
            "patient_id": "patient-001",
            "time_offset": -240,  # 4:00 AM
            "duration": 30,
            "visit_type": "Follow-up",
            "chief_complaint": "Blood pressure check",
            "flags": [AppointmentFlag(type="critical_lab", message="A1C elevated at 8.2%")],
        },
        {
            "patient_id": "patient-002",
            "time_offset": 30,  # 8:30 AM
            "duration": 45,
            "visit_type": "Office Visit",
            "chief_complaint": "Persistent heartburn",
            "flags": [],
        },
        {
            "patient_id": "patient-003",
            "time_offset": 75,  # 9:15 AM
            "duration": 30,
            "visit_type": "Follow-up",
            "chief_complaint": "Asthma follow-up",
            "flags": [AppointmentFlag(type="overdue_screening", message="Overdue for cervical cancer screening")],
        },
        {
            "patient_id": "patient-004",
            "time_offset": 120,  # 10:00 AM
            "duration": 60,
            "visit_type": "Annual Physical",
            "chief_complaint": None,
            "flags": [AppointmentFlag(type="special_needs", message="Latex allergy - use nitrile gloves")],
        },
        {
            "patient_id": "patient-005",
            "time_offset": 180,  # 11:00 AM
            "duration": 30,
            "visit_type": "New Patient",
            "chief_complaint": "Establish care, general wellness",
            "flags": [AppointmentFlag(type="new_patient", message="New patient - allow extra time")],
        },
        {
            "patient_id": "patient-006",
            "time_offset": 240,  # 12:00 PM
            "duration": 30,
            "visit_type": "Urgent",
            "chief_complaint": "Chest pain - stable, for evaluation",
            "flags": [AppointmentFlag(type="critical_lab", message="INR out of range at 4.1")],
        },
        {
            "patient_id": "patient-007",
            "time_offset": 300,  # 1:00 PM
            "duration": 30,
            "visit_type": "Follow-up",
            "chief_complaint": "Medication review",
            "flags": [],
        },
        {
            "patient_id": "patient-001",
            "time_offset": 300,  # 1:00 PM (double-booked)
            "duration": 15,
            "visit_type": "Procedure",
            "chief_complaint": "Blood draw",
            "flags": [],
            "is_double_booked": True,
        },
        {
            "patient_id": "patient-002",
            "time_offset": 330,  # 1:30 PM
            "duration": 30,
            "visit_type": "Follow-up",
            "chief_complaint": "Review endoscopy results",
            "flags": [],
        },
        {
            "patient_id": "patient-003",
            "time_offset": 360,  # 2:00 PM
            "duration": 30,
            "visit_type": "Office Visit",
            "chief_complaint": "Shortness of breath with exercise",
            "flags": [],
        },
        {
            "patient_id": "patient-004",
            "time_offset": 390,  # 2:30 PM
            "duration": 45,
            "visit_type": "Follow-up",
            "chief_complaint": "Pain management review",
            "flags": [],
        },
        {
            "patient_id": "patient-005",
            "time_offset": 450,  # 3:30 PM
            "duration": 30,
            "visit_type": "Office Visit",
            "chief_complaint": "Fatigue and low energy",
            "flags": [],
        },
    ]

    appointments = []
    for idx, template in enumerate(templates):
        appt_start = base_time + timedelta(minutes=template["time_offset"])
        appt_end = appt_start + timedelta(minutes=template["duration"])

        # Determine status based on current time
        if appt_end < now:
            status = AppointmentStatus.FULFILLED
        elif appt_start <= now < appt_end:
            status = AppointmentStatus.ARRIVED
        else:
            status = AppointmentStatus.BOOKED
            if now >= appt_start - timedelta(minutes=30):
                status = AppointmentStatus.CHECKED_IN

        appointments.append(
            Appointment(
                id=f"appt-{today.isoformat()}-{idx:03d}",
                status=status,
                appointment_type=CodeableConcept(
                    code=template["visit_type"].lower().replace(" ", "-"),
                    display=template["visit_type"],
                ),
                start=appt_start,
                end=appt_end,
                duration_minutes=template["duration"],
                reason=template["chief_complaint"],
                participants=[
                    AppointmentParticipant(
                        actor=Reference.to("Patient", template["patient_id"]),
                        type="patient",
                    ),
                    AppointmentParticipant(
                        actor=Reference.to("Practitioner", "provider-001", "Dr. Elizabeth Frost"),
                        type="practitioner",
                    ),
                ],
                flags=template["flags"],
                is_double_booked=template.get("is_double_booked", False),
            )
        )

    repo._seed(appointments)


def seed_all(
    patient_repo: PatientRepository,
    practitioner_repo: PractitionerRepository,
    allergy_repo: AllergyIntoleranceRepository,
    medication_request_repo: MedicationRequestRepository,
    appointment_repo: AppointmentRepository,
    encounter_repo: EncounterRepository,
) -> None:
    """Seed all repositories with initial data."""
    seed_patients(patient_repo)
    seed_practitioners(practitioner_repo)
    seed_allergies(allergy_repo)
    seed_medication_requests(medication_request_repo)
    seed_appointments(appointment_repo, patient_repo)
    # Encounters are created dynamically when appointments are started
    print("[DATA SEEDER] All repositories seeded with initial data")
