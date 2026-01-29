"""
API endpoints for managing encounters and encounter notes.
"""

from fastapi import APIRouter, HTTPException, Path, Query, Request
from pydantic import BaseModel
from typing import Literal

from bff import dependencies
from services import VersionConflictError, EncounterNotFoundError, InvalidStatusTransitionError
from resources import EncounterStatus


router = APIRouter(prefix='/encounters', tags=['encounters'])


class SaveNoteRequest(BaseModel):
    """Request body for saving an encounter note."""
    content: str
    expectedVersion: int
    saveType: Literal["auto", "manual"] = "auto"


class CreateEncounterRequest(BaseModel):
    """Request body for creating an encounter."""
    patientId: str
    providerId: str
    encounterType: str | None = None
    chiefComplaint: str | None = None


class TransitionStatusRequest(BaseModel):
    """Request body for transitioning encounter status."""
    newStatus: Literal["scheduled", "in_progress", "completed", "signed"]
    reason: str | None = None
    userId: str | None = None
    userName: str | None = None


class CreateAddendumRequest(BaseModel):
    """Request body for creating an addendum to a signed encounter."""
    content: str
    reason: str
    userId: str | None = None
    userName: str | None = None


@router.get("/{encounter_id}")
async def get_encounter(
    encounter_id: str = Path(..., description="The encounter ID"),
):
    """
    Get an encounter with full patient and clinical context.

    Returns:
    - Encounter details (id, status, type, chief complaint, note content/version)
    - Patient summary (id, name, DOB, MRN, gender)
    - Clinical context:
        - Recent vitals
        - Active medications
        - Allergies
        - Problem list
        - Recent labs
        - Recent visits
    """
    encounter_note_service = dependencies.get_encounter_note_service()

    try:
        result = await encounter_note_service.get_encounter_with_context(encounter_id)
        return result.to_dict()
    except EncounterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{encounter_id}/note")
async def save_encounter_note(
    request: SaveNoteRequest,
    encounter_id: str = Path(..., description="The encounter ID"),
):
    """
    Save an encounter note with optimistic locking.

    Uses version-based conflict detection:
    - Client sends expected version
    - Server checks if current version matches
    - If mismatch, returns 409 Conflict with server content

    Request body:
    - content: The note text content
    - expectedVersion: The version client is editing from
    - saveType: 'auto' (debounced auto-save) or 'manual' (user-triggered)

    Returns:
    - success: boolean
    - version: new version number
    - wordCount: updated word count
    - savedAt: timestamp of save
    """
    encounter_note_service = dependencies.get_encounter_note_service()

    try:
        result = await encounter_note_service.save_note(
            encounter_id=encounter_id,
            content=request.content,
            expected_version=request.expectedVersion,
            save_type=request.saveType,
        )
        return result.to_dict()
    except EncounterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except VersionConflictError as e:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "version_conflict",
                "message": str(e),
                "expectedVersion": e.expected_version,
                "currentVersion": e.current_version,
                "serverContent": e.server_content,
            }
        )


@router.get("/{encounter_id}/versions")
async def get_note_versions(
    encounter_id: str = Path(..., description="The encounter ID"),
):
    """
    Get version history for an encounter note.

    Returns list of versions (newest first) with:
    - id: version record ID
    - version: version number
    - wordCount: word count at that version
    - saveType: 'auto' or 'manual'
    - createdAt: when the version was created
    """
    encounter_note_service = dependencies.get_encounter_note_service()

    # First verify encounter exists
    encounter_repo = dependencies.get_encounter_repo()
    encounter = await encounter_repo.get(encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail=f"Encounter {encounter_id} not found")

    versions = await encounter_note_service.get_note_versions(encounter_id)
    return {
        "versions": [v.to_dict() for v in versions],
    }


@router.get("/{encounter_id}/versions/{version}")
async def get_note_version_content(
    encounter_id: str = Path(..., description="The encounter ID"),
    version: int = Path(..., description="The version number", ge=1),
):
    """
    Get the content of a specific note version.

    Useful for:
    - Viewing historical versions
    - Conflict resolution (comparing versions)
    - Recovery of previous content
    """
    encounter_note_service = dependencies.get_encounter_note_service()

    content = await encounter_note_service.get_note_version_content(
        encounter_id=encounter_id,
        version=version,
    )

    if content is None:
        raise HTTPException(
            status_code=404,
            detail=f"Version {version} not found for encounter {encounter_id}"
        )

    return {
        "encounterId": encounter_id,
        "version": version,
        "content": content,
    }


@router.patch("/{encounter_id}/status")
async def transition_encounter_status(
    request: TransitionStatusRequest,
    encounter_id: str = Path(..., description="The encounter ID"),
    http_request: Request = None,
):
    """
    Transition an encounter to a new status.

    Valid transitions:
    - scheduled -> in_progress
    - in_progress -> completed, signed
    - completed -> in_progress (reopen), signed
    - signed -> (no transitions allowed)

    Request body:
    - newStatus: The target status
    - reason: Optional reason for the transition
    - userId: Optional user ID making the change
    - userName: Optional user display name

    Returns:
    - encounter: The updated encounter
    - historyEntry: The audit trail entry created
    """
    encounter_status_service = dependencies.get_encounter_status_service()

    try:
        new_status = EncounterStatus(request.newStatus)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status: {request.newStatus}"
        )

    # Get request context for audit
    ip_address = None
    user_agent = None
    if http_request:
        ip_address = http_request.client.host if http_request.client else None
        user_agent = http_request.headers.get("user-agent", "")[:500]

    try:
        result = await encounter_status_service.transition_status(
            encounter_id=encounter_id,
            new_status=new_status,
            user_id=request.userId,
            user_name=request.userName,
            reason=request.reason,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return result.to_dict()
    except EncounterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidStatusTransitionError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_transition",
                "message": str(e),
                "currentStatus": e.current_status,
                "targetStatus": e.new_status,
                "allowedTransitions": e.allowed,
            }
        )


@router.get("/{encounter_id}/audit")
async def get_encounter_audit_trail(
    encounter_id: str = Path(..., description="The encounter ID"),
):
    """
    Get the status change audit trail for an encounter.

    Returns list of status history entries (newest first) with:
    - id: Entry ID
    - fromStatus: Previous status (null for initial creation)
    - toStatus: New status
    - changedByName: Name of user who made the change
    - changedAt: When the change occurred
    - reason: Optional reason for the change
    """
    encounter_status_service = dependencies.get_encounter_status_service()

    # First verify encounter exists
    encounter_repo = dependencies.get_encounter_repo()
    encounter = await encounter_repo.get(encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail=f"Encounter {encounter_id} not found")

    history = await encounter_status_service.get_audit_trail(encounter_id)
    return {
        "encounterId": encounter_id,
        "entries": [h.to_dict() for h in history],
    }


@router.post("/{encounter_id}/addendum")
async def create_encounter_addendum(
    request: CreateAddendumRequest,
    encounter_id: str = Path(..., description="The encounter ID"),
):
    """
    Add an addendum to a signed encounter.

    Addendums can only be added to encounters in 'signed' status.
    The addendum is appended to the existing note content with metadata.

    Request body:
    - content: The addendum text
    - reason: Why the addendum is being added
    - userId: Optional user ID creating the addendum
    - userName: Optional user display name

    Returns:
    - encounter: The updated encounter
    - addendumVersion: The new note version number
    """
    encounter_status_service = dependencies.get_encounter_status_service()

    try:
        result = await encounter_status_service.create_addendum(
            encounter_id=encounter_id,
            content=request.content,
            reason=request.reason,
            user_id=request.userId,
            user_name=request.userName,
        )
        return result.to_dict()
    except EncounterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidStatusTransitionError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_operation",
                "message": "Addendums can only be added to signed encounters",
                "currentStatus": e.current_status,
            }
        )


# Appointment-scoped encounter endpoint
appointment_router = APIRouter(prefix='/appointments', tags=['appointments'])


@appointment_router.get("/{appointment_id}/encounter")
async def get_encounter_by_appointment(
    appointment_id: str = Path(..., description="The appointment ID"),
):
    """
    Get the encounter associated with an appointment.

    Returns:
    - encounter: The encounter if one exists, null otherwise
    - appointmentId: The requested appointment ID
    """
    encounter_repo = dependencies.get_encounter_repo()

    # Find encounter with this appointment ID
    encounters = await encounter_repo.list()
    for encounter in encounters:
        if encounter.appointment and encounter.appointment.id == appointment_id:
            return {
                "appointmentId": appointment_id,
                "encounter": encounter.to_bff_dict(),
            }

    return {
        "appointmentId": appointment_id,
        "encounter": None,
    }


# Patient-scoped encounter endpoints
patient_router = APIRouter(prefix='/patients', tags=['patients'])


@patient_router.post("/{patient_id}/encounters")
async def create_encounter(
    request: CreateEncounterRequest,
    patient_id: str = Path(..., description="The patient ID"),
):
    """
    Create a new encounter for a patient.

    This is typically called when starting a visit from the schedule.

    Returns the newly created encounter with full patient context.
    """
    import uuid
    from datetime import datetime
    from resources import Encounter, EncounterStatus, EncounterClass, EncounterParticipant
    from resources.core import Reference, Period, CodeableConcept

    # Verify patient exists
    patient_repo = dependencies.get_patient_repo()
    patient = await patient_repo.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Verify provider exists
    practitioner_repo = dependencies.get_practitioner_repo()
    provider = await practitioner_repo.get(request.providerId)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Create the encounter
    encounter_id = str(uuid.uuid4())
    now = datetime.utcnow()

    encounter = Encounter(
        id=encounter_id,
        status=EncounterStatus.IN_PROGRESS,
        encounter_class=EncounterClass.AMBULATORY,
        type=CodeableConcept(
            code=request.encounterType or "office-visit",
            display=request.encounterType or "Office Visit",
        ) if request.encounterType else None,
        subject=Reference(reference=f"Patient/{patient_id}"),
        participants=[
            EncounterParticipant(
                individual=Reference(
                    reference=f"Practitioner/{request.providerId}",
                    display=provider.display_name,
                ),
                type="primary",
            )
        ],
        period=Period(start=now),
        chief_complaint=request.chiefComplaint,
        note_content="",
        note_version=1,
        note_word_count=0,
        note_updated_at=None,
        opened_at=now,  # Mark when encounter was opened
    )

    encounter_repo = dependencies.get_encounter_repo()
    await encounter_repo.create(encounter)

    # Return with full context
    encounter_note_service = dependencies.get_encounter_note_service()
    result = await encounter_note_service.get_encounter_with_context(encounter_id)
    return result.to_dict()
