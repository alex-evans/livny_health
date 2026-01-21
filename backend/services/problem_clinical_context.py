"""
Problem Clinical Context Service.

Provides clinical context enrichment for problems including:
- Clinical category grouping based on ICD-10 codes
- Complexity determination
- Related visits, medications, and lab results linking
"""

from dataclasses import dataclass
from datetime import date

from resources import (
    Problem,
    ClinicalCategory,
    ProblemComplexity,
    ProblemSeverity,
    RelatedVisit,
    RelatedMedication,
    RelatedLabResult,
    PatientRepository,
    MedicationRequestRepository,
    VisitNoteRepository,
    LabResultRepository,
)


# ICD-10 code prefix to clinical category mapping
# Based on ICD-10-CM chapter structure
ICD10_CATEGORY_MAP: dict[str, ClinicalCategory] = {
    # Cardiovascular (I00-I99)
    "I": ClinicalCategory.CARDIOVASCULAR,
    # Endocrine, nutritional and metabolic (E00-E89)
    "E": ClinicalCategory.ENDOCRINE,
    # Respiratory (J00-J99)
    "J": ClinicalCategory.RESPIRATORY,
    # Musculoskeletal (M00-M99)
    "M": ClinicalCategory.MUSCULOSKELETAL,
    # Nervous system (G00-G99)
    "G": ClinicalCategory.NEUROLOGICAL,
    # Digestive system (K00-K95)
    "K": ClinicalCategory.GASTROINTESTINAL,
    # Mental/behavioral (F00-F99)
    "F": ClinicalCategory.PSYCHIATRIC,
    # Infectious (A00-B99)
    "A": ClinicalCategory.INFECTIOUS,
    "B": ClinicalCategory.INFECTIOUS,
    # Neoplasms (C00-D49)
    "C": ClinicalCategory.ONCOLOGY,
    "D0": ClinicalCategory.ONCOLOGY,
    "D1": ClinicalCategory.ONCOLOGY,
    "D2": ClinicalCategory.ONCOLOGY,
    "D3": ClinicalCategory.ONCOLOGY,
    "D4": ClinicalCategory.ONCOLOGY,
    # Genitourinary/Renal (N00-N99)
    "N": ClinicalCategory.RENAL,
    # Skin (L00-L99)
    "L": ClinicalCategory.DERMATOLOGICAL,
}

# More specific ICD-10 code mappings for common conditions
ICD10_SPECIFIC_MAP: dict[str, ClinicalCategory] = {
    # Diabetes complications often coded under E category
    "E10": ClinicalCategory.ENDOCRINE,  # Type 1 DM
    "E11": ClinicalCategory.ENDOCRINE,  # Type 2 DM
    "E13": ClinicalCategory.ENDOCRINE,  # Other DM
    # Hypertension-related conditions
    "I10": ClinicalCategory.CARDIOVASCULAR,  # Essential HTN
    "I11": ClinicalCategory.CARDIOVASCULAR,  # HTN heart disease
    "I12": ClinicalCategory.CARDIOVASCULAR,  # HTN kidney disease
    "I13": ClinicalCategory.CARDIOVASCULAR,  # HTN heart+kidney
    # Heart failure
    "I50": ClinicalCategory.CARDIOVASCULAR,
    # Atrial fibrillation
    "I48": ClinicalCategory.CARDIOVASCULAR,
}

# Problem-to-medication indication mappings
# Maps problem ICD-10 prefixes to medication indications/drug classes
PROBLEM_MEDICATION_MAP: dict[str, list[str]] = {
    # Hypertension
    "I10": ["hypertension", "htn", "ace inhibitor", "arb", "beta blocker", "calcium channel blocker", "diuretic", "antihypertensive"],
    "I11": ["hypertension", "htn", "ace inhibitor", "arb", "beta blocker", "diuretic", "heart failure"],
    # Diabetes
    "E10": ["diabetes", "type 1", "insulin"],
    "E11": ["diabetes", "type 2", "metformin", "biguanide", "sglt2", "glp-1", "sulfonylurea", "insulin"],
    # Heart failure
    "I50": ["heart failure", "chf", "ace inhibitor", "arb", "beta blocker", "diuretic"],
    # AFib
    "I48": ["atrial fibrillation", "afib", "anticoagulant", "warfarin", "rate control", "rhythm control", "beta blocker"],
    # Hyperlipidemia
    "E78": ["lipid", "cholesterol", "statin", "hyperlipidemia"],
    # Asthma
    "J45": ["asthma", "beta-2 agonist", "inhaler", "bronchodilator", "corticosteroid"],
    # GERD
    "K21": ["gerd", "reflux", "ppi", "proton pump", "h2 blocker"],
    # Depression
    "F32": ["depression", "ssri", "snri", "antidepressant"],
    "F33": ["depression", "ssri", "snri", "antidepressant"],
    # Anxiety
    "F41": ["anxiety", "ssri", "snri", "benzodiazepine", "anxiolytic"],
    # Chronic pain
    "G89": ["pain", "analgesic", "opioid", "nsaid", "neuropathic"],
    # Neuropathy
    "G62": ["neuropathy", "gabapentin", "pregabalin", "neuropathic"],
}

# Problem-to-lab test mappings
# Maps problem ICD-10 prefixes to relevant lab tests
PROBLEM_LAB_MAP: dict[str, list[str]] = {
    # Diabetes
    "E10": ["hba1c", "a1c", "glucose", "fasting glucose", "bmp", "cmp"],
    "E11": ["hba1c", "a1c", "glucose", "fasting glucose", "bmp", "cmp"],
    # Hyperlipidemia
    "E78": ["lipid panel", "cholesterol", "ldl", "hdl", "triglycerides"],
    # Hypertension
    "I10": ["bmp", "cmp", "creatinine", "potassium", "sodium"],
    # Heart failure
    "I50": ["bnp", "bmp", "cmp", "creatinine"],
    # AFib
    "I48": ["inr", "pt", "ptt", "coagulation"],
    # Kidney disease
    "N18": ["creatinine", "bun", "gfr", "urine albumin", "urine protein"],
    # Anemia
    "D50": ["cbc", "iron", "ferritin", "tibc"],
    # Thyroid
    "E03": ["tsh", "t4", "t3", "thyroid"],
    "E05": ["tsh", "t4", "t3", "thyroid"],
}

# Keywords indicating complexity in problem names
# Ordered from most specific to least specific to avoid partial matches
COMPLEXITY_KEYWORDS: list[tuple[str, ProblemComplexity]] = [
    # More specific patterns first
    ("with complications", ProblemComplexity.WITH_COMPLICATIONS),
    ("with complication", ProblemComplexity.WITH_COMPLICATIONS),
    ("complicated", ProblemComplexity.WITH_COMPLICATIONS),
    ("well-controlled", ProblemComplexity.CONTROLLED),
    ("well controlled", ProblemComplexity.CONTROLLED),
    ("uncontrolled", ProblemComplexity.UNCONTROLLED),  # Must come before "controlled"
    ("poorly controlled", ProblemComplexity.UNCONTROLLED),
    ("controlled", ProblemComplexity.CONTROLLED),  # After more specific patterns
    ("progressive", ProblemComplexity.PROGRESSIVE),
    ("worsening", ProblemComplexity.PROGRESSIVE),
    ("advanced", ProblemComplexity.PROGRESSIVE),
]


@dataclass
class ProblemWithContext:
    """Problem with enriched clinical context."""
    problem: Problem
    category: ClinicalCategory
    complexity: ProblemComplexity | None
    related_visits: list[RelatedVisit]
    related_medications: list[RelatedMedication]
    related_labs: list[RelatedLabResult]


@dataclass
class GroupedProblem:
    """A group of related problems by clinical category."""
    category: ClinicalCategory
    problems: list[ProblemWithContext]
    has_complications: bool = False


class ProblemClinicalContextService:
    """
    Service for enriching problems with clinical context.

    Provides:
    - Clinical category classification based on ICD-10 codes
    - Complexity determination from problem names and severity
    - Related visits linking by diagnosis codes
    - Related medications linking by indication
    - Related lab results linking by clinical association
    """

    def __init__(
        self,
        patient_repo: PatientRepository,
        medication_repo: MedicationRequestRepository,
        visit_note_repo: VisitNoteRepository | None = None,
        lab_result_repo: LabResultRepository | None = None,
    ):
        self.patient_repo = patient_repo
        self.medication_repo = medication_repo
        self.visit_note_repo = visit_note_repo
        self.lab_result_repo = lab_result_repo

    def get_clinical_category(self, icd10_code: str) -> ClinicalCategory:
        """
        Determine the clinical category from an ICD-10 code.

        Uses a hierarchical lookup:
        1. Check specific code mappings (e.g., E11 for Type 2 DM)
        2. Check two-character prefix (e.g., D0 for neoplasms)
        3. Check single-character prefix (e.g., I for cardiovascular)
        4. Default to OTHER
        """
        if not icd10_code:
            return ClinicalCategory.OTHER

        code = icd10_code.upper().strip()

        # Check specific mappings first
        for prefix, category in ICD10_SPECIFIC_MAP.items():
            if code.startswith(prefix):
                return category

        # Check two-character prefix
        if len(code) >= 2:
            two_char = code[:2]
            if two_char in ICD10_CATEGORY_MAP:
                return ICD10_CATEGORY_MAP[two_char]

        # Check single-character prefix
        if len(code) >= 1:
            one_char = code[0]
            if one_char in ICD10_CATEGORY_MAP:
                return ICD10_CATEGORY_MAP[one_char]

        return ClinicalCategory.OTHER

    def determine_complexity(self, problem: Problem) -> ProblemComplexity | None:
        """
        Determine problem complexity from name and severity.

        Checks for keywords in the problem name and considers severity.
        Keywords are checked in order from most specific to least specific.
        """
        if not problem.name:
            return None

        name_lower = problem.name.lower()

        # Check for explicit keywords in problem name (ordered by specificity)
        for keyword, complexity in COMPLEXITY_KEYWORDS:
            if keyword in name_lower:
                return complexity

        # Infer from severity if available
        if problem.severity:
            if problem.severity == ProblemSeverity.WELL_CONTROLLED:
                return ProblemComplexity.CONTROLLED
            elif problem.severity == ProblemSeverity.SEVERE:
                return ProblemComplexity.WITH_COMPLICATIONS

        return ProblemComplexity.SIMPLE

    async def get_related_visits(
        self,
        patient_id: str,
        icd10_code: str,
        limit: int = 3,
    ) -> list[RelatedVisit]:
        """
        Find visits that addressed this problem.

        Matches visits by ICD-10 diagnosis codes.
        """
        if not self.visit_note_repo:
            return []

        try:
            visit_notes = await self.visit_note_repo.get_by_patient(patient_id)
            if not visit_notes:
                return []

            code_prefix = icd10_code[:3] if len(icd10_code) >= 3 else icd10_code

            related = []
            for visit in visit_notes:
                # Check if any diagnosis matches
                if visit.diagnoses:
                    for diagnosis in visit.diagnoses:
                        if diagnosis.code and diagnosis.code.startswith(code_prefix):
                            related.append(RelatedVisit(
                                visit_id=visit.id,
                                date=visit.date.date() if hasattr(visit.date, 'date') else visit.date,
                                visit_type=visit.visit_type or "office_visit",
                                provider_name=visit.provider.name if visit.provider else None,
                            ))
                            break

                if len(related) >= limit:
                    break

            # Sort by date (most recent first)
            related.sort(key=lambda v: v.date if v.date else date.min, reverse=True)
            return related[:limit]

        except Exception:
            return []

    async def get_related_medications(
        self,
        patient_id: str,
        icd10_code: str,
    ) -> list[RelatedMedication]:
        """
        Find medications related to this problem.

        Matches by indication keywords and drug class.
        """
        try:
            medications = await self.medication_repo.get_active_by_patient(patient_id)
            if not medications:
                return []

            # Get the keywords for this ICD-10 code
            code_prefix = icd10_code[:3] if len(icd10_code) >= 3 else icd10_code
            keywords = PROBLEM_MEDICATION_MAP.get(code_prefix, [])

            if not keywords:
                return []

            related = []
            for med in medications:
                # Check indication
                indication = (med.indication or "").lower()
                drug_class = (med.drug_class or "").lower()
                med_name = (med.medication.display or "").lower() if med.medication else ""

                for keyword in keywords:
                    if keyword in indication or keyword in drug_class or keyword in med_name:
                        dosage = None
                        if med.dosage_instruction and len(med.dosage_instruction) > 0:
                            dosage = med.dosage_instruction[0].text

                        related.append(RelatedMedication(
                            medication_id=med.id,
                            name=med.medication.display if med.medication else "Unknown",
                            dosage=dosage,
                        ))
                        break

            return related

        except Exception:
            return []

    async def get_related_labs(
        self,
        patient_id: str,
        icd10_code: str,
    ) -> list[RelatedLabResult]:
        """
        Find lab results related to this problem.

        Matches by lab test name based on clinical association.
        """
        if not self.lab_result_repo:
            return []

        try:
            # Get the keywords for this ICD-10 code
            code_prefix = icd10_code[:3] if len(icd10_code) >= 3 else icd10_code
            keywords = PROBLEM_LAB_MAP.get(code_prefix, [])

            if not keywords:
                return []

            labs = await self.lab_result_repo.get_by_patient(patient_id)
            if not labs:
                return []

            # Create a map of test name to most recent result
            test_map: dict[str, RelatedLabResult] = {}

            for lab in labs:
                test_name_lower = lab.test_name.lower()

                for keyword in keywords:
                    if keyword in test_name_lower:
                        # Only keep the most recent result for each test type
                        if test_name_lower not in test_map or (
                            lab.collection_date and
                            test_map[test_name_lower].most_recent_date and
                            lab.collection_date > test_map[test_name_lower].most_recent_date
                        ):
                            test_map[test_name_lower] = RelatedLabResult(
                                lab_name=lab.test_name,
                                most_recent_value=f"{lab.value} {lab.unit}" if lab.unit else lab.value,
                                most_recent_date=lab.collection_date,
                                status=lab.status.value if lab.status else None,
                            )
                        break

            return list(test_map.values())

        except Exception:
            return []

    async def enrich_problem(
        self,
        patient_id: str,
        problem: Problem,
    ) -> Problem:
        """
        Enrich a problem with clinical context.

        Returns a new Problem instance with clinical context fields populated.
        """
        # Determine category and complexity
        category = self.get_clinical_category(problem.icd10_code)
        complexity = self.determine_complexity(problem)

        # Get related items
        related_visits = await self.get_related_visits(patient_id, problem.icd10_code)
        related_meds = await self.get_related_medications(patient_id, problem.icd10_code)
        related_labs = await self.get_related_labs(patient_id, problem.icd10_code)

        # Create a new Problem with enriched data
        return Problem(
            name=problem.name,
            icd10_code=problem.icd10_code,
            onset_date=problem.onset_date,
            status=problem.status,
            priority=problem.priority,
            severity=problem.severity,
            documenting_provider=problem.documenting_provider,
            documented_date=problem.documented_date,
            is_critical=problem.is_critical,
            clinical_category=category,
            complexity=complexity,
            parent_problem_code=problem.parent_problem_code,
            related_visits=related_visits if related_visits else None,
            related_medications=related_meds if related_meds else None,
            related_labs=related_labs if related_labs else None,
        )

    async def enrich_problem_list(
        self,
        patient_id: str,
        problems: list[Problem],
    ) -> list[Problem]:
        """
        Enrich all problems in a list with clinical context.
        """
        enriched = []
        for problem in problems:
            enriched_problem = await self.enrich_problem(patient_id, problem)
            enriched.append(enriched_problem)
        return enriched

    def group_problems_by_category(
        self,
        problems: list[Problem],
    ) -> dict[ClinicalCategory, list[Problem]]:
        """
        Group problems by their clinical category.

        Returns a dictionary mapping categories to lists of problems.
        """
        groups: dict[ClinicalCategory, list[Problem]] = {}

        for problem in problems:
            category = problem.clinical_category or self.get_clinical_category(problem.icd10_code)
            if category not in groups:
                groups[category] = []
            groups[category].append(problem)

        return groups

    def identify_parent_child_relationships(
        self,
        problems: list[Problem],
    ) -> list[Problem]:
        """
        Identify parent-child relationships between problems.

        For example, "Type 2 diabetes mellitus with diabetic nephropathy"
        is a complication of "Type 2 diabetes mellitus".

        Updates the parent_problem_code field for complications.
        """
        # Map of base codes to their problems
        base_problem_map: dict[str, Problem] = {}
        for problem in problems:
            if problem.icd10_code:
                # Use the first 3 characters as base code
                base_code = problem.icd10_code[:3]
                if base_code not in base_problem_map:
                    base_problem_map[base_code] = problem

        # Look for complications
        updated_problems = []
        for problem in problems:
            if not problem.icd10_code:
                updated_problems.append(problem)
                continue

            # Check for diabetes complications (E10.x, E11.x, E13.x)
            code = problem.icd10_code.upper()
            if code.startswith(("E10", "E11", "E13")) and len(code) > 4:
                # The complication code is after the decimal
                # E11.9 = no complications, E11.2x = kidney, E11.3x = eye, etc.
                if code[4] != "9":  # .9 = without complications
                    # Find the base diabetes problem
                    base_code = code[:3]
                    if base_code in base_problem_map:
                        parent = base_problem_map[base_code]
                        if parent.icd10_code != code:  # Don't link to self
                            problem = Problem(
                                name=problem.name,
                                icd10_code=problem.icd10_code,
                                onset_date=problem.onset_date,
                                status=problem.status,
                                priority=problem.priority,
                                severity=problem.severity,
                                documenting_provider=problem.documenting_provider,
                                documented_date=problem.documented_date,
                                is_critical=problem.is_critical,
                                clinical_category=problem.clinical_category,
                                complexity=ProblemComplexity.WITH_COMPLICATIONS,
                                parent_problem_code=parent.icd10_code,
                                related_visits=problem.related_visits,
                                related_medications=problem.related_medications,
                                related_labs=problem.related_labs,
                            )

            updated_problems.append(problem)

        return updated_problems
