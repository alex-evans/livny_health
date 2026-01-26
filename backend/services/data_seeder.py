"""
Data Seeder.

Initializes repositories with seed data for development.
"""

from datetime import date, datetime, timedelta

from resources import (
    Patient,
    PatientRepository,
    Problem,
    ProblemStatus,
    ProblemPriority,
    ProblemSeverity,
    RecentVitals,
    Insurance,
    AllergyReviewStatus,
    Practitioner,
    PractitionerRepository,
    AllergyIntolerance,
    AllergyReaction,
    AllergyCategory,
    AllergyIntoleranceRepository,
    MedicationRequest,
    MedicationRequestStatus,
    MedicationRequestIntent,
    MedicationForm,
    Dosage,
    MedicationRequestRepository,
    Appointment,
    AppointmentStatus,
    AppointmentParticipant,
    AppointmentFlag,
    AppointmentRepository,
    EncounterRepository,
    VisitNote,
    VisitNoteRepository,
    SOAPNote,
    VisitVitals,
    VisitMedication,
    VisitOrder,
    VisitDiagnosis,
    VisitProvider,
    MedicationAction,
    OrderType,
    OrderStatus,
    OrderPriority,
)
from resources.core import (
    HumanName,
    Gender,
    Identifier,
    Reference,
    CodeableConcept,
    ContactPoint,
)
from resources import (
    ImagingStudy,
    ImagingStudyRepository,
    RadiologyReport,
    ComparisonStudy,
)
from resources import (
    VitalSign,
    VitalSignRepository,
    VITAL_REFERENCE_RANGES,
)
from resources import (
    SocialFamilyHistory,
    SocialFamilyHistoryRepository,
    SocialHistory,
    FamilyHistory,
    SmokingHistory,
    AlcoholHistory,
    SubstanceUseHistory,
    FamilyMember,
    FamilyMemberCondition,
    SignificantCondition,
)
from resources import (
    LabResult,
    LabResultRepository,
)


def seed_patients(repo: PatientRepository) -> None:
    """Seed patient data."""
    # Reference to provider for allergy reviews
    provider_ref = Reference.to("Practitioner", "provider-001", "Dr. Elizabeth Frost")

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
                Problem(
                    name="Essential hypertension",
                    icd10_code="I10",
                    onset_date=date(2020, 3, 15),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    severity=ProblemSeverity.WELL_CONTROLLED,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2020, 3, 15),
                ),
                Problem(
                    name="Type 2 diabetes mellitus without complications",
                    icd10_code="E11.9",
                    onset_date=date(2021, 6, 10),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    severity=ProblemSeverity.MODERATE,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2021, 6, 10),
                ),
                Problem(
                    name="Hyperlipidemia, unspecified",
                    icd10_code="E78.5",
                    onset_date=date(2022, 1, 20),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    severity=ProblemSeverity.MILD,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2022, 1, 20),
                ),
                Problem(
                    name="Obesity, unspecified",
                    icd10_code="E66.9",
                    onset_date=date(2019, 5, 1),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2019, 5, 1),
                ),
                Problem(
                    name="Acute sinusitis, unspecified",
                    icd10_code="J01.90",
                    onset_date=date(2024, 9, 15),
                    status=ProblemStatus.RESOLVED,
                    priority=ProblemPriority.RESOLVED,
                    documenting_provider="Dr. Michael Torres",
                    documented_date=date(2024, 9, 15),
                    resolved_date=date(2024, 9, 28),
                    resolved_by_provider="Dr. Michael Torres",
                ),
                Problem(
                    name="Anxiety disorder, unspecified",
                    icd10_code="F41.9",
                    onset_date=date(2023, 4, 20),
                    status=ProblemStatus.INACTIVE,
                    priority=ProblemPriority.INACTIVE,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2023, 4, 20),
                ),
                Problem(
                    name="Acute upper respiratory infection",
                    icd10_code="J06.9",
                    onset_date=date.today() - timedelta(days=5),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.ACUTE,
                    severity=ProblemSeverity.MILD,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date.today() - timedelta(days=5),
                ),
                Problem(
                    name="Urinary tract infection, site not specified",
                    icd10_code="N39.0",
                    onset_date=date(2024, 6, 12),
                    status=ProblemStatus.RESOLVED,
                    priority=ProblemPriority.RESOLVED,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2024, 6, 12),
                    resolved_date=date(2024, 6, 22),
                    resolved_by_provider="Dr. Elizabeth Frost",
                ),
            ],
            recent_vitals=RecentVitals(
                date="01/10/2025",
                blood_pressure="138/82",
                weight="156 lbs",
                temperature="98.4°F",
            ),
            # Recently reviewed - within last month
            allergy_review_status=AllergyReviewStatus(
                reviewed_at=datetime.now() - timedelta(days=30),
                reviewed_by=provider_ref,
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
                Problem(
                    name="Gastro-esophageal reflux disease without esophagitis",
                    icd10_code="K21.0",
                    onset_date=date(2019, 2, 14),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                ),
                Problem(
                    name="Generalized anxiety disorder",
                    icd10_code="F41.1",
                    onset_date=date(2020, 8, 5),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                ),
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
                Problem(
                    name="Mild persistent asthma, uncomplicated",
                    icd10_code="J45.30",
                    onset_date=date(2015, 4, 12),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                ),
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
                Problem(
                    name="Essential hypertension",
                    icd10_code="I10",
                    onset_date=date(2010, 7, 1),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    severity=ProblemSeverity.MODERATE,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2010, 7, 22),
                ),
                Problem(
                    name="Chronic pain syndrome",
                    icd10_code="G89.4",
                    onset_date=date(2018, 3, 1),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    severity=ProblemSeverity.SEVERE,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2018, 3, 8),
                    is_critical=True,  # Severe chronic condition affecting quality of life
                ),
                Problem(
                    name="Peripheral neuropathy, unspecified",
                    icd10_code="G62.9",
                    onset_date=date(2019, 11, 1),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    severity=ProblemSeverity.MODERATE,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2019, 11, 15),
                ),
                Problem(
                    name="Lumbar spinal stenosis",
                    icd10_code="M48.06",
                    onset_date=date(2017, 5, 1),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    severity=ProblemSeverity.MODERATE,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2017, 5, 3),
                ),
                Problem(
                    name="Benign prostatic hyperplasia without obstruction",
                    icd10_code="N40.0",
                    onset_date=date(2020, 2, 1),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    severity=ProblemSeverity.MILD,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2020, 2, 10),
                ),
                Problem(
                    name="Vitamin D deficiency, unspecified",
                    icd10_code="E55.9",
                    onset_date=date(2021, 9, 1),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    severity=ProblemSeverity.WELL_CONTROLLED,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2021, 9, 1),
                ),
                Problem(
                    name="Acute low back pain",
                    icd10_code="M54.5",
                    onset_date=date(2024, 11, 20),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.ACUTE,
                    severity=ProblemSeverity.SEVERE,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2024, 11, 20),
                ),
                Problem(
                    name="Rotator cuff tendinitis, right shoulder",
                    icd10_code="M75.101",
                    onset_date=date(2023, 6, 15),
                    status=ProblemStatus.RESOLVED,
                    priority=ProblemPriority.RESOLVED,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2023, 6, 15),
                    resolved_date=date(2023, 10, 20),
                    resolved_by_provider="Dr. Elizabeth Frost",
                ),
                Problem(
                    name="Prostate cancer",
                    icd10_code="C61",
                    onset_date=date(2025, 1, 10),
                    status=ProblemStatus.RULE_OUT,
                    priority=ProblemPriority.ACUTE,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2025, 1, 10),
                    is_critical=True,  # Life-threatening condition under investigation
                ),
            ],
            recent_vitals=RecentVitals(
                date="01/12/2025",
                blood_pressure="142/88",
                weight="210 lbs",
                temperature="98.6°F",
            ),
            # STALE review - over 1 year old, should trigger warning
            allergy_review_status=AllergyReviewStatus(
                reviewed_at=datetime.now() - timedelta(days=400),
                reviewed_by=provider_ref,
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
                Problem(
                    name="Atrial fibrillation, unspecified",
                    icd10_code="I48.91",
                    onset_date=date(2018, 9, 5),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                ),
                Problem(
                    name="Essential hypertension",
                    icd10_code="I10",
                    onset_date=date(2012, 4, 18),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                ),
                Problem(
                    name="Heart failure, unspecified",
                    icd10_code="I50.9",
                    onset_date=date(2020, 1, 12),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    severity=ProblemSeverity.MODERATE,
                    is_critical=True,  # Life-threatening cardiac condition
                ),
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
                Problem(
                    name="Atrial fibrillation, unspecified",
                    icd10_code="I48.91",
                    onset_date=date(2019, 3, 28),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                ),
                Problem(
                    name="Essential hypertension",
                    icd10_code="I10",
                    onset_date=date(2015, 6, 15),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                ),
                Problem(
                    name="Major depressive disorder, single episode, moderate",
                    icd10_code="F32.1",
                    onset_date=date(2020, 10, 5),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                ),
                Problem(
                    name="Hyperlipidemia, unspecified",
                    icd10_code="E78.5",
                    onset_date=date(2017, 8, 22),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                ),
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
    # Reference to the documenting provider
    provider_ref = Reference.to("Practitioner", "provider-001", "Dr. Elizabeth Frost")

    allergies = [
        # Patient 001 - Sarah Johnson
        AllergyIntolerance(
            id="allergy-1",
            patient=Reference.to("Patient", "patient-001", "Sarah Johnson"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            reactions=[
                AllergyReaction(manifestation="Anaphylaxis", severity="severe", description="Immediate onset within 10 minutes"),
                AllergyReaction(manifestation="Hives", severity="moderate", description="Developed after initial anaphylaxis treatment"),
            ],
            recorded_date=datetime(2020, 1, 15),
            last_updated=datetime(2024, 6, 10),
            recorder=provider_ref,
            notes="Patient carries EpiPen. Avoid all penicillin-class antibiotics including amoxicillin.",
        ),
        AllergyIntolerance(
            id="allergy-2",
            patient=Reference.to("Patient", "patient-001", "Sarah Johnson"),
            code=CodeableConcept(code="sulfa", display="Sulfa"),
            reactions=[AllergyReaction(manifestation="Rash", severity="moderate")],
            recorded_date=datetime(2019, 6, 20),
            last_updated=datetime(2023, 11, 5),
            recorder=provider_ref,
            notes="Cross-reactivity with sulfasalazine noted.",
        ),
        # Food allergy for Sarah Johnson
        AllergyIntolerance(
            id="allergy-6",
            patient=Reference.to("Patient", "patient-001", "Sarah Johnson"),
            code=CodeableConcept(code="peanuts", display="Peanuts"),
            category=AllergyCategory.FOOD,
            reactions=[
                AllergyReaction(manifestation="Anaphylaxis", severity="severe", description="Throat swelling, difficulty breathing"),
                AllergyReaction(manifestation="Facial swelling", severity="moderate"),
                AllergyReaction(manifestation="Hives", severity="mild"),
            ],
            recorded_date=datetime(2018, 3, 10),
            last_updated=datetime(2024, 1, 15),
            recorder=provider_ref,
            notes="Patient carries EpiPen. Avoid all tree nuts as precaution.",
        ),
        # Environmental allergy for Sarah Johnson
        AllergyIntolerance(
            id="allergy-7",
            patient=Reference.to("Patient", "patient-001", "Sarah Johnson"),
            code=CodeableConcept(code="dust-mites", display="Dust Mites"),
            category=AllergyCategory.ENVIRONMENT,
            reactions=[AllergyReaction(manifestation="Rhinitis, sneezing", severity="mild")],
            recorded_date=datetime(2015, 7, 22),
            last_updated=datetime(2022, 8, 30),
            recorder=provider_ref,
        ),
        # Patient 002 - Michael Chen
        AllergyIntolerance(
            id="allergy-3",
            patient=Reference.to("Patient", "patient-002", "Michael Chen"),
            code=CodeableConcept(code="aspirin", display="Aspirin"),
            reactions=[AllergyReaction(manifestation="Hives", severity="mild")],
            recorded_date=datetime(2018, 4, 10),
            last_updated=datetime(2023, 5, 20),
            recorder=provider_ref,
            notes="Can tolerate acetaminophen.",
        ),
        # Patient 004 - James Williams
        AllergyIntolerance(
            id="allergy-4",
            patient=Reference.to("Patient", "patient-004", "James Williams"),
            code=CodeableConcept(code="codeine", display="Codeine"),
            reactions=[
                AllergyReaction(manifestation="Nausea and vomiting", severity="moderate"),
                AllergyReaction(manifestation="Severe constipation", severity="mild"),
            ],
            recorded_date=datetime(2015, 8, 22),
            last_updated=datetime(2024, 2, 14),
            recorder=provider_ref,
            notes="May tolerate tramadol per previous trial. Avoid all opioids if possible.",
        ),
        AllergyIntolerance(
            id="allergy-5",
            patient=Reference.to("Patient", "patient-004", "James Williams"),
            code=CodeableConcept(code="latex", display="Latex"),
            category=AllergyCategory.ENVIRONMENT,
            reactions=[AllergyReaction(manifestation="Contact dermatitis", severity="mild")],
            recorded_date=datetime(2010, 3, 15),
            last_updated=datetime(2020, 9, 8),
            recorder=provider_ref,
            notes="Use nitrile gloves only.",
        ),
        # INACTIVE/RESOLVED ALLERGIES
        # Patient 001 - Sarah Johnson - Resolved allergy (outgrown)
        AllergyIntolerance(
            id="allergy-8",
            patient=Reference.to("Patient", "patient-001", "Sarah Johnson"),
            code=CodeableConcept(code="egg", display="Egg"),
            category=AllergyCategory.FOOD,
            clinical_status="resolved",
            reactions=[AllergyReaction(manifestation="Hives", severity="mild")],
            recorded_date=datetime(1990, 5, 10),
            last_updated=datetime(2010, 8, 15),
            recorder=provider_ref,
            notes="Childhood allergy, outgrown. Tolerates egg products now. Confirmed via oral challenge 2010.",
        ),
        # Patient 004 - James Williams - Inactive allergy (refuted after testing)
        AllergyIntolerance(
            id="allergy-9",
            patient=Reference.to("Patient", "patient-004", "James Williams"),
            code=CodeableConcept(code="ibuprofen", display="Ibuprofen"),
            clinical_status="inactive",
            reactions=[AllergyReaction(manifestation="Reported GI upset", severity="mild")],
            recorded_date=datetime(2018, 11, 20),
            last_updated=datetime(2022, 3, 10),
            recorder=provider_ref,
            notes="Patient reported intolerance, not true allergy. Tolerated in controlled setting. Marked inactive.",
        ),
        # Patient 002 - Michael Chen - Resolved environmental allergy
        AllergyIntolerance(
            id="allergy-10",
            patient=Reference.to("Patient", "patient-002", "Michael Chen"),
            code=CodeableConcept(code="cats", display="Cat Dander"),
            category=AllergyCategory.ENVIRONMENT,
            clinical_status="resolved",
            reactions=[AllergyReaction(manifestation="Rhinitis, watery eyes", severity="mild")],
            recorded_date=datetime(2005, 6, 15),
            last_updated=datetime(2020, 1, 8),
            recorder=provider_ref,
            notes="After immunotherapy course 2018-2020, no longer symptomatic around cats.",
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
            dispense_refills=3,
            pharmacy="CVS Pharmacy - 123 Main St",
            indication="Hypertension management",
            prescriber_notes="Monitor potassium levels",
            drug_class="ACE Inhibitor",
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
            dispense_refills=5,
            pharmacy="CVS Pharmacy - 123 Main St",
            indication="Type 2 Diabetes",
            prescriber_notes="Take with meals to reduce GI upset",
            drug_class="Biguanide",
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
            dispense_refills=2,
            pharmacy="CVS Pharmacy - 123 Main St",
            indication="Hyperlipidemia",
            prescriber_notes="Check LFTs annually",
            drug_class="Statin",
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
            dispense_refills=4,
            pharmacy="CVS Pharmacy - 123 Main St",
            indication="Hypertension, rate control",
            prescriber_notes="Monitor heart rate",
            drug_class="Beta Blocker",
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
            dispense_refills=11,
            pharmacy="CVS Pharmacy - 123 Main St",
            indication="Cardiovascular protection",
            drug_class="NSAID / Antiplatelet",
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
            dispense_refills=2,
            pharmacy="CVS Pharmacy - 123 Main St",
            indication="Hypertension, edema",
            prescriber_notes="Monitor electrolytes",
            drug_class="Thiazide Diuretic",
        ),
        MedicationRequest(
            id="med-17",
            status=MedicationRequestStatus.ACTIVE,
            medication=CodeableConcept(code="tramadol", display="Tramadol"),
            brand_name="Ultram",
            strength="50mg",
            form=MedicationForm.TABLET,
            is_controlled=True,  # Schedule IV controlled substance
            subject=Reference.to("Patient", "patient-001"),
            requester=prescriber,
            authored_on=datetime.now() - timedelta(days=3),  # Recently prescribed
            dosage_instruction=[Dosage(text="50mg every 6 hours as needed", dose="1 tablet", frequency="every 6 hours", route="oral", as_needed=True)],
            dispense_refills=0,
            pharmacy="CVS Pharmacy - 123 Main St",
            indication="Acute pain management",
            prescriber_notes="Limit to 7 days. Reassess if pain persists.",
            drug_class="Opioid Analgesic",
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
            dispense_refills=5,
            pharmacy="Walgreens - 456 Oak Ave",
            indication="GERD",
            prescriber_notes="Take 30 min before eating",
            drug_class="Proton Pump Inhibitor",
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
            dispense_refills=6,
            pharmacy="Rite Aid - 789 Elm St",
            indication="Asthma - rescue inhaler",
            prescriber_notes="Use spacer if available. If using >2x/week, reassess controller therapy.",
            drug_class="Beta-2 Agonist",
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
            dispense_refills=3,
            pharmacy="Costco Pharmacy - 555 Commerce Dr",
            indication="Hypertension",
            prescriber_notes="Monitor for peripheral edema",
            drug_class="Calcium Channel Blocker",
        ),
        MedicationRequest(
            id="med-7",
            status=MedicationRequestStatus.ACTIVE,
            medication=CodeableConcept(code="gabapentin", display="Gabapentin"),
            brand_name="Neurontin",
            strength="300mg",
            form=MedicationForm.CAPSULE,
            is_controlled=True,  # Schedule V controlled substance
            subject=Reference.to("Patient", "patient-004"),
            requester=prescriber,
            authored_on=datetime(2023, 4, 15),
            dosage_instruction=[Dosage(text="300mg three times daily", dose="1 capsule", frequency="three times daily", route="oral")],
            dispense_refills=2,
            pharmacy="Costco Pharmacy - 555 Commerce Dr",
            indication="Peripheral neuropathy",
            prescriber_notes="May cause dizziness. Avoid driving until tolerance established.",
            drug_class="Anticonvulsant / Neuropathic Pain",
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
            dispense_refills=1,
            pharmacy="CVS Pharmacy - 123 Main St",
            indication="Atrial fibrillation - stroke prevention",
            prescriber_notes="Target INR 2-3. Weekly INR monitoring.",
            drug_class="Anticoagulant",
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
            dispense_refills=4,
            pharmacy="CVS Pharmacy - 123 Main St",
            indication="Hypertension, heart failure",
            prescriber_notes="Monitor renal function",
            drug_class="ACE Inhibitor",
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
            dispense_refills=2,
            pharmacy="Walgreens - 456 Oak Ave",
            indication="Atrial fibrillation",
            prescriber_notes="INR goal 2-3",
            drug_class="Anticoagulant",
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
            dispense_refills=3,
            pharmacy="Walgreens - 456 Oak Ave",
            indication="Hyperlipidemia",
            prescriber_notes="Avoid grapefruit juice",
            drug_class="Statin",
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
            dispense_refills=5,
            pharmacy="Walgreens - 456 Oak Ave",
            indication="Depression",
            prescriber_notes="May take 4-6 weeks for full effect",
            drug_class="SSRI",
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
            dispense_refills=4,
            pharmacy="Walgreens - 456 Oak Ave",
            indication="Hypertension",
            drug_class="ACE Inhibitor",
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


def seed_visit_notes(repo: VisitNoteRepository) -> None:
    """Seed visit note data with SOAP notes, vitals, medications, and orders."""
    now = datetime.utcnow()

    visit_notes = [
        # Patient 001 - Sarah Johnson - Recent visits
        VisitNote(
            id="v1",
            encounter=Reference.to("Encounter", "enc-001"),
            subject=Reference.to("Patient", "patient-001"),
            visit_type="annual_physical",  # Changed to annual_physical
            status="completed",
            date=now - timedelta(days=35),
            chief_complaint="Annual wellness exam",
            has_follow_up_required=True,
            follow_up_summary="Schedule colonoscopy screening (due). Recheck HbA1c in 3 months.",
            location="Livny Health Clinic - Main",
            duration=45,
            provider=VisitProvider(
                id="provider-001",
                name="Dr. Emily Chen",
                role="Attending",
                specialty="Internal Medicine",
            ),
            diagnoses=[
                VisitDiagnosis(code="Z00.00", description="Encounter for general adult medical examination without abnormal findings", is_primary=True),
                VisitDiagnosis(code="E11.9", description="Type 2 diabetes mellitus without complications", is_primary=False),
            ],
            soap_note=SOAPNote(
                subjective="Patient presents for annual wellness exam. Reports feeling generally well. Denies chest pain, shortness of breath, or palpitations. Diabetes well-controlled with current regimen. Occasional mild headaches, relieved with acetaminophen. Sleep quality good, 7-8 hours nightly. No recent weight changes.",
                objective="General: Well-appearing, no acute distress. HEENT: PERRLA, oropharynx clear. CV: RRR, no murmurs. Lungs: CTA bilaterally. Abdomen: Soft, non-tender, no organomegaly. Extremities: No edema, pulses 2+ bilaterally. Skin: No rashes or lesions. Neuro: A&O x3, cranial nerves intact.",
                assessment="1. Type 2 diabetes mellitus - well controlled on current regimen\n2. Essential hypertension - at goal\n3. Hyperlipidemia - stable on statin therapy\n4. Health maintenance up to date",
                plan="1. Continue current medications\n2. HbA1c in 3 months\n3. Lipid panel in 6 months\n4. Schedule colonoscopy (due for screening)\n5. Flu vaccine administered today\n6. Return in 6 months or sooner if concerns",
            ),
            vitals=VisitVitals(
                blood_pressure_systolic=132,
                blood_pressure_diastolic=78,
                heart_rate=72,
                temperature=98.4,
                temperature_unit="F",
                weight=156,
                weight_unit="lbs",
                oxygen_saturation=98,
                respiratory_rate=16,
                recorded_at=now - timedelta(days=35),
            ),
            medications=[
                VisitMedication(id="vm-1", name="Influenza Vaccine", dosage="0.5mL", frequency="once", action=MedicationAction.PRESCRIBED, route="IM", instructions="Administered left deltoid"),
            ],
            orders=[
                VisitOrder(id="ord-1", order_type=OrderType.LAB, name="HbA1c", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=35), completed_at=now - timedelta(days=33), result="6.8%", priority=OrderPriority.ROUTINE),
                VisitOrder(id="ord-2", order_type=OrderType.LAB, name="Lipid Panel", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=35), completed_at=now - timedelta(days=33), result="TC 210, LDL 135, HDL 55, TG 150", priority=OrderPriority.ROUTINE),
                VisitOrder(id="ord-3", order_type=OrderType.REFERRAL, name="Colonoscopy - GI", status=OrderStatus.PENDING, ordered_at=now - timedelta(days=35), priority=OrderPriority.ROUTINE),
            ],
        ),
        VisitNote(
            id="v2",
            encounter=Reference.to("Encounter", "enc-002"),
            subject=Reference.to("Patient", "patient-001"),
            visit_type="follow_up",
            status="completed",
            date=now - timedelta(days=90),
            chief_complaint="Diabetes follow-up, medication review",
            location="Livny Health Clinic - Main",
            duration=30,
            has_follow_up_required=True,
            follow_up_summary="Recheck A1C in 3 months. Annual eye exam referral placed.",
            provider=VisitProvider(
                id="provider-001",
                name="Dr. Emily Chen",
                role="Attending",
                specialty="Internal Medicine",
            ),
            diagnoses=[
                VisitDiagnosis(code="E11.65", description="Type 2 diabetes mellitus with hyperglycemia", is_primary=True),
            ],
            soap_note=SOAPNote(
                subjective="Patient returns for diabetes follow-up. Reports good compliance with metformin. Checking blood sugars 2-3x weekly, fasting readings 110-130. No hypoglycemic episodes. Denies polyuria, polydipsia, or blurred vision. Diet adherence fair - admits to occasional sweets.",
                objective="General: NAD. Weight stable. CV: RRR. Extremities: No ulcers, sensation intact to monofilament bilateral feet. Skin: No concerning lesions.",
                assessment="Type 2 DM with recent hyperglycemia, improving with lifestyle modifications. A1C elevated at 7.2% (down from 7.8%).",
                plan="1. Continue metformin 500mg BID\n2. Reinforce dietary counseling - limit simple carbohydrates\n3. Increase home glucose monitoring to daily fasting\n4. Recheck A1C in 3 months\n5. Annual eye exam due - referral placed\n6. Follow up in 3 months",
            ),
            vitals=VisitVitals(
                blood_pressure_systolic=138,
                blood_pressure_diastolic=82,
                heart_rate=76,
                temperature=98.6,
                weight=158,
                weight_unit="lbs",
                oxygen_saturation=97,
                recorded_at=now - timedelta(days=90),
            ),
            orders=[
                VisitOrder(id="ord-4", order_type=OrderType.LAB, name="HbA1c", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=90), completed_at=now - timedelta(days=88), result="7.2%", priority=OrderPriority.ROUTINE),
                VisitOrder(id="ord-5", order_type=OrderType.REFERRAL, name="Ophthalmology - Diabetic Eye Exam", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=90), completed_at=now - timedelta(days=60), result="No diabetic retinopathy", priority=OrderPriority.ROUTINE),
            ],
        ),
        VisitNote(
            id="v3",
            encounter=Reference.to("Encounter", "enc-003"),
            subject=Reference.to("Patient", "patient-001"),
            visit_type="urgent_care",
            status="completed",
            date=now - timedelta(days=130),
            chief_complaint="Acute sinusitis symptoms x 5 days",
            location="Livny Health Urgent Care",
            duration=20,
            provider=VisitProvider(
                id="provider-002",
                name="Dr. Michael Torres",
                role="Attending",
                specialty="Family Medicine",
            ),
            diagnoses=[
                VisitDiagnosis(code="J01.90", description="Acute sinusitis, unspecified", is_primary=True),
            ],
            soap_note=SOAPNote(
                subjective="Patient presents with 5-day history of nasal congestion, facial pressure/pain over maxillary sinuses bilaterally, thick yellow-green nasal discharge, and low-grade fever (100.2°F at home). Tried OTC decongestants with minimal relief. Denies severe headache, vision changes, or neck stiffness. Has known penicillin allergy (anaphylaxis).",
                objective="T 99.8°F. General: Mild distress due to congestion. HEENT: Tenderness to palpation over maxillary sinuses bilaterally, nasal mucosa erythematous with purulent discharge, posterior pharynx with postnasal drip, TMs clear. Lungs: CTA. No lymphadenopathy.",
                assessment="Acute bacterial sinusitis, likely secondary to viral URI. Patient has penicillin allergy precluding amoxicillin use.",
                plan="1. Azithromycin 500mg day 1, then 250mg days 2-5 (Z-pack) - avoiding penicillin class due to allergy\n2. Nasal saline irrigation TID\n3. Sudafed 30mg q6h PRN congestion\n4. Increase fluid intake\n5. Return if worsening, high fever, or no improvement in 72 hours\n6. Follow up with PCP if symptoms persist beyond 10 days",
            ),
            vitals=VisitVitals(
                blood_pressure_systolic=128,
                blood_pressure_diastolic=76,
                heart_rate=84,
                temperature=99.8,
                weight=155,
                weight_unit="lbs",
                oxygen_saturation=98,
                recorded_at=now - timedelta(days=130),
            ),
            medications=[
                VisitMedication(id="vm-2", name="Azithromycin (Z-pack)", dosage="250mg", frequency="daily x 5 days", action=MedicationAction.PRESCRIBED, route="oral", instructions="500mg day 1, then 250mg days 2-5"),
            ],
            notes="Prescribed azithromycin due to penicillin allergy. Return if symptoms worsen.",
        ),
        VisitNote(
            id="v4",
            encounter=Reference.to("Encounter", "enc-004"),
            subject=Reference.to("Patient", "patient-001"),
            visit_type="telehealth",
            status="completed",
            date=now - timedelta(days=185),
            chief_complaint="Blood pressure medication refill",
            location=None,
            duration=15,
            provider=VisitProvider(
                id="provider-001",
                name="Dr. Emily Chen",
                role="Attending",
                specialty="Internal Medicine",
            ),
            diagnoses=[
                VisitDiagnosis(code="I10", description="Essential (primary) hypertension", is_primary=True),
            ],
            soap_note=SOAPNote(
                subjective="Telehealth visit for BP medication refill. Patient reports home BP readings averaging 130-135/80-85. Taking lisinopril 10mg daily as prescribed. No dizziness, cough, or swelling. No chest pain or shortness of breath.",
                objective="Patient appears well via video. Alert and oriented. No visible distress. Patient reports home BP today 134/82.",
                assessment="Essential hypertension, reasonably controlled on current regimen.",
                plan="1. Continue lisinopril 10mg daily\n2. Refill authorized - 90-day supply with 3 refills\n3. Continue home BP monitoring\n4. Labs due at next in-person visit\n5. Follow up in 6 months or sooner if BP consistently elevated",
            ),
            medications=[
                VisitMedication(id="vm-3", name="Lisinopril", dosage="10mg", frequency="daily", action=MedicationAction.CONTINUED, route="oral"),
            ],
        ),
        VisitNote(
            id="v5",
            encounter=Reference.to("Encounter", "enc-005"),
            subject=Reference.to("Patient", "patient-001"),
            visit_type="lab_only",
            status="completed",
            date=now - timedelta(days=250),
            chief_complaint="Routine lab work - HbA1c, lipid panel",
            location="Livny Health Lab Services",
            duration=10,
            provider=VisitProvider(
                id="lab-services",
                name="Lab Services",
                role="Laboratory",
            ),
            diagnoses=[
                VisitDiagnosis(code="Z13.1", description="Encounter for screening for diabetes mellitus", is_primary=True),
            ],
            soap_note=SOAPNote(
                subjective="Patient presents for scheduled lab work. Fasting since midnight. No acute complaints.",
                objective="Venipuncture performed, left antecubital fossa. Hemostasis achieved.",
                assessment="Lab draw completed without complication.",
                plan="Results to be reviewed by PCP and communicated to patient.",
            ),
            vitals=VisitVitals(
                blood_pressure_systolic=130,
                blood_pressure_diastolic=80,
                heart_rate=70,
                recorded_at=now - timedelta(days=250),
            ),
            orders=[
                VisitOrder(id="ord-6", order_type=OrderType.LAB, name="HbA1c", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=250), completed_at=now - timedelta(days=249), result="7.8%", priority=OrderPriority.ROUTINE),
                VisitOrder(id="ord-7", order_type=OrderType.LAB, name="Lipid Panel", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=250), completed_at=now - timedelta(days=249), result="TC 225, LDL 142, HDL 48, TG 165", priority=OrderPriority.ROUTINE),
            ],
        ),
        VisitNote(
            id="v6",
            encounter=Reference.to("Encounter", "enc-006"),
            subject=Reference.to("Patient", "patient-001"),
            visit_type="office_visit",
            status="completed",
            date=now - timedelta(days=300),
            chief_complaint="Follow-up hypertension, diabetes management",
            location="Livny Health Clinic - Main",
            duration=30,
            has_critical_findings=True,
            critical_findings_summary="BP significantly elevated at 148/92. Weight gain 4 lbs. Trace ankle edema. Started HCTZ.",
            has_follow_up_required=True,
            follow_up_summary="Follow up in 1 month to recheck BP. Labs in 2 weeks for electrolytes.",
            provider=VisitProvider(
                id="provider-001",
                name="Dr. Emily Chen",
                role="Attending",
                specialty="Internal Medicine",
            ),
            diagnoses=[
                VisitDiagnosis(code="I10", description="Essential (primary) hypertension", is_primary=True),
                VisitDiagnosis(code="E11.9", description="Type 2 diabetes mellitus without complications", is_primary=False),
            ],
            soap_note=SOAPNote(
                subjective="Patient here for chronic disease management. BP has been elevated at home, averaging 145/90. Some dietary indiscretions over holidays. Diabetes: checking sugars sporadically, fasting 130-150. No hypoglycemia. No chest pain, SOB, edema, or vision changes.",
                objective="BP 148/92 (elevated). Weight up 4 lbs since last visit. CV: RRR, no murmurs. Lungs: Clear. Extremities: Trace bilateral ankle edema.",
                assessment="1. Hypertension - suboptimally controlled\n2. Type 2 DM - fair control, needs reinforcement\n3. Weight gain - likely contributing to above",
                plan="1. Add HCTZ 25mg daily for better BP control\n2. Continue metformin, lisinopril at current doses\n3. Dietary counseling - DASH diet handout provided\n4. Increase physical activity - goal 150 min/week\n5. Labs in 2 weeks to check electrolytes\n6. Follow up in 1 month",
            ),
            vitals=VisitVitals(
                blood_pressure_systolic=148,
                blood_pressure_diastolic=92,
                heart_rate=78,
                temperature=98.4,
                weight=160,
                weight_unit="lbs",
                oxygen_saturation=97,
                recorded_at=now - timedelta(days=300),
            ),
            medications=[
                VisitMedication(id="vm-4", name="Hydrochlorothiazide", dosage="25mg", frequency="daily", action=MedicationAction.PRESCRIBED, route="oral", instructions="Take in the morning"),
            ],
            orders=[
                VisitOrder(id="ord-8", order_type=OrderType.LAB, name="BMP (Basic Metabolic Panel)", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=300), completed_at=now - timedelta(days=285), result="Na 140, K 4.2, Cr 0.9, all WNL", priority=OrderPriority.ROUTINE),
            ],
        ),
        VisitNote(
            id="v7",
            encounter=Reference.to("Encounter", "enc-007"),
            subject=Reference.to("Patient", "patient-001"),
            visit_type="procedure",
            status="completed",
            date=now - timedelta(days=430),
            chief_complaint="Colonoscopy - routine screening",
            location="Livny Health Surgery Center",
            duration=60,
            has_critical_findings=True,
            critical_findings_summary="Two tubular adenomas found and removed. Low-grade dysplasia. Requires surveillance colonoscopy in 5 years.",
            has_follow_up_required=True,
            follow_up_summary="Repeat colonoscopy in 5 years due to adenomatous polyps.",
            provider=VisitProvider(
                id="provider-004",
                name="Dr. Sarah Kim",
                role="Attending",
                specialty="Gastroenterology",
            ),
            diagnoses=[
                VisitDiagnosis(code="Z12.11", description="Encounter for screening for malignant neoplasm of colon", is_primary=True),
                VisitDiagnosis(code="K63.5", description="Polyp of colon", is_primary=False),
            ],
            soap_note=SOAPNote(
                subjective="Patient presents for routine screening colonoscopy. Age-appropriate screening. No family history of colon cancer. No recent GI symptoms, bleeding, or weight loss. Completed bowel prep without difficulty.",
                objective="Procedure: Colonoscopy performed under moderate sedation (midazolam 3mg, fentanyl 75mcg). Scope advanced to cecum. Cecal landmarks identified. Two small sessile polyps (3mm and 4mm) identified in sigmoid colon and removed via cold snare polypectomy. No complications. Patient tolerated procedure well.",
                assessment="1. Screening colonoscopy - complete to cecum\n2. Two small sigmoid polyps - removed, sent to pathology",
                plan="1. Await pathology results (typically 5-7 days)\n2. If tubular adenomas: repeat colonoscopy in 5 years\n3. If hyperplastic only: repeat in 10 years\n4. Resume regular diet today\n5. No driving for 24 hours due to sedation\n6. Call if fever, severe pain, or bleeding",
            ),
            vitals=VisitVitals(
                blood_pressure_systolic=125,
                blood_pressure_diastolic=75,
                heart_rate=68,
                oxygen_saturation=99,
                recorded_at=now - timedelta(days=430),
            ),
            orders=[
                VisitOrder(id="ord-9", order_type=OrderType.PROCEDURE, name="Colonoscopy with polypectomy", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=430), completed_at=now - timedelta(days=430), priority=OrderPriority.ROUTINE),
                VisitOrder(id="ord-10", order_type=OrderType.LAB, name="Pathology - Colon polyps", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=430), completed_at=now - timedelta(days=423), result="Two tubular adenomas, low-grade dysplasia. Margins clear.", priority=OrderPriority.ROUTINE),
            ],
            notes="Two small polyps removed and sent to pathology. Recommend follow-up colonoscopy in 5 years.",
        ),
        VisitNote(
            id="v8",
            encounter=Reference.to("Encounter", "enc-008"),
            subject=Reference.to("Patient", "patient-001"),
            visit_type="emergency",
            status="completed",
            date=now - timedelta(days=530),
            chief_complaint="Chest pain, shortness of breath",
            location="Livny Health Emergency Department",
            duration=180,
            has_critical_findings=True,
            critical_findings_summary="Chest pain with negative cardiac workup. Anxiety/panic attack likely. Follow up with PCP required.",
            has_follow_up_required=True,
            follow_up_summary="Follow up with PCP within 1 week. Consider outpatient cardiology referral if symptoms recur.",
            provider=VisitProvider(
                id="provider-005",
                name="Dr. James Wilson",
                role="Attending",
                specialty="Emergency Medicine",
            ),
            diagnoses=[
                VisitDiagnosis(code="R07.9", description="Chest pain, unspecified", is_primary=True),
                VisitDiagnosis(code="R06.02", description="Shortness of breath", is_primary=False),
                VisitDiagnosis(code="F41.9", description="Anxiety disorder, unspecified", is_primary=False),
            ],
            soap_note=SOAPNote(
                subjective="45 y/o female presents to ED with acute onset chest tightness and shortness of breath x 2 hours. Describes pressure-like sensation across chest, non-radiating. Associated with palpitations and feeling of impending doom. Symptoms began while at work during stressful meeting. No prior cardiac history. Denies diaphoresis, nausea, or arm/jaw pain. History of occasional anxiety. No recent illness, travel, or immobilization.",
                objective="T 98.2, HR 102, BP 145/88, RR 22, SpO2 98% RA. General: Anxious-appearing, mild distress. CV: Tachycardic, regular rhythm, no murmurs/rubs/gallops. Lungs: CTA bilaterally, no wheezes. Chest wall non-tender. Extremities: No edema, calves non-tender.\n\nEKG: Sinus tachycardia, no ST changes, no ischemic changes.\nTroponin: <0.01 (negative) x2 at 0h and 3h\nD-dimer: Normal\nCXR: No acute cardiopulmonary process\nBMP: Normal",
                assessment="Chest pain with negative cardiac workup. Clinical presentation most consistent with acute anxiety/panic attack. Low suspicion for ACS given negative troponins, normal EKG, and atypical presentation. PE ruled out with normal D-dimer and low pretest probability.",
                plan="1. Cardiac workup negative - reassurance provided\n2. Discussed anxiety as likely etiology\n3. Lorazepam 0.5mg given in ED with symptom resolution\n4. Discharge home in stable condition\n5. Follow up with PCP within 1 week\n6. Consider outpatient cardiology referral if symptoms recur\n7. Discussed stress management techniques\n8. Return precautions reviewed: return immediately if chest pain recurs, worsens, or associated with diaphoresis/radiation",
            ),
            vitals=VisitVitals(
                blood_pressure_systolic=145,
                blood_pressure_diastolic=88,
                heart_rate=102,
                temperature=98.2,
                oxygen_saturation=98,
                respiratory_rate=22,
                recorded_at=now - timedelta(days=530),
            ),
            medications=[
                VisitMedication(id="vm-5", name="Lorazepam", dosage="0.5mg", frequency="once", action=MedicationAction.PRESCRIBED, route="oral", instructions="Given in ED for acute anxiety"),
            ],
            orders=[
                VisitOrder(id="ord-11", order_type=OrderType.LAB, name="Troponin I (serial)", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=530), completed_at=now - timedelta(days=530), result="<0.01 ng/mL (negative x2)", priority=OrderPriority.STAT),
                VisitOrder(id="ord-12", order_type=OrderType.LAB, name="D-dimer", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=530), completed_at=now - timedelta(days=530), result="0.3 (normal <0.5)", priority=OrderPriority.STAT),
                VisitOrder(id="ord-13", order_type=OrderType.LAB, name="BMP", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=530), completed_at=now - timedelta(days=530), result="All values within normal limits", priority=OrderPriority.STAT),
                VisitOrder(id="ord-14", order_type=OrderType.IMAGING, name="Chest X-ray", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=530), completed_at=now - timedelta(days=530), result="No acute cardiopulmonary process", priority=OrderPriority.STAT),
                VisitOrder(id="ord-15", order_type=OrderType.PROCEDURE, name="EKG", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=530), completed_at=now - timedelta(days=530), result="Sinus tachycardia, no ischemic changes", priority=OrderPriority.STAT),
            ],
            notes="Cardiac workup negative. Symptoms attributed to anxiety/panic attack. Discharged with PCP follow-up.",
        ),
    ]

    repo._seed(visit_notes)


def seed_imaging_studies(repo: ImagingStudyRepository) -> None:
    """Seed imaging study data with realistic radiology reports."""
    now = datetime.utcnow()

    imaging_studies = [
        # Patient 001 - Sarah Johnson - Multiple imaging studies
        ImagingStudy(
            id="img-001",
            patient_id="patient-001",
            accession_number="ACC-2024-001",
            modality="CT",
            body_part="Chest",
            study_date=now - timedelta(days=45),
            facility="Livny Health Imaging Center",
            ordering_provider="Dr. Elizabeth Frost",
            reading_radiologist="Dr. Robert Kim, MD",
            indication="Cough and shortness of breath, rule out pneumonia",
            series_count=3,
            image_count=156,
            has_images=True,
            report_status="final",
            report=RadiologyReport(
                clinical_indication="45-year-old female with persistent cough and shortness of breath for 2 weeks. Evaluate for pneumonia or other pulmonary pathology.",
                technique="CT chest performed without IV contrast. Axial images obtained from lung apices through lung bases with 1.25mm slice thickness. Coronal and sagittal reformations performed.",
                findings="LUNGS: No focal consolidation, mass, or nodule identified. Minimal bibasilar dependent atelectasis. No pleural effusion. Airways patent to subsegmental level.\n\nMEDIASTINUM: Heart size normal. No pericardial effusion. Mediastinal structures unremarkable. No significant lymphadenopathy.\n\nCHEST WALL: Unremarkable. No osseous lesion.",
                impression="1. No evidence of pneumonia or acute cardiopulmonary disease.\n2. Minimal bibasilar atelectasis, likely positional.\n3. Recommend clinical correlation and follow-up as needed.",
                comparison_studies=[],
                critical_finding=False,
            ),
        ),
        ImagingStudy(
            id="img-002",
            patient_id="patient-001",
            accession_number="ACC-2024-002",
            modality="XR",
            body_part="Chest",
            study_date=now - timedelta(days=90),
            facility="Livny Health Clinic",
            ordering_provider="Dr. Elizabeth Frost",
            reading_radiologist="Dr. Sarah Chen, MD",
            indication="Annual physical, baseline chest X-ray",
            series_count=1,
            image_count=2,
            has_images=True,
            report_status="final",
            report=RadiologyReport(
                clinical_indication="39-year-old female, routine chest X-ray for annual physical examination.",
                technique="PA and lateral chest radiographs obtained.",
                findings="HEART: Normal size and configuration.\nLUNGS: Clear bilaterally. No focal consolidation, pleural effusion, or pneumothorax.\nMEDIASTINUM: Unremarkable.\nBONES: No acute osseous abnormality.",
                impression="Normal chest radiograph. No acute cardiopulmonary disease.",
                comparison_studies=[],
                critical_finding=False,
            ),
        ),
        ImagingStudy(
            id="img-003",
            patient_id="patient-001",
            accession_number="ACC-2024-003",
            modality="US",
            body_part="Abdomen",
            study_date=now - timedelta(days=120),
            facility="Livny Health Imaging Center",
            ordering_provider="Dr. Elizabeth Frost",
            reading_radiologist="Dr. Maria Lopez, MD",
            indication="Abdominal pain, evaluate gallbladder",
            series_count=1,
            image_count=24,
            has_images=True,
            report_status="final",
            report=RadiologyReport(
                clinical_indication="Patient with intermittent right upper quadrant pain after meals. Evaluate for cholelithiasis.",
                technique="Real-time grayscale and color Doppler ultrasound examination of the abdomen performed.",
                findings="LIVER: Normal size, echogenicity, and echotexture. No focal hepatic lesion identified. Main portal vein is patent with normal hepatopetal flow.\n\nGALLBLADDER: Normal wall thickness. No gallstones or sludge. No pericholecystic fluid. Positive sonographic Murphy sign not elicited.\n\nBILE DUCTS: Common bile duct measures 4mm, within normal limits. No intrahepatic biliary ductal dilation.\n\nPANCREAS: Visualized portions unremarkable.\n\nKIDNEYS: Right kidney 10.2cm, left kidney 10.5cm. Normal cortical echogenicity bilaterally. No hydronephrosis or renal calculus.",
                impression="1. No cholelithiasis or sonographic evidence of acute cholecystitis.\n2. Normal liver, kidneys, and visualized pancreas.\n3. Consider other etiologies for patient's symptoms.",
                comparison_studies=[],
                critical_finding=False,
            ),
        ),
        ImagingStudy(
            id="img-004",
            patient_id="patient-001",
            accession_number="ACC-2023-004",
            modality="MAMMO",
            body_part="Bilateral Breasts",
            study_date=now - timedelta(days=180),
            facility="Livny Health Women's Imaging",
            ordering_provider="Dr. Elizabeth Frost",
            reading_radiologist="Dr. Jennifer Park, MD",
            indication="Annual screening mammography",
            series_count=2,
            image_count=4,
            has_images=True,
            report_status="final",
            report=RadiologyReport(
                clinical_indication="39-year-old female for annual screening mammography. No breast symptoms or concerns.",
                technique="Standard 2D digital mammographic views obtained including bilateral CC and MLO projections.",
                findings="BREAST COMPOSITION: The breasts are heterogeneously dense, which may obscure small masses (ACR Category C).\n\nFINDINGS:\nRight breast: No suspicious masses, architectural distortion, or suspicious calcifications.\nLeft breast: No suspicious masses, architectural distortion, or suspicious calcifications.\n\nSKIN/NIPPLE: Normal bilaterally.\nAXILLAE: No suspicious lymph nodes.",
                impression="BI-RADS Category 1: Negative.\nNo mammographic evidence of malignancy. Annual screening mammography recommended.",
                comparison_studies=[],
                critical_finding=False,
            ),
        ),

        # Patient 004 - James Williams - Pain patient with multiple imaging
        ImagingStudy(
            id="img-005",
            patient_id="patient-004",
            accession_number="ACC-2024-005",
            modality="MRI",
            body_part="Lumbar Spine",
            study_date=now - timedelta(days=30),
            facility="Livny Health Imaging Center",
            ordering_provider="Dr. Elizabeth Frost",
            reading_radiologist="Dr. David Martinez, MD",
            indication="Chronic low back pain with radiculopathy, evaluate for disc herniation",
            series_count=5,
            image_count=245,
            has_images=True,
            report_status="final",
            report=RadiologyReport(
                clinical_indication="56-year-old male with chronic low back pain radiating to bilateral lower extremities. History of lumbar spinal stenosis. Evaluate for disc herniation or progression.",
                technique="MRI of the lumbar spine performed without IV contrast. Sequences include sagittal T1, sagittal T2, sagittal STIR, axial T1, and axial T2.",
                findings="VERTEBRAL BODIES: Normal height and signal intensity. No compression fracture or marrow replacement lesion.\n\nDISCS:\nL3-L4: Mild disc desiccation. Mild broad-based disc bulge. Mild bilateral facet arthropathy. No significant central canal or foraminal stenosis.\n\nL4-L5: Moderate disc desiccation with loss of disc height. Broad-based disc bulge with superimposed left paracentral disc protrusion measuring 4mm. Moderate bilateral facet arthropathy with ligamentum flavum hypertrophy. Moderate central canal stenosis with AP diameter of 8mm. Moderate left and mild right neural foraminal stenosis.\n\nL5-S1: Mild disc desiccation. Mild broad-based disc bulge. Mild bilateral facet arthropathy. No significant stenosis.\n\nCONUS: Normal position and signal.\nPARAVERTEBRAL SOFT TISSUES: Unremarkable.",
                impression="1. L4-L5: Left paracentral disc protrusion with moderate central canal stenosis and moderate left neural foraminal stenosis. This may account for patient's left-sided radicular symptoms.\n2. Multilevel degenerative changes as described.\n3. Recommend clinical correlation and neurosurgical consultation if symptoms persist.",
                comparison_studies=[
                    ComparisonStudy(
                        study_id="img-old-001",
                        date=now - timedelta(days=365),
                        modality="MRI",
                        body_part="Lumbar Spine",
                    ),
                ],
                critical_finding=False,
            ),
        ),
        ImagingStudy(
            id="img-006",
            patient_id="patient-004",
            accession_number="ACC-2024-006",
            modality="XR",
            body_part="Lumbar Spine",
            study_date=now - timedelta(days=60),
            facility="Livny Health Clinic",
            ordering_provider="Dr. Elizabeth Frost",
            reading_radiologist="Dr. Sarah Chen, MD",
            indication="Chronic low back pain, evaluate alignment",
            series_count=1,
            image_count=3,
            has_images=True,
            report_status="final",
            report=RadiologyReport(
                clinical_indication="56-year-old male with chronic low back pain. Evaluate for alignment and degenerative changes.",
                technique="AP, lateral, and lateral flexion/extension views of the lumbar spine obtained.",
                findings="ALIGNMENT: Mild lumbar lordosis. No spondylolisthesis on neutral or flexion/extension views.\nVERTEBRAL BODIES: Maintained height. Mild anterior osteophytes L3-L5.\nDISC SPACES: Mild narrowing at L4-L5.\nFACET JOINTS: Mild facet arthropathy L4-L5.\nSACROILIAC JOINTS: Unremarkable.\nSOFT TISSUES: Unremarkable.",
                impression="1. Mild multilevel degenerative changes most prominent at L4-L5.\n2. No spondylolisthesis or acute osseous abnormality.",
                comparison_studies=[],
                critical_finding=False,
            ),
        ),
        ImagingStudy(
            id="img-007",
            patient_id="patient-004",
            accession_number="ACC-2024-007",
            modality="CT",
            body_part="Abdomen/Pelvis",
            study_date=now - timedelta(days=14),
            facility="Livny Health Imaging Center",
            ordering_provider="Dr. Elizabeth Frost",
            reading_radiologist="Dr. Robert Kim, MD",
            indication="Elevated PSA, evaluate prostate",
            series_count=2,
            image_count=312,
            has_images=True,
            report_status="preliminary",
            report=RadiologyReport(
                clinical_indication="56-year-old male with elevated PSA (5.8 ng/mL). Evaluate for prostatic abnormality and staging if applicable.",
                technique="CT abdomen and pelvis performed with IV and oral contrast. Arterial and portal venous phases obtained.",
                findings="LIVER: Normal size and attenuation. No focal hepatic lesion.\nGALLBLADDER/BILE DUCTS: Unremarkable.\nPANCREAS: Normal.\nSPLEEN: Normal size.\nADRENAL GLANDS: Unremarkable.\nKIDNEYS: Normal enhancement bilaterally. No hydronephrosis or renal mass. 3mm non-obstructing left renal calculus.\nBLADDER: Normal distention. No mass.\nPROSTATE: Enlarged, measuring approximately 45cc. Heterogeneous enhancement. No definite focal mass, though CT is limited for prostate evaluation.\nLYMPH NODES: No pathologically enlarged pelvic or retroperitoneal lymph nodes.\nBOWEL: Normal.\nBONES: Degenerative changes as noted on prior lumbar imaging. No suspicious osseous lesion.",
                impression="1. Benign prostatic enlargement. CT is limited for prostate evaluation; MRI of the prostate recommended for further characterization given elevated PSA.\n2. Small left renal calculus, non-obstructing.\n3. No lymphadenopathy or distant metastatic disease.",
                comparison_studies=[],
                critical_finding=False,
            ),
        ),

        # Patient 006 - Robert Thompson - Cardiac patient
        ImagingStudy(
            id="img-008",
            patient_id="patient-006",
            accession_number="ACC-2024-008",
            modality="XR",
            body_part="Chest",
            study_date=now - timedelta(days=7),
            facility="Livny Health Emergency Department",
            ordering_provider="Dr. James Wilson",
            reading_radiologist="Dr. Sarah Chen, MD",
            indication="Chest pain, shortness of breath",
            series_count=1,
            image_count=1,
            has_images=True,
            report_status="final",
            report=RadiologyReport(
                clinical_indication="66-year-old male with known heart failure presenting with chest pain and shortness of breath. Evaluate for acute cardiopulmonary process.",
                technique="Portable AP chest radiograph obtained.",
                findings="HEART: Cardiomegaly, stable compared to prior.\nLUNGS: Mild pulmonary vascular congestion. No focal consolidation. Small bilateral pleural effusions, left greater than right.\nMEDIASTINUM: Widened mediastinum consistent with known cardiomegaly.\nBONES: Degenerative changes. Sternotomy wires intact (patient has history of CABG).",
                impression="1. Mild pulmonary vascular congestion with small bilateral pleural effusions, consistent with mild heart failure decompensation.\n2. Cardiomegaly, stable.\n3. No pneumonia.",
                comparison_studies=[
                    ComparisonStudy(
                        study_id="img-old-002",
                        date=now - timedelta(days=90),
                        modality="XR",
                        body_part="Chest",
                    ),
                ],
                critical_finding=False,
            ),
        ),
        ImagingStudy(
            id="img-009",
            patient_id="patient-006",
            accession_number="ACC-2024-009",
            modality="US",
            body_part="Heart (Echocardiogram)",
            study_date=now - timedelta(days=60),
            facility="Livny Health Cardiology",
            ordering_provider="Dr. Elizabeth Frost",
            reading_radiologist="Dr. Michael Chang, MD, FACC",
            indication="Heart failure follow-up, assess LV function",
            series_count=1,
            image_count=45,
            has_images=True,
            report_status="final",
            report=RadiologyReport(
                clinical_indication="66-year-old male with known ischemic cardiomyopathy and heart failure, on Coumadin for atrial fibrillation. Follow-up echocardiogram to assess LV function.",
                technique="Transthoracic echocardiogram performed with 2D, M-mode, spectral Doppler, and color flow imaging.",
                findings="LEFT VENTRICLE: Mildly dilated. Moderate global hypokinesis. Akinesis of inferior wall. Estimated ejection fraction 35-40%.\n\nRIGHT VENTRICLE: Normal size. Mildly reduced systolic function.\n\nLEFT ATRIUM: Moderately dilated.\n\nRIGHT ATRIUM: Mildly dilated.\n\nAORTIC VALVE: Mildly thickened. No stenosis. Trace regurgitation.\n\nMITRAL VALVE: Mildly thickened. Mild regurgitation.\n\nTRICUSPID VALVE: Trace regurgitation. Estimated RVSP 35 mmHg.\n\nPERICARDIUM: No effusion.\n\nIVC: Normal caliber with >50% respiratory variation.",
                impression="1. Moderate LV systolic dysfunction (EF 35-40%), improved from prior (30-35%).\n2. Regional wall motion abnormality with inferior akinesis, consistent with prior inferior MI.\n3. Moderate LA dilation.\n4. Mild MR and TR.",
                comparison_studies=[
                    ComparisonStudy(
                        study_id="img-old-003",
                        date=now - timedelta(days=180),
                        modality="US",
                        body_part="Heart",
                    ),
                ],
                critical_finding=False,
            ),
        ),

        # Patient 003 - Emily Rodriguez - Asthma patient
        ImagingStudy(
            id="img-010",
            patient_id="patient-003",
            accession_number="ACC-2024-010",
            modality="XR",
            body_part="Chest",
            study_date=now - timedelta(days=150),
            facility="Livny Health Clinic",
            ordering_provider="Dr. Elizabeth Frost",
            reading_radiologist="Dr. Sarah Chen, MD",
            indication="Asthma exacerbation, rule out pneumonia",
            series_count=1,
            image_count=2,
            has_images=True,
            report_status="final",
            report=RadiologyReport(
                clinical_indication="34-year-old female with known asthma presenting with wheezing and cough. Evaluate for pneumonia or complication.",
                technique="PA and lateral chest radiographs obtained.",
                findings="HEART: Normal size.\nLUNGS: Hyperinflation consistent with air trapping. No focal consolidation, mass, or nodule. No pleural effusion or pneumothorax.\nMEDIASTINUM: Unremarkable.\nBONES: No acute osseous abnormality.",
                impression="1. Hyperinflation consistent with obstructive airway disease/air trapping.\n2. No pneumonia or acute cardiopulmonary disease.",
                comparison_studies=[],
                critical_finding=False,
            ),
        ),

        # Pending study example
        ImagingStudy(
            id="img-011",
            patient_id="patient-004",
            accession_number="ACC-2025-001",
            modality="MRI",
            body_part="Prostate",
            study_date=now - timedelta(days=2),
            facility="Livny Health Imaging Center",
            ordering_provider="Dr. Elizabeth Frost",
            reading_radiologist=None,
            indication="Elevated PSA, further evaluation of prostate",
            series_count=6,
            image_count=0,
            has_images=True,
            report_status="pending",
            report=None,
        ),

        # Critical finding example
        ImagingStudy(
            id="img-012",
            patient_id="patient-006",
            accession_number="ACC-2025-002",
            modality="CT",
            body_part="Chest",
            study_date=now - timedelta(days=5),
            facility="Livny Health Emergency Department",
            ordering_provider="Dr. James Wilson",
            reading_radiologist="Dr. Robert Kim, MD",
            indication="Acute shortness of breath, rule out PE",
            series_count=2,
            image_count=198,
            has_images=True,
            report_status="final",
            report=RadiologyReport(
                clinical_indication="66-year-old male with acute onset shortness of breath and known atrial fibrillation on warfarin. D-dimer elevated. Rule out pulmonary embolism.",
                technique="CT angiography of the chest performed with IV contrast. Timing optimized for pulmonary arterial enhancement.",
                findings="PULMONARY ARTERIES: No pulmonary embolism. Main pulmonary artery measures 28mm (upper limit of normal).\n\nHEART: Cardiomegaly. No pericardial effusion.\n\nLUNGS: Mild pulmonary vascular congestion. Small bilateral pleural effusions, unchanged. Bibasilar atelectasis. No pneumonia.\n\nMEDIASTINUM: Calcified mediastinal lymph nodes, likely granulomatous. No pathologic lymphadenopathy.\n\nAORTA: Mildly ectatic ascending aorta (4.0cm). Mild atherosclerotic calcification.\n\nBONES: Sternotomy wires intact. Degenerative changes.",
                impression="1. No pulmonary embolism.\n2. Mild pulmonary vascular congestion and small bilateral pleural effusions, consistent with mild heart failure.\n3. INCIDENTAL FINDING: Mildly ectatic ascending aorta (4.0cm). Recommend follow-up CT or echocardiogram in 1 year.",
                comparison_studies=[
                    ComparisonStudy(
                        study_id="img-008",
                        date=now - timedelta(days=7),
                        modality="XR",
                        body_part="Chest",
                    ),
                ],
                critical_finding=False,
                addendum="Addendum (1/18/2025): Incidental finding of ectatic ascending aorta communicated to ordering provider Dr. Wilson by phone at 14:35.",
            ),
        ),
    ]

    repo._seed(imaging_studies)


def seed_vitals(repo: VitalSignRepository) -> None:
    """Seed vital signs data with 12+ months of realistic data for patient-001."""
    import random

    patient_id = "patient-001"
    today = datetime.now()

    # Base values for Sarah Johnson (slightly elevated BP, normal weight)
    base_values = {
        "blood_pressure_systolic": 132,
        "blood_pressure_diastolic": 78,
        "heart_rate": 72,
        "temperature": 98.4,
        "weight": 156,
        "oxygen_saturation": 98,
        "respiratory_rate": 16,
        "height": 65,  # 5'5"
    }

    # Units for each vital type
    units = {
        "blood_pressure_systolic": "mmHg",
        "blood_pressure_diastolic": "mmHg",
        "heart_rate": "bpm",
        "temperature": "°F",
        "weight": "lbs",
        "oxygen_saturation": "%",
        "respiratory_rate": "breaths/min",
        "height": "in",
    }

    locations = ["Livny Health Clinic - Main", "Livny Health Urgent Care", "Home Monitoring"]
    providers = ["Dr. Elizabeth Frost", "Dr. Emily Chen", "MA Thompson", None]

    vital_id = 0

    # Height - only measured once (or very rarely)
    vital = VitalSign(
        id=f"vital-{vital_id}",
        vital_type="height",
        value=base_values["height"],
        unit=units["height"],
        status="normal",
        subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
        recorded_at=today - timedelta(days=365),
        recorded_by="MA Thompson",
        location="Livny Health Clinic - Main",
    )
    repo._store[vital.id] = vital
    vital_id += 1

    # Generate 18 months of data for other vitals at various frequencies
    # BP, HR, weight - monthly visits + some urgent/extra readings
    # Temperature, O2 sat, respiratory rate - less frequent, mainly at visits

    for months_ago in range(18, -1, -1):
        days_ago = months_ago * 30 + random.randint(-5, 5)
        if days_ago < 0:
            days_ago = 0

        recorded_at = today - timedelta(days=days_ago)
        location = random.choice(locations[:2])  # Clinic or urgent care
        provider = random.choice(providers[:3])  # Exclude None for regular visits

        # Weight trend: started higher, gradually decreasing (good trend for this patient)
        weight_trend_factor = 1 + (months_ago * 0.003)  # Started about 5% higher
        weight_value = round(base_values["weight"] * weight_trend_factor + random.uniform(-2, 2), 1)

        # BP trend: started higher, improving with treatment
        bp_sys_trend = 1 + (months_ago * 0.005)  # Started about 9% higher
        bp_sys_value = round(base_values["blood_pressure_systolic"] * bp_sys_trend + random.uniform(-5, 5))
        bp_dia_trend = 1 + (months_ago * 0.004)
        bp_dia_value = round(base_values["blood_pressure_diastolic"] * bp_dia_trend + random.uniform(-3, 3))

        # Heart rate - relatively stable
        hr_value = round(base_values["heart_rate"] + random.uniform(-8, 8))

        # O2 sat - mostly stable, high
        o2_value = round(base_values["oxygen_saturation"] + random.uniform(-2, 1))
        o2_value = min(100, max(92, o2_value))  # Keep in realistic range

        # Respiratory rate - stable
        rr_value = round(base_values["respiratory_rate"] + random.uniform(-2, 2))

        # Temperature - normal most of the time
        temp_value = round(base_values["temperature"] + random.uniform(-0.5, 0.5), 1)

        # Add systolic BP
        status = VitalSign.determine_status("blood_pressure_systolic", bp_sys_value)
        vital = VitalSign(
            id=f"vital-{vital_id}",
            vital_type="blood_pressure_systolic",
            value=bp_sys_value,
            unit=units["blood_pressure_systolic"],
            status=status,
            subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
            recorded_at=recorded_at,
            recorded_by=provider,
            location=location,
        )
        repo._store[vital.id] = vital
        vital_id += 1

        # Add diastolic BP
        status = VitalSign.determine_status("blood_pressure_diastolic", bp_dia_value)
        vital = VitalSign(
            id=f"vital-{vital_id}",
            vital_type="blood_pressure_diastolic",
            value=bp_dia_value,
            unit=units["blood_pressure_diastolic"],
            status=status,
            subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
            recorded_at=recorded_at,
            recorded_by=provider,
            location=location,
        )
        repo._store[vital.id] = vital
        vital_id += 1

        # Add heart rate
        status = VitalSign.determine_status("heart_rate", hr_value)
        vital = VitalSign(
            id=f"vital-{vital_id}",
            vital_type="heart_rate",
            value=hr_value,
            unit=units["heart_rate"],
            status=status,
            subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
            recorded_at=recorded_at,
            recorded_by=provider,
            location=location,
        )
        repo._store[vital.id] = vital
        vital_id += 1

        # Add weight
        status = VitalSign.determine_status("weight", weight_value)
        vital = VitalSign(
            id=f"vital-{vital_id}",
            vital_type="weight",
            value=weight_value,
            unit=units["weight"],
            status=status,
            subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
            recorded_at=recorded_at,
            recorded_by=provider,
            location=location,
        )
        repo._store[vital.id] = vital
        vital_id += 1

        # Add O2 sat, respiratory rate, and temperature less frequently
        if months_ago % 3 == 0 or months_ago <= 2:
            # O2 sat
            status = VitalSign.determine_status("oxygen_saturation", o2_value)
            vital = VitalSign(
                id=f"vital-{vital_id}",
                vital_type="oxygen_saturation",
                value=o2_value,
                unit=units["oxygen_saturation"],
                status=status,
                subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
                recorded_at=recorded_at,
                recorded_by=provider,
                location=location,
            )
            repo._store[vital.id] = vital
            vital_id += 1

            # Respiratory rate
            status = VitalSign.determine_status("respiratory_rate", rr_value)
            vital = VitalSign(
                id=f"vital-{vital_id}",
                vital_type="respiratory_rate",
                value=rr_value,
                unit=units["respiratory_rate"],
                status=status,
                subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
                recorded_at=recorded_at,
                recorded_by=provider,
                location=location,
            )
            repo._store[vital.id] = vital
            vital_id += 1

            # Temperature
            status = VitalSign.determine_status("temperature", temp_value)
            vital = VitalSign(
                id=f"vital-{vital_id}",
                vital_type="temperature",
                value=temp_value,
                unit=units["temperature"],
                status=status,
                subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
                recorded_at=recorded_at,
                recorded_by=provider,
                location=location,
            )
            repo._store[vital.id] = vital
            vital_id += 1

    # Add some critical/abnormal readings for realism
    # High BP reading from urgent care visit (9 months ago)
    urgent_care_date = today - timedelta(days=270)
    vital = VitalSign(
        id=f"vital-{vital_id}",
        vital_type="blood_pressure_systolic",
        value=165,
        unit="mmHg",
        status="critical",
        subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
        recorded_at=urgent_care_date,
        recorded_by="Dr. Michael Torres",
        location="Livny Health Urgent Care",
    )
    repo._store[vital.id] = vital
    vital_id += 1

    vital = VitalSign(
        id=f"vital-{vital_id}",
        vital_type="blood_pressure_diastolic",
        value=105,
        unit="mmHg",
        status="critical",
        subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
        recorded_at=urgent_care_date,
        recorded_by="Dr. Michael Torres",
        location="Livny Health Urgent Care",
    )
    repo._store[vital.id] = vital
    vital_id += 1

    # Fever reading during sinusitis visit (from visit history)
    sinusitis_date = today - timedelta(days=135)  # Sept 8 from mock visits
    vital = VitalSign(
        id=f"vital-{vital_id}",
        vital_type="temperature",
        value=99.8,
        unit="°F",
        status="abnormal",
        subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
        recorded_at=sinusitis_date,
        recorded_by="Dr. Michael Torres",
        location="Livny Health Urgent Care",
    )
    repo._store[vital.id] = vital
    vital_id += 1

    # RECENT CRITICAL VITALS (for testing clinical alerts)
    # High blood pressure from today - needs attention
    recent_date = today - timedelta(hours=4)
    vital = VitalSign(
        id=f"vital-{vital_id}",
        vital_type="blood_pressure_systolic",
        value=185,
        unit="mmHg",
        status="critical",
        subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
        recorded_at=recent_date,
        recorded_by="Dr. Emily Chen",
        location="Livny Health Clinic - Main",
    )
    repo._store[vital.id] = vital
    vital_id += 1

    vital = VitalSign(
        id=f"vital-{vital_id}",
        vital_type="blood_pressure_diastolic",
        value=120,
        unit="mmHg",
        status="critical",
        subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
        recorded_at=recent_date,
        recorded_by="Dr. Emily Chen",
        location="Livny Health Clinic - Main",
    )
    repo._store[vital.id] = vital


def seed_social_family_history(repo: SocialFamilyHistoryRepository) -> None:
    """Seed social and family history data for test patients."""

    # Patient-001: Sarah Johnson
    # Former smoker, occasional alcohol, married, family history of diabetes/HTN/breast cancer
    patient_001_history = SocialFamilyHistory(
        id="sfh-001",
        subject=Reference.to("Patient", "patient-001", "Sarah Johnson"),
        social_history=SocialHistory(
            smoking=SmokingHistory(
                status="former",
                pack_years=8.5,
                quit_date=date(2018, 6, 1),
                notes="Quit smoking after diabetes diagnosis. Previously smoked 1/2 pack/day for 17 years.",
            ),
            alcohol=AlcoholHistory(
                use_level="occasional",
                drinks_per_week=2,
                history_of_abuse=False,
                notes="Social drinking only, wine with dinner 1-2x/week.",
            ),
            substance_use=SubstanceUseHistory(
                level="none",
                substances=[],
                iv_drug_use=False,
            ),
            occupation="Marketing Manager",
            occupation_hazards=[],
            living_situation="Lives with spouse and two children in suburban home",
            marital_status="married",
            exercise="light",
            diet="diabetic",
            diet_notes="Following low-carb diet for diabetes management. Avoids peanuts (allergy).",
            last_reviewed=datetime(2024, 11, 15),
            reviewed_by="Dr. Elizabeth Frost",
        ),
        family_history=FamilyHistory(
            family_members=[
                FamilyMember(
                    id="fm-001-1",
                    relative_type="father",
                    is_living=True,
                    conditions=[
                        FamilyMemberCondition(
                            condition_name="Type 2 diabetes mellitus",
                            icd10_code="E11",
                            age_at_onset=52,
                            notes="Diet-controlled initially, now on metformin",
                        ),
                        FamilyMemberCondition(
                            condition_name="Essential hypertension",
                            icd10_code="I10",
                            age_at_onset=48,
                        ),
                    ],
                ),
                FamilyMember(
                    id="fm-001-2",
                    relative_type="mother",
                    is_living=True,
                    conditions=[
                        FamilyMemberCondition(
                            condition_name="Breast cancer",
                            icd10_code="C50.9",
                            age_at_onset=58,
                            notes="Stage IIA, successfully treated with lumpectomy and radiation",
                        ),
                        FamilyMemberCondition(
                            condition_name="Osteoarthritis",
                            icd10_code="M19.90",
                            age_at_onset=62,
                        ),
                    ],
                ),
                FamilyMember(
                    id="fm-001-3",
                    relative_type="maternal_grandmother",
                    is_living=False,
                    age_at_death=78,
                    cause_of_death="Breast cancer",
                    conditions=[
                        FamilyMemberCondition(
                            condition_name="Breast cancer",
                            icd10_code="C50.9",
                            age_at_onset=72,
                        ),
                    ],
                ),
                FamilyMember(
                    id="fm-001-4",
                    relative_type="paternal_grandfather",
                    is_living=False,
                    age_at_death=71,
                    cause_of_death="Myocardial infarction",
                    conditions=[
                        FamilyMemberCondition(
                            condition_name="Coronary artery disease",
                            icd10_code="I25.10",
                            age_at_onset=58,
                        ),
                        FamilyMemberCondition(
                            condition_name="Type 2 diabetes mellitus",
                            icd10_code="E11",
                            age_at_onset=55,
                        ),
                    ],
                ),
                FamilyMember(
                    id="fm-001-5",
                    relative_type="brother",
                    is_living=True,
                    conditions=[
                        FamilyMemberCondition(
                            condition_name="Pre-diabetes",
                            icd10_code="R73.03",
                            age_at_onset=35,
                        ),
                    ],
                ),
            ],
            significant_conditions=[
                SignificantCondition(
                    condition_name="Type 2 diabetes mellitus",
                    icd10_code="E11",
                    affected_relatives=["father", "paternal_grandfather", "brother (pre-diabetes)"],
                    notes="Strong family history of diabetes, multiple first-degree relatives affected",
                ),
                SignificantCondition(
                    condition_name="Breast cancer",
                    icd10_code="C50.9",
                    affected_relatives=["mother", "maternal_grandmother"],
                    notes="Two generations affected, recommend genetic counseling",
                ),
                SignificantCondition(
                    condition_name="Cardiovascular disease",
                    icd10_code="I25",
                    affected_relatives=["paternal_grandfather", "father (HTN)"],
                ),
            ],
            hereditary_syndromes=[],
            adoption_status="not_adopted",
            last_reviewed=datetime(2024, 11, 15),
            reviewed_by="Dr. Elizabeth Frost",
        ),
    )

    # Patient-002: Robert Chen
    # Never smoker, moderate alcohol, divorced, family history varies
    patient_002_history = SocialFamilyHistory(
        id="sfh-002",
        subject=Reference.to("Patient", "patient-002", "Robert Chen"),
        social_history=SocialHistory(
            smoking=SmokingHistory(
                status="never",
                pack_years=None,
                quit_date=None,
            ),
            alcohol=AlcoholHistory(
                use_level="moderate",
                drinks_per_week=7,
                history_of_abuse=False,
                notes="1-2 beers daily after work",
            ),
            substance_use=SubstanceUseHistory(
                level="past",
                substances=["marijuana"],
                iv_drug_use=False,
                notes="Occasional marijuana use in college, none since age 25",
            ),
            occupation="Software Engineer",
            occupation_hazards=["Prolonged sitting", "Screen time"],
            living_situation="Lives alone in downtown apartment",
            marital_status="divorced",
            exercise="sedentary",
            diet="regular",
            diet_notes="Fast food 3-4x/week, limited fruits and vegetables",
            last_reviewed=datetime(2024, 10, 20),
            reviewed_by="Dr. Elizabeth Frost",
        ),
        family_history=FamilyHistory(
            family_members=[
                FamilyMember(
                    id="fm-002-1",
                    relative_type="father",
                    is_living=True,
                    conditions=[
                        FamilyMemberCondition(
                            condition_name="Hyperlipidemia",
                            icd10_code="E78.5",
                            age_at_onset=45,
                        ),
                        FamilyMemberCondition(
                            condition_name="Gastroesophageal reflux disease",
                            icd10_code="K21.0",
                            age_at_onset=50,
                        ),
                    ],
                ),
                FamilyMember(
                    id="fm-002-2",
                    relative_type="mother",
                    is_living=True,
                    conditions=[
                        FamilyMemberCondition(
                            condition_name="Migraine",
                            icd10_code="G43.9",
                            age_at_onset=30,
                        ),
                    ],
                ),
                FamilyMember(
                    id="fm-002-3",
                    relative_type="paternal_grandfather",
                    is_living=False,
                    age_at_death=82,
                    cause_of_death="Prostate cancer",
                    conditions=[
                        FamilyMemberCondition(
                            condition_name="Prostate cancer",
                            icd10_code="C61",
                            age_at_onset=78,
                        ),
                        FamilyMemberCondition(
                            condition_name="Benign prostatic hyperplasia",
                            icd10_code="N40.0",
                            age_at_onset=65,
                        ),
                    ],
                ),
            ],
            significant_conditions=[
                SignificantCondition(
                    condition_name="Hyperlipidemia",
                    icd10_code="E78.5",
                    affected_relatives=["father"],
                ),
            ],
            hereditary_syndromes=[],
            adoption_status="not_adopted",
            last_reviewed=datetime(2024, 10, 20),
            reviewed_by="Dr. Elizabeth Frost",
        ),
    )

    repo._store[patient_001_history.id] = patient_001_history
    repo._store[patient_002_history.id] = patient_002_history


def seed_all(
    patient_repo: PatientRepository,
    practitioner_repo: PractitionerRepository,
    allergy_repo: AllergyIntoleranceRepository,
    medication_request_repo: MedicationRequestRepository,
    appointment_repo: AppointmentRepository,
    encounter_repo: EncounterRepository,
    visit_note_repo: VisitNoteRepository | None = None,
    imaging_study_repo: ImagingStudyRepository | None = None,
    vitals_repo: VitalSignRepository | None = None,
    social_family_history_repo: SocialFamilyHistoryRepository | None = None,
) -> None:
    """Seed all repositories with initial data."""
    seed_patients(patient_repo)
    seed_practitioners(practitioner_repo)
    seed_allergies(allergy_repo)
    seed_medication_requests(medication_request_repo)
    seed_appointments(appointment_repo, patient_repo)
    if visit_note_repo:
        seed_visit_notes(visit_note_repo)
    if imaging_study_repo:
        seed_imaging_studies(imaging_study_repo)
    if vitals_repo:
        seed_vitals(vitals_repo)
    if social_family_history_repo:
        seed_social_family_history(social_family_history_repo)
    # Encounters are created dynamically when appointments are started
    print("[DATA SEEDER] All repositories seeded with initial data")


# ============================================================================
# ASYNC SEEDING FOR POSTGRESQL
# ============================================================================
# These functions generate the same data as their sync counterparts
# but call await repo._seed() for async PostgreSQL repositories.


async def seed_patients_async(repo) -> None:
    """Seed patient data (async version for PostgreSQL)."""
    provider_ref = Reference.to("Practitioner", "provider-001", "Dr. Elizabeth Frost")

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
                Problem(
                    name="Essential hypertension",
                    icd10_code="I10",
                    onset_date=date(2020, 3, 15),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    severity=ProblemSeverity.WELL_CONTROLLED,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2020, 3, 15),
                ),
                Problem(
                    name="Type 2 diabetes mellitus without complications",
                    icd10_code="E11.9",
                    onset_date=date(2021, 6, 10),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    severity=ProblemSeverity.MODERATE,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2021, 6, 10),
                ),
                Problem(
                    name="Hyperlipidemia, unspecified",
                    icd10_code="E78.5",
                    onset_date=date(2022, 1, 20),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    severity=ProblemSeverity.MILD,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2022, 1, 20),
                ),
                Problem(
                    name="Obesity, unspecified",
                    icd10_code="E66.9",
                    onset_date=date(2019, 5, 1),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2019, 5, 1),
                ),
                Problem(
                    name="Acute upper respiratory infection",
                    icd10_code="J06.9",
                    onset_date=date.today() - timedelta(days=5),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.ACUTE,
                    severity=ProblemSeverity.MILD,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date.today() - timedelta(days=5),
                ),
            ],
            recent_vitals=RecentVitals(
                date="01/10/2025",
                blood_pressure="138/82",
                weight="156 lbs",
                temperature="98.4°F",
            ),
            allergy_review_status=AllergyReviewStatus(
                reviewed_at=datetime.now() - timedelta(days=30),
                reviewed_by=provider_ref,
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
                Problem(
                    name="Gastro-esophageal reflux disease without esophagitis",
                    icd10_code="K21.0",
                    onset_date=date(2019, 2, 14),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                ),
                Problem(
                    name="Generalized anxiety disorder",
                    icd10_code="F41.1",
                    onset_date=date(2020, 8, 5),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                ),
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
                Problem(
                    name="Mild persistent asthma, uncomplicated",
                    icd10_code="J45.30",
                    onset_date=date(2015, 4, 12),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                ),
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
                Problem(
                    name="Essential hypertension",
                    icd10_code="I10",
                    onset_date=date(2010, 7, 1),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    severity=ProblemSeverity.MODERATE,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2010, 7, 22),
                ),
                Problem(
                    name="Chronic pain syndrome",
                    icd10_code="G89.4",
                    onset_date=date(2018, 3, 1),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    severity=ProblemSeverity.SEVERE,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2018, 3, 8),
                    is_critical=True,
                ),
                Problem(
                    name="Lumbar spinal stenosis",
                    icd10_code="M48.06",
                    onset_date=date(2017, 5, 1),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    severity=ProblemSeverity.MODERATE,
                    documenting_provider="Dr. Elizabeth Frost",
                    documented_date=date(2017, 5, 3),
                ),
            ],
            recent_vitals=RecentVitals(
                date="01/12/2025",
                blood_pressure="142/88",
                weight="210 lbs",
                temperature="98.6°F",
            ),
            allergy_review_status=AllergyReviewStatus(
                reviewed_at=datetime.now() - timedelta(days=400),
                reviewed_by=provider_ref,
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
                Problem(
                    name="Atrial fibrillation, unspecified",
                    icd10_code="I48.91",
                    onset_date=date(2018, 9, 5),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                ),
                Problem(
                    name="Essential hypertension",
                    icd10_code="I10",
                    onset_date=date(2012, 4, 18),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                ),
                Problem(
                    name="Heart failure, unspecified",
                    icd10_code="I50.9",
                    onset_date=date(2020, 1, 12),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                    severity=ProblemSeverity.MODERATE,
                    is_critical=True,
                ),
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
                Problem(
                    name="Atrial fibrillation, unspecified",
                    icd10_code="I48.91",
                    onset_date=date(2019, 3, 28),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                ),
                Problem(
                    name="Essential hypertension",
                    icd10_code="I10",
                    onset_date=date(2015, 6, 15),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                ),
                Problem(
                    name="Major depressive disorder, single episode, moderate",
                    icd10_code="F32.1",
                    onset_date=date(2020, 10, 5),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                ),
                Problem(
                    name="Hyperlipidemia, unspecified",
                    icd10_code="E78.5",
                    onset_date=date(2017, 8, 22),
                    status=ProblemStatus.ACTIVE,
                    priority=ProblemPriority.CHRONIC,
                ),
            ],
            recent_vitals=RecentVitals(
                date="01/05/2025",
                blood_pressure="132/80",
                weight="165 lbs",
                temperature="98.4°F",
            ),
        ),
    ]
    await repo._seed(patients)


async def seed_practitioners_async(repo) -> None:
    """Seed practitioner data (async version for PostgreSQL)."""
    practitioners = [
        Practitioner(
            id="provider-001",
            name=HumanName(family="Frost", given=["Elizabeth"]),
            identifiers=[Identifier(system="http://hl7.org/fhir/sid/us-npi", value="1234567890")],
            qualifications=[
                CodeableConcept(code="MD", display="Doctor of Medicine"),
                CodeableConcept(code="IM", display="Internal Medicine"),
            ],
        ),
        Practitioner(
            id="provider-002",
            name=HumanName(family="Chen", given=["Emily"]),
            identifiers=[Identifier(system="http://hl7.org/fhir/sid/us-npi", value="0987654321")],
            qualifications=[
                CodeableConcept(code="MD", display="Doctor of Medicine"),
                CodeableConcept(code="FM", display="Family Medicine"),
            ],
        ),
    ]
    await repo._seed(practitioners)


async def seed_allergies_async(repo) -> None:
    """Seed allergy data (async version for PostgreSQL)."""
    provider_ref = Reference.to("Practitioner", "provider-001", "Dr. Elizabeth Frost")

    allergies = [
        AllergyIntolerance(
            id="allergy-1",
            patient=Reference.to("Patient", "patient-001", "Sarah Johnson"),
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            reactions=[
                AllergyReaction(manifestation="Anaphylaxis", severity="severe", description="Immediate onset within 10 minutes"),
                AllergyReaction(manifestation="Hives", severity="moderate", description="Developed after initial anaphylaxis treatment"),
            ],
            recorded_date=datetime(2020, 1, 15),
            last_updated=datetime(2024, 6, 10),
            recorder=provider_ref,
            notes="Patient carries EpiPen. Avoid all penicillin-class antibiotics including amoxicillin.",
        ),
        AllergyIntolerance(
            id="allergy-2",
            patient=Reference.to("Patient", "patient-001", "Sarah Johnson"),
            code=CodeableConcept(code="sulfa", display="Sulfa"),
            reactions=[AllergyReaction(manifestation="Rash", severity="moderate")],
            recorded_date=datetime(2019, 6, 20),
            last_updated=datetime(2023, 11, 5),
            recorder=provider_ref,
            notes="Cross-reactivity with sulfasalazine noted.",
        ),
        AllergyIntolerance(
            id="allergy-6",
            patient=Reference.to("Patient", "patient-001", "Sarah Johnson"),
            code=CodeableConcept(code="peanuts", display="Peanuts"),
            category=AllergyCategory.FOOD,
            reactions=[
                AllergyReaction(manifestation="Anaphylaxis", severity="severe", description="Throat swelling, difficulty breathing"),
            ],
            recorded_date=datetime(2018, 3, 10),
            last_updated=datetime(2024, 1, 15),
            recorder=provider_ref,
            notes="Patient carries EpiPen. Avoid all tree nuts as precaution.",
        ),
        AllergyIntolerance(
            id="allergy-3",
            patient=Reference.to("Patient", "patient-002", "Michael Chen"),
            code=CodeableConcept(code="aspirin", display="Aspirin"),
            reactions=[AllergyReaction(manifestation="Bronchospasm", severity="severe")],
            recorded_date=datetime(2018, 3, 10),
            last_updated=datetime(2024, 2, 20),
            recorder=provider_ref,
            notes="Aspirin-exacerbated respiratory disease. Avoid all NSAIDs.",
        ),
    ]
    await repo._seed(allergies)


async def seed_medication_requests_async(repo) -> None:
    """Seed medication request data (async version for PostgreSQL)."""
    medications = [
        MedicationRequest(
            id="medrx-001",
            medication=CodeableConcept(code="lisinopril", display="Lisinopril"),
            dosage_instruction=[Dosage(text="10mg daily", dose="10mg", frequency="once daily", route="oral")],
            subject=Reference(reference="Patient/patient-001"),
            requester=Reference(reference="Practitioner/provider-001", display="Dr. Elizabeth Frost"),
            status=MedicationRequestStatus.ACTIVE,
            form=MedicationForm.TABLET,
            intent=MedicationRequestIntent.ORDER,
            authored_on=datetime(2023, 1, 15),
        ),
        MedicationRequest(
            id="medrx-002",
            medication=CodeableConcept(code="metformin", display="Metformin"),
            dosage_instruction=[Dosage(text="500mg twice daily", dose="500mg", frequency="twice daily", route="oral")],
            subject=Reference(reference="Patient/patient-001"),
            requester=Reference(reference="Practitioner/provider-001", display="Dr. Elizabeth Frost"),
            status=MedicationRequestStatus.ACTIVE,
            form=MedicationForm.TABLET,
            intent=MedicationRequestIntent.ORDER,
            authored_on=datetime(2023, 2, 1),
        ),
        MedicationRequest(
            id="medrx-003",
            medication=CodeableConcept(code="albuterol", display="Albuterol"),
            dosage_instruction=[Dosage(text="90mcg as needed", dose="2 puffs", frequency="as needed", route="inhalation", as_needed=True)],
            subject=Reference(reference="Patient/patient-002"),
            requester=Reference(reference="Practitioner/provider-002", display="Dr. Emily Chen"),
            status=MedicationRequestStatus.ACTIVE,
            form=MedicationForm.INHALER,
            intent=MedicationRequestIntent.ORDER,
            authored_on=datetime(2023, 3, 10),
        ),
    ]
    await repo._seed(medications)


async def seed_appointments_async(appointment_repo, patient_repo) -> None:
    """Seed appointment data (async version for PostgreSQL)."""
    today = date.today()
    base_time = datetime.combine(today, datetime.min.time()).replace(hour=8, minute=0)
    now = datetime.now()

    templates = [
        {
            "patient_id": "patient-001",
            "time_offset": -240,  # 4:00 AM (past)
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
                        actor=Reference.to("Practitioner", "provider-002", "Dr. Emily Chen"),
                        type="practitioner",
                    ),
                ],
                flags=template["flags"],
                is_double_booked=template.get("is_double_booked", False),
            )
        )

    await appointment_repo._seed(appointments)


async def seed_visit_notes_async(repo) -> None:
    """Seed visit note data (async version for PostgreSQL)."""
    now = datetime.utcnow()

    visit_notes = [
        # Patient 001 - Sarah Johnson - Recent visits
        VisitNote(
            id="v1",
            encounter=Reference.to("Encounter", "enc-001"),
            subject=Reference.to("Patient", "patient-001"),
            visit_type="annual_physical",
            status="completed",
            date=now - timedelta(days=35),
            chief_complaint="Annual wellness exam",
            has_follow_up_required=True,
            follow_up_summary="Schedule colonoscopy screening (due). Recheck HbA1c in 3 months.",
            location="Livny Health Clinic - Main",
            duration=45,
            provider=VisitProvider(
                id="provider-001",
                name="Dr. Emily Chen",
                role="Attending",
                specialty="Internal Medicine",
            ),
            diagnoses=[
                VisitDiagnosis(code="Z00.00", description="Encounter for general adult medical examination without abnormal findings", is_primary=True),
                VisitDiagnosis(code="E11.9", description="Type 2 diabetes mellitus without complications", is_primary=False),
            ],
            soap_note=SOAPNote(
                subjective="Patient presents for annual wellness exam. Reports feeling generally well. Denies chest pain, shortness of breath, or palpitations. Diabetes well-controlled with current regimen. Occasional mild headaches, relieved with acetaminophen. Sleep quality good, 7-8 hours nightly. No recent weight changes.",
                objective="General: Well-appearing, no acute distress. HEENT: PERRLA, oropharynx clear. CV: RRR, no murmurs. Lungs: CTA bilaterally. Abdomen: Soft, non-tender, no organomegaly. Extremities: No edema, pulses 2+ bilaterally. Skin: No rashes or lesions. Neuro: A&O x3, cranial nerves intact.",
                assessment="1. Type 2 diabetes mellitus - well controlled on current regimen\n2. Essential hypertension - at goal\n3. Hyperlipidemia - stable on statin therapy\n4. Health maintenance up to date",
                plan="1. Continue current medications\n2. HbA1c in 3 months\n3. Lipid panel in 6 months\n4. Schedule colonoscopy (due for screening)\n5. Flu vaccine administered today\n6. Return in 6 months or sooner if concerns",
            ),
            vitals=VisitVitals(
                blood_pressure_systolic=132,
                blood_pressure_diastolic=78,
                heart_rate=72,
                temperature=98.4,
                temperature_unit="F",
                weight=156,
                weight_unit="lbs",
                oxygen_saturation=98,
                respiratory_rate=16,
                recorded_at=now - timedelta(days=35),
            ),
            medications=[
                VisitMedication(id="vm-1", name="Influenza Vaccine", dosage="0.5mL", frequency="once", action=MedicationAction.PRESCRIBED, route="IM", instructions="Administered left deltoid"),
            ],
            orders=[
                VisitOrder(id="ord-1", order_type=OrderType.LAB, name="HbA1c", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=35), completed_at=now - timedelta(days=33), result="6.8%", priority=OrderPriority.ROUTINE),
                VisitOrder(id="ord-2", order_type=OrderType.LAB, name="Lipid Panel", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=35), completed_at=now - timedelta(days=33), result="TC 210, LDL 135, HDL 55, TG 150", priority=OrderPriority.ROUTINE),
                VisitOrder(id="ord-3", order_type=OrderType.REFERRAL, name="Colonoscopy - GI", status=OrderStatus.PENDING, ordered_at=now - timedelta(days=35), priority=OrderPriority.ROUTINE),
            ],
        ),
        VisitNote(
            id="v2",
            encounter=Reference.to("Encounter", "enc-002"),
            subject=Reference.to("Patient", "patient-001"),
            visit_type="follow_up",
            status="completed",
            date=now - timedelta(days=90),
            chief_complaint="Diabetes follow-up, medication review",
            location="Livny Health Clinic - Main",
            duration=30,
            has_follow_up_required=True,
            follow_up_summary="Recheck A1C in 3 months. Annual eye exam referral placed.",
            provider=VisitProvider(
                id="provider-001",
                name="Dr. Emily Chen",
                role="Attending",
                specialty="Internal Medicine",
            ),
            diagnoses=[
                VisitDiagnosis(code="E11.65", description="Type 2 diabetes mellitus with hyperglycemia", is_primary=True),
            ],
            soap_note=SOAPNote(
                subjective="Patient returns for diabetes follow-up. Reports good compliance with metformin. Checking blood sugars 2-3x weekly, fasting readings 110-130. No hypoglycemic episodes. Denies polyuria, polydipsia, or blurred vision. Diet adherence fair - admits to occasional sweets.",
                objective="General: NAD. Weight stable. CV: RRR. Extremities: No ulcers, sensation intact to monofilament bilateral feet. Skin: No concerning lesions.",
                assessment="Type 2 DM with recent hyperglycemia, improving with lifestyle modifications. A1C elevated at 7.2% (down from 7.8%).",
                plan="1. Continue metformin 500mg BID\n2. Reinforce dietary counseling - limit simple carbohydrates\n3. Increase home glucose monitoring to daily fasting\n4. Recheck A1C in 3 months\n5. Annual eye exam due - referral placed\n6. Follow up in 3 months",
            ),
            vitals=VisitVitals(
                blood_pressure_systolic=138,
                blood_pressure_diastolic=82,
                heart_rate=76,
                temperature=98.6,
                weight=158,
                weight_unit="lbs",
                oxygen_saturation=97,
                recorded_at=now - timedelta(days=90),
            ),
            orders=[
                VisitOrder(id="ord-4", order_type=OrderType.LAB, name="HbA1c", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=90), completed_at=now - timedelta(days=88), result="7.2%", priority=OrderPriority.ROUTINE),
                VisitOrder(id="ord-5", order_type=OrderType.REFERRAL, name="Ophthalmology - Diabetic Eye Exam", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=90), completed_at=now - timedelta(days=60), result="No diabetic retinopathy", priority=OrderPriority.ROUTINE),
            ],
        ),
        VisitNote(
            id="v3",
            encounter=Reference.to("Encounter", "enc-003"),
            subject=Reference.to("Patient", "patient-001"),
            visit_type="urgent_care",
            status="completed",
            date=now - timedelta(days=130),
            chief_complaint="Acute sinusitis symptoms x 5 days",
            location="Livny Health Urgent Care",
            duration=20,
            provider=VisitProvider(
                id="provider-002",
                name="Dr. Michael Torres",
                role="Attending",
                specialty="Family Medicine",
            ),
            diagnoses=[
                VisitDiagnosis(code="J01.90", description="Acute sinusitis, unspecified", is_primary=True),
            ],
            soap_note=SOAPNote(
                subjective="Patient presents with 5-day history of nasal congestion, facial pressure/pain over maxillary sinuses bilaterally, thick yellow-green nasal discharge, and low-grade fever (100.2°F at home). Tried OTC decongestants with minimal relief. Denies severe headache, vision changes, or neck stiffness. Has known penicillin allergy (anaphylaxis).",
                objective="T 99.8°F. General: Mild distress due to congestion. HEENT: Tenderness to palpation over maxillary sinuses bilaterally, nasal mucosa erythematous with purulent discharge, posterior pharynx with postnasal drip, TMs clear. Lungs: CTA. No lymphadenopathy.",
                assessment="Acute bacterial sinusitis, likely secondary to viral URI. Patient has penicillin allergy precluding amoxicillin use.",
                plan="1. Azithromycin 500mg day 1, then 250mg days 2-5 (Z-pack) - avoiding penicillin class due to allergy\n2. Nasal saline irrigation TID\n3. Sudafed 30mg q6h PRN congestion\n4. Increase fluid intake\n5. Return if worsening, high fever, or no improvement in 72 hours\n6. Follow up with PCP if symptoms persist beyond 10 days",
            ),
            vitals=VisitVitals(
                blood_pressure_systolic=128,
                blood_pressure_diastolic=76,
                heart_rate=84,
                temperature=99.8,
                weight=155,
                weight_unit="lbs",
                oxygen_saturation=98,
                recorded_at=now - timedelta(days=130),
            ),
            medications=[
                VisitMedication(id="vm-2", name="Azithromycin (Z-pack)", dosage="250mg", frequency="daily x 5 days", action=MedicationAction.PRESCRIBED, route="oral", instructions="500mg day 1, then 250mg days 2-5"),
            ],
            notes="Prescribed azithromycin due to penicillin allergy. Return if symptoms worsen.",
        ),
        VisitNote(
            id="v4",
            encounter=Reference.to("Encounter", "enc-004"),
            subject=Reference.to("Patient", "patient-001"),
            visit_type="telehealth",
            status="completed",
            date=now - timedelta(days=185),
            chief_complaint="Blood pressure medication refill",
            location=None,
            duration=15,
            provider=VisitProvider(
                id="provider-001",
                name="Dr. Emily Chen",
                role="Attending",
                specialty="Internal Medicine",
            ),
            diagnoses=[
                VisitDiagnosis(code="I10", description="Essential (primary) hypertension", is_primary=True),
            ],
            soap_note=SOAPNote(
                subjective="Telehealth visit for BP medication refill. Patient reports home BP readings averaging 130-135/80-85. Taking lisinopril 10mg daily as prescribed. No dizziness, cough, or swelling. No chest pain or shortness of breath.",
                objective="Patient appears well via video. Alert and oriented. No visible distress. Patient reports home BP today 134/82.",
                assessment="Essential hypertension, reasonably controlled on current regimen.",
                plan="1. Continue lisinopril 10mg daily\n2. Refill authorized - 90-day supply with 3 refills\n3. Continue home BP monitoring\n4. Labs due at next in-person visit\n5. Follow up in 6 months or sooner if BP consistently elevated",
            ),
            medications=[
                VisitMedication(id="vm-3", name="Lisinopril", dosage="10mg", frequency="daily", action=MedicationAction.CONTINUED, route="oral"),
            ],
        ),
        VisitNote(
            id="v5",
            encounter=Reference.to("Encounter", "enc-005"),
            subject=Reference.to("Patient", "patient-001"),
            visit_type="lab_only",
            status="completed",
            date=now - timedelta(days=250),
            chief_complaint="Routine lab work - HbA1c, lipid panel",
            location="Livny Health Lab Services",
            duration=10,
            provider=VisitProvider(
                id="lab-services",
                name="Lab Services",
                role="Laboratory",
            ),
            diagnoses=[
                VisitDiagnosis(code="Z13.1", description="Encounter for screening for diabetes mellitus", is_primary=True),
            ],
            soap_note=SOAPNote(
                subjective="Patient presents for scheduled lab work. Fasting since midnight. No acute complaints.",
                objective="Venipuncture performed, left antecubital fossa. Hemostasis achieved.",
                assessment="Lab draw completed without complication.",
                plan="Results to be reviewed by PCP and communicated to patient.",
            ),
            vitals=VisitVitals(
                blood_pressure_systolic=130,
                blood_pressure_diastolic=80,
                heart_rate=70,
                recorded_at=now - timedelta(days=250),
            ),
            orders=[
                VisitOrder(id="ord-6", order_type=OrderType.LAB, name="HbA1c", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=250), completed_at=now - timedelta(days=249), result="7.8%", priority=OrderPriority.ROUTINE),
                VisitOrder(id="ord-7", order_type=OrderType.LAB, name="Lipid Panel", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=250), completed_at=now - timedelta(days=249), result="TC 225, LDL 142, HDL 48, TG 165", priority=OrderPriority.ROUTINE),
            ],
        ),
        VisitNote(
            id="v6",
            encounter=Reference.to("Encounter", "enc-006"),
            subject=Reference.to("Patient", "patient-001"),
            visit_type="office_visit",
            status="completed",
            date=now - timedelta(days=300),
            chief_complaint="Follow-up hypertension, diabetes management",
            location="Livny Health Clinic - Main",
            duration=30,
            has_critical_findings=True,
            critical_findings_summary="BP significantly elevated at 148/92. Weight gain 4 lbs. Trace ankle edema. Started HCTZ.",
            has_follow_up_required=True,
            follow_up_summary="Follow up in 1 month to recheck BP. Labs in 2 weeks for electrolytes.",
            provider=VisitProvider(
                id="provider-001",
                name="Dr. Emily Chen",
                role="Attending",
                specialty="Internal Medicine",
            ),
            diagnoses=[
                VisitDiagnosis(code="I10", description="Essential (primary) hypertension", is_primary=True),
                VisitDiagnosis(code="E11.9", description="Type 2 diabetes mellitus without complications", is_primary=False),
            ],
            soap_note=SOAPNote(
                subjective="Patient here for chronic disease management. BP has been elevated at home, averaging 145/90. Some dietary indiscretions over holidays. Diabetes: checking sugars sporadically, fasting 130-150. No hypoglycemia. No chest pain, SOB, edema, or vision changes.",
                objective="BP 148/92 (elevated). Weight up 4 lbs since last visit. CV: RRR, no murmurs. Lungs: Clear. Extremities: Trace bilateral ankle edema.",
                assessment="1. Hypertension - suboptimally controlled\n2. Type 2 DM - fair control, needs reinforcement\n3. Weight gain - likely contributing to above",
                plan="1. Add HCTZ 25mg daily for better BP control\n2. Continue metformin, lisinopril at current doses\n3. Dietary counseling - DASH diet handout provided\n4. Increase physical activity - goal 150 min/week\n5. Labs in 2 weeks to check electrolytes\n6. Follow up in 1 month",
            ),
            vitals=VisitVitals(
                blood_pressure_systolic=148,
                blood_pressure_diastolic=92,
                heart_rate=78,
                temperature=98.4,
                weight=160,
                weight_unit="lbs",
                oxygen_saturation=97,
                recorded_at=now - timedelta(days=300),
            ),
            medications=[
                VisitMedication(id="vm-4", name="Hydrochlorothiazide", dosage="25mg", frequency="daily", action=MedicationAction.PRESCRIBED, route="oral", instructions="Take in the morning"),
            ],
            orders=[
                VisitOrder(id="ord-8", order_type=OrderType.LAB, name="BMP (Basic Metabolic Panel)", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=300), completed_at=now - timedelta(days=285), result="Na 140, K 4.2, Cr 0.9, all WNL", priority=OrderPriority.ROUTINE),
            ],
        ),
        VisitNote(
            id="v7",
            encounter=Reference.to("Encounter", "enc-007"),
            subject=Reference.to("Patient", "patient-001"),
            visit_type="procedure",
            status="completed",
            date=now - timedelta(days=430),
            chief_complaint="Colonoscopy - routine screening",
            location="Livny Health Surgery Center",
            duration=60,
            has_critical_findings=True,
            critical_findings_summary="Two tubular adenomas found and removed. Low-grade dysplasia. Requires surveillance colonoscopy in 5 years.",
            has_follow_up_required=True,
            follow_up_summary="Repeat colonoscopy in 5 years due to adenomatous polyps.",
            provider=VisitProvider(
                id="provider-004",
                name="Dr. Sarah Kim",
                role="Attending",
                specialty="Gastroenterology",
            ),
            diagnoses=[
                VisitDiagnosis(code="Z12.11", description="Encounter for screening for malignant neoplasm of colon", is_primary=True),
                VisitDiagnosis(code="K63.5", description="Polyp of colon", is_primary=False),
            ],
            soap_note=SOAPNote(
                subjective="Patient presents for routine screening colonoscopy. Age-appropriate screening. No family history of colon cancer. No recent GI symptoms, bleeding, or weight loss. Completed bowel prep without difficulty.",
                objective="Procedure: Colonoscopy performed under moderate sedation (midazolam 3mg, fentanyl 75mcg). Scope advanced to cecum. Cecal landmarks identified. Two small sessile polyps (3mm and 4mm) identified in sigmoid colon and removed via cold snare polypectomy. No complications. Patient tolerated procedure well.",
                assessment="1. Screening colonoscopy - complete to cecum\n2. Two small sigmoid polyps - removed, sent to pathology",
                plan="1. Await pathology results (typically 5-7 days)\n2. If tubular adenomas: repeat colonoscopy in 5 years\n3. If hyperplastic only: repeat in 10 years\n4. Resume regular diet today\n5. No driving for 24 hours due to sedation\n6. Call if fever, severe pain, or bleeding",
            ),
            vitals=VisitVitals(
                blood_pressure_systolic=125,
                blood_pressure_diastolic=75,
                heart_rate=68,
                oxygen_saturation=99,
                recorded_at=now - timedelta(days=430),
            ),
            orders=[
                VisitOrder(id="ord-9", order_type=OrderType.PROCEDURE, name="Colonoscopy with polypectomy", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=430), completed_at=now - timedelta(days=430), priority=OrderPriority.ROUTINE),
                VisitOrder(id="ord-10", order_type=OrderType.LAB, name="Pathology - Colon polyps", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=430), completed_at=now - timedelta(days=423), result="Two tubular adenomas, low-grade dysplasia. Margins clear.", priority=OrderPriority.ROUTINE),
            ],
            notes="Two small polyps removed and sent to pathology. Recommend follow-up colonoscopy in 5 years.",
        ),
        VisitNote(
            id="v8",
            encounter=Reference.to("Encounter", "enc-008"),
            subject=Reference.to("Patient", "patient-001"),
            visit_type="emergency",
            status="completed",
            date=now - timedelta(days=530),
            chief_complaint="Chest pain, shortness of breath",
            location="Livny Health Emergency Department",
            duration=180,
            has_critical_findings=True,
            critical_findings_summary="Chest pain with negative cardiac workup. Anxiety/panic attack likely. Follow up with PCP required.",
            has_follow_up_required=True,
            follow_up_summary="Follow up with PCP within 1 week. Consider outpatient cardiology referral if symptoms recur.",
            provider=VisitProvider(
                id="provider-005",
                name="Dr. James Wilson",
                role="Attending",
                specialty="Emergency Medicine",
            ),
            diagnoses=[
                VisitDiagnosis(code="R07.9", description="Chest pain, unspecified", is_primary=True),
                VisitDiagnosis(code="R06.02", description="Shortness of breath", is_primary=False),
                VisitDiagnosis(code="F41.9", description="Anxiety disorder, unspecified", is_primary=False),
            ],
            soap_note=SOAPNote(
                subjective="45 y/o female presents to ED with acute onset chest tightness and shortness of breath x 2 hours. Describes pressure-like sensation across chest, non-radiating. Associated with palpitations and feeling of impending doom. Symptoms began while at work during stressful meeting. No prior cardiac history. Denies diaphoresis, nausea, or arm/jaw pain. History of occasional anxiety. No recent illness, travel, or immobilization.",
                objective="T 98.2, HR 102, BP 145/88, RR 22, SpO2 98% RA. General: Anxious-appearing, mild distress. CV: Tachycardic, regular rhythm, no murmurs/rubs/gallops. Lungs: CTA bilaterally, no wheezes. Chest wall non-tender. Extremities: No edema, calves non-tender.\n\nEKG: Sinus tachycardia, no ST changes, no ischemic changes.\nTroponin: <0.01 (negative) x2 at 0h and 3h\nD-dimer: Normal\nCXR: No acute cardiopulmonary process\nBMP: Normal",
                assessment="Chest pain with negative cardiac workup. Clinical presentation most consistent with acute anxiety/panic attack. Low suspicion for ACS given negative troponins, normal EKG, and atypical presentation. PE ruled out with normal D-dimer and low pretest probability.",
                plan="1. Cardiac workup negative - reassurance provided\n2. Discussed anxiety as likely etiology\n3. Lorazepam 0.5mg given in ED with symptom resolution\n4. Discharge home in stable condition\n5. Follow up with PCP within 1 week\n6. Consider outpatient cardiology referral if symptoms recur\n7. Discussed stress management techniques\n8. Return precautions reviewed: return immediately if chest pain recurs, worsens, or associated with diaphoresis/radiation",
            ),
            vitals=VisitVitals(
                blood_pressure_systolic=145,
                blood_pressure_diastolic=88,
                heart_rate=102,
                temperature=98.2,
                oxygen_saturation=98,
                respiratory_rate=22,
                recorded_at=now - timedelta(days=530),
            ),
            medications=[
                VisitMedication(id="vm-5", name="Lorazepam", dosage="0.5mg", frequency="once", action=MedicationAction.PRESCRIBED, route="oral", instructions="Given in ED for acute anxiety"),
            ],
            orders=[
                VisitOrder(id="ord-11", order_type=OrderType.LAB, name="Troponin I (serial)", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=530), completed_at=now - timedelta(days=530), result="<0.01 ng/mL (negative x2)", priority=OrderPriority.STAT),
                VisitOrder(id="ord-12", order_type=OrderType.LAB, name="D-dimer", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=530), completed_at=now - timedelta(days=530), result="0.3 (normal <0.5)", priority=OrderPriority.STAT),
                VisitOrder(id="ord-13", order_type=OrderType.LAB, name="BMP", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=530), completed_at=now - timedelta(days=530), result="All values within normal limits", priority=OrderPriority.STAT),
                VisitOrder(id="ord-14", order_type=OrderType.IMAGING, name="Chest X-ray", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=530), completed_at=now - timedelta(days=530), result="No acute cardiopulmonary process", priority=OrderPriority.STAT),
                VisitOrder(id="ord-15", order_type=OrderType.PROCEDURE, name="EKG", status=OrderStatus.COMPLETED, ordered_at=now - timedelta(days=530), completed_at=now - timedelta(days=530), result="Sinus tachycardia, no ischemic changes", priority=OrderPriority.STAT),
            ],
            notes="Cardiac workup negative. Symptoms attributed to anxiety/panic attack. Discharged with PCP follow-up.",
        ),
    ]
    await repo._seed(visit_notes)


async def seed_imaging_studies_async(repo) -> None:
    """Seed imaging study data (async version for PostgreSQL)."""
    imaging_studies = [
        ImagingStudy(
            id="img-001",
            patient_id="patient-001",
            study_date=datetime(2024, 1, 10, 14, 30),
            modality="XR",
            modality_name="Chest X-Ray PA and Lateral",
            report_status="final",
            body_part="Chest",
            reading_radiologist="Dr. James Wilson",
            report=RadiologyReport(
                clinical_indication="Annual physical exam",
                technique="PA and lateral views of the chest",
                findings="Lungs are clear bilaterally. No pleural effusions. Heart size is normal.",
                impression="Normal chest radiograph.",
            ),
        ),
    ]
    await repo._seed(imaging_studies)


async def seed_vitals_async(repo) -> None:
    """Seed vital signs data (async version for PostgreSQL)."""
    import random

    patient_id = "patient-001"
    today = datetime.now()

    base_values = {
        "blood_pressure_systolic": 132,
        "blood_pressure_diastolic": 78,
        "heart_rate": 72,
        "temperature": 98.4,
        "weight": 156,
        "oxygen_saturation": 98,
        "respiratory_rate": 16,
        "height": 65,
    }

    units = {
        "blood_pressure_systolic": "mmHg",
        "blood_pressure_diastolic": "mmHg",
        "heart_rate": "bpm",
        "temperature": "°F",
        "weight": "lbs",
        "oxygen_saturation": "%",
        "respiratory_rate": "breaths/min",
        "height": "in",
    }

    vitals = []
    vital_id = 0

    # Height measurement
    vitals.append(VitalSign(
        id=f"vital-{vital_id}",
        vital_type="height",
        value=base_values["height"],
        unit=units["height"],
        status="normal",
        subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
        recorded_at=today - timedelta(days=365),
        recorded_by="MA Thompson",
        location="Livny Health Clinic - Main",
    ))
    vital_id += 1

    # Generate 18 months of data
    for months_ago in range(18, -1, -1):
        days_ago = months_ago * 30 + random.randint(-5, 5)
        if days_ago < 0:
            days_ago = 0

        recorded_at = today - timedelta(days=days_ago)

        # BP systolic
        bp_sys_trend = 1 + (months_ago * 0.005)
        bp_sys_value = round(base_values["blood_pressure_systolic"] * bp_sys_trend + random.uniform(-5, 5))
        status = VitalSign.determine_status("blood_pressure_systolic", bp_sys_value)
        vitals.append(VitalSign(
            id=f"vital-{vital_id}",
            vital_type="blood_pressure_systolic",
            value=bp_sys_value,
            unit=units["blood_pressure_systolic"],
            status=status,
            subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
            recorded_at=recorded_at,
            recorded_by="Dr. Elizabeth Frost",
            location="Livny Health Clinic - Main",
        ))
        vital_id += 1

        # BP diastolic
        bp_dia_trend = 1 + (months_ago * 0.004)
        bp_dia_value = round(base_values["blood_pressure_diastolic"] * bp_dia_trend + random.uniform(-3, 3))
        status = VitalSign.determine_status("blood_pressure_diastolic", bp_dia_value)
        vitals.append(VitalSign(
            id=f"vital-{vital_id}",
            vital_type="blood_pressure_diastolic",
            value=bp_dia_value,
            unit=units["blood_pressure_diastolic"],
            status=status,
            subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
            recorded_at=recorded_at,
            recorded_by="Dr. Elizabeth Frost",
            location="Livny Health Clinic - Main",
        ))
        vital_id += 1

        # Heart rate
        hr_value = round(base_values["heart_rate"] + random.uniform(-8, 8))
        status = VitalSign.determine_status("heart_rate", hr_value)
        vitals.append(VitalSign(
            id=f"vital-{vital_id}",
            vital_type="heart_rate",
            value=hr_value,
            unit=units["heart_rate"],
            status=status,
            subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
            recorded_at=recorded_at,
            recorded_by="Dr. Elizabeth Frost",
            location="Livny Health Clinic - Main",
        ))
        vital_id += 1

        # Weight
        weight_trend_factor = 1 + (months_ago * 0.003)
        weight_value = round(base_values["weight"] * weight_trend_factor + random.uniform(-2, 2), 1)
        status = VitalSign.determine_status("weight", weight_value)
        vitals.append(VitalSign(
            id=f"vital-{vital_id}",
            vital_type="weight",
            value=weight_value,
            unit=units["weight"],
            status=status,
            subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
            recorded_at=recorded_at,
            recorded_by="Dr. Elizabeth Frost",
            location="Livny Health Clinic - Main",
        ))
        vital_id += 1

    # Add critical BP reading
    recent_date = today - timedelta(hours=4)
    vitals.append(VitalSign(
        id=f"vital-{vital_id}",
        vital_type="blood_pressure_systolic",
        value=185,
        unit="mmHg",
        status="critical",
        subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
        recorded_at=recent_date,
        recorded_by="Dr. Emily Chen",
        location="Livny Health Clinic - Main",
    ))
    vital_id += 1

    vitals.append(VitalSign(
        id=f"vital-{vital_id}",
        vital_type="blood_pressure_diastolic",
        value=120,
        unit="mmHg",
        status="critical",
        subject=Reference.to("Patient", patient_id, "Sarah Johnson"),
        recorded_at=recent_date,
        recorded_by="Dr. Emily Chen",
        location="Livny Health Clinic - Main",
    ))

    await repo._seed(vitals)


async def seed_social_family_history_async(repo) -> None:
    """Seed social and family history data (async version for PostgreSQL)."""
    histories = [
        SocialFamilyHistory(
            id="sfh-001",
            subject=Reference.to("Patient", "patient-001", "Sarah Johnson"),
            social_history=SocialHistory(
                smoking=SmokingHistory(
                    status="former",
                    pack_years=5,
                    quit_date=date(2015, 6, 1),
                ),
                alcohol=AlcoholHistory(
                    use_level="occasional",
                    drinks_per_week=2,
                ),
                occupation="Software Engineer",
                marital_status="married",
                last_reviewed=datetime(2024, 10, 20),
                reviewed_by="Dr. Elizabeth Frost",
            ),
            family_history=FamilyHistory(
                family_members=[
                    FamilyMember(
                        id="fm-001",
                        relative_type="father",
                        conditions=[
                            FamilyMemberCondition(
                                condition_name="Type 2 diabetes",
                                age_at_onset=55,
                            ),
                            FamilyMemberCondition(
                                condition_name="Hypertension",
                                age_at_onset=50,
                            ),
                        ],
                    ),
                    FamilyMember(
                        id="fm-002",
                        relative_type="mother",
                        conditions=[
                            FamilyMemberCondition(
                                condition_name="Breast cancer",
                                age_at_onset=62,
                            ),
                        ],
                    ),
                ],
            ),
        ),
        SocialFamilyHistory(
            id="sfh-002",
            subject=Reference.to("Patient", "patient-002", "Michael Chen"),
            social_history=SocialHistory(
                smoking=SmokingHistory(status="never"),
                alcohol=AlcoholHistory(use_level="none"),
                occupation="Teacher",
                marital_status="single",
            ),
            family_history=FamilyHistory(
                family_members=[
                    FamilyMember(
                        id="fm-003",
                        relative_type="mother",
                        conditions=[
                            FamilyMemberCondition(
                                condition_name="Asthma",
                                age_at_onset=30,
                            ),
                        ],
                    ),
                ],
            ),
        ),
    ]
    await repo._seed(histories)


async def seed_lab_results_async(repo) -> None:
    """Seed lab result data for PostgreSQL."""
    today = datetime.now()
    patient_id = "patient-001"

    lab_results = []

    # Glucose history (showing improvement then slight increase)
    glucose_history = [
        ("130", "abnormal", 365, True, "dr-smith", 360),
        ("125", "abnormal", 300, True, "dr-smith", 295),
        ("118", "abnormal", 240, True, "dr-jones", 235),
        ("110", "abnormal", 180, True, "dr-smith", 175),
        ("105", "normal", 120, True, "dr-smith", 115),
        ("98", "normal", 14, True, "dr-smith", 13),
    ]

    for i, (value, status, days_ago, acked, acked_by, acked_days_ago) in enumerate(glucose_history):
        collection_date = today - timedelta(days=days_ago)
        lab_results.append(LabResult(
            id=f"glucose-{i}",
            test_name="Glucose",
            test_code="2339-0",
            value=value,
            unit="mg/dL",
            reference_range="70-100",
            status=status,
            subject=Reference(reference=f"Patient/{patient_id}"),
            collection_date=collection_date,
            performing_lab="Quest Diagnostics",
            panel_id="bmp" if days_ago <= 180 else None,
            last_updated=collection_date + timedelta(hours=2),
            acknowledged=acked,
            acknowledged_by=acked_by if acked else None,
            acknowledged_at=today - timedelta(days=acked_days_ago) if acked else None,
        ))

    # Creatinine history (showing worsening trend)
    creatinine_history = [
        ("0.9", "normal", 365, True, "dr-smith", 360),
        ("1.0", "normal", 300, True, "dr-smith", 295),
        ("1.1", "normal", 240, True, "dr-jones", 235),
        ("1.1", "normal", 180, True, "dr-smith", 175),
        ("1.2", "normal", 90, True, "dr-smith", 85),
        ("1.4", "abnormal", 14, True, "dr-smith", 13),
    ]

    for i, (value, status, days_ago, acked, acked_by, acked_days_ago) in enumerate(creatinine_history):
        collection_date = today - timedelta(days=days_ago)
        lab_results.append(LabResult(
            id=f"creatinine-{i}",
            test_name="Creatinine",
            test_code="2160-0",
            value=value,
            unit="mg/dL",
            reference_range="0.7-1.3",
            status=status,
            subject=Reference(reference=f"Patient/{patient_id}"),
            collection_date=collection_date,
            performing_lab="Quest Diagnostics",
            panel_id="bmp",
            last_updated=collection_date + timedelta(hours=3),
            acknowledged=acked,
            acknowledged_by=acked_by if acked else None,
            acknowledged_at=today - timedelta(days=acked_days_ago) if acked else None,
        ))

    # Potassium history (showing sudden spike - critical, most recent UNACKNOWLEDGED)
    potassium_history = [
        ("4.2", "normal", 365, True, "dr-smith", 360),
        ("4.3", "normal", 270, True, "dr-smith", 265),
        ("4.1", "normal", 180, True, "dr-jones", 175),
        ("4.5", "normal", 120, True, "dr-smith", 115),
        ("4.8", "normal", 90, True, "dr-smith", 85),
        ("5.8", "critical", 1, False, None, None),
    ]

    for i, (value, status, days_ago, acked, acked_by, acked_days_ago) in enumerate(potassium_history):
        collection_date = today - timedelta(days=days_ago)
        lab_results.append(LabResult(
            id=f"potassium-{i}",
            test_name="Potassium",
            test_code="2823-3",
            value=value,
            unit="mEq/L",
            reference_range="3.5-5.0",
            status=status,
            subject=Reference(reference=f"Patient/{patient_id}"),
            collection_date=collection_date,
            performing_lab="Quest Diagnostics",
            panel_id="bmp",
            last_updated=collection_date + timedelta(hours=1),
            acknowledged=acked,
            acknowledged_by=acked_by,
            acknowledged_at=today - timedelta(days=acked_days_ago) if acked_days_ago else None,
        ))

    # HbA1c history (showing worsening control)
    hba1c_history = [
        ("5.8", "abnormal", 365, True, "dr-smith", 360),
        ("6.0", "abnormal", 270, True, "dr-smith", 265),
        ("6.2", "abnormal", 180, True, "dr-jones", 175),
        ("6.5", "abnormal", 120, True, "dr-smith", 115),
        ("6.8", "abnormal", 30, True, "dr-smith", 28),
    ]

    for i, (value, status, days_ago, acked, acked_by, acked_days_ago) in enumerate(hba1c_history):
        collection_date = today - timedelta(days=days_ago)
        lab_results.append(LabResult(
            id=f"hba1c-{i}",
            test_name="HbA1c",
            test_code="4548-4",
            value=value,
            unit="%",
            reference_range="<5.7",
            status=status,
            subject=Reference(reference=f"Patient/{patient_id}"),
            collection_date=collection_date,
            performing_lab="LabCorp",
            last_updated=collection_date + timedelta(days=1),
            acknowledged=acked,
            acknowledged_by=acked_by if acked else None,
            acknowledged_at=today - timedelta(days=acked_days_ago) if acked else None,
        ))

    # LDL history (showing improvement with treatment)
    ldl_history = [
        ("165", "abnormal", 365, True, "dr-smith", 360),
        ("155", "abnormal", 270, True, "dr-smith", 265),
        ("145", "abnormal", 180, True, "dr-jones", 175),
        ("135", "abnormal", 45, True, "dr-smith", 43),
    ]

    for i, (value, status, days_ago, acked, acked_by, acked_days_ago) in enumerate(ldl_history):
        collection_date = today - timedelta(days=days_ago)
        lab_results.append(LabResult(
            id=f"ldl-{i}",
            test_name="LDL",
            test_code="2089-1",
            value=value,
            unit="mg/dL",
            reference_range="<100",
            status=status,
            subject=Reference(reference=f"Patient/{patient_id}"),
            collection_date=collection_date,
            performing_lab="Quest Diagnostics",
            panel_id="lipid",
            last_updated=collection_date + timedelta(hours=4),
            acknowledged=acked,
            acknowledged_by=acked_by if acked else None,
            acknowledged_at=today - timedelta(days=acked_days_ago) if acked else None,
        ))

    # eGFR history (showing gradual decline)
    egfr_history = [
        ("85", "normal", 365, True, "dr-smith", 360),
        ("80", "normal", 270, True, "dr-smith", 265),
        ("75", "normal", 180, True, "dr-jones", 175),
        ("72", "normal", 90, True, "dr-smith", 85),
        ("65", "normal", 14, True, "dr-smith", 13),
    ]

    for i, (value, status, days_ago, acked, acked_by, acked_days_ago) in enumerate(egfr_history):
        collection_date = today - timedelta(days=days_ago)
        lab_results.append(LabResult(
            id=f"egfr-{i}",
            test_name="eGFR",
            test_code="33914-3",
            value=value,
            unit="mL/min/1.73m²",
            reference_range=">60",
            status=status,
            subject=Reference(reference=f"Patient/{patient_id}"),
            collection_date=collection_date,
            performing_lab="Quest Diagnostics",
            last_updated=collection_date + timedelta(hours=2),
            acknowledged=acked,
            acknowledged_by=acked_by if acked else None,
            acknowledged_at=today - timedelta(days=acked_days_ago) if acked else None,
        ))

    # CBC - Pending results (ordered but not yet complete)
    lab_results.append(LabResult(
        id="cbc-pending-1",
        test_name="CBC",
        test_code="58410-2",
        value="",
        unit="",
        reference_range="",
        status="pending",
        subject=Reference(reference=f"Patient/{patient_id}"),
        collection_date=today - timedelta(hours=6),
        performing_lab="Quest Diagnostics",
        panel_id="cbc",
        last_updated=today - timedelta(hours=6),
        acknowledged=False,
    ))

    # TSH - In Progress (sample received, processing)
    lab_results.append(LabResult(
        id="tsh-inprogress-1",
        test_name="TSH",
        test_code="3016-3",
        value="",
        unit="mIU/L",
        reference_range="0.4-4.0",
        status="in_progress",
        subject=Reference(reference=f"Patient/{patient_id}"),
        collection_date=today - timedelta(hours=4),
        performing_lab="LabCorp",
        last_updated=today - timedelta(hours=2),
        acknowledged=False,
    ))

    # Troponin - Critical and UNACKNOWLEDGED (urgent alert scenario)
    lab_results.append(LabResult(
        id="troponin-critical-1",
        test_name="Troponin I",
        test_code="10839-9",
        value="0.85",
        unit="ng/mL",
        reference_range="<0.04",
        status="critical",
        subject=Reference(reference=f"Patient/{patient_id}"),
        collection_date=today - timedelta(hours=2),
        performing_lab="Quest Diagnostics",
        last_updated=today - timedelta(hours=1),
        acknowledged=False,
    ))

    await repo._seed(lab_results)


async def seed_all_async(
    patient_repo,
    practitioner_repo,
    allergy_repo,
    medication_request_repo,
    appointment_repo,
    encounter_repo,
    visit_note_repo=None,
    imaging_study_repo=None,
    vitals_repo=None,
    social_family_history_repo=None,
    lab_result_repo=None,
) -> None:
    """Seed all repositories with initial data (async version for PostgreSQL)."""
    await seed_patients_async(patient_repo)
    await seed_practitioners_async(practitioner_repo)
    await seed_allergies_async(allergy_repo)
    await seed_medication_requests_async(medication_request_repo)
    await seed_appointments_async(appointment_repo, patient_repo)
    if visit_note_repo:
        await seed_visit_notes_async(visit_note_repo)
    if imaging_study_repo:
        await seed_imaging_studies_async(imaging_study_repo)
    if vitals_repo:
        await seed_vitals_async(vitals_repo)
    if social_family_history_repo:
        await seed_social_family_history_async(social_family_history_repo)
    if lab_result_repo:
        await seed_lab_results_async(lab_result_repo)
    print("[DATA SEEDER] All PostgreSQL repositories seeded with initial data")
