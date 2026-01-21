"""
Unit tests for ProblemClinicalContextService.

Tests clinical category classification, complexity determination, and related item linking.
"""
import asyncio
import pytest
from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

from services.problem_clinical_context import (
    ProblemClinicalContextService,
    ICD10_CATEGORY_MAP,
    ICD10_SPECIFIC_MAP,
    COMPLEXITY_KEYWORDS,
    PROBLEM_MEDICATION_MAP,
    PROBLEM_LAB_MAP,
)
from resources import (
    Problem,
    ProblemStatus,
    ProblemPriority,
    ProblemSeverity,
    ClinicalCategory,
    ProblemComplexity,
    PatientRepository,
    MedicationRequestRepository,
    VisitNoteRepository,
    LabResultRepository,
    MedicationRequest,
    VisitNote,
    VisitDiagnosis,
    VisitProvider,
    LabResult,
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
class TestClinicalCategoryClassification:
    """Tests for ICD-10 to clinical category mapping."""

    @pytest.fixture
    def service(self):
        """Create service with minimal mocks."""
        patient_repo = MagicMock(spec=PatientRepository)
        medication_repo = MagicMock(spec=MedicationRequestRepository)
        return ProblemClinicalContextService(
            patient_repo=patient_repo,
            medication_repo=medication_repo,
        )

    def test_cardiovascular_codes(self, service):
        """Should classify I codes as cardiovascular."""
        assert service.get_clinical_category("I10") == ClinicalCategory.CARDIOVASCULAR
        assert service.get_clinical_category("I50.9") == ClinicalCategory.CARDIOVASCULAR
        assert service.get_clinical_category("I48.0") == ClinicalCategory.CARDIOVASCULAR

    def test_endocrine_codes(self, service):
        """Should classify E codes as endocrine."""
        assert service.get_clinical_category("E11.9") == ClinicalCategory.ENDOCRINE
        assert service.get_clinical_category("E10.65") == ClinicalCategory.ENDOCRINE
        assert service.get_clinical_category("E78.5") == ClinicalCategory.ENDOCRINE

    def test_respiratory_codes(self, service):
        """Should classify J codes as respiratory."""
        assert service.get_clinical_category("J45.20") == ClinicalCategory.RESPIRATORY
        assert service.get_clinical_category("J06.9") == ClinicalCategory.RESPIRATORY

    def test_musculoskeletal_codes(self, service):
        """Should classify M codes as musculoskeletal."""
        assert service.get_clinical_category("M54.5") == ClinicalCategory.MUSCULOSKELETAL

    def test_neurological_codes(self, service):
        """Should classify G codes as neurological."""
        assert service.get_clinical_category("G89.4") == ClinicalCategory.NEUROLOGICAL
        assert service.get_clinical_category("G62.0") == ClinicalCategory.NEUROLOGICAL

    def test_gastrointestinal_codes(self, service):
        """Should classify K codes as gastrointestinal."""
        assert service.get_clinical_category("K21.0") == ClinicalCategory.GASTROINTESTINAL

    def test_psychiatric_codes(self, service):
        """Should classify F codes as psychiatric."""
        assert service.get_clinical_category("F32.1") == ClinicalCategory.PSYCHIATRIC
        assert service.get_clinical_category("F41.1") == ClinicalCategory.PSYCHIATRIC

    def test_infectious_codes(self, service):
        """Should classify A and B codes as infectious."""
        assert service.get_clinical_category("A09") == ClinicalCategory.INFECTIOUS
        assert service.get_clinical_category("B20") == ClinicalCategory.INFECTIOUS

    def test_oncology_codes(self, service):
        """Should classify C and D0-D4 codes as oncology."""
        assert service.get_clinical_category("C50.9") == ClinicalCategory.ONCOLOGY
        assert service.get_clinical_category("D05.1") == ClinicalCategory.ONCOLOGY

    def test_renal_codes(self, service):
        """Should classify N codes as renal."""
        assert service.get_clinical_category("N18.3") == ClinicalCategory.RENAL

    def test_dermatological_codes(self, service):
        """Should classify L codes as dermatological."""
        assert service.get_clinical_category("L30.9") == ClinicalCategory.DERMATOLOGICAL

    def test_unknown_code_returns_other(self, service):
        """Should return OTHER for unknown codes."""
        assert service.get_clinical_category("Z00") == ClinicalCategory.OTHER
        assert service.get_clinical_category("") == ClinicalCategory.OTHER
        assert service.get_clinical_category("XYZ") == ClinicalCategory.OTHER

    def test_specific_codes_take_precedence(self, service):
        """Should use specific mappings over prefix mappings."""
        # E11 should map to ENDOCRINE via specific mapping
        assert service.get_clinical_category("E11") == ClinicalCategory.ENDOCRINE
        assert service.get_clinical_category("I10") == ClinicalCategory.CARDIOVASCULAR


@pytest.mark.unit
class TestComplexityDetermination:
    """Tests for problem complexity determination."""

    @pytest.fixture
    def service(self):
        """Create service with minimal mocks."""
        patient_repo = MagicMock(spec=PatientRepository)
        medication_repo = MagicMock(spec=MedicationRequestRepository)
        return ProblemClinicalContextService(
            patient_repo=patient_repo,
            medication_repo=medication_repo,
        )

    def test_with_complications_keyword(self, service):
        """Should detect WITH_COMPLICATIONS from keywords."""
        problem = Problem(
            name="Type 2 diabetes with complications",
            icd10_code="E11.9",
            onset_date=date.today(),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        assert service.determine_complexity(problem) == ProblemComplexity.WITH_COMPLICATIONS

    def test_complicated_keyword(self, service):
        """Should detect WITH_COMPLICATIONS from 'complicated'."""
        problem = Problem(
            name="Complicated UTI",
            icd10_code="N39.0",
            onset_date=date.today(),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.ACUTE,
        )

        assert service.determine_complexity(problem) == ProblemComplexity.WITH_COMPLICATIONS

    def test_well_controlled_keyword(self, service):
        """Should detect CONTROLLED from 'well-controlled'."""
        problem = Problem(
            name="Type 2 diabetes, well-controlled",
            icd10_code="E11.9",
            onset_date=date.today(),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        assert service.determine_complexity(problem) == ProblemComplexity.CONTROLLED

    def test_uncontrolled_keyword(self, service):
        """Should detect UNCONTROLLED from keyword."""
        problem = Problem(
            name="Uncontrolled hypertension",
            icd10_code="I10",
            onset_date=date.today(),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        assert service.determine_complexity(problem) == ProblemComplexity.UNCONTROLLED

    def test_poorly_controlled_keyword(self, service):
        """Should detect UNCONTROLLED from 'poorly controlled'."""
        problem = Problem(
            name="Type 2 diabetes, poorly controlled",
            icd10_code="E11.9",
            onset_date=date.today(),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        assert service.determine_complexity(problem) == ProblemComplexity.UNCONTROLLED

    def test_progressive_keyword(self, service):
        """Should detect PROGRESSIVE from keyword."""
        problem = Problem(
            name="Progressive CKD",
            icd10_code="N18.3",
            onset_date=date.today(),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        assert service.determine_complexity(problem) == ProblemComplexity.PROGRESSIVE

    def test_worsening_keyword(self, service):
        """Should detect PROGRESSIVE from 'worsening'."""
        problem = Problem(
            name="Worsening heart failure",
            icd10_code="I50.9",
            onset_date=date.today(),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        assert service.determine_complexity(problem) == ProblemComplexity.PROGRESSIVE

    def test_severity_well_controlled(self, service):
        """Should infer CONTROLLED from severity."""
        problem = Problem(
            name="Type 2 diabetes",
            icd10_code="E11.9",
            onset_date=date.today(),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
            severity=ProblemSeverity.WELL_CONTROLLED,
        )

        assert service.determine_complexity(problem) == ProblemComplexity.CONTROLLED

    def test_severity_severe(self, service):
        """Should infer WITH_COMPLICATIONS from severe severity."""
        problem = Problem(
            name="Heart failure",
            icd10_code="I50.9",
            onset_date=date.today(),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
            severity=ProblemSeverity.SEVERE,
        )

        assert service.determine_complexity(problem) == ProblemComplexity.WITH_COMPLICATIONS

    def test_no_keywords_returns_simple(self, service):
        """Should return SIMPLE when no keywords found."""
        problem = Problem(
            name="Type 2 diabetes",
            icd10_code="E11.9",
            onset_date=date.today(),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        assert service.determine_complexity(problem) == ProblemComplexity.SIMPLE

    def test_empty_name_returns_none(self, service):
        """Should return None for empty problem name."""
        problem = Problem(
            name="",
            icd10_code="E11.9",
            onset_date=date.today(),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        assert service.determine_complexity(problem) is None


@pytest.mark.unit
class TestRelatedVisits:
    """Tests for related visit linking."""

    @pytest.fixture
    def mock_repos(self):
        """Create mock repositories."""
        return {
            "patient": MagicMock(spec=PatientRepository),
            "medication": MagicMock(spec=MedicationRequestRepository),
            "visit_note": MagicMock(spec=VisitNoteRepository),
            "lab_result": MagicMock(spec=LabResultRepository),
        }

    @pytest.fixture
    def service(self, mock_repos):
        """Create service with mocks."""
        return ProblemClinicalContextService(
            patient_repo=mock_repos["patient"],
            medication_repo=mock_repos["medication"],
            visit_note_repo=mock_repos["visit_note"],
            lab_result_repo=mock_repos["lab_result"],
        )

    def test_get_related_visits_matches_diagnosis(self, service, mock_repos):
        """Should find visits with matching diagnosis codes."""
        now = datetime.now(timezone.utc)
        visit = VisitNote(
            id="visit-001",
            encounter=Reference(reference="Encounter/enc-001"),
            subject=Reference(reference="Patient/patient-001"),
            date=now,
            visit_type="office_visit",
            chief_complaint="Follow-up",
            provider=VisitProvider(id="pract-001", name="Dr. Smith", role="Attending"),
            diagnoses=[
                VisitDiagnosis(code="E11.9", description="Type 2 diabetes"),
            ],
        )
        mock_repos["visit_note"].get_by_patient = AsyncMock(return_value=[visit])

        related = run_async(service.get_related_visits("patient-001", "E11.9"))

        assert len(related) == 1
        assert related[0].visit_id == "visit-001"

    def test_get_related_visits_no_visit_repo(self, mock_repos):
        """Should return empty list when no visit repo."""
        service = ProblemClinicalContextService(
            patient_repo=mock_repos["patient"],
            medication_repo=mock_repos["medication"],
            visit_note_repo=None,
        )

        related = run_async(service.get_related_visits("patient-001", "E11.9"))

        assert related == []

    def test_get_related_visits_no_matches(self, service, mock_repos):
        """Should return empty list when no matching visits."""
        now = datetime.now(timezone.utc)
        visit = VisitNote(
            id="visit-001",
            encounter=Reference(reference="Encounter/enc-001"),
            subject=Reference(reference="Patient/patient-001"),
            date=now,
            visit_type="office_visit",
            chief_complaint="Cold",
            diagnoses=[
                VisitDiagnosis(code="J06.9", description="Upper respiratory infection"),
            ],
        )
        mock_repos["visit_note"].get_by_patient = AsyncMock(return_value=[visit])

        related = run_async(service.get_related_visits("patient-001", "E11.9"))

        assert related == []


@pytest.mark.unit
class TestRelatedMedications:
    """Tests for related medication linking."""

    @pytest.fixture
    def mock_repos(self):
        """Create mock repositories."""
        return {
            "patient": MagicMock(spec=PatientRepository),
            "medication": MagicMock(spec=MedicationRequestRepository),
        }

    @pytest.fixture
    def service(self, mock_repos):
        """Create service with mocks."""
        return ProblemClinicalContextService(
            patient_repo=mock_repos["patient"],
            medication_repo=mock_repos["medication"],
        )

    def test_get_related_medications_by_indication(self, service, mock_repos):
        """Should find medications matching by indication."""
        med = MagicMock(spec=MedicationRequest)
        med.id = "med-001"
        med.indication = "Type 2 diabetes"
        med.drug_class = "biguanide"
        med.medication = CodeableConcept(code="metformin", display="Metformin")
        med.dosage_instruction = [Dosage(text="500mg twice daily")]
        med.status = "active"

        mock_repos["medication"].get_active_by_patient = AsyncMock(return_value=[med])

        related = run_async(service.get_related_medications("patient-001", "E11.9"))

        assert len(related) == 1
        assert related[0].medication_id == "med-001"
        assert related[0].name == "Metformin"

    def test_get_related_medications_no_matches(self, service, mock_repos):
        """Should return empty list when no matching medications."""
        med = MagicMock(spec=MedicationRequest)
        med.indication = "Hypertension"
        med.drug_class = "ACE inhibitor"
        med.medication = CodeableConcept(code="lisinopril", display="Lisinopril")

        mock_repos["medication"].get_active_by_patient = AsyncMock(return_value=[med])

        # Using diabetes code, should not match hypertension med
        related = run_async(service.get_related_medications("patient-001", "E11.9"))

        assert len(related) == 0


@pytest.mark.unit
class TestRelatedLabs:
    """Tests for related lab linking."""

    @pytest.fixture
    def mock_repos(self):
        """Create mock repositories."""
        return {
            "patient": MagicMock(spec=PatientRepository),
            "medication": MagicMock(spec=MedicationRequestRepository),
            "lab_result": MagicMock(spec=LabResultRepository),
        }

    @pytest.fixture
    def service(self, mock_repos):
        """Create service with mocks."""
        return ProblemClinicalContextService(
            patient_repo=mock_repos["patient"],
            medication_repo=mock_repos["medication"],
            lab_result_repo=mock_repos["lab_result"],
        )

    def test_get_related_labs_for_diabetes(self, service, mock_repos):
        """Should find labs related to diabetes."""
        now = datetime.now(timezone.utc)
        lab = MagicMock(spec=LabResult)
        lab.test_name = "HbA1c"
        lab.value = "7.2"
        lab.unit = "%"
        lab.collection_date = now
        lab.status = MagicMock()
        lab.status.value = "final"

        mock_repos["lab_result"].get_by_patient = AsyncMock(return_value=[lab])

        related = run_async(service.get_related_labs("patient-001", "E11.9"))

        assert len(related) == 1
        assert related[0].lab_name == "HbA1c"

    def test_get_related_labs_no_repo(self, mock_repos):
        """Should return empty list when no lab repo."""
        service = ProblemClinicalContextService(
            patient_repo=mock_repos["patient"],
            medication_repo=mock_repos["medication"],
            lab_result_repo=None,
        )

        related = run_async(service.get_related_labs("patient-001", "E11.9"))

        assert related == []


@pytest.mark.unit
class TestEnrichProblem:
    """Tests for problem enrichment."""

    @pytest.fixture
    def mock_repos(self):
        """Create mock repositories."""
        return {
            "patient": MagicMock(spec=PatientRepository),
            "medication": MagicMock(spec=MedicationRequestRepository),
            "visit_note": MagicMock(spec=VisitNoteRepository),
            "lab_result": MagicMock(spec=LabResultRepository),
        }

    @pytest.fixture
    def service(self, mock_repos):
        """Create service with mocks."""
        return ProblemClinicalContextService(
            patient_repo=mock_repos["patient"],
            medication_repo=mock_repos["medication"],
            visit_note_repo=mock_repos["visit_note"],
            lab_result_repo=mock_repos["lab_result"],
        )

    def test_enrich_problem_adds_category_and_complexity(self, service, mock_repos):
        """Should enrich problem with category and complexity."""
        mock_repos["visit_note"].get_by_patient = AsyncMock(return_value=[])
        mock_repos["medication"].get_active_by_patient = AsyncMock(return_value=[])
        mock_repos["lab_result"].get_by_patient = AsyncMock(return_value=[])

        problem = Problem(
            name="Type 2 diabetes, well-controlled",
            icd10_code="E11.9",
            onset_date=date.today(),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        enriched = run_async(service.enrich_problem("patient-001", problem))

        assert enriched.clinical_category == ClinicalCategory.ENDOCRINE
        assert enriched.complexity == ProblemComplexity.CONTROLLED


@pytest.mark.unit
class TestGroupProblemsByCategory:
    """Tests for grouping problems by category."""

    @pytest.fixture
    def service(self):
        """Create service with minimal mocks."""
        patient_repo = MagicMock(spec=PatientRepository)
        medication_repo = MagicMock(spec=MedicationRequestRepository)
        return ProblemClinicalContextService(
            patient_repo=patient_repo,
            medication_repo=medication_repo,
        )

    def test_group_problems_by_category(self, service):
        """Should group problems by clinical category."""
        today = date.today()
        problems = [
            Problem(name="Diabetes", icd10_code="E11.9", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC, clinical_category=ClinicalCategory.ENDOCRINE),
            Problem(name="Hypertension", icd10_code="I10", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC, clinical_category=ClinicalCategory.CARDIOVASCULAR),
            Problem(name="Hyperlipidemia", icd10_code="E78.5", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC, clinical_category=ClinicalCategory.ENDOCRINE),
        ]

        groups = service.group_problems_by_category(problems)

        assert ClinicalCategory.ENDOCRINE in groups
        assert ClinicalCategory.CARDIOVASCULAR in groups
        assert len(groups[ClinicalCategory.ENDOCRINE]) == 2
        assert len(groups[ClinicalCategory.CARDIOVASCULAR]) == 1

    def test_group_problems_infers_category(self, service):
        """Should infer category from ICD-10 code if not set."""
        today = date.today()
        problems = [
            Problem(name="Diabetes", icd10_code="E11.9", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC),  # No category set
        ]

        groups = service.group_problems_by_category(problems)

        assert ClinicalCategory.ENDOCRINE in groups


@pytest.mark.unit
class TestParentChildRelationships:
    """Tests for identifying parent-child problem relationships."""

    @pytest.fixture
    def service(self):
        """Create service with minimal mocks."""
        patient_repo = MagicMock(spec=PatientRepository)
        medication_repo = MagicMock(spec=MedicationRequestRepository)
        return ProblemClinicalContextService(
            patient_repo=patient_repo,
            medication_repo=medication_repo,
        )

    def test_identify_diabetes_complications(self, service):
        """Should link diabetes complications to base diabetes."""
        today = date.today()
        problems = [
            Problem(name="Type 2 diabetes mellitus", icd10_code="E11.9", onset_date=today - timedelta(days=365), status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC),
            Problem(name="Diabetic nephropathy", icd10_code="E11.21", onset_date=today - timedelta(days=100), status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC),
        ]

        updated = service.identify_parent_child_relationships(problems)

        # The complication should have parent_problem_code set
        nephropathy = next(p for p in updated if "nephropathy" in p.name.lower())
        assert nephropathy.parent_problem_code == "E11.9"
        assert nephropathy.complexity == ProblemComplexity.WITH_COMPLICATIONS

    def test_base_diabetes_not_linked_to_self(self, service):
        """Should not link base diabetes to itself."""
        today = date.today()
        problems = [
            Problem(name="Type 2 diabetes mellitus", icd10_code="E11.9", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC),
        ]

        updated = service.identify_parent_child_relationships(problems)

        assert updated[0].parent_problem_code is None

    def test_non_complication_codes_not_linked(self, service):
        """Should not link non-complication codes."""
        today = date.today()
        problems = [
            Problem(name="Type 2 diabetes mellitus", icd10_code="E11.9", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC),
            Problem(name="Hypertension", icd10_code="I10", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC),
        ]

        updated = service.identify_parent_child_relationships(problems)

        htn = next(p for p in updated if "Hypertension" in p.name)
        assert htn.parent_problem_code is None

    def test_handles_problems_without_icd10(self, service):
        """Should handle problems without ICD-10 codes."""
        today = date.today()
        problems = [
            Problem(name="Unknown condition", icd10_code="", onset_date=today, status=ProblemStatus.ACTIVE, priority=ProblemPriority.CHRONIC),
        ]

        updated = service.identify_parent_child_relationships(problems)

        assert len(updated) == 1
        assert updated[0].parent_problem_code is None
