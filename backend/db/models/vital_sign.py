"""
VitalSign ORM model.
"""

from datetime import datetime

from sqlalchemy import String, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class VitalSignORM(Base):
    """ORM model for VitalSign resource."""

    __tablename__ = "vital_signs"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # What vital
    vital_type: Mapped[str] = mapped_column(String(50), index=True)

    # Result value
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="normal", index=True)

    # For whom
    subject_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("patients.id"), index=True
    )

    # When
    recorded_at: Mapped[datetime] = mapped_column(DateTime, index=True)

    # Additional context
    recorded_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Metadata
    meta_version_id: Mapped[str] = mapped_column(String(10), default="1")
    meta_last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
