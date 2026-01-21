"""
Problem Detail Service.

Provides detailed problem history including:
- Onset, progression, treatments, and outcomes timeline
- Current treatment information
- Last addressed date
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import TYPE_CHECKING

from resources import (
    Problem,
    PatientRepository,
    MedicationRequestRepository,
    VisitNoteRepository,
)

if TYPE_CHECKING:
    pass


@dataclass
class ProblemHistoryEntry:
    """A single entry in the problem history timeline."""
    date: date
    entry_type: str  # onset, progression, treatment, status_change, visit
    description: str
    provider: str | None = None
    visit_id: str | None = None


@dataclass
class ProblemTreatmentOutcome:
    """Treatment and its outcome for a problem."""
    treatment: str
    start_date: date
    end_date: date | None = None
    outcome: str = "ongoing"  # effective, partially_effective, ineffective, ongoing
    notes: str | None = None


@dataclass
class ProblemDetailResponse:
    """Response containing detailed problem information with history."""
    problem: Problem
    history_timeline: list[ProblemHistoryEntry] = field(default_factory=list)
    treatments: list[ProblemTreatmentOutcome] = field(default_factory=list)
    last_addressed: date | None = None
    current_treatment: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "problem": self.problem.to_bff_dict(),
            "historyTimeline": [
                {
                    "date": h.date.isoformat() if h.date else None,
                    "type": h.entry_type,
                    "description": h.description,
                    "provider": h.provider,
                    "visitId": h.visit_id,
                }
                for h in self.history_timeline
            ],
            "treatments": [
                {
                    "treatment": t.treatment,
                    "startDate": t.start_date.isoformat() if t.start_date else None,
                    "endDate": t.end_date.isoformat() if t.end_date else None,
                    "outcome": t.outcome,
                    "notes": t.notes,
                }
                for t in self.treatments
            ],
            "lastAddressed": self.last_addressed.isoformat() if self.last_addressed else None,
            "currentTreatment": self.current_treatment,
        }


class ProblemDetailService:
    """
    Service for retrieving detailed problem history.

    Provides:
    - Problem timeline (onset, progression, visits, status changes)
    - Treatment history with outcomes
    - Current treatment information
    - Last addressed date
    """

    def __init__(
        self,
        patient_repo: PatientRepository,
        medication_repo: MedicationRequestRepository,
        visit_note_repo: VisitNoteRepository | None = None,
    ):
        self.patient_repo = patient_repo
        self.medication_repo = medication_repo
        self.visit_note_repo = visit_note_repo

    async def get_problem_detail(
        self,
        patient_id: str,
        icd10_code: str,
    ) -> ProblemDetailResponse | None:
        """
        Get detailed information for a specific problem.

        Args:
            patient_id: The patient ID
            icd10_code: The ICD-10 code of the problem

        Returns:
            ProblemDetailResponse with full history, or None if not found
        """
        patient = await self.patient_repo.get(patient_id)

        if not patient:
            return None

        # Find the problem
        problem = None
        for p in patient.problem_list or []:
            if p.icd10_code == icd10_code:
                problem = p
                break

        if not problem:
            return None

        # Build history timeline
        history_timeline = await self._build_history_timeline(patient_id, problem)

        # Get treatments
        treatments = await self._get_treatments(patient_id, problem)

        # Get last addressed date and current treatment
        last_addressed = await self._get_last_addressed_date(patient_id, problem)
        current_treatment = await self._get_current_treatment(patient_id, problem)

        return ProblemDetailResponse(
            problem=problem,
            history_timeline=history_timeline,
            treatments=treatments,
            last_addressed=last_addressed,
            current_treatment=current_treatment,
        )

    async def _build_history_timeline(
        self,
        patient_id: str,
        problem: Problem,
    ) -> list[ProblemHistoryEntry]:
        """Build a timeline of events for the problem."""
        timeline = []

        # Add onset entry
        if problem.onset_date:
            timeline.append(ProblemHistoryEntry(
                date=problem.onset_date,
                entry_type="onset",
                description=f"Problem onset: {problem.name}",
                provider=problem.documenting_provider,
            ))

        # Add documented date if different from onset
        if problem.documented_date and problem.documented_date != problem.onset_date:
            timeline.append(ProblemHistoryEntry(
                date=problem.documented_date,
                entry_type="status_change",
                description=f"Problem documented in medical record",
                provider=problem.documenting_provider,
            ))

        # Add visits that addressed this problem
        if self.visit_note_repo:
            try:
                visit_notes = await self.visit_note_repo.get_by_patient(patient_id)
                if visit_notes:
                    code_prefix = problem.icd10_code[:3] if len(problem.icd10_code) >= 3 else problem.icd10_code

                    for visit in visit_notes:
                        if visit.diagnoses:
                            for diagnosis in visit.diagnoses:
                                if diagnosis.code and diagnosis.code.startswith(code_prefix):
                                    visit_date = visit.date.date() if hasattr(visit.date, 'date') else visit.date
                                    timeline.append(ProblemHistoryEntry(
                                        date=visit_date,
                                        entry_type="visit",
                                        description=f"Addressed in {visit.visit_type or 'visit'}: {visit.chief_complaint or 'Follow-up'}",
                                        provider=visit.provider.name if visit.provider else None,
                                        visit_id=visit.id,
                                    ))
                                    break
            except Exception:
                pass

        # Sort timeline by date (most recent first)
        timeline.sort(key=lambda h: h.date if h.date else date.min, reverse=True)

        return timeline

    async def _get_treatments(
        self,
        patient_id: str,
        problem: Problem,
    ) -> list[ProblemTreatmentOutcome]:
        """Get treatments related to this problem."""
        treatments = []

        try:
            medications = await self.medication_repo.get_active_by_patient(patient_id)
            if not medications:
                return treatments

            # Keywords for matching
            keywords = self._get_medication_keywords(problem.icd10_code)

            for med in medications:
                indication = (med.indication or "").lower()
                drug_class = (med.drug_class or "").lower()
                med_name = (med.medication.display or "").lower() if med.medication else ""

                for keyword in keywords:
                    if keyword in indication or keyword in drug_class or keyword in med_name:
                        dosage = None
                        if med.dosage_instruction and len(med.dosage_instruction) > 0:
                            dosage = med.dosage_instruction[0].text

                        treatments.append(ProblemTreatmentOutcome(
                            treatment=f"{med.medication.display if med.medication else 'Unknown'} {dosage or ''}".strip(),
                            start_date=med.authored_on.date() if hasattr(med.authored_on, 'date') else med.authored_on,
                            outcome="ongoing" if med.status == "active" else "effective",
                        ))
                        break

        except Exception:
            pass

        return treatments

    async def _get_last_addressed_date(
        self,
        patient_id: str,
        problem: Problem,
    ) -> date | None:
        """Get the most recent date this problem was addressed."""
        if not self.visit_note_repo:
            return None

        try:
            visit_notes = await self.visit_note_repo.get_by_patient(patient_id)
            if not visit_notes:
                return None

            code_prefix = problem.icd10_code[:3] if len(problem.icd10_code) >= 3 else problem.icd10_code

            most_recent = None
            for visit in visit_notes:
                if visit.diagnoses:
                    for diagnosis in visit.diagnoses:
                        if diagnosis.code and diagnosis.code.startswith(code_prefix):
                            visit_date = visit.date.date() if hasattr(visit.date, 'date') else visit.date
                            if most_recent is None or visit_date > most_recent:
                                most_recent = visit_date
                            break

            return most_recent

        except Exception:
            return None

    async def _get_current_treatment(
        self,
        patient_id: str,
        problem: Problem,
    ) -> str | None:
        """Get the current primary treatment for this problem."""
        try:
            medications = await self.medication_repo.get_active_by_patient(patient_id)
            if not medications:
                return None

            keywords = self._get_medication_keywords(problem.icd10_code)

            for med in medications:
                indication = (med.indication or "").lower()
                drug_class = (med.drug_class or "").lower()
                med_name = (med.medication.display or "").lower() if med.medication else ""

                for keyword in keywords:
                    if keyword in indication or keyword in drug_class or keyword in med_name:
                        dosage = None
                        if med.dosage_instruction and len(med.dosage_instruction) > 0:
                            dosage = med.dosage_instruction[0].text

                        return f"{med.medication.display if med.medication else 'Unknown'} {dosage or ''}".strip()

            return None

        except Exception:
            return None

    def _get_medication_keywords(self, icd10_code: str) -> list[str]:
        """Get medication keywords for matching based on ICD-10 code."""
        # Map of ICD-10 prefixes to medication keywords
        keyword_map = {
            "I10": ["hypertension", "htn", "ace inhibitor", "arb", "beta blocker", "diuretic", "antihypertensive"],
            "I11": ["hypertension", "htn", "ace inhibitor", "arb", "beta blocker", "diuretic"],
            "E10": ["diabetes", "type 1", "insulin"],
            "E11": ["diabetes", "type 2", "metformin", "sglt2", "glp-1", "insulin"],
            "I50": ["heart failure", "chf", "ace inhibitor", "arb", "beta blocker", "diuretic"],
            "I48": ["atrial fibrillation", "afib", "anticoagulant", "warfarin", "beta blocker"],
            "E78": ["lipid", "cholesterol", "statin", "hyperlipidemia"],
            "J45": ["asthma", "inhaler", "bronchodilator", "corticosteroid"],
            "K21": ["gerd", "reflux", "ppi", "proton pump"],
            "F32": ["depression", "ssri", "snri", "antidepressant"],
            "F33": ["depression", "ssri", "snri", "antidepressant"],
            "F41": ["anxiety", "ssri", "snri", "benzodiazepine"],
            "G89": ["pain", "analgesic", "opioid", "nsaid"],
            "G62": ["neuropathy", "gabapentin", "pregabalin"],
        }

        code_prefix = icd10_code[:3] if len(icd10_code) >= 3 else icd10_code
        return keyword_map.get(code_prefix, [])
