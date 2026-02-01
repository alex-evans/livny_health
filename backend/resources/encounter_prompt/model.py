"""
Encounter Prompt resource model.

Represents contextual prompts that guide physicians through encounters,
generated based on visit type, patient conditions, clinical alerts, and follow-up items.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Literal

from resources.core import DomainResource


PromptType = Literal[
    "chief_complaint",
    "review",
    "alert",
    "follow_up",
    "assessment",
    "plan",
    "free_text",
]

PromptStatus = Literal["pending", "addressed", "skipped", "deferred"]

ViewerSection = Literal["subjective", "objective", "assessment", "plan"]

AlertLevel = Literal["critical", "high", "medium", "low"]


@dataclass
class EncounterPrompt(DomainResource):
    """
    A contextual prompt for guiding a physician through an encounter.

    Prompts are generated when an encounter is opened and guide the physician
    through reviewing relevant patient information and documenting the visit.
    """
    resource_type: ClassVar[str] = "EncounterPrompt"

    # Required fields
    encounter_id: str = ""
    prompt_type: PromptType = "review"
    prompt_text: str = ""
    prompt_order: int = 0
    status: PromptStatus = "pending"

    # Optional classification
    prompt_subtype: str | None = None  # vitals, medications, a1c_review, etc.

    # Response tracking
    response_data: dict = field(default_factory=dict)

    # Display configuration
    viewer_section: ViewerSection | None = None  # Where in the note this applies
    alert_level: AlertLevel | None = None  # For alert-type prompts
    is_skippable: bool = True

    # Source tracking
    source_reference: str | None = None  # Reference to source entity (e.g., condition ID)
    source_context: dict = field(default_factory=dict)  # Additional context about the source

    # Resolution tracking
    addressed_at: datetime | None = None
    addressed_by_id: str | None = None

    def address(self, by_id: str, response: dict | None = None) -> None:
        """Mark the prompt as addressed with optional response data."""
        self.status = "addressed"
        self.addressed_at = datetime.utcnow()
        self.addressed_by_id = by_id
        if response is not None:
            self.response_data = response
        self.meta_last_updated = datetime.utcnow()

    def skip(self, by_id: str, reason: str | None = None) -> None:
        """Mark the prompt as skipped."""
        if not self.is_skippable:
            raise ValueError("This prompt cannot be skipped")
        self.status = "skipped"
        self.addressed_at = datetime.utcnow()
        self.addressed_by_id = by_id
        if reason:
            self.response_data = {"skip_reason": reason}
        self.meta_last_updated = datetime.utcnow()

    def defer(self, by_id: str) -> None:
        """Mark the prompt as deferred for later."""
        self.status = "deferred"
        self.addressed_at = datetime.utcnow()
        self.addressed_by_id = by_id
        self.meta_last_updated = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "resourceType": self.resource_type,
            "encounterId": self.encounter_id,
            "promptType": self.prompt_type,
            "promptSubtype": self.prompt_subtype,
            "promptText": self.prompt_text,
            "promptOrder": self.prompt_order,
            "status": self.status,
            "responseData": self.response_data,
            "viewerSection": self.viewer_section,
            "alertLevel": self.alert_level,
            "isSkippable": self.is_skippable,
            "sourceReference": self.source_reference,
            "sourceContext": self.source_context,
            "addressedAt": self.addressed_at.isoformat() if self.addressed_at else None,
            "addressedById": self.addressed_by_id,
            "metaVersionId": self.meta_version_id,
            "metaLastUpdated": self.meta_last_updated.isoformat(),
        }

    def to_bff_dict(self) -> dict:
        """Convert to BFF-friendly format."""
        return self.to_dict()


@dataclass
class PromptGenerationResult:
    """Result of generating prompts for an encounter."""
    prompts: list[EncounterPrompt] = field(default_factory=list)
    total_count: int = 0
    pending_count: int = 0
    critical_count: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "prompts": [p.to_dict() for p in self.prompts],
            "totalCount": self.total_count,
            "pendingCount": self.pending_count,
            "criticalCount": self.critical_count,
        }
