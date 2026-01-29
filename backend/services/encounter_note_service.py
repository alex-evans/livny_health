"""
Encounter Note Service.

Provides encounter note management including creation, saving, and version history.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import uuid

from resources import (
    Encounter,
    EncounterRepository,
    EncounterNoteVersion,
    EncounterNoteVersionRepository,
    SaveType,
    Patient,
    PatientRepository,
    AllergyIntolerance,
    AllergyIntoleranceRepository,
    MedicationRequest,
    MedicationRequestRepository,
    VitalSign,
    VitalSignRepository,
    LabResult,
    LabResultRepository,
    VisitNote,
    VisitNoteRepository,
)
from resources.core import Reference


class VersionConflictError(Exception):
    """Raised when there's a version conflict during save."""
    def __init__(self, expected_version: int, current_version: int, server_content: str):
        self.expected_version = expected_version
        self.current_version = current_version
        self.server_content = server_content
        super().__init__(
            f"Version conflict: expected {expected_version}, but current is {current_version}"
        )


class EncounterNotFoundError(Exception):
    """Raised when encounter is not found."""
    pass


@dataclass
class PatientSummary:
    """Summary of patient information for encounter context."""
    id: str
    name: str
    date_of_birth: str
    mrn: str
    gender: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "dateOfBirth": self.date_of_birth,
            "mrn": self.mrn,
            "gender": self.gender,
        }


@dataclass
class EncounterContext:
    """Clinical context for the encounter."""
    vitals: list[VitalSign] = field(default_factory=list)
    medications: list[MedicationRequest] = field(default_factory=list)
    allergies: list[AllergyIntolerance] = field(default_factory=list)
    problems: list[dict] = field(default_factory=list)
    recent_labs: list[LabResult] = field(default_factory=list)
    recent_visits: list[VisitNote] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "vitals": [v.to_bff_dict() for v in self.vitals],
            "medications": [m.to_bff_dict() for m in self.medications],
            "allergies": [a.to_bff_dict() for a in self.allergies],
            "problems": self.problems,
            "recentLabs": [l.to_bff_dict() for l in self.recent_labs],
            "recentVisits": [v.to_bff_dict() for v in self.recent_visits],
        }


@dataclass
class EncounterWithContext:
    """Full encounter with patient and clinical context."""
    encounter: Encounter
    patient: PatientSummary
    context: EncounterContext

    def to_dict(self) -> dict:
        return {
            "encounter": self.encounter.to_bff_dict(),
            "patient": self.patient.to_dict(),
            "context": self.context.to_dict(),
        }


@dataclass
class NoteSaveResult:
    """Result of saving an encounter note."""
    success: bool
    version: int
    word_count: int
    saved_at: datetime

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "version": self.version,
            "wordCount": self.word_count,
            "savedAt": self.saved_at.isoformat(),
        }


@dataclass
class NoteVersionSummary:
    """Summary of a note version."""
    id: str
    version: int
    word_count: int
    save_type: str
    created_at: datetime

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "version": self.version,
            "wordCount": self.word_count,
            "saveType": self.save_type,
            "createdAt": self.created_at.isoformat(),
        }


def count_words(text: str | None) -> int:
    """Count words in text."""
    if not text:
        return 0
    return len(text.split())


class EncounterNoteService:
    """
    Service for managing encounter notes.

    Provides:
    - Encounter creation with patient context
    - Note saving with optimistic locking
    - Version history for audit and recovery
    """

    def __init__(
        self,
        encounter_repo: EncounterRepository,
        encounter_note_version_repo: EncounterNoteVersionRepository,
        patient_repo: PatientRepository,
        allergy_repo: AllergyIntoleranceRepository,
        medication_request_repo: MedicationRequestRepository,
        vitals_repo: VitalSignRepository,
        lab_result_repo: LabResultRepository,
        visit_note_repo: VisitNoteRepository,
    ):
        self.encounter_repo = encounter_repo
        self.encounter_note_version_repo = encounter_note_version_repo
        self.patient_repo = patient_repo
        self.allergy_repo = allergy_repo
        self.medication_request_repo = medication_request_repo
        self.vitals_repo = vitals_repo
        self.lab_result_repo = lab_result_repo
        self.visit_note_repo = visit_note_repo

    async def get_encounter_with_context(
        self, encounter_id: str
    ) -> EncounterWithContext:
        """
        Get an encounter with full patient and clinical context.

        Args:
            encounter_id: The encounter ID

        Returns:
            EncounterWithContext with encounter, patient, and context

        Raises:
            EncounterNotFoundError: If encounter not found
        """
        # Get the encounter
        encounter = await self.encounter_repo.get(encounter_id)
        if not encounter:
            raise EncounterNotFoundError(f"Encounter {encounter_id} not found")

        patient_id = encounter.patient_id

        # Get patient info
        patient = await self.patient_repo.get(patient_id)
        if not patient:
            raise EncounterNotFoundError(f"Patient {patient_id} not found for encounter")

        # Build patient summary
        patient_summary = PatientSummary(
            id=patient.id,
            name=patient.display_name,
            date_of_birth=patient.birth_date.isoformat() if patient.birth_date else "",
            mrn=patient.mrn or "",
            gender=patient.gender.value if patient.gender else "unknown",
        )

        # Gather clinical context in parallel-ish (still sequential but organized)
        context = await self._build_encounter_context(patient_id, patient)

        return EncounterWithContext(
            encounter=encounter,
            patient=patient_summary,
            context=context,
        )

    async def _build_encounter_context(
        self, patient_id: str, patient: Patient
    ) -> EncounterContext:
        """Build clinical context for an encounter."""
        # Get recent vitals (last 30 days)
        vitals = await self.vitals_repo.list(patient_id=patient_id, days_back=30)

        # Get active medications
        medications = await self.medication_request_repo.list(
            patient_id=patient_id, status="active"
        )

        # Get allergies
        allergies = await self.allergy_repo.list(patient_id=patient_id)

        # Get problems from patient
        problems = []
        if patient.problem_list:
            for p in patient.problem_list:
                problems.append({
                    "name": p.name,
                    "icd10Code": p.icd10_code,
                    "status": p.status.value,
                    "priority": p.priority.value,
                    "isCritical": p.is_critical,
                })

        # Get recent labs (last 90 days)
        recent_labs = await self.lab_result_repo.list(
            patient_id=patient_id, days_back=90
        )
        # Limit to most recent 10
        recent_labs = recent_labs[:10] if len(recent_labs) > 10 else recent_labs

        # Get recent visits (last 180 days)
        recent_visits = await self.visit_note_repo.list(
            patient_id=patient_id, days_back=180
        )
        # Limit to most recent 5
        recent_visits = recent_visits[:5] if len(recent_visits) > 5 else recent_visits

        return EncounterContext(
            vitals=vitals,
            medications=medications,
            allergies=allergies,
            problems=problems,
            recent_labs=recent_labs,
            recent_visits=recent_visits,
        )

    async def save_note(
        self,
        encounter_id: str,
        content: str,
        expected_version: int,
        save_type: str = "auto",
    ) -> NoteSaveResult:
        """
        Save an encounter note with optimistic locking.

        Args:
            encounter_id: The encounter ID
            content: The note content
            expected_version: The version the client expects (for conflict detection)
            save_type: 'auto' or 'manual'

        Returns:
            NoteSaveResult with new version and metadata

        Raises:
            EncounterNotFoundError: If encounter not found
            VersionConflictError: If version mismatch (concurrent edit)
        """
        # Get the encounter
        encounter = await self.encounter_repo.get(encounter_id)
        if not encounter:
            raise EncounterNotFoundError(f"Encounter {encounter_id} not found")

        # Check for version conflict
        if encounter.note_version != expected_version:
            raise VersionConflictError(
                expected_version=expected_version,
                current_version=encounter.note_version,
                server_content=encounter.note_content or "",
            )

        # Calculate word count
        word_count = count_words(content)
        new_version = encounter.note_version + 1
        now = datetime.utcnow()

        # Create version history entry
        version_entry = EncounterNoteVersion(
            id=str(uuid.uuid4()),
            encounter=Reference(reference=f"Encounter/{encounter_id}"),
            version=new_version,
            content=content,
            word_count=word_count,
            save_type=SaveType(save_type) if save_type in ["auto", "manual"] else SaveType.AUTO,
            created_at=now,
        )
        await self.encounter_note_version_repo.create(version_entry)

        # Update the encounter with new note content
        encounter.note_content = content
        encounter.note_version = new_version
        encounter.note_word_count = word_count
        encounter.note_updated_at = now
        encounter.meta_last_updated = now

        await self.encounter_repo.update(encounter_id, encounter)

        return NoteSaveResult(
            success=True,
            version=new_version,
            word_count=word_count,
            saved_at=now,
        )

    async def get_note_versions(
        self, encounter_id: str
    ) -> list[NoteVersionSummary]:
        """
        Get version history for an encounter note.

        Args:
            encounter_id: The encounter ID

        Returns:
            List of version summaries, newest first
        """
        versions = await self.encounter_note_version_repo.get_by_encounter(encounter_id)
        return [
            NoteVersionSummary(
                id=v.id,
                version=v.version,
                word_count=v.word_count,
                save_type=v.save_type.value,
                created_at=v.created_at,
            )
            for v in versions
        ]

    async def get_note_version_content(
        self, encounter_id: str, version: int
    ) -> str | None:
        """
        Get the content of a specific note version.

        Args:
            encounter_id: The encounter ID
            version: The version number

        Returns:
            The content if found, None otherwise
        """
        version_entry = await self.encounter_note_version_repo.get_version(
            encounter_id, version
        )
        return version_entry.content if version_entry else None
