"""
Appointment ORM model.
"""

from datetime import datetime

from sqlalchemy import String, DateTime, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class AppointmentORM(Base):
    """ORM model for Appointment resource."""

    __tablename__ = "appointments"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="booked", index=True)

    # Type - CodeableConcept as JSONB
    appointment_type: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Timing
    start: Mapped[datetime] = mapped_column(DateTime, index=True)
    end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)

    # Reason
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Participants as JSONB array
    participants: Mapped[list] = mapped_column(JSONB, default=list)

    # Clinical flags as JSONB array
    flags: Mapped[list] = mapped_column(JSONB, default=list)

    # Double-booking indicator
    is_double_booked: Mapped[bool] = mapped_column(Boolean, default=False)

    # Metadata
    meta_version_id: Mapped[str] = mapped_column(String(10), default="1")
    meta_last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
