"""
Encounter ORM model.
"""

from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class EncounterORM(Base):
    """ORM model for Encounter resource."""

    __tablename__ = "encounters"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="scheduled", index=True)

    # Classification
    encounter_class: Mapped[str] = mapped_column(String(20), default="AMB")

    # Type - CodeableConcept as JSONB
    type: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Who is the patient
    subject_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("patients.id"), index=True
    )

    # Participants as JSONB array
    participants: Mapped[list] = mapped_column(JSONB, default=list)

    # Period as JSONB
    period: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Reason for visit as JSONB array
    reason: Mapped[list] = mapped_column(JSONB, default=list)
    chief_complaint: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Link to appointment
    appointment_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Note fields (migration 002)
    note_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    note_version: Mapped[int] = mapped_column(Integer, default=1)
    note_word_count: Mapped[int] = mapped_column(Integer, default=0)
    note_updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Workflow timestamps (migration 003)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    signed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reopened_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Signature tracking (migration 003)
    signed_by_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    signed_by_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Metadata
    meta_version_id: Mapped[str] = mapped_column(String(10), default="1")
    meta_last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
