"""
Prompt Generators for Encounter Prompts.

Each generator is responsible for creating prompts based on different sources:
- Visit type (base prompts for the visit)
- Patient conditions (condition-specific prompts)
- Clinical alerts (prompts from active alerts)
- Follow-up items (prompts from previous visit plans)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from resources import (
    ClinicalAlert,
    ClinicalAlertRepository,
    Patient,
    PatientRepository,
)
from resources.encounter_prompt import EncounterPrompt
from resources.core import generate_id
from services.prompt_templates import (
    get_templates_for_visit_type,
    get_condition_templates,
    PromptTemplate,
)

if TYPE_CHECKING:
    from services.encounter_note_service import EncounterContext


class PromptGenerator(ABC):
    """Base class for prompt generators."""

    @abstractmethod
    async def generate_prompts(
        self,
        encounter_id: str,
        patient: Patient,
        context: "EncounterContext",
        visit_type: str,
    ) -> list[EncounterPrompt]:
        """
        Generate prompts for an encounter.

        Args:
            encounter_id: The encounter ID
            patient: The patient record
            context: Clinical context (vitals, meds, labs, etc.)
            visit_type: Type of visit (follow_up, annual_physical, urgent)

        Returns:
            List of generated EncounterPrompt objects
        """
        ...


class VisitTypePromptGenerator(PromptGenerator):
    """Generates base prompts from visit type templates."""

    async def generate_prompts(
        self,
        encounter_id: str,
        patient: Patient,
        context: "EncounterContext",
        visit_type: str,
    ) -> list[EncounterPrompt]:
        """Generate prompts based on visit type templates."""
        prompts = []
        templates = get_templates_for_visit_type(visit_type)

        for template in templates:
            prompt = self._template_to_prompt(encounter_id, template)
            prompts.append(prompt)

        return prompts

    def _template_to_prompt(
        self, encounter_id: str, template: PromptTemplate
    ) -> EncounterPrompt:
        """Convert a template to an EncounterPrompt."""
        return EncounterPrompt(
            id=generate_id("prompt"),
            encounter_id=encounter_id,
            prompt_type=template.prompt_type,
            prompt_subtype=template.prompt_subtype,
            prompt_text=template.prompt_text,
            prompt_order=template.base_order,
            status="pending",
            viewer_section=template.viewer_section,
            is_skippable=template.is_skippable,
            source_reference=f"template:{template.prompt_subtype}",
            source_context={"template_type": "visit_type"},
        )


class ConditionPromptGenerator(PromptGenerator):
    """Generates condition-specific prompts based on patient's problem list."""

    def __init__(self, patient_repo: PatientRepository):
        self.patient_repo = patient_repo

    async def generate_prompts(
        self,
        encounter_id: str,
        patient: Patient,
        context: "EncounterContext",
        visit_type: str,
    ) -> list[EncounterPrompt]:
        """Generate prompts based on patient conditions."""
        prompts = []
        condition_templates = get_condition_templates()

        # Get active ICD-10 codes from patient's problem list
        patient_icd_codes = set()
        if patient.problem_list:
            for problem in patient.problem_list:
                if problem.status == "active" and problem.icd10_code:
                    patient_icd_codes.add(problem.icd10_code)

        # Get active medications (by name, lowercase)
        patient_medications = set()
        for med in context.medications:
            if med.medication_name:
                patient_medications.add(med.medication_name.lower())

        # Check each template
        for template in condition_templates:
            if self._template_applies(template, patient_icd_codes, patient_medications):
                prompt = self._template_to_prompt(encounter_id, template)
                prompts.append(prompt)

        return prompts

    def _template_applies(
        self,
        template: PromptTemplate,
        patient_icd_codes: set[str],
        patient_medications: set[str],
    ) -> bool:
        """Check if a condition template applies to this patient."""
        # Check required conditions (any match)
        if template.required_conditions:
            has_condition = any(
                any(icd.startswith(prefix) for icd in patient_icd_codes)
                for prefix in template.required_conditions
            )
            if not has_condition:
                return False

        # Check required medications (any match)
        if template.required_medications:
            has_medication = any(
                any(keyword in med for med in patient_medications)
                for keyword in template.required_medications
            )
            if not has_medication:
                return False

        return True

    def _template_to_prompt(
        self, encounter_id: str, template: PromptTemplate
    ) -> EncounterPrompt:
        """Convert a template to an EncounterPrompt."""
        return EncounterPrompt(
            id=generate_id("prompt"),
            encounter_id=encounter_id,
            prompt_type=template.prompt_type,
            prompt_subtype=template.prompt_subtype,
            prompt_text=template.prompt_text,
            prompt_order=template.base_order,
            status="pending",
            viewer_section=template.viewer_section,
            is_skippable=template.is_skippable,
            source_reference=f"condition:{template.prompt_subtype}",
            source_context={
                "template_type": "condition",
                "required_conditions": template.required_conditions,
                "required_medications": template.required_medications,
            },
        )


class AlertPromptGenerator(PromptGenerator):
    """Generates prompts from active clinical alerts."""

    SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    def __init__(self, alert_repo: ClinicalAlertRepository):
        self.alert_repo = alert_repo

    async def generate_prompts(
        self,
        encounter_id: str,
        patient: Patient,
        context: "EncounterContext",
        visit_type: str,
    ) -> list[EncounterPrompt]:
        """Generate prompts from active clinical alerts."""
        prompts = []

        # Get active alerts for this patient
        alerts = await self.alert_repo.get_by_patient(patient.id, status="active")

        for alert in alerts:
            prompt = self._alert_to_prompt(encounter_id, alert)
            prompts.append(prompt)

        return prompts

    def _alert_to_prompt(
        self, encounter_id: str, alert: ClinicalAlert
    ) -> EncounterPrompt:
        """Convert a clinical alert to an EncounterPrompt."""
        # Alerts get very low order numbers (high priority)
        severity_offset = self.SEVERITY_ORDER.get(alert.severity, 3)
        order = -100 + severity_offset  # Critical = -100, high = -99, etc.

        return EncounterPrompt(
            id=generate_id("prompt"),
            encounter_id=encounter_id,
            prompt_type="alert",
            prompt_subtype=alert.alert_type,
            prompt_text=f"[{alert.severity.upper()}] {alert.title}: {alert.description}",
            prompt_order=order,
            status="pending",
            viewer_section="objective",  # Most alerts relate to objective findings
            alert_level=alert.severity,
            is_skippable=alert.severity != "critical",  # Critical alerts not skippable
            source_reference=f"alert:{alert.id}",
            source_context={
                "alert_id": alert.id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "source": alert.source,
                "source_id": alert.source_id,
                "recommended_actions": alert.recommended_actions,
            },
        )


class FollowUpPromptGenerator(PromptGenerator):
    """Generates prompts from previous visit follow-up items."""

    async def generate_prompts(
        self,
        encounter_id: str,
        patient: Patient,
        context: "EncounterContext",
        visit_type: str,
    ) -> list[EncounterPrompt]:
        """Generate prompts from follow-up items in recent visits."""
        prompts = []

        # Look at recent visits for follow-up items
        for visit in context.recent_visits:
            # Check for plan items that need follow-up
            plan = visit.plan if hasattr(visit, "plan") else None
            if plan and hasattr(plan, "follow_up_items"):
                for item in plan.follow_up_items:
                    prompt = self._follow_up_to_prompt(encounter_id, visit, item)
                    prompts.append(prompt)

        return prompts

    def _follow_up_to_prompt(
        self, encounter_id: str, visit: any, item: str
    ) -> EncounterPrompt:
        """Convert a follow-up item to an EncounterPrompt."""
        visit_date = ""
        if hasattr(visit, "visit_date"):
            visit_date = visit.visit_date.strftime("%m/%d/%Y")

        return EncounterPrompt(
            id=generate_id("prompt"),
            encounter_id=encounter_id,
            prompt_type="follow_up",
            prompt_subtype="previous_visit",
            prompt_text=f"Follow-up from {visit_date}: {item}",
            prompt_order=5,  # After chief complaint, before reviews
            status="pending",
            viewer_section="subjective",
            is_skippable=True,
            source_reference=f"visit:{visit.id if hasattr(visit, 'id') else 'unknown'}",
            source_context={
                "visit_id": visit.id if hasattr(visit, "id") else None,
                "visit_date": visit_date,
                "follow_up_item": item,
            },
        )
