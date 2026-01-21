"""
Problem Clinical Context Service Integration Tests.

Tests for clinical context enrichment including:
- Clinical category classification
- Complexity determination
- Related visits, medications, and labs linking
"""

from datetime import date, timedelta
import pytest

from resources import (
    Problem,
    ProblemStatus,
    ProblemPriority,
    ProblemSeverity,
    ClinicalCategory,
    ProblemComplexity,
)
from services.problem_clinical_context import ProblemClinicalContextService


@pytest.mark.integration
class TestClinicalCategoryClassification:
    """
    Tests for ICD-10 to clinical category mapping.
    """

    def test_cardiovascular_codes(self):
        """Cardiovascular ICD-10 codes (I00-I99) should map to CARDIOVASCULAR."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        # Essential hypertension
        assert service.get_clinical_category("I10") == ClinicalCategory.CARDIOVASCULAR
        # Atrial fibrillation
        assert service.get_clinical_category("I48.91") == ClinicalCategory.CARDIOVASCULAR
        # Heart failure
        assert service.get_clinical_category("I50.9") == ClinicalCategory.CARDIOVASCULAR
        # Acute MI
        assert service.get_clinical_category("I21.3") == ClinicalCategory.CARDIOVASCULAR

    def test_endocrine_codes(self):
        """Endocrine ICD-10 codes (E00-E89) should map to ENDOCRINE."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        # Type 2 diabetes
        assert service.get_clinical_category("E11.9") == ClinicalCategory.ENDOCRINE
        # Type 1 diabetes
        assert service.get_clinical_category("E10.9") == ClinicalCategory.ENDOCRINE
        # Hyperlipidemia
        assert service.get_clinical_category("E78.5") == ClinicalCategory.ENDOCRINE
        # Obesity
        assert service.get_clinical_category("E66.9") == ClinicalCategory.ENDOCRINE

    def test_respiratory_codes(self):
        """Respiratory ICD-10 codes (J00-J99) should map to RESPIRATORY."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        # Asthma
        assert service.get_clinical_category("J45.30") == ClinicalCategory.RESPIRATORY
        # Acute sinusitis
        assert service.get_clinical_category("J01.90") == ClinicalCategory.RESPIRATORY
        # Upper respiratory infection
        assert service.get_clinical_category("J06.9") == ClinicalCategory.RESPIRATORY

    def test_musculoskeletal_codes(self):
        """Musculoskeletal ICD-10 codes (M00-M99) should map to MUSCULOSKELETAL."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        # Low back pain
        assert service.get_clinical_category("M54.5") == ClinicalCategory.MUSCULOSKELETAL
        # Lumbar spinal stenosis
        assert service.get_clinical_category("M48.06") == ClinicalCategory.MUSCULOSKELETAL
        # Rotator cuff tendinitis
        assert service.get_clinical_category("M75.101") == ClinicalCategory.MUSCULOSKELETAL

    def test_neurological_codes(self):
        """Neurological ICD-10 codes (G00-G99) should map to NEUROLOGICAL."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        # Peripheral neuropathy
        assert service.get_clinical_category("G62.9") == ClinicalCategory.NEUROLOGICAL
        # Chronic pain syndrome
        assert service.get_clinical_category("G89.4") == ClinicalCategory.NEUROLOGICAL

    def test_psychiatric_codes(self):
        """Psychiatric ICD-10 codes (F00-F99) should map to PSYCHIATRIC."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        # Anxiety disorder
        assert service.get_clinical_category("F41.9") == ClinicalCategory.PSYCHIATRIC
        # Generalized anxiety disorder
        assert service.get_clinical_category("F41.1") == ClinicalCategory.PSYCHIATRIC
        # Depression
        assert service.get_clinical_category("F32.1") == ClinicalCategory.PSYCHIATRIC

    def test_gastrointestinal_codes(self):
        """Gastrointestinal ICD-10 codes (K00-K95) should map to GASTROINTESTINAL."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        # GERD
        assert service.get_clinical_category("K21.0") == ClinicalCategory.GASTROINTESTINAL

    def test_oncology_codes(self):
        """Oncology ICD-10 codes (C00-D49) should map to ONCOLOGY."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        # Prostate cancer
        assert service.get_clinical_category("C61") == ClinicalCategory.ONCOLOGY
        # Lung cancer
        assert service.get_clinical_category("C34.90") == ClinicalCategory.ONCOLOGY

    def test_renal_codes(self):
        """Renal/Urological ICD-10 codes (N00-N99) should map to RENAL."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        # Benign prostatic hyperplasia
        assert service.get_clinical_category("N40.0") == ClinicalCategory.RENAL
        # CKD
        assert service.get_clinical_category("N18.3") == ClinicalCategory.RENAL

    def test_unknown_codes_default_to_other(self):
        """Unknown or unusual codes should default to OTHER."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        assert service.get_clinical_category("Z00.00") == ClinicalCategory.OTHER
        assert service.get_clinical_category("") == ClinicalCategory.OTHER


@pytest.mark.integration
class TestComplexityDetermination:
    """
    Tests for problem complexity determination.
    """

    def test_with_complications_keyword(self):
        """Problems with 'with complications' in name should be WITH_COMPLICATIONS."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        problem = Problem(
            name="Type 2 diabetes mellitus with complications",
            icd10_code="E11.8",
            onset_date=date(2020, 1, 1),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        assert service.determine_complexity(problem) == ProblemComplexity.WITH_COMPLICATIONS

    def test_controlled_keyword(self):
        """Problems with 'controlled' in name should be CONTROLLED."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        problem = Problem(
            name="Hypertension, well-controlled",
            icd10_code="I10",
            onset_date=date(2020, 1, 1),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        assert service.determine_complexity(problem) == ProblemComplexity.CONTROLLED

    def test_uncontrolled_keyword(self):
        """Problems with 'uncontrolled' in name should be UNCONTROLLED."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        problem = Problem(
            name="Uncontrolled type 2 diabetes",
            icd10_code="E11.65",
            onset_date=date(2020, 1, 1),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        assert service.determine_complexity(problem) == ProblemComplexity.UNCONTROLLED

    def test_progressive_keyword(self):
        """Problems with 'progressive' in name should be PROGRESSIVE."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        problem = Problem(
            name="Progressive renal disease",
            icd10_code="N18.4",
            onset_date=date(2020, 1, 1),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        assert service.determine_complexity(problem) == ProblemComplexity.PROGRESSIVE

    def test_well_controlled_severity(self):
        """Problems with WELL_CONTROLLED severity should be CONTROLLED."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        problem = Problem(
            name="Essential hypertension",
            icd10_code="I10",
            onset_date=date(2020, 1, 1),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
            severity=ProblemSeverity.WELL_CONTROLLED,
        )

        assert service.determine_complexity(problem) == ProblemComplexity.CONTROLLED

    def test_severe_severity(self):
        """Problems with SEVERE severity should be WITH_COMPLICATIONS."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        problem = Problem(
            name="Chronic pain syndrome",
            icd10_code="G89.4",
            onset_date=date(2020, 1, 1),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
            severity=ProblemSeverity.SEVERE,
        )

        assert service.determine_complexity(problem) == ProblemComplexity.WITH_COMPLICATIONS

    def test_simple_problem(self):
        """Problems without complexity indicators should be SIMPLE."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        problem = Problem(
            name="Essential hypertension",
            icd10_code="I10",
            onset_date=date(2020, 1, 1),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        assert service.determine_complexity(problem) == ProblemComplexity.SIMPLE


@pytest.mark.integration
class TestProblemGrouping:
    """
    Tests for problem grouping by clinical category.
    """

    def test_group_problems_by_category(self):
        """Problems should be grouped by clinical category."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        problems = [
            Problem(
                name="Essential hypertension",
                icd10_code="I10",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
                clinical_category=ClinicalCategory.CARDIOVASCULAR,
            ),
            Problem(
                name="Type 2 diabetes",
                icd10_code="E11.9",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
                clinical_category=ClinicalCategory.ENDOCRINE,
            ),
            Problem(
                name="Atrial fibrillation",
                icd10_code="I48.91",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
                clinical_category=ClinicalCategory.CARDIOVASCULAR,
            ),
        ]

        groups = service.group_problems_by_category(problems)

        assert ClinicalCategory.CARDIOVASCULAR in groups
        assert ClinicalCategory.ENDOCRINE in groups
        assert len(groups[ClinicalCategory.CARDIOVASCULAR]) == 2
        assert len(groups[ClinicalCategory.ENDOCRINE]) == 1

    def test_group_problems_without_category_uses_lookup(self):
        """Problems without category should use ICD-10 lookup."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        problems = [
            Problem(
                name="Essential hypertension",
                icd10_code="I10",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
                # No clinical_category set
            ),
        ]

        groups = service.group_problems_by_category(problems)

        assert ClinicalCategory.CARDIOVASCULAR in groups
        assert len(groups[ClinicalCategory.CARDIOVASCULAR]) == 1


@pytest.mark.integration
class TestParentChildRelationships:
    """
    Tests for identifying parent-child problem relationships.
    """

    def test_diabetes_complication_linked_to_parent(self):
        """Diabetes complications should link to base diabetes problem."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        problems = [
            Problem(
                name="Type 2 diabetes mellitus without complications",
                icd10_code="E11.9",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
            ),
            Problem(
                name="Type 2 diabetes mellitus with diabetic nephropathy",
                icd10_code="E11.21",  # .21 = with diabetic CKD
                onset_date=date(2022, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
            ),
        ]

        updated = service.identify_parent_child_relationships(problems)

        # The complication should have parent_problem_code set
        complication = next(p for p in updated if "nephropathy" in p.name.lower())
        assert complication.parent_problem_code == "E11.9"
        assert complication.complexity == ProblemComplexity.WITH_COMPLICATIONS

    def test_base_diabetes_not_linked(self):
        """Base diabetes without complications should not have parent."""
        service = ProblemClinicalContextService(
            patient_repo=None,
            medication_repo=None,
        )

        problems = [
            Problem(
                name="Type 2 diabetes mellitus without complications",
                icd10_code="E11.9",
                onset_date=date(2020, 1, 1),
                status=ProblemStatus.ACTIVE,
                priority=ProblemPriority.CHRONIC,
            ),
        ]

        updated = service.identify_parent_child_relationships(problems)

        assert updated[0].parent_problem_code is None


@pytest.mark.integration
class TestProblemToBffDict:
    """
    Tests for Problem.to_bff_dict() with clinical context fields.
    """

    def test_to_bff_dict_includes_clinical_context(self):
        """to_bff_dict should include clinical context fields when set."""
        from resources import RelatedVisit, RelatedMedication, RelatedLabResult

        problem = Problem(
            name="Essential hypertension",
            icd10_code="I10",
            onset_date=date(2020, 3, 15),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
            clinical_category=ClinicalCategory.CARDIOVASCULAR,
            complexity=ProblemComplexity.CONTROLLED,
            related_visits=[
                RelatedVisit(
                    visit_id="v1",
                    date=date(2024, 1, 15),
                    visit_type="follow_up",
                    provider_name="Dr. Smith",
                ),
            ],
            related_medications=[
                RelatedMedication(
                    medication_id="med-1",
                    name="Lisinopril",
                    dosage="10mg daily",
                ),
            ],
            related_labs=[
                RelatedLabResult(
                    lab_name="BMP",
                    most_recent_value="K 4.2",
                    most_recent_date=date(2024, 1, 10),
                    status="normal",
                ),
            ],
        )

        data = problem.to_bff_dict()

        assert data["clinicalCategory"] == "cardiovascular"
        assert data["complexity"] == "controlled"
        assert len(data["relatedVisits"]) == 1
        assert data["relatedVisits"][0]["visitId"] == "v1"
        assert len(data["relatedMedications"]) == 1
        assert data["relatedMedications"][0]["name"] == "Lisinopril"
        assert len(data["relatedLabs"]) == 1
        assert data["relatedLabs"][0]["labName"] == "BMP"

    def test_to_bff_dict_omits_empty_context(self):
        """to_bff_dict should not include clinical context fields when not set."""
        problem = Problem(
            name="Essential hypertension",
            icd10_code="I10",
            onset_date=date(2020, 3, 15),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
        )

        data = problem.to_bff_dict()

        assert "clinicalCategory" not in data
        assert "complexity" not in data
        assert "relatedVisits" not in data
        assert "relatedMedications" not in data
        assert "relatedLabs" not in data

    def test_to_bff_dict_includes_parent_problem_code(self):
        """to_bff_dict should include parentProblemCode when set."""
        problem = Problem(
            name="Type 2 diabetes with nephropathy",
            icd10_code="E11.21",
            onset_date=date(2022, 1, 1),
            status=ProblemStatus.ACTIVE,
            priority=ProblemPriority.CHRONIC,
            parent_problem_code="E11.9",
        )

        data = problem.to_bff_dict()

        assert data["parentProblemCode"] == "E11.9"
