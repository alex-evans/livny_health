"""Tests for PatientContextService."""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from services.patient_context_service import (
    PatientContextService,
    PatientNotFoundError,
    HIGH_ALERT_MEDICATIONS,
    HIGH_ALERT_DRUG_CLASSES,
    VITAL_THRESHOLDS,
)
from resources import (
    PatientRepository,
    AllergyIntoleranceRepository,
    MedicationRequestRepository,
    VitalSignRepository,
    LabResultRepository,
    VisitNoteRepository,
)
from resources.vitals import VitalSign
from resources.medication_request import MedicationRequest, MedicationRequestStatus
from resources.allergy_intolerance import AllergyIntolerance, AllergyReaction, AllergyCriticality
from resources.lab_result import LabResult
from resources.visit_note import VisitNote
from resources.patient import Patient, Problem, ProblemStatus, ProblemPriority
from resources.core import Reference, CodeableConcept, HumanName, Gender


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.fixture
def mock_repos():
    """Create mock repositories for testing."""
    return {
        "patient": MagicMock(spec=PatientRepository),
        "allergy": MagicMock(spec=AllergyIntoleranceRepository),
        "medication_request": MagicMock(spec=MedicationRequestRepository),
        "vitals": MagicMock(spec=VitalSignRepository),
        "lab_result": MagicMock(spec=LabResultRepository),
        "visit_note": MagicMock(spec=VisitNoteRepository),
    }


@pytest.fixture
def service(mock_repos):
    """Create a PatientContextService with mock repos."""
    return PatientContextService(
        patient_repo=mock_repos["patient"],
        allergy_repo=mock_repos["allergy"],
        medication_request_repo=mock_repos["medication_request"],
        vitals_repo=mock_repos["vitals"],
        lab_result_repo=mock_repos["lab_result"],
        visit_note_repo=mock_repos["visit_note"],
    )


@pytest.fixture
def sample_patient():
    """Create a sample patient."""
    from datetime import date
    return Patient(
        id="patient-001",
        name=HumanName(
            family="Doe",
            given=["John"],
        ),
        birth_date=date(1980, 1, 15),
        gender=Gender.MALE,
        problem_list=[
            Problem(
                name="Type 2 Diabetes Mellitus",
                icd10_code="E11.9",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
            ),
            Problem(
                name="Essential Hypertension",
                icd10_code="I10",
                onset_date=date(2018, 6, 15),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
                is_critical=True,
            ),
        ],
    )


@pytest.fixture
def sample_vitals():
    """Create sample vital signs."""
    today = datetime.utcnow()
    return [
        VitalSign(
            id="vital-1",
            vital_type="blood_pressure_systolic",
            value=145.0,
            unit="mmHg",
            status="abnormal",
            subject=Reference.to("Patient", "patient-001", "John Doe"),
            recorded_at=today,
        ),
        VitalSign(
            id="vital-2",
            vital_type="blood_pressure_systolic",
            value=150.0,
            unit="mmHg",
            status="abnormal",
            subject=Reference.to("Patient", "patient-001", "John Doe"),
            recorded_at=today - timedelta(days=7),
        ),
        VitalSign(
            id="vital-3",
            vital_type="heart_rate",
            value=72.0,
            unit="bpm",
            status="normal",
            subject=Reference.to("Patient", "patient-001", "John Doe"),
            recorded_at=today,
        ),
        VitalSign(
            id="vital-4",
            vital_type="oxygen_saturation",
            value=92.0,
            unit="%",
            status="abnormal",
            subject=Reference.to("Patient", "patient-001", "John Doe"),
            recorded_at=today,
        ),
        VitalSign(
            id="vital-5",
            vital_type="oxygen_saturation",
            value=98.0,
            unit="%",
            status="normal",
            subject=Reference.to("Patient", "patient-001", "John Doe"),
            recorded_at=today - timedelta(days=7),
        ),
    ]


@pytest.fixture
def sample_medications():
    """Create sample medications using mocks."""
    today = datetime.utcnow()
    meds = []

    # Metformin - active, not high-alert
    med1 = MagicMock()
    med1.id = "med-1"
    med1.medication_name = "Metformin"
    med1.dosage = "500mg"
    med1.frequency = "Twice daily"
    med1.status = MedicationRequestStatus.ACTIVE
    med1.authored_on = today - timedelta(days=60)
    med1.drug_class = "Biguanide"
    med1.route = "oral"
    med1.generic_name = "Metformin HCl"
    med1.prescriber_name = "Dr. Smith"
    meds.append(med1)

    # Lisinopril - recently started
    med2 = MagicMock()
    med2.id = "med-2"
    med2.medication_name = "Lisinopril"
    med2.dosage = "10mg"
    med2.frequency = "Once daily"
    med2.status = MedicationRequestStatus.ACTIVE
    med2.authored_on = today - timedelta(days=10)
    med2.drug_class = "ACE Inhibitor"
    med2.route = "oral"
    meds.append(med2)

    # Warfarin - high-alert
    med3 = MagicMock()
    med3.id = "med-3"
    med3.medication_name = "Warfarin"
    med3.dosage = "5mg"
    med3.frequency = "Once daily"
    med3.status = MedicationRequestStatus.ACTIVE
    med3.authored_on = today - timedelta(days=90)
    med3.drug_class = "Anticoagulant"
    med3.route = "oral"
    meds.append(med3)

    # Atorvastatin - recently discontinued
    med4 = MagicMock()
    med4.id = "med-4"
    med4.medication_name = "Atorvastatin"
    med4.dosage = "20mg"
    med4.frequency = "Once daily"
    med4.status = MedicationRequestStatus.STOPPED
    med4.authored_on = today - timedelta(days=120)
    med4.end_date = today - timedelta(days=15)
    med4.discontinue_reason = "Patient preference"
    med4.drug_class = "Statin"
    med4.route = "oral"
    meds.append(med4)

    return meds


@pytest.fixture
def sample_allergies():
    """Create sample allergies."""
    return [
        AllergyIntolerance(
            id="allergy-1",
            code=CodeableConcept(code="penicillin", display="Penicillin"),
            reactions=[AllergyReaction(manifestation="Anaphylaxis", severity="severe")],
            criticality=AllergyCriticality.HIGH,
            clinical_status="active",
            patient=Reference.to("Patient", "patient-001", "John Doe"),
        ),
        AllergyIntolerance(
            id="allergy-2",
            code=CodeableConcept(code="sulfa", display="Sulfa"),
            reactions=[AllergyReaction(manifestation="Rash", severity="moderate")],
            criticality=AllergyCriticality.HIGH,
            clinical_status="active",
            patient=Reference.to("Patient", "patient-001", "John Doe"),
        ),
        AllergyIntolerance(
            id="allergy-3",
            code=CodeableConcept(code="ibuprofen", display="Ibuprofen"),
            reactions=[AllergyReaction(manifestation="Upset stomach", severity="mild")],
            criticality=AllergyCriticality.LOW,
            clinical_status="active",
            patient=Reference.to("Patient", "patient-001", "John Doe"),
        ),
    ]


@pytest.fixture
def sample_labs():
    """Create sample lab results."""
    today = datetime.utcnow()
    return [
        LabResult(
            id="lab-1",
            test_name="Hemoglobin A1C",
            value="7.2",
            unit="%",
            reference_range="4.0-5.6",
            status="abnormal",
            collection_date=today - timedelta(days=10),
            subject=Reference.to("Patient", "patient-001", "John Doe"),
        ),
        LabResult(
            id="lab-2",
            test_name="Creatinine",
            value="1.1",
            unit="mg/dL",
            reference_range="0.7-1.3",
            status="normal",
            collection_date=today - timedelta(days=10),
            subject=Reference.to("Patient", "patient-001", "John Doe"),
        ),
        LabResult(
            id="lab-3",
            test_name="BMP",
            value="",
            unit="",
            reference_range="",
            status="pending",
            collection_date=today - timedelta(days=1),
            subject=Reference.to("Patient", "patient-001", "John Doe"),
        ),
    ]


@pytest.fixture
def sample_visits():
    """Create sample visits."""
    today = datetime.utcnow()
    return [
        VisitNote(
            id="visit-1",
            visit_date=today - timedelta(days=14),
            visit_type="Follow-up",
            chief_complaint="Diabetes management",
            provider_name="Dr. Smith",
            patient=Reference.to("Patient", "patient-001", "John Doe"),
        ),
        VisitNote(
            id="visit-2",
            visit_date=today - timedelta(days=90),
            visit_type="Annual Physical",
            chief_complaint="Annual wellness exam",
            provider_name="Dr. Johnson",
            patient=Reference.to("Patient", "patient-001", "John Doe"),
        ),
    ]


def setup_mock_repos(mock_repos, patient, vitals, medications, allergies, labs, visits):
    """Setup mock repository return values."""
    mock_repos["patient"].get = AsyncMock(return_value=patient)
    mock_repos["vitals"].list = AsyncMock(return_value=vitals)
    mock_repos["medication_request"].list = AsyncMock(return_value=medications)
    mock_repos["allergy"].list = AsyncMock(return_value=allergies)
    mock_repos["lab_result"].list = AsyncMock(return_value=labs)
    mock_repos["visit_note"].list = AsyncMock(return_value=visits)


@pytest.mark.unit
class TestGetPatientContext:
    """Tests for get_patient_context method."""

    def test_returns_context_for_valid_patient(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test that context is returned for valid patient."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))

        assert context.patient_id == "patient-001"
        assert context.generated_at is not None

    def test_raises_error_for_unknown_patient(self, service, mock_repos):
        """Test that error is raised for unknown patient."""
        mock_repos["patient"].get = AsyncMock(return_value=None)

        with pytest.raises(PatientNotFoundError):
            run_async(service.get_patient_context("unknown-patient"))

    def test_context_includes_all_sections(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test that context includes all expected sections."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))

        assert "active" in context.medications
        assert "recentlyDiscontinued" in context.medications
        assert context.allergies is not None
        assert "active" in context.problems
        assert "mostRecent" in context.vitals
        assert "results" in context.recent_labs
        assert context.recent_visits is not None
        assert context.quick_summary is not None

    def test_to_dict_conversion(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test to_dict conversion."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))
        d = context.to_dict()

        assert "patientId" in d
        assert "generatedAt" in d
        assert "medications" in d
        assert "allergies" in d
        assert "problems" in d
        assert "vitals" in d
        assert "recentVisits" in d
        assert "recentLabs" in d
        assert "quickSummary" in d


@pytest.mark.unit
class TestVitalTrendCalculation:
    """Tests for vital trend calculation."""

    def test_improving_bp_when_decreasing_from_high(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test BP trend is 'improving' when decreasing from elevated."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))
        bp_vital = context.vitals["mostRecent"].get("blood_pressure_systolic")

        assert bp_vital is not None
        assert bp_vital.trend == "improving"  # 145 < 150, both abnormal

    def test_worsening_o2_when_decreasing(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test O2 saturation trend is 'worsening' when decreasing."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))
        o2_vital = context.vitals["mostRecent"].get("oxygen_saturation")

        assert o2_vital is not None
        assert o2_vital.trend == "worsening"  # 92 < 98

    def test_stable_trend_for_small_changes(self, service):
        """Test that small changes result in 'stable' trend."""
        # Create vitals with <5% change
        today = datetime.utcnow()
        v1 = MagicMock()
        v1.value = 100.0
        v1.effective_date_time = today
        v2 = MagicMock()
        v2.value = 102.0  # 2% change
        v2.effective_date_time = today - timedelta(days=7)

        trend = service._calculate_vital_trend("heart_rate", v1, v2)
        assert trend == "stable"

    def test_no_trend_without_previous(self, service):
        """Test that no trend is returned without previous value."""
        v1 = MagicMock()
        v1.value = 100.0

        trend = service._calculate_vital_trend("heart_rate", v1, None)
        assert trend is None


@pytest.mark.unit
class TestVitalStatus:
    """Tests for vital status determination."""

    def test_normal_heart_rate(self, service):
        """Test normal heart rate detection."""
        status = service._get_vital_status("heart_rate", 75)
        assert status == "normal"

    def test_abnormal_heart_rate_high(self, service):
        """Test abnormal high heart rate detection."""
        status = service._get_vital_status("heart_rate", 110)
        assert status == "abnormal"

    def test_critical_heart_rate(self, service):
        """Test critical heart rate detection."""
        status = service._get_vital_status("heart_rate", 160)
        assert status == "critical"

    def test_critical_low_bp(self, service):
        """Test critical low blood pressure detection."""
        status = service._get_vital_status("blood_pressure_systolic", 75)
        assert status == "critical"

    def test_abnormal_low_o2(self, service):
        """Test abnormal low oxygen saturation detection."""
        status = service._get_vital_status("oxygen_saturation", 93)
        assert status == "abnormal"


@pytest.mark.unit
class TestHighAlertMedications:
    """Tests for high-alert medication detection."""

    def test_detects_warfarin_as_high_alert(self, service):
        """Test that warfarin is detected as high-alert."""
        med = MagicMock()
        med.medication_name = "Warfarin 5mg"
        med.drug_class = ""

        assert service._is_high_alert_medication(med) is True

    def test_detects_insulin_as_high_alert(self, service):
        """Test that insulin is detected as high-alert."""
        med = MagicMock()
        med.medication_name = "Insulin Glargine"
        med.drug_class = "Insulin"

        assert service._is_high_alert_medication(med) is True

    def test_detects_opioid_class_as_high_alert(self, service):
        """Test that opioid class is detected as high-alert."""
        med = MagicMock()
        med.medication_name = "Tramadol"
        med.drug_class = "Opioid Analgesic"

        assert service._is_high_alert_medication(med) is True

    def test_non_high_alert_medication(self, service):
        """Test that regular medications are not high-alert."""
        med = MagicMock()
        med.medication_name = "Metformin"
        med.drug_class = "Biguanide"

        assert service._is_high_alert_medication(med) is False


@pytest.mark.unit
class TestMedicationCategorization:
    """Tests for medication categorization."""

    def test_categorizes_ace_inhibitor(self, service):
        """Test ACE inhibitor categorization."""
        med = MagicMock()
        med.drug_class = "ACE Inhibitor"

        category = service._categorize_medication(med)
        assert category == "Cardiovascular"

    def test_categorizes_biguanide(self, service):
        """Test biguanide categorization."""
        med = MagicMock()
        med.drug_class = "Biguanide"

        category = service._categorize_medication(med)
        assert category == "Diabetes"

    def test_categorizes_ssri(self, service):
        """Test SSRI categorization."""
        med = MagicMock()
        med.drug_class = "SSRI"

        category = service._categorize_medication(med)
        assert category == "Mental Health"

    def test_unknown_class_returns_other(self, service):
        """Test unknown drug class returns 'Other'."""
        med = MagicMock()
        med.drug_class = "Unknown Class"

        category = service._categorize_medication(med)
        assert category == "Other"


@pytest.mark.unit
class TestRecentlyStartedLogic:
    """Tests for recently started medication logic."""

    def test_detects_recently_started(self, service):
        """Test detection of recently started medications."""
        med = MagicMock()
        med.authored_on = datetime.utcnow() - timedelta(days=10)

        threshold = datetime.utcnow() - timedelta(days=30)
        assert service._is_recently_started(med, threshold) is True

    def test_not_recently_started(self, service):
        """Test non-recent medications."""
        med = MagicMock()
        med.authored_on = datetime.utcnow() - timedelta(days=60)

        threshold = datetime.utcnow() - timedelta(days=30)
        assert service._is_recently_started(med, threshold) is False

    def test_handles_missing_date(self, service):
        """Test handling of missing authored_on date."""
        med = MagicMock()
        med.authored_on = None

        threshold = datetime.utcnow() - timedelta(days=30)
        assert service._is_recently_started(med, threshold) is False


@pytest.mark.unit
class TestAllergySeverityOrdering:
    """Tests for allergy severity ordering."""

    def test_critical_allergies_first(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test that critical allergies are sorted first."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))

        # First allergy should be Penicillin (critical, anaphylaxis)
        assert context.allergies[0].allergen == "Penicillin"
        assert context.allergies[0].severity == "critical"

    def test_anaphylaxis_prioritized(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test that anaphylaxis allergies are prioritized."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))

        # First allergy should have is_anaphylaxis = True
        assert context.allergies[0].is_anaphylaxis is True


@pytest.mark.unit
class TestMedicationProcessing:
    """Tests for medication processing."""

    def test_separates_active_and_discontinued(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test that active and discontinued meds are separated."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))

        # Should have 3 active, 1 discontinued
        assert len(context.medications["active"]) == 3
        assert len(context.medications["recentlyDiscontinued"]) == 1

    def test_high_alert_meds_sorted_first(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test that high-alert medications are sorted first."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))

        # First medication should be Warfarin (high-alert)
        assert context.medications["active"][0].name == "Warfarin"
        assert context.medications["active"][0].is_high_alert is True

    def test_recently_started_flagged(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test that recently started medications are flagged."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))

        # Find Lisinopril (recently started)
        lisinopril = next(
            (m for m in context.medications["active"] if m.name == "Lisinopril"),
            None
        )
        assert lisinopril is not None
        assert lisinopril.is_recently_started is True


@pytest.mark.unit
class TestQuickSummaryGeneration:
    """Tests for quick summary generation."""

    def test_includes_primary_vital(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test that primary vital is included in summary."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))

        assert context.quick_summary.primary_vital is not None
        assert "label" in context.quick_summary.primary_vital
        assert "value" in context.quick_summary.primary_vital

    def test_includes_critical_allergies(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test that critical allergies are in summary."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))

        assert "Penicillin" in context.quick_summary.critical_allergies

    def test_includes_top_medications(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test that top medications are in summary."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))

        assert len(context.quick_summary.medication_names) <= 3
        assert len(context.quick_summary.medication_names) > 0

    def test_includes_key_lab(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test that key lab (abnormal) is in summary."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))

        assert context.quick_summary.key_lab is not None
        # Should be A1C since it's abnormal (high)
        assert "Hemoglobin A1C" in context.quick_summary.key_lab["name"]

    def test_includes_problem_count(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test that problem count is in summary."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))

        assert context.quick_summary.problem_count == 2


@pytest.mark.unit
class TestModeAwareFiltering:
    """Tests for mode-aware filtering."""

    def test_documentation_mode_limits_medications(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_allergies, sample_labs, sample_visits
    ):
        """Test that documentation mode limits medication count."""
        # Create many medications
        today = datetime.utcnow()
        many_meds = [
            MedicationRequest(
                id=f"med-{i}",
                medication_name=f"Medication {i}",
                dosage="10mg",
                frequency="Once daily",
                status=MedicationRequestStatus.ACTIVE,
                patient=Reference.to("Patient", "patient-001", "John Doe"),
                authored_on=today - timedelta(days=60),
                drug_class="Test Class",
            )
            for i in range(15)
        ]

        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            many_meds, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(
            service.get_patient_context("patient-001", mode="documentation")
        )

        # Documentation mode should limit to 10 active meds
        assert len(context.medications["active"]) <= 10

    def test_documentation_mode_limits_visits(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs
    ):
        """Test that documentation mode limits visit count."""
        # Create many visits
        today = datetime.utcnow()
        many_visits = [
            VisitNote(
                id=f"visit-{i}",
                visit_date=today - timedelta(days=i * 14),
                visit_type="Follow-up",
                chief_complaint=f"Visit {i}",
                provider_name="Dr. Smith",
                patient=Reference.to("Patient", "patient-001", "John Doe"),
            )
            for i in range(10)
        ]

        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, many_visits
        )

        context = run_async(
            service.get_patient_context("patient-001", mode="documentation")
        )

        # Documentation mode should limit to 3 visits
        assert len(context.recent_visits) <= 3

    def test_review_mode_allows_more_data(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs
    ):
        """Test that review mode allows more visits."""
        # Create many visits
        today = datetime.utcnow()
        many_visits = [
            VisitNote(
                id=f"visit-{i}",
                visit_date=today - timedelta(days=i * 14),
                visit_type="Follow-up",
                chief_complaint=f"Visit {i}",
                provider_name="Dr. Smith",
                patient=Reference.to("Patient", "patient-001", "John Doe"),
            )
            for i in range(10)
        ]

        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, many_visits
        )

        context = run_async(
            service.get_patient_context("patient-001", mode="review")
        )

        # Review mode should allow up to 5 visits
        assert len(context.recent_visits) <= 5


@pytest.mark.unit
class TestLabProcessing:
    """Tests for lab result processing."""

    def test_separates_pending_labs(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test that pending labs are separated."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))

        assert len(context.recent_labs["pending"]) == 1
        assert context.recent_labs["pending"][0]["name"] == "BMP"

    def test_detects_abnormal_labs(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test that abnormal lab status is detected."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))

        # Find A1C (should be high since status is 'abnormal')
        a1c = next(
            (l for l in context.recent_labs["results"] if l.name == "Hemoglobin A1C"),
            None
        )
        assert a1c is not None
        assert a1c.status in ("high", "low", "critical")  # Any abnormal status


@pytest.mark.unit
class TestVisitProcessing:
    """Tests for visit processing."""

    def test_calculates_days_ago(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test that days ago is calculated correctly."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))

        # First visit should be ~14 days ago
        assert context.recent_visits[0].days_ago >= 13
        assert context.recent_visits[0].days_ago <= 15

    def test_visits_sorted_by_date(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test that visits are sorted most recent first."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        context = run_async(service.get_patient_context("patient-001"))

        # Most recent visit should be first
        assert context.recent_visits[0].chief_complaint == "Diabetes management"


@pytest.mark.unit
class TestEmptyData:
    """Tests for handling empty data."""

    def test_handles_no_vitals(self, service, mock_repos, sample_patient):
        """Test handling when no vitals exist."""
        setup_mock_repos(mock_repos, sample_patient, [], [], [], [], [])

        context = run_async(service.get_patient_context("patient-001"))

        assert context.vitals["mostRecent"] == {}
        assert context.vitals["recordedAt"] is None

    def test_handles_no_medications(self, service, mock_repos, sample_patient):
        """Test handling when no medications exist."""
        setup_mock_repos(mock_repos, sample_patient, [], [], [], [], [])

        context = run_async(service.get_patient_context("patient-001"))

        assert len(context.medications["active"]) == 0
        assert len(context.medications["recentlyDiscontinued"]) == 0

    def test_handles_no_allergies(self, service, mock_repos, sample_patient):
        """Test handling when no allergies exist."""
        setup_mock_repos(mock_repos, sample_patient, [], [], [], [], [])

        context = run_async(service.get_patient_context("patient-001"))

        assert len(context.allergies) == 0

    def test_handles_no_problems(self, service, mock_repos):
        """Test handling when patient has no problems."""
        from datetime import date
        patient = Patient(
            id="patient-002",
            name=HumanName(family="Smith", given=["Jane"]),
            birth_date=date(1985, 5, 20),
            gender=Gender.FEMALE,
            problem_list=[],
        )
        setup_mock_repos(mock_repos, patient, [], [], [], [], [])

        context = run_async(service.get_patient_context("patient-002"))

        assert len(context.problems["active"]) == 0
        assert context.quick_summary.problem_count == 0


@pytest.mark.unit
class TestQuickContextSummary:
    """Tests for get_quick_context_summary method."""

    def test_returns_summary_directly(
        self, service, mock_repos, sample_patient, sample_vitals,
        sample_medications, sample_allergies, sample_labs, sample_visits
    ):
        """Test that quick summary can be fetched directly."""
        setup_mock_repos(
            mock_repos, sample_patient, sample_vitals,
            sample_medications, sample_allergies, sample_labs, sample_visits
        )

        summary = run_async(service.get_quick_context_summary("patient-001"))

        assert summary is not None
        assert summary.primary_vital is not None
        assert len(summary.medication_names) > 0
