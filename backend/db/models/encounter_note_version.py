"""
Encounter Note Version ORM model.
"""

from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class EncounterNoteVersionORM(Base):
    """ORM model for EncounterNoteVersion resource."""

    __tablename__ = "encounter_note_versions"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Reference to encounter
    encounter_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("encounters.id"), index=True
    )

    # Version number
    version: Mapped[int] = mapped_column(Integer, nullable=False)

    # Content
    content: Mapped[str] = mapped_column(Text, default="")
    word_count: Mapped[int] = mapped_column(Integer, default=0)

    # Save type: 'auto' or 'manual'
    save_type: Mapped[str] = mapped_column(String(20), default="auto")

    # When this version was created
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Metadata
    meta_version_id: Mapped[str] = mapped_column(String(10), default="1")
    meta_last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
