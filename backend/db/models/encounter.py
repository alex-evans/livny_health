"""
Encounter ORM model.
"""

from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class EncounterORM(Base):
    """ORM model for Encounter resource."""

    __tablename__ = "encounters"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="planned", index=True)

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

    # Metadata
    meta_version_id: Mapped[str] = mapped_column(String(10), default="1")
    meta_last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
