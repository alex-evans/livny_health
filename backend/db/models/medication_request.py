"""
MedicationRequest ORM model.
"""

from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class MedicationRequestORM(Base):
    """ORM model for MedicationRequest resource."""

    __tablename__ = "medication_requests"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Status and intent
    status: Mapped[str] = mapped_column(String(50), default="active", index=True)
    intent: Mapped[str] = mapped_column(String(50), default="order")

    # What medication - CodeableConcept as JSONB
    medication: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Medication details
    brand_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    strength: Mapped[str | None] = mapped_column(String(100), nullable=True)
    form: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_controlled: Mapped[bool] = mapped_column(Boolean, default=False)

    # For whom - patient reference
    subject_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("patients.id"), index=True
    )

    # Context - encounter reference (optional)
    encounter_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Who wrote it - requester reference as JSONB
    requester: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # When
    authored_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Dosage instructions as JSONB array
    dosage_instruction: Mapped[list] = mapped_column(JSONB, default=list)

    # Dispensing
    dispense_quantity: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    dispense_refills: Mapped[int] = mapped_column(Integer, default=0)

    # Status reason
    status_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Additional clinical info
    pharmacy: Mapped[str | None] = mapped_column(String(255), nullable=True)
    indication: Mapped[str | None] = mapped_column(String(500), nullable=True)
    prescriber_notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    drug_class: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Metadata
    meta_version_id: Mapped[str] = mapped_column(String(10), default="1")
    meta_last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
