"""
LabResult ORM model.
"""

from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class LabResultORM(Base):
    """ORM model for LabResult resource."""

    __tablename__ = "lab_results"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # What test
    test_name: Mapped[str] = mapped_column(String(255), index=True)
    test_code: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Result value
    value: Mapped[str] = mapped_column(String(100))
    unit: Mapped[str] = mapped_column(String(50))
    reference_range: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="normal", index=True)

    # For whom
    subject_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("patients.id"), index=True
    )

    # When
    collection_date: Mapped[datetime] = mapped_column(DateTime, index=True)

    # Additional context
    performing_lab: Mapped[str | None] = mapped_column(String(255), nullable=True)
    panel_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Data completeness tracking
    last_updated: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=True)
    acknowledged_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Metadata
    meta_version_id: Mapped[str] = mapped_column(String(10), default="1")
    meta_last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
