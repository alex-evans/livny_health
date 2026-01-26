"""
Practitioner ORM model.
"""

from datetime import datetime

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class PractitionerORM(Base):
    """ORM model for Practitioner resource."""

    __tablename__ = "practitioners"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Core demographics - split HumanName for querying
    name_family: Mapped[str] = mapped_column(String(255), index=True)
    name_given: Mapped[list] = mapped_column(JSONB, default=list)
    name_prefix: Mapped[list] = mapped_column(JSONB, default=list)
    name_suffix: Mapped[list] = mapped_column(JSONB, default=list)

    gender: Mapped[str] = mapped_column(String(20), default="unknown")

    # Status
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Complex nested data as JSONB
    identifiers: Mapped[list] = mapped_column(JSONB, default=list)
    telecom: Mapped[list] = mapped_column(JSONB, default=list)
    qualifications: Mapped[list] = mapped_column(JSONB, default=list)

    # Metadata
    meta_version_id: Mapped[str] = mapped_column(String(10), default="1")
    meta_last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
