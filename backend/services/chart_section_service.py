"""
Chart Section Service.

Provides chart navigation sections with dynamic badge counts and alert levels.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from resources import (
    PatientRepository,
    AllergyIntoleranceRepository,
    MedicationRequestRepository,
    VisitNoteRepository,
    LabResultRepository,
    ImagingStudyRepository,
    VitalSignRepository,
    SocialFamilyHistoryRepository,
)
from resources.chart_section import (
    AlertLevel,
    SectionIcon,
    KeyboardShortcut,
    ChartSection,
    ChartSectionsResponse,
)


# Static section definitions with keyboard shortcuts
SECTION_DEFINITIONS: list[dict] = [
    {
        "id": "visits",
        "name": "Chart Notes",
        "icon": "document",
        "order": 1,
        "shortcut_key": "V",
        "shortcut_description": "Go to Chart Notes",
    },
    {
        "id": "medications",
        "name": "Medications",
        "icon": "pill",
        "order": 2,
        "shortcut_key": "M",
        "shortcut_description": "Go to Medications",
    },
    {
        "id": "allergies",
        "name": "Allergies",
        "icon": "exclamation-triangle",
        "order": 3,
        "shortcut_key": "A",
        "shortcut_description": "Go to Allergies",
    },
    {
        "id": "labs",
        "name": "Labs",
        "icon": "beaker",
        "order": 4,
        "shortcut_key": "L",
        "shortcut_description": "Go to Labs",
    },
    {
        "id": "problems",
        "name": "Problems",
        "icon": "clipboard-list",
        "order": 5,
        "shortcut_key": "P",
        "shortcut_description": "Go to Problems",
    },
    {
        "id": "vitals",
        "name": "Vitals",
        "icon": "heart-pulse",
        "order": 6,
        "shortcut_key": "T",
        "shortcut_description": "Go to Vitals",
    },
    {
        "id": "imaging",
        "name": "Imaging",
        "icon": "film",
        "order": 7,
        "shortcut_key": "I",
        "shortcut_description": "Go to Imaging",
    },
    {
        "id": "social-family",
        "name": "Social/Family Hx",
        "icon": "users",
        "order": 8,
        "shortcut_key": "S",
        "shortcut_description": "Go to Social/Family History",
    },
]


@dataclass
class ChartSectionServiceResponse:
    """Response from the chart section service."""
    patient_id: str
    sections: list[ChartSection]

    def to_dict(self) -> dict:
        return {
            "patientId": self.patient_id,
            "sections": [s.to_dict() for s in self.sections],
        }


class ChartSectionService:
    """
    Service for retrieving chart sections with dynamic data.
    """

    def __init__(
        self,
        patient_repo: PatientRepository,
        allergy_repo: AllergyIntoleranceRepository,
        medication_request_repo: MedicationRequestRepository,
        visit_note_repo: VisitNoteRepository,
        lab_result_repo: LabResultRepository,
        imaging_study_repo: ImagingStudyRepository,
        vitals_repo: VitalSignRepository,
        social_family_history_repo: SocialFamilyHistoryRepository,
    ):
        self.patient_repo = patient_repo
        self.allergy_repo = allergy_repo
        self.medication_request_repo = medication_request_repo
        self.visit_note_repo = visit_note_repo
        self.lab_result_repo = lab_result_repo
        self.imaging_study_repo = imaging_study_repo
        self.vitals_repo = vitals_repo
        self.social_family_history_repo = social_family_history_repo

    async def get_chart_sections(self, patient_id: str) -> ChartSectionsResponse | None:
        """
        Get all chart sections for a patient with dynamic badge counts and alerts.

        Args:
            patient_id: The patient ID

        Returns:
            ChartSectionsResponse or None if patient not found
        """
        # Verify patient exists
        patient = await self.patient_repo.get(patient_id)
        if not patient:
            return None

        sections: list[ChartSection] = []

        for definition in SECTION_DEFINITIONS:
            section_id = definition["id"]

            # Get dynamic data for each section
            badge_count, alert_level, has_data, last_updated = await self._get_section_data(
                patient_id, section_id, patient
            )

            sections.append(
                ChartSection(
                    id=section_id,
                    name=definition["name"],
                    icon=definition["icon"],
                    order=definition["order"],
                    has_data=has_data,
                    last_updated=last_updated,
                    alert_level=alert_level,
                    badge_count=badge_count,
                    keyboard_shortcut=KeyboardShortcut(
                        key=definition["shortcut_key"],
                        modifier="Alt",
                        description=definition["shortcut_description"],
                    ),
                )
            )

        return ChartSectionsResponse(patient_id=patient_id, sections=sections)

    async def _get_section_data(
        self,
        patient_id: str,
        section_id: str,
        patient,
    ) -> tuple[int | None, AlertLevel, bool, datetime | None]:
        """
        Get dynamic data for a section.

        Returns:
            Tuple of (badge_count, alert_level, has_data, last_updated)
        """
        badge_count: int | None = None
        alert_level: AlertLevel = "none"
        has_data: bool = False
        last_updated: datetime | None = None

        if section_id == "visits":
            # Get visit count
            visits = await self.visit_note_repo.get_by_patient(patient_id)
            if visits:
                badge_count = len(visits)
                has_data = True
                last_updated = max(v.date for v in visits)

        elif section_id == "medications":
            # Get active medication count
            meds = await self.medication_request_repo.get_active_for_patient(patient_id)
            if meds:
                badge_count = len(meds)
                has_data = True
                # Find most recently started
                last_updated = max(m.authored_on for m in meds if m.authored_on)

        elif section_id == "allergies":
            # Get allergy count and check for severe/critical allergies
            allergies = await self.allergy_repo.get_by_patient(patient_id)
            if allergies:
                badge_count = len(allergies)
                has_data = True

                # Check for critical allergies (severe or anaphylaxis risk)
                has_severe = any(
                    a.criticality == "high" or
                    (a.reactions and any(r.severity == "severe" for r in a.reactions))
                    for a in allergies
                )
                if has_severe:
                    alert_level = "critical"
                elif allergies:
                    alert_level = "warning"

                # Use most recently recorded
                last_updated = max(
                    (a.recorded_date for a in allergies if a.recorded_date),
                    default=None
                )

        elif section_id == "labs":
            # Get recent lab count
            labs = await self.lab_result_repo.get_by_patient(patient_id)
            if labs:
                badge_count = len(labs)
                has_data = True
                last_updated = labs[0].collection_date if labs else None

                # Check for critical lab values
                has_critical = any(l.status == "critical" for l in labs)
                has_abnormal = any(l.status == "abnormal" for l in labs)
                if has_critical:
                    alert_level = "critical"
                elif has_abnormal:
                    alert_level = "warning"

        elif section_id == "problems":
            # Get active problem count
            if patient.problem_list:
                active_problems = [p for p in patient.problem_list if p.status == "active"]
                badge_count = len(active_problems)
                has_data = len(patient.problem_list) > 0

        elif section_id == "vitals":
            # Get current vitals
            current_vitals = await self.vitals_repo.get_current_vitals(patient_id)
            if current_vitals:
                badge_count = len(current_vitals)
                has_data = True
                last_updated = max(
                    (v.recorded_at for v in current_vitals.values()),
                    default=None
                )

                # Check for abnormal vitals
                has_critical = any(v.status == "critical" for v in current_vitals.values())
                has_abnormal = any(v.status in ("high", "low") for v in current_vitals.values())
                if has_critical:
                    alert_level = "critical"
                elif has_abnormal:
                    alert_level = "warning"

        elif section_id == "imaging":
            # Get imaging study count
            studies = await self.imaging_study_repo.get_by_patient(patient_id)
            if studies:
                badge_count = len(studies)
                has_data = True
                last_updated = max(s.study_date for s in studies)

        elif section_id == "social-family":
            # Get social/family history
            history = await self.social_family_history_repo.get_by_patient(patient_id)
            if history:
                has_data = True
                last_updated = history.meta_last_updated

                # Check for high-risk conditions
                if history.risk_assessments:
                    high_risks = [
                        ra for ra in history.risk_assessments
                        if ra.risk_level == "high"
                    ]
                    if high_risks:
                        alert_level = "warning"

        return badge_count, alert_level, has_data, last_updated
