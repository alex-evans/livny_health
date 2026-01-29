"""
Encounter Status Service.

Handles encounter status transitions with validation and audit logging.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, Any

from resources.encounter import Encounter, EncounterStatus
from resources.encounter_status_history import EncounterStatusHistory


class EncounterRepository(Protocol):
    """Protocol for encounter repository."""

    async def get(self, id: str) -> Encounter | None:
        ...

    async def update(self, resource: Encounter) -> Encounter:
        ...


class EncounterStatusHistoryRepository(Protocol):
    """Protocol for encounter status history repository."""

    async def create(self, resource: EncounterStatusHistory) -> EncounterStatusHistory:
        ...

    async def get_by_encounter(self, encounter_id: str) -> list[EncounterStatusHistory]:
        ...


class EncounterNoteVersionRepository(Protocol):
    """Protocol for encounter note version repository."""

    async def create(self, resource: Any) -> Any:
        ...


class InvalidStatusTransitionError(Exception):
    """Raised when an invalid status transition is attempted."""

    def __init__(
        self, current_status: str, new_status: str, allowed: list[str]
    ):
        self.current_status = current_status
        self.new_status = new_status
        self.allowed = allowed
        super().__init__(
            f"Cannot transition from '{current_status}' to '{new_status}'. "
            f"Allowed transitions: {allowed}"
        )


class EncounterNotFoundError(Exception):
    """Raised when an encounter is not found."""

    def __init__(self, encounter_id: str):
        self.encounter_id = encounter_id
        super().__init__(f"Encounter not found: {encounter_id}")


@dataclass
class StatusTransitionResult:
    """Result of a status transition."""

    encounter: Encounter
    history_entry: EncounterStatusHistory

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "encounterId": self.encounter.id,
            "previousStatus": self.history_entry.from_status,
            "newStatus": self.history_entry.to_status,
            "transitionedAt": self.history_entry.changed_at.isoformat() if self.history_entry.changed_at else None,
            "signedByName": self.encounter.signed_by_name,
        }


@dataclass
class AddendumResult:
    """Result of adding an addendum."""

    encounter: Encounter
    addendum_version: int
    addendum_content: str = ""
    addendum_reason: str = ""
    addendum_created_at: datetime | None = None
    addendum_created_by_name: str | None = None
    addendum_created_by_id: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "encounterId": self.encounter.id,
            "addendum": {
                "id": f"addendum-{self.addendum_version}",
                "content": self.addendum_content,
                "reason": self.addendum_reason,
                "createdAt": self.addendum_created_at.isoformat() if self.addendum_created_at else None,
                "createdById": self.addendum_created_by_id,
                "createdByName": self.addendum_created_by_name,
            },
        }


class EncounterStatusService:
    """
    Service for managing encounter status transitions.

    Validates transitions and maintains audit history.
    """

    # Valid status transitions
    VALID_TRANSITIONS: dict[EncounterStatus, list[EncounterStatus]] = {
        EncounterStatus.SCHEDULED: [EncounterStatus.IN_PROGRESS],
        EncounterStatus.IN_PROGRESS: [
            EncounterStatus.COMPLETED,
            EncounterStatus.SIGNED,
        ],
        EncounterStatus.COMPLETED: [
            EncounterStatus.IN_PROGRESS,  # Reopen
            EncounterStatus.SIGNED,
        ],
        EncounterStatus.SIGNED: [],  # No transitions allowed from signed
    }

    def __init__(
        self,
        encounter_repo: EncounterRepository,
        status_history_repo: EncounterStatusHistoryRepository,
        encounter_note_version_repo: EncounterNoteVersionRepository,
    ):
        self._encounter_repo = encounter_repo
        self._status_history_repo = status_history_repo
        self._encounter_note_version_repo = encounter_note_version_repo

    async def transition_status(
        self,
        encounter_id: str,
        new_status: EncounterStatus,
        user_id: str | None = None,
        user_name: str | None = None,
        reason: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> StatusTransitionResult:
        """
        Transition an encounter to a new status.

        Args:
            encounter_id: The encounter ID
            new_status: The target status
            user_id: The user making the change
            user_name: The user's display name
            reason: Optional reason for the transition
            ip_address: Optional IP address for audit
            user_agent: Optional user agent for audit

        Returns:
            StatusTransitionResult with updated encounter and history entry

        Raises:
            EncounterNotFoundError: If encounter doesn't exist
            InvalidStatusTransitionError: If transition is not allowed
        """
        # Get the encounter
        encounter = await self._encounter_repo.get(encounter_id)
        if not encounter:
            raise EncounterNotFoundError(encounter_id)

        # Validate the transition
        current_status = encounter.status
        allowed = self.VALID_TRANSITIONS.get(current_status, [])

        if new_status not in allowed:
            raise InvalidStatusTransitionError(
                current_status.value,
                new_status.value,
                [s.value for s in allowed],
            )

        # Update the encounter
        now = datetime.utcnow()
        old_status_value = encounter.status.value
        encounter.status = new_status
        encounter.meta_last_updated = now

        # Set appropriate timestamps based on transition
        if new_status == EncounterStatus.IN_PROGRESS:
            if current_status == EncounterStatus.SCHEDULED:
                encounter.opened_at = now
            elif current_status == EncounterStatus.COMPLETED:
                # Reopening
                encounter.reopened_at = now
        elif new_status == EncounterStatus.COMPLETED:
            encounter.completed_at = now
        elif new_status == EncounterStatus.SIGNED:
            encounter.signed_at = now
            encounter.signed_by_id = user_id
            encounter.signed_by_name = user_name

        # Save the encounter
        await self._encounter_repo.update(encounter_id, encounter)

        # Create history entry
        history_entry = EncounterStatusHistory(
            id=str(uuid.uuid4()),
            encounter_id=encounter_id,
            from_status=old_status_value,
            to_status=new_status.value,
            changed_by_id=user_id,
            changed_by_name=user_name,
            changed_at=now,
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self._status_history_repo.create(history_entry)

        return StatusTransitionResult(
            encounter=encounter,
            history_entry=history_entry,
        )

    async def get_audit_trail(
        self, encounter_id: str
    ) -> list[EncounterStatusHistory]:
        """
        Get the status change audit trail for an encounter.

        Args:
            encounter_id: The encounter ID

        Returns:
            List of status history entries, newest first
        """
        return await self._status_history_repo.get_by_encounter(encounter_id)

    async def create_addendum(
        self,
        encounter_id: str,
        content: str,
        reason: str,
        user_id: str | None = None,
        user_name: str | None = None,
    ) -> AddendumResult:
        """
        Add an addendum to a signed encounter.

        Addendums are stored as new note versions with the addendum content
        appended to the existing note.

        Args:
            encounter_id: The encounter ID
            content: The addendum content
            reason: The reason for the addendum
            user_id: The user creating the addendum
            user_name: The user's display name

        Returns:
            AddendumResult with updated encounter and addendum version

        Raises:
            EncounterNotFoundError: If encounter doesn't exist
            InvalidStatusTransitionError: If encounter is not signed
        """
        from resources.encounter_note_version import EncounterNoteVersion, SaveType
        from resources.core import Reference

        # Get the encounter
        encounter = await self._encounter_repo.get(encounter_id)
        if not encounter:
            raise EncounterNotFoundError(encounter_id)

        # Verify encounter is signed
        if encounter.status != EncounterStatus.SIGNED:
            raise InvalidStatusTransitionError(
                encounter.status.value,
                "addendum",
                ["addendum only allowed on signed encounters"],
            )

        # Format the addendum
        now = datetime.utcnow()
        addendum_header = (
            f"\n\n--- ADDENDUM ---\n"
            f"Date: {now.strftime('%Y-%m-%d %H:%M')}\n"
            f"Author: {user_name or 'Unknown'}\n"
            f"Reason: {reason}\n\n"
        )
        addendum_text = addendum_header + content

        # Update the note content
        original_content = encounter.note_content or ""
        new_content = original_content + addendum_text
        new_version = encounter.note_version + 1

        # Count words
        word_count = len(new_content.split()) if new_content.strip() else 0

        # Create a new version for the addendum
        version = EncounterNoteVersion(
            id=str(uuid.uuid4()),
            encounter=Reference(reference=f"Encounter/{encounter_id}"),
            version=new_version,
            content=new_content,
            word_count=word_count,
            save_type=SaveType.MANUAL,
            created_at=now,
        )
        await self._encounter_note_version_repo.create(version)

        # Update the encounter
        encounter.note_content = new_content
        encounter.note_version = new_version
        encounter.note_word_count = word_count
        encounter.note_updated_at = now
        encounter.meta_last_updated = now
        await self._encounter_repo.update(encounter_id, encounter)

        return AddendumResult(
            encounter=encounter,
            addendum_version=new_version,
            addendum_content=content,
            addendum_reason=reason,
            addendum_created_at=now,
            addendum_created_by_id=user_id,
            addendum_created_by_name=user_name,
        )

    def get_valid_transitions(
        self, current_status: EncounterStatus
    ) -> list[EncounterStatus]:
        """Get the valid transitions from a given status."""
        return self.VALID_TRANSITIONS.get(current_status, [])
