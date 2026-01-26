"""
VisitNote ORM model.
"""

from datetime import datetime

from sqlalchemy import String, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class VisitNoteORM(Base):
    """ORM model for VisitNote resource."""

    __tablename__ = "visit_notes"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Reference to the encounter this note is for
    encounter_id: Mapped[str] = mapped_column(String(64), index=True)

    # Reference to the patient
    subject_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("patients.id"), index=True
    )

    # Visit details
    visit_type: Mapped[str] = mapped_column(String(50), default="office_visit")
    status: Mapped[str] = mapped_column(String(50), default="completed")
    date: Mapped[datetime] = mapped_column(DateTime, index=True)
    chief_complaint: Mapped[str] = mapped_column(String(500), default="")
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Provider as JSONB
    provider: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Diagnoses as JSONB array
    diagnoses: Mapped[list] = mapped_column(JSONB, default=list)

    # Clinical documentation as JSONB
    soap_note: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    vitals: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    medications: Mapped[list] = mapped_column(JSONB, default=list)
    orders: Mapped[list] = mapped_column(JSONB, default=list)

    # Brief summary
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    # Timeline enhancement fields
    has_critical_findings: Mapped[bool] = mapped_column(Boolean, default=False)
    critical_findings_summary: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    has_follow_up_required: Mapped[bool] = mapped_column(Boolean, default=False)
    follow_up_summary: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Metadata
    meta_version_id: Mapped[str] = mapped_column(String(10), default="1")
    meta_last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
