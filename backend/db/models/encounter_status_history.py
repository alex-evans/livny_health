"""
Encounter Status History ORM model.

Tracks all status transitions for audit purposes.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class EncounterStatusHistoryORM(Base):
    """ORM model for Encounter Status History - audit trail for status changes."""

    __tablename__ = "encounter_status_history"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Reference to encounter
    encounter_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("encounters.id"), index=True
    )

    # Status transition
    from_status: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # null for initial creation
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)

    # Who made the change
    changed_by_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    changed_by_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # When
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Reason for change (optional)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Request context for audit
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True
    )  # IPv6 max length
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Metadata
    meta_version_id: Mapped[str] = mapped_column(String(10), default="1")
    meta_last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
