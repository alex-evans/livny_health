"""
Patient ORM model.
"""

from datetime import date, datetime

from sqlalchemy import String, Date, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class PatientORM(Base):
    """ORM model for Patient resource."""

    __tablename__ = "patients"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Core demographics - split HumanName into columns for querying
    name_family: Mapped[str] = mapped_column(String(255), index=True)
    name_given: Mapped[list] = mapped_column(JSONB, default=list)
    name_prefix: Mapped[list] = mapped_column(JSONB, default=list)
    name_suffix: Mapped[list] = mapped_column(JSONB, default=list)

    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str] = mapped_column(String(20), default="unknown")

    # Status
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Complex nested data as JSONB
    identifiers: Mapped[list] = mapped_column(JSONB, default=list)
    telecom: Mapped[list] = mapped_column(JSONB, default=list)
    address: Mapped[list] = mapped_column(JSONB, default=list)
    problem_list: Mapped[list] = mapped_column(JSONB, default=list)
    recent_vitals: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    insurance: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    allergy_review_status: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Metadata
    meta_version_id: Mapped[str] = mapped_column(String(10), default="1")
    meta_last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
