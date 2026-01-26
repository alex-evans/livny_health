"""
SocialFamilyHistory ORM model.
"""

from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class SocialFamilyHistoryORM(Base):
    """ORM model for SocialFamilyHistory resource."""

    __tablename__ = "social_family_histories"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # For whom
    subject_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("patients.id"), index=True, unique=True
    )

    # History sections as JSONB - complex nested structures
    social_history: Mapped[dict] = mapped_column(JSONB, default=dict)
    family_history: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Calculated risk assessments as JSONB array
    risk_assessments: Mapped[list] = mapped_column(JSONB, default=list)

    # Metadata
    meta_version_id: Mapped[str] = mapped_column(String(10), default="1")
    meta_last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
