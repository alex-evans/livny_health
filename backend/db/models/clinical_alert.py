"""
ClinicalAlert ORM model.
"""

from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class ClinicalAlertORM(Base):
    """ORM model for ClinicalAlert resource."""

    __tablename__ = "clinical_alerts"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Required fields
    patient_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("patients.id"), index=True
    )
    alert_type: Mapped[str] = mapped_column(String(50), default="critical_lab")
    severity: Mapped[str] = mapped_column(String(50), default="medium", index=True)
    status: Mapped[str] = mapped_column(String(50), default="active", index=True)
    title: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(String(1000), default="")
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Source information
    source: Mapped[str] = mapped_column(String(100), default="")
    source_id: Mapped[str] = mapped_column(String(64), default="")
    source_link: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Additional context as JSONB
    context: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Recommended actions as JSONB array
    recommended_actions: Mapped[list] = mapped_column(JSONB, default=list)

    # Acknowledgment tracking as JSONB
    acknowledgment: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Dismissal tracking
    dismissed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    dismissed_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    dismissed_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Metadata
    meta_version_id: Mapped[str] = mapped_column(String(10), default="1")
    meta_last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
