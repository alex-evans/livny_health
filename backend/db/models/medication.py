"""
Medication ORM model.
"""

from datetime import datetime

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class MedicationORM(Base):
    """ORM model for Medication resource."""

    __tablename__ = "medications"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Drug identification - code stored as JSONB (CodeableConcept)
    code: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Form and strength
    form: Mapped[str | None] = mapped_column(String(100), nullable=True)
    strength: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Clinical properties
    is_controlled: Mapped[bool] = mapped_column(Boolean, default=False)

    # Common dosing patterns
    common_dosing: Mapped[list] = mapped_column(JSONB, default=list)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="active")

    # Metadata
    meta_version_id: Mapped[str] = mapped_column(String(10), default="1")
    meta_last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
