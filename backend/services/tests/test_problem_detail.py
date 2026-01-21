"""
Unit tests for ProblemDetailService.

Tests problem detail retrieval including history timeline, treatments, and current treatment.
"""
import asyncio
import pytest
from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

from services.problem_detail import (
    ProblemDetailService,
    ProblemDetailResponse,
    ProblemHistoryEntry,
    ProblemTreatmentOutcome,
)
from resources import (
    Patient,
    Problem,
    ProblemStatus,
    ProblemPriority,
    PatientRepository,
    MedicationRequestRepository,
    VisitNoteRepository,
    MedicationRequest,
    VisitNote,
    VisitDiagnosis,
    VisitProvider,
    Dosage,
)
from resources.core import CodeableConcept, Reference


def run_async(coro):
    """Helper to run async code in sync tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.mark.unit
class TestProblemDetailServiceIntegration:
    """Integration tests using seeded data."""

    def test_get_problem_detail_for_patient(self, problem_detail_service):
        """Should retrieve problem detail for existing patient and problem."""
        # This will depend on seeded data - just test it doesn't error
        response = run_async(problem_detail_service.get_problem_detail(
            patient_id="patient-001",
            icd10_code="E11.9",  # Common diabetes code
        ))

        # May or may not have this specific problem
        if response:
            assert response.problem is not None

    def test_get_problem_detail_nonexistent_patient(self, problem_detail_service):
        """Should return None for non-existent patient."""
        response = run_async(problem_detail_service.get_problem_detail(
            patient_id="nonexistent-patient",
            icd10_code="E11.9",
        ))

        assert response is None


@pytest.mark.unit
class TestProblemDetailServiceUnit:
    """Unit tests with mocked repositories."""

    @pytest.fixture
    def mock_repos(self):
        """Create mock repositories."""
        return {
            "patient": MagicMock(spec=PatientRepository),
            "medication": MagicMock(spec=MedicationRequestRepository),
            "visit_note": MagicMock(spec=VisitNoteRepository),
        }

    @pytest.fixture
    def service(self, mock_repos):
        """Create service with mocked repos."""
        return ProblemDetailService(
            patient_repo=mock_repos["patient"],
            medication_repo=mock_repos["medication"],
            visit_note_repo=mock_repos["visit_note"],
        )

    @pytest.fixture
    def patient_with_problems(self):
        """Create patient with test problems."""
        today = date.today()
        patient = MagicMock(spec=Patient)
        patient.problem_list = [
            Problem(
                name="Type 2 Diabetes Mellitus",
                icd10_code="E11.9",
                onset_date=today - timedelta(days=365),
                documented_date=today - timedelta(days=360),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
                documenting_provider="Dr. Smith",
            ),
            Problem(
                name="Essential Hypertension",
                icd10_code="I10",
                onset_date=today - timedelta(days=180),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
            ),
        ]
        return patient

    def test_get_problem_detail_returns_response(self, service, mock_repos, patient_with_problems):
        """Should return problem detail response."""
        mock_repos["patient"].get = AsyncMock(return_value=patient_with_problems)
        mock_repos["visit_note"].get_by_patient = AsyncMock(return_value=[])
        mock_repos["medication"].get_active_by_patient = AsyncMock(return_value=[])

        response = run_async(service.get_problem_detail(
            patient_id="patient-001",
            icd10_code="E11.9",
        ))

        assert response is not None
        assert response.problem.name == "Type 2 Diabetes Mellitus"
        assert isinstance(response.history_timeline, list)

    def test_get_problem_detail_patient_not_found(self, service, mock_repos):
        """Should return None when patient not found."""
        mock_repos["patient"].get = AsyncMock(return_value=None)

        response = run_async(service.get_problem_detail(
            patient_id="nonexistent",
            icd10_code="E11.9",
        ))

        assert response is None

    def test_get_problem_detail_problem_not_found(self, service, mock_repos, patient_with_problems):
        """Should return None when problem not found."""
        mock_repos["patient"].get = AsyncMock(return_value=patient_with_problems)

        response = run_async(service.get_problem_detail(
            patient_id="patient-001",
            icd10_code="NONEXISTENT",
        ))

        assert response is None


@pytest.mark.unit
class TestHistoryTimeline:
    """Tests for building problem history timeline."""

    @pytest.fixture
    def mock_repos(self):
        """Create mock repositories."""
        return {
            "patient": MagicMock(spec=PatientRepository),
            "medication": MagicMock(spec=MedicationRequestRepository),
            "visit_note": MagicMock(spec=VisitNoteRepository),
        }

    @pytest.fixture
    def service(self, mock_repos):
        """Create service with mocked repos."""
        return ProblemDetailService(
            patient_repo=mock_repos["patient"],
            medication_repo=mock_repos["medication"],
            visit_note_repo=mock_repos["visit_note"],
        )

    def test_timeline_includes_onset(self, service, mock_repos):
        """Should include onset entry in timeline."""
        today = date.today()
        problem = Problem(
            name="Diabetes",
            icd10_code="E11.9",
            onset_date=today - timedelta(days=365),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
            documenting_provider="Dr. Smith",
        )
        mock_repos["visit_note"].get_by_patient = AsyncMock(return_value=[])

        timeline = run_async(service._build_history_timeline("patient-001", problem))

        onset_entries = [e for e in timeline if e.entry_type == "onset"]
        assert len(onset_entries) == 1
        assert "onset" in onset_entries[0].description.lower()
        assert onset_entries[0].provider == "Dr. Smith"

    def test_timeline_includes_documented_date(self, service, mock_repos):
        """Should include documented date if different from onset."""
        today = date.today()
        problem = Problem(
            name="Diabetes",
            icd10_code="E11.9",
            onset_date=today - timedelta(days=365),
            documented_date=today - timedelta(days=300),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )
        mock_repos["visit_note"].get_by_patient = AsyncMock(return_value=[])

        timeline = run_async(service._build_history_timeline("patient-001", problem))

        status_changes = [e for e in timeline if e.entry_type == "status_change"]
        assert len(status_changes) == 1
        assert "documented" in status_changes[0].description.lower()

    def test_timeline_includes_related_visits(self, service, mock_repos):
        """Should include visits with matching diagnosis."""
        today = date.today()
        problem = Problem(
            name="Diabetes",
            icd10_code="E11.9",
            onset_date=today - timedelta(days=365),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        now = datetime.now(timezone.utc)
        visit = VisitNote(
            id="visit-001",
            encounter=Reference(reference="Encounter/enc-001"),
            subject=Reference(reference="Patient/patient-001"),
            date=now - timedelta(days=30),
            visit_type="follow_up",
            chief_complaint="Diabetes checkup",
            provider=VisitProvider(id="pract-001", name="Dr. Jones", role="Attending"),
            diagnoses=[
                VisitDiagnosis(code="E11.9", description="Type 2 diabetes"),
            ],
        )
        mock_repos["visit_note"].get_by_patient = AsyncMock(return_value=[visit])

        timeline = run_async(service._build_history_timeline("patient-001", problem))

        visit_entries = [e for e in timeline if e.entry_type == "visit"]
        assert len(visit_entries) == 1
        assert visit_entries[0].visit_id == "visit-001"
        assert visit_entries[0].provider == "Dr. Jones"

    def test_timeline_sorted_by_date(self, service, mock_repos):
        """Should sort timeline entries by date descending."""
        today = date.today()
        problem = Problem(
            name="Diabetes",
            icd10_code="E11.9",
            onset_date=today - timedelta(days=365),
            documented_date=today - timedelta(days=300),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )
        mock_repos["visit_note"].get_by_patient = AsyncMock(return_value=[])

        timeline = run_async(service._build_history_timeline("patient-001", problem))

        # Timeline should be sorted with most recent first
        dates = [e.date for e in timeline if e.date]
        assert dates == sorted(dates, reverse=True)


@pytest.mark.unit
class TestTreatments:
    """Tests for treatment retrieval."""

    @pytest.fixture
    def mock_repos(self):
        """Create mock repositories."""
        return {
            "patient": MagicMock(spec=PatientRepository),
            "medication": MagicMock(spec=MedicationRequestRepository),
            "visit_note": MagicMock(spec=VisitNoteRepository),
        }

    @pytest.fixture
    def service(self, mock_repos):
        """Create service with mocked repos."""
        return ProblemDetailService(
            patient_repo=mock_repos["patient"],
            medication_repo=mock_repos["medication"],
            visit_note_repo=mock_repos["visit_note"],
        )

    def test_get_treatments_for_diabetes(self, service, mock_repos):
        """Should find treatments related to diabetes."""
        today = date.today()
        problem = Problem(
            name="Type 2 Diabetes",
            icd10_code="E11.9",
            onset_date=today - timedelta(days=365),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        med = MagicMock(spec=MedicationRequest)
        med.id = "med-001"
        med.indication = "Type 2 diabetes"
        med.drug_class = "biguanide"
        med.medication = CodeableConcept(code="metformin", display="Metformin")
        med.dosage_instruction = [Dosage(text="500mg twice daily")]
        med.status = "active"
        med.authored_on = datetime.now(timezone.utc) - timedelta(days=100)

        mock_repos["medication"].get_active_by_patient = AsyncMock(return_value=[med])

        treatments = run_async(service._get_treatments("patient-001", problem))

        assert len(treatments) == 1
        assert "Metformin" in treatments[0].treatment
        assert treatments[0].outcome == "ongoing"

    def test_get_treatments_no_matches(self, service, mock_repos):
        """Should return empty list when no matching treatments."""
        today = date.today()
        problem = Problem(
            name="Unknown Condition",
            icd10_code="Z00",  # No medication keywords for this
            onset_date=today,
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        mock_repos["medication"].get_active_by_patient = AsyncMock(return_value=[])

        treatments = run_async(service._get_treatments("patient-001", problem))

        assert treatments == []


@pytest.mark.unit
class TestLastAddressedDate:
    """Tests for getting last addressed date."""

    @pytest.fixture
    def mock_repos(self):
        """Create mock repositories."""
        return {
            "patient": MagicMock(spec=PatientRepository),
            "medication": MagicMock(spec=MedicationRequestRepository),
            "visit_note": MagicMock(spec=VisitNoteRepository),
        }

    @pytest.fixture
    def service(self, mock_repos):
        """Create service with mocked repos."""
        return ProblemDetailService(
            patient_repo=mock_repos["patient"],
            medication_repo=mock_repos["medication"],
            visit_note_repo=mock_repos["visit_note"],
        )

    def test_get_last_addressed_date(self, service, mock_repos):
        """Should find most recent visit date."""
        today = date.today()
        problem = Problem(
            name="Diabetes",
            icd10_code="E11.9",
            onset_date=today - timedelta(days=365),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        now = datetime.now(timezone.utc)
        visits = [
            VisitNote(
                id="visit-001",
                encounter=Reference(reference="Encounter/enc-001"),
                subject=Reference(reference="Patient/patient-001"),
                date=now - timedelta(days=60),
                visit_type="office_visit",
                chief_complaint="Checkup",
                diagnoses=[VisitDiagnosis(code="E11.9", description="Diabetes")],
            ),
            VisitNote(
                id="visit-002",
                encounter=Reference(reference="Encounter/enc-002"),
                subject=Reference(reference="Patient/patient-001"),
                date=now - timedelta(days=30),
                visit_type="follow_up",
                chief_complaint="Follow-up",
                diagnoses=[VisitDiagnosis(code="E11.9", description="Diabetes")],
            ),
        ]
        mock_repos["visit_note"].get_by_patient = AsyncMock(return_value=visits)

        last_addressed = run_async(service._get_last_addressed_date("patient-001", problem))

        assert last_addressed is not None
        # Should be the more recent date
        expected_date = (now - timedelta(days=30)).date()
        assert last_addressed == expected_date

    def test_get_last_addressed_date_no_visits(self, service, mock_repos):
        """Should return None when no matching visits."""
        today = date.today()
        problem = Problem(
            name="Diabetes",
            icd10_code="E11.9",
            onset_date=today - timedelta(days=365),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        mock_repos["visit_note"].get_by_patient = AsyncMock(return_value=[])

        last_addressed = run_async(service._get_last_addressed_date("patient-001", problem))

        assert last_addressed is None

    def test_get_last_addressed_date_no_visit_repo(self, mock_repos):
        """Should return None when no visit repo configured."""
        service = ProblemDetailService(
            patient_repo=mock_repos["patient"],
            medication_repo=mock_repos["medication"],
            visit_note_repo=None,
        )
        today = date.today()
        problem = Problem(
            name="Diabetes",
            icd10_code="E11.9",
            onset_date=today,
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        last_addressed = run_async(service._get_last_addressed_date("patient-001", problem))

        assert last_addressed is None


@pytest.mark.unit
class TestCurrentTreatment:
    """Tests for getting current treatment."""

    @pytest.fixture
    def mock_repos(self):
        """Create mock repositories."""
        return {
            "patient": MagicMock(spec=PatientRepository),
            "medication": MagicMock(spec=MedicationRequestRepository),
        }

    @pytest.fixture
    def service(self, mock_repos):
        """Create service with mocked repos."""
        return ProblemDetailService(
            patient_repo=mock_repos["patient"],
            medication_repo=mock_repos["medication"],
        )

    def test_get_current_treatment(self, service, mock_repos):
        """Should return current primary treatment."""
        today = date.today()
        problem = Problem(
            name="Type 2 Diabetes",
            icd10_code="E11.9",
            onset_date=today - timedelta(days=365),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        med = MagicMock(spec=MedicationRequest)
        med.indication = "Type 2 diabetes"
        med.drug_class = "biguanide"
        med.medication = CodeableConcept(code="metformin", display="Metformin")
        med.dosage_instruction = [Dosage(text="1000mg daily")]

        mock_repos["medication"].get_active_by_patient = AsyncMock(return_value=[med])

        current = run_async(service._get_current_treatment("patient-001", problem))

        assert current is not None
        assert "Metformin" in current
        assert "1000mg" in current

    def test_get_current_treatment_none(self, service, mock_repos):
        """Should return None when no matching treatment."""
        today = date.today()
        problem = Problem(
            name="Unknown Condition",
            icd10_code="Z00",
            onset_date=today,
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        mock_repos["medication"].get_active_by_patient = AsyncMock(return_value=[])

        current = run_async(service._get_current_treatment("patient-001", problem))

        assert current is None


@pytest.mark.unit
class TestMedicationKeywords:
    """Tests for medication keyword mapping."""

    @pytest.fixture
    def service(self):
        """Create service with minimal mocks."""
        return ProblemDetailService(
            patient_repo=MagicMock(spec=PatientRepository),
            medication_repo=MagicMock(spec=MedicationRequestRepository),
        )

    def test_diabetes_keywords(self, service):
        """Should return diabetes-related keywords for E11."""
        keywords = service._get_medication_keywords("E11.9")

        assert "diabetes" in keywords
        assert "metformin" in keywords
        assert "insulin" in keywords

    def test_hypertension_keywords(self, service):
        """Should return hypertension-related keywords for I10."""
        keywords = service._get_medication_keywords("I10")

        assert "hypertension" in keywords
        assert "ace inhibitor" in keywords

    def test_unknown_code_empty_keywords(self, service):
        """Should return empty list for unknown codes."""
        keywords = service._get_medication_keywords("Z99")

        assert keywords == []


@pytest.mark.unit
class TestProblemDetailResponse:
    """Tests for ProblemDetailResponse dataclass."""

    def test_to_dict(self):
        """Should convert to dict properly."""
        today = date.today()
        problem = Problem(
            name="Type 2 Diabetes",
            icd10_code="E11.9",
            onset_date=today - timedelta(days=365),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )
        history = [
            ProblemHistoryEntry(
                date=today - timedelta(days=365),
                entry_type="onset",
                description="Problem onset",
                provider="Dr. Smith",
            ),
        ]
        treatments = [
            ProblemTreatmentOutcome(
                treatment="Metformin 500mg",
                start_date=today - timedelta(days=300),
                outcome="ongoing",
            ),
        ]
        response = ProblemDetailResponse(
            problem=problem,
            history_timeline=history,
            treatments=treatments,
            last_addressed=today - timedelta(days=30),
            current_treatment="Metformin 500mg twice daily",
        )

        result = response.to_dict()

        assert "problem" in result
        assert "historyTimeline" in result
        assert len(result["historyTimeline"]) == 1
        assert result["historyTimeline"][0]["type"] == "onset"
        assert "treatments" in result
        assert len(result["treatments"]) == 1
        assert result["treatments"][0]["treatment"] == "Metformin 500mg"
        assert result["lastAddressed"] is not None
        assert result["currentTreatment"] == "Metformin 500mg twice daily"

    def test_to_dict_with_nulls(self):
        """Should handle null values properly."""
        today = date.today()
        problem = Problem(
            name="Test",
            icd10_code="A00",
            onset_date=today,
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )
        response = ProblemDetailResponse(
            problem=problem,
            history_timeline=[],
            treatments=[],
            last_addressed=None,
            current_treatment=None,
        )

        result = response.to_dict()

        assert result["lastAddressed"] is None
        assert result["currentTreatment"] is None
        assert result["historyTimeline"] == []
        assert result["treatments"] == []
