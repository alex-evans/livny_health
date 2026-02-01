"""
Prompt templates for different visit types and conditions.

Defines the prompts that guide physicians through encounters based on
visit type, patient conditions, and clinical context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


VisitType = Literal["follow_up", "annual_physical", "urgent"]


@dataclass
class PromptTemplate:
    """
    Template for generating an encounter prompt.

    Attributes:
        prompt_type: Type of prompt (chief_complaint, review, alert, etc.)
        prompt_subtype: Subtype for more specific categorization
        prompt_text: The text displayed to the physician
        viewer_section: SOAP section this prompt relates to
        is_skippable: Whether the physician can skip this prompt
        base_order: Base ordering priority (lower = earlier)
        required_conditions: ICD-10 prefixes that must be present
        required_medications: Drug class keywords that must be present
    """
    prompt_type: str
    prompt_subtype: str | None
    prompt_text: str
    viewer_section: str | None
    is_skippable: bool = True
    base_order: int = 0
    required_conditions: list[str] = field(default_factory=list)
    required_medications: list[str] = field(default_factory=list)


# Visit type templates define the base prompts for each visit type
VISIT_TYPE_TEMPLATES: dict[str, list[PromptTemplate]] = {
    "follow_up": [
        PromptTemplate(
            prompt_type="chief_complaint",
            prompt_subtype="reason_for_visit",
            prompt_text="What brings the patient in today?",
            viewer_section="subjective",
            is_skippable=False,
            base_order=0,
        ),
        PromptTemplate(
            prompt_type="review",
            prompt_subtype="vitals",
            prompt_text="Review current vital signs",
            viewer_section="objective",
            is_skippable=True,
            base_order=10,
        ),
        PromptTemplate(
            prompt_type="review",
            prompt_subtype="medications",
            prompt_text="Review current medications - any changes or concerns?",
            viewer_section="objective",
            is_skippable=True,
            base_order=20,
        ),
        PromptTemplate(
            prompt_type="assessment",
            prompt_subtype="clinical_impression",
            prompt_text="Document your clinical assessment",
            viewer_section="assessment",
            is_skippable=False,
            base_order=100,
        ),
        PromptTemplate(
            prompt_type="plan",
            prompt_subtype="treatment_plan",
            prompt_text="Document the treatment plan and next steps",
            viewer_section="plan",
            is_skippable=False,
            base_order=110,
        ),
    ],
    "annual_physical": [
        PromptTemplate(
            prompt_type="chief_complaint",
            prompt_subtype="reason_for_visit",
            prompt_text="Annual physical examination",
            viewer_section="subjective",
            is_skippable=False,
            base_order=0,
        ),
        PromptTemplate(
            prompt_type="review",
            prompt_subtype="vitals",
            prompt_text="Review vital signs and compare to previous visits",
            viewer_section="objective",
            is_skippable=False,
            base_order=10,
        ),
        PromptTemplate(
            prompt_type="review",
            prompt_subtype="medications",
            prompt_text="Complete medication reconciliation",
            viewer_section="objective",
            is_skippable=False,
            base_order=20,
        ),
        PromptTemplate(
            prompt_type="review",
            prompt_subtype="family_history",
            prompt_text="Review and update family history",
            viewer_section="subjective",
            is_skippable=True,
            base_order=30,
        ),
        PromptTemplate(
            prompt_type="review",
            prompt_subtype="social_history",
            prompt_text="Review social history (smoking, alcohol, exercise)",
            viewer_section="subjective",
            is_skippable=True,
            base_order=40,
        ),
        PromptTemplate(
            prompt_type="review",
            prompt_subtype="preventive_care",
            prompt_text="Review preventive care and immunization status",
            viewer_section="plan",
            is_skippable=False,
            base_order=50,
        ),
        PromptTemplate(
            prompt_type="review",
            prompt_subtype="screenings",
            prompt_text="Review recommended health screenings",
            viewer_section="plan",
            is_skippable=False,
            base_order=60,
        ),
        PromptTemplate(
            prompt_type="assessment",
            prompt_subtype="clinical_impression",
            prompt_text="Document overall health assessment",
            viewer_section="assessment",
            is_skippable=False,
            base_order=100,
        ),
        PromptTemplate(
            prompt_type="plan",
            prompt_subtype="treatment_plan",
            prompt_text="Document preventive care plan and follow-up schedule",
            viewer_section="plan",
            is_skippable=False,
            base_order=110,
        ),
    ],
    "urgent": [
        PromptTemplate(
            prompt_type="chief_complaint",
            prompt_subtype="acute_complaint",
            prompt_text="Document the acute presenting complaint",
            viewer_section="subjective",
            is_skippable=False,
            base_order=0,
        ),
        PromptTemplate(
            prompt_type="review",
            prompt_subtype="vitals",
            prompt_text="Review vital signs - note any abnormalities",
            viewer_section="objective",
            is_skippable=False,
            base_order=10,
        ),
        PromptTemplate(
            prompt_type="assessment",
            prompt_subtype="clinical_impression",
            prompt_text="Document rapid clinical assessment",
            viewer_section="assessment",
            is_skippable=False,
            base_order=50,
        ),
        PromptTemplate(
            prompt_type="plan",
            prompt_subtype="treatment_plan",
            prompt_text="Document immediate treatment plan",
            viewer_section="plan",
            is_skippable=False,
            base_order=60,
        ),
    ],
}


# Condition-specific prompts that are added when the patient has certain conditions
CONDITION_TEMPLATES: list[PromptTemplate] = [
    # Diabetes
    PromptTemplate(
        prompt_type="review",
        prompt_subtype="a1c_review",
        prompt_text="Review A1C - current value and trend",
        viewer_section="objective",
        is_skippable=True,
        base_order=25,
        required_conditions=["E10", "E11", "E13"],  # Type 1, Type 2, Other diabetes
    ),
    PromptTemplate(
        prompt_type="review",
        prompt_subtype="diabetes_complications",
        prompt_text="Screen for diabetic complications (nephropathy, retinopathy, neuropathy)",
        viewer_section="assessment",
        is_skippable=True,
        base_order=75,
        required_conditions=["E10", "E11", "E13"],
    ),
    # Hypertension
    PromptTemplate(
        prompt_type="review",
        prompt_subtype="bp_review",
        prompt_text="Review blood pressure readings - current and trend",
        viewer_section="objective",
        is_skippable=True,
        base_order=15,
        required_conditions=["I10", "I11", "I12", "I13", "I15"],  # Hypertension codes
    ),
    # Chronic Kidney Disease
    PromptTemplate(
        prompt_type="review",
        prompt_subtype="renal_function",
        prompt_text="Review renal function - eGFR and creatinine trend",
        viewer_section="objective",
        is_skippable=True,
        base_order=26,
        required_conditions=["N18"],  # CKD
    ),
    # Anticoagulation
    PromptTemplate(
        prompt_type="review",
        prompt_subtype="inr_review",
        prompt_text="Review INR - current value and time in therapeutic range",
        viewer_section="objective",
        is_skippable=True,
        base_order=27,
        required_medications=["warfarin", "coumadin"],
    ),
    # Heart Failure
    PromptTemplate(
        prompt_type="review",
        prompt_subtype="heart_failure_status",
        prompt_text="Assess heart failure status - symptoms, weight, edema",
        viewer_section="objective",
        is_skippable=True,
        base_order=28,
        required_conditions=["I50"],  # Heart failure
    ),
    # COPD/Asthma
    PromptTemplate(
        prompt_type="review",
        prompt_subtype="respiratory_status",
        prompt_text="Review respiratory status and inhaler technique",
        viewer_section="objective",
        is_skippable=True,
        base_order=29,
        required_conditions=["J44", "J45"],  # COPD, Asthma
    ),
]


def get_templates_for_visit_type(visit_type: str) -> list[PromptTemplate]:
    """
    Get the base templates for a visit type.

    Args:
        visit_type: The type of visit (follow_up, annual_physical, urgent)

    Returns:
        List of PromptTemplate objects for the visit type
    """
    return VISIT_TYPE_TEMPLATES.get(visit_type, VISIT_TYPE_TEMPLATES["follow_up"])


def get_condition_templates() -> list[PromptTemplate]:
    """
    Get all condition-specific templates.

    Returns:
        List of all condition-specific PromptTemplate objects
    """
    return CONDITION_TEMPLATES.copy()
