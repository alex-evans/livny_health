"""
AllergyIntolerance ORM model.
"""

from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class AllergyIntoleranceORM(Base):
    """ORM model for AllergyIntolerance resource."""

    __tablename__ = "allergy_intolerances"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Who has the allergy - patient reference
    patient_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("patients.id"), index=True
    )

    # What they're allergic to - CodeableConcept as JSONB
    code: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Category and criticality
    category: Mapped[str] = mapped_column(String(50), default="medication")
    criticality: Mapped[str] = mapped_column(String(50), default="high")

    # Status
    clinical_status: Mapped[str] = mapped_column(String(50), default="active")
    verification_status: Mapped[str] = mapped_column(String(50), default="confirmed")

    # Reactions as JSONB array
    reactions: Mapped[list] = mapped_column(JSONB, default=list)

    # When recorded
    recorded_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    recorder: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    last_updated: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Metadata
    meta_version_id: Mapped[str] = mapped_column(String(10), default="1")
    meta_last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
