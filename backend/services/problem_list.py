"""
Problem List Service.

Provides problem list retrieval with clinical priority sorting and status management.
"""

from __future__ import annotations
from dataclasses import dataclass, field, replace
from datetime import date
from typing import TYPE_CHECKING

from resources import Problem, ProblemStatus, ProblemPriority, PatientRepository, ClinicalCategory

if TYPE_CHECKING:
    from services.problem_clinical_context import ProblemClinicalContextService


@dataclass
class ProblemGroup:
    """A group of problems by clinical category."""
    category: ClinicalCategory
    category_label: str
    problems: list[Problem] = field(default_factory=list)


@dataclass
class ProblemListResponse:
    """Response containing sorted problem list."""
    problems: list[Problem]
    active_count: int
    total_count: int
    critical_count: int = 0
    new_count: int = 0
    groups: list[ProblemGroup] | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "problems": [p.to_bff_dict() for p in self.problems],
            "activeCount": self.active_count,
            "totalCount": self.total_count,
            "criticalCount": self.critical_count,
            "newCount": self.new_count,
        }
        if self.groups:
            result["groups"] = [
                {
                    "category": g.category.value,
                    "categoryLabel": g.category_label,
                    "problems": [p.to_bff_dict() for p in g.problems],
                }
                for g in self.groups
            ]
        return result


# Category display labels
CATEGORY_LABELS: dict[ClinicalCategory, str] = {
    ClinicalCategory.CARDIOVASCULAR: "Cardiovascular",
    ClinicalCategory.ENDOCRINE: "Endocrine & Metabolic",
    ClinicalCategory.RESPIRATORY: "Respiratory",
    ClinicalCategory.MUSCULOSKELETAL: "Musculoskeletal",
    ClinicalCategory.NEUROLOGICAL: "Neurological",
    ClinicalCategory.GASTROINTESTINAL: "Gastrointestinal",
    ClinicalCategory.PSYCHIATRIC: "Mental Health",
    ClinicalCategory.INFECTIOUS: "Infectious Disease",
    ClinicalCategory.ONCOLOGY: "Oncology",
    ClinicalCategory.RENAL: "Renal & Urological",
    ClinicalCategory.DERMATOLOGICAL: "Dermatological",
    ClinicalCategory.OTHER: "Other",
}


class ProblemListService:
    """
    Service for retrieving and sorting patient problem lists.

    Sorts problems by clinical priority:
    1. Critical/life-threatening problems (regardless of priority)
    2. Acute problems (current active issues requiring attention)
    3. Chronic problems (ongoing conditions requiring management)
    4. Inactive problems (not currently being addressed)
    5. Resolved problems (historical, no longer present)

    Within each category, problems are sorted by onset date (most recent first).
    """

    # Priority order for sorting (lower number = higher priority)
    PRIORITY_ORDER = {
        ProblemPriority.ACUTE: 0,
        ProblemPriority.CHRONIC: 1,
        ProblemPriority.INACTIVE: 2,
        ProblemPriority.RESOLVED: 3,
    }

    def __init__(self, patient_repo: PatientRepository):
        self.patient_repo = patient_repo

    async def get_problem_list(
        self,
        patient_id: str,
        include_resolved: bool = True,
    ) -> ProblemListResponse | None:
        """
        Get the sorted problem list for a patient.

        Args:
            patient_id: The patient ID
            include_resolved: Whether to include resolved problems

        Returns:
            ProblemListResponse with sorted problems, or None if patient not found
        """
        patient = await self.patient_repo.get(patient_id)

        if not patient:
            return None

        problems = patient.problem_list or []

        # Filter out resolved if requested
        if not include_resolved:
            problems = [
                p for p in problems
                if p.status != ProblemStatus.RESOLVED
            ]

        # Sort by clinical priority
        sorted_problems = self.sort_by_priority(problems)

        # Count active problems (active status, regardless of priority)
        active_count = sum(
            1 for p in problems
            if p.status == ProblemStatus.ACTIVE
        )

        # Count critical problems
        critical_count = sum(1 for p in problems if p.is_critical)

        # Count new problems (documented within last 30 days)
        new_count = sum(1 for p in problems if p.is_new)

        return ProblemListResponse(
            problems=sorted_problems,
            active_count=active_count,
            total_count=len(problems),
            critical_count=critical_count,
            new_count=new_count,
        )

    def sort_by_priority(self, problems: list[Problem]) -> list[Problem]:
        """
        Sort problems by clinical priority.

        Sorting order:
        1. Critical/life-threatening problems first (regardless of priority)
        2. Acute problems (current issues needing attention)
        3. Chronic problems (ongoing conditions)
        4. Inactive problems
        5. Resolved problems last

        Within each category, sort by onset date (most recent first).
        """
        return sorted(
            problems,
            key=lambda p: (
                # Primary sort: critical problems come first (0=critical, 1=non-critical)
                0 if p.is_critical else 1,
                # Secondary sort: by clinical priority
                self.PRIORITY_ORDER.get(p.priority, 99),
                # Tertiary sort: most recent onset first
                -p.onset_date.toordinal() if p.onset_date else 0,
            ),
        )

    def get_active_problems(self, problems: list[Problem]) -> list[Problem]:
        """
        Get only problems with active status.

        Returns problems that are currently active (not inactive or resolved).
        """
        return [
            p for p in problems
            if p.status == ProblemStatus.ACTIVE
        ]

    def get_problems_by_status(
        self,
        problems: list[Problem],
        status: ProblemStatus,
    ) -> list[Problem]:
        """
        Filter problems by status.

        Args:
            problems: List of problems to filter
            status: The status to filter by

        Returns:
            List of problems with the specified status
        """
        return [p for p in problems if p.status == status]

    async def get_problem_list_with_context(
        self,
        patient_id: str,
        clinical_context_service: ProblemClinicalContextService,
        include_resolved: bool = True,
        group_by_category: bool = True,
    ) -> ProblemListResponse | None:
        """
        Get problem list enriched with clinical context.

        Args:
            patient_id: The patient ID
            clinical_context_service: Service for enriching problems
            include_resolved: Whether to include resolved problems
            group_by_category: Whether to group problems by clinical category

        Returns:
            ProblemListResponse with enriched problems and optional grouping
        """
        patient = await self.patient_repo.get(patient_id)

        if not patient:
            return None

        problems = patient.problem_list or []

        # Filter out resolved if requested
        if not include_resolved:
            problems = [
                p for p in problems
                if p.status != ProblemStatus.RESOLVED
            ]

        # Enrich problems with clinical context
        enriched_problems = await clinical_context_service.enrich_problem_list(
            patient_id, problems
        )

        # Identify parent-child relationships
        enriched_problems = clinical_context_service.identify_parent_child_relationships(
            enriched_problems
        )

        # Sort by clinical priority
        sorted_problems = self.sort_by_priority(enriched_problems)

        # Count stats
        active_count = sum(
            1 for p in enriched_problems
            if p.status == ProblemStatus.ACTIVE
        )
        critical_count = sum(1 for p in enriched_problems if p.is_critical)
        new_count = sum(1 for p in enriched_problems if p.is_new)

        # Create groups if requested
        groups = None
        if group_by_category:
            category_map = clinical_context_service.group_problems_by_category(sorted_problems)

            # Define category priority for ordering groups
            category_order = [
                ClinicalCategory.ONCOLOGY,  # Cancer first
                ClinicalCategory.CARDIOVASCULAR,
                ClinicalCategory.ENDOCRINE,
                ClinicalCategory.RESPIRATORY,
                ClinicalCategory.NEUROLOGICAL,
                ClinicalCategory.PSYCHIATRIC,
                ClinicalCategory.GASTROINTESTINAL,
                ClinicalCategory.RENAL,
                ClinicalCategory.MUSCULOSKELETAL,
                ClinicalCategory.INFECTIOUS,
                ClinicalCategory.DERMATOLOGICAL,
                ClinicalCategory.OTHER,
            ]

            groups = []
            for category in category_order:
                if category in category_map:
                    groups.append(ProblemGroup(
                        category=category,
                        category_label=CATEGORY_LABELS.get(category, category.value),
                        problems=category_map[category],
                    ))

        return ProblemListResponse(
            problems=sorted_problems,
            active_count=active_count,
            total_count=len(enriched_problems),
            critical_count=critical_count,
            new_count=new_count,
            groups=groups,
        )

    async def update_problem_status(
        self,
        patient_id: str,
        icd10_code: str,
        new_status: ProblemStatus,
        provider_name: str,
    ) -> Problem | None:
        """
        Update the status of a problem.

        When marking as resolved, automatically sets resolved_date and resolved_by_provider.
        When reactivating, clears the resolution fields.

        Args:
            patient_id: The patient ID
            icd10_code: ICD-10 code of the problem to update
            new_status: The new status to set
            provider_name: Name of the provider making the change

        Returns:
            Updated Problem if found, None otherwise
        """
        patient = await self.patient_repo.get(patient_id)

        if not patient or not patient.problem_list:
            return None

        # Find the problem by ICD-10 code
        problem_index = None
        for i, p in enumerate(patient.problem_list):
            if p.icd10_code == icd10_code:
                problem_index = i
                break

        if problem_index is None:
            return None

        problem = patient.problem_list[problem_index]

        # Determine updated fields based on new status
        if new_status == ProblemStatus.RESOLVED:
            # Set resolution tracking fields
            updated_problem = replace(
                problem,
                status=ProblemStatus.RESOLVED,
                priority=ProblemPriority.RESOLVED,
                resolved_date=date.today(),
                resolved_by_provider=provider_name,
            )
        elif new_status == ProblemStatus.ACTIVE:
            # Clear resolution fields when reactivating
            updated_problem = replace(
                problem,
                status=ProblemStatus.ACTIVE,
                priority=problem.priority if problem.priority != ProblemPriority.RESOLVED else ProblemPriority.CHRONIC,
                resolved_date=None,
                resolved_by_provider=None,
            )
        else:
            # For inactive or rule_out status
            updated_problem = replace(
                problem,
                status=new_status,
                priority=ProblemPriority.INACTIVE if new_status == ProblemStatus.INACTIVE else problem.priority,
            )

        # Update the problem in the list
        patient.problem_list[problem_index] = updated_problem

        # Persist the change
        await self.patient_repo.update(patient_id, patient)

        return updated_problem

    async def resolve_problem(
        self,
        patient_id: str,
        icd10_code: str,
        provider_name: str,
    ) -> Problem | None:
        """
        Mark a problem as resolved.

        Convenience method that sets status to RESOLVED and records the
        resolution date and provider.

        Args:
            patient_id: The patient ID
            icd10_code: ICD-10 code of the problem to resolve
            provider_name: Name of the provider resolving the problem

        Returns:
            Updated Problem if found, None otherwise
        """
        return await self.update_problem_status(
            patient_id,
            icd10_code,
            ProblemStatus.RESOLVED,
            provider_name,
        )

    async def reactivate_problem(
        self,
        patient_id: str,
        icd10_code: str,
        provider_name: str,
    ) -> Problem | None:
        """
        Reactivate a resolved or inactive problem.

        Sets status back to ACTIVE and clears resolution tracking fields.
        Useful when a previously resolved condition recurs.

        Args:
            patient_id: The patient ID
            icd10_code: ICD-10 code of the problem to reactivate
            provider_name: Name of the provider reactivating the problem

        Returns:
            Updated Problem if found, None otherwise
        """
        return await self.update_problem_status(
            patient_id,
            icd10_code,
            ProblemStatus.ACTIVE,
            provider_name,
        )

    async def get_resolved_problems(
        self,
        patient_id: str,
    ) -> list[Problem]:
        """
        Get all resolved problems for a patient.

        Returns problems sorted by resolved date (most recently resolved first).

        Args:
            patient_id: The patient ID

        Returns:
            List of resolved problems
        """
        patient = await self.patient_repo.get(patient_id)

        if not patient or not patient.problem_list:
            return []

        resolved = [
            p for p in patient.problem_list
            if p.status == ProblemStatus.RESOLVED
        ]

        # Sort by resolved date (most recent first), then by onset date
        return sorted(
            resolved,
            key=lambda p: (
                -p.resolved_date.toordinal() if p.resolved_date else 0,
                -p.onset_date.toordinal() if p.onset_date else 0,
            ),
        )
