"""
EncounterPrompt ORM model.
"""

from datetime import datetime

from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class EncounterPromptORM(Base):
    """ORM model for EncounterPrompt resource."""

    __tablename__ = "encounter_prompts"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Required fields
    encounter_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("encounters.id"), index=True
    )
    prompt_type: Mapped[str] = mapped_column(String(50), default="review")
    prompt_subtype: Mapped[str | None] = mapped_column(String(50), nullable=True)
    prompt_text: Mapped[str] = mapped_column(Text, default="")
    prompt_order: Mapped[int] = mapped_column(Integer, default=0)

    # Status tracking
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    response_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Display configuration
    viewer_section: Mapped[str | None] = mapped_column(String(50), nullable=True)
    alert_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_skippable: Mapped[bool] = mapped_column(Boolean, default=True)

    # Source tracking
    source_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_context: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Resolution tracking
    addressed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    addressed_by_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Metadata
    meta_version_id: Mapped[str] = mapped_column(String(10), default="1")
    meta_last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
