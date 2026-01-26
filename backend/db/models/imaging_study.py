"""
ImagingStudy ORM model.
"""

from datetime import datetime

from sqlalchemy import String, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class ImagingStudyORM(Base):
    """ORM model for ImagingStudy resource."""

    __tablename__ = "imaging_studies"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Study identification
    patient_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("patients.id"), index=True
    )
    accession_number: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # What type of study
    modality: Mapped[str] = mapped_column(String(20), default="XR", index=True)
    modality_name: Mapped[str] = mapped_column(String(100), default="")
    body_part: Mapped[str] = mapped_column(String(100), default="")

    # When and where
    study_date: Mapped[datetime] = mapped_column(DateTime, index=True)
    facility: Mapped[str] = mapped_column(String(255), default="")

    # Who ordered/read
    ordering_provider: Mapped[str] = mapped_column(String(255), default="")
    reading_radiologist: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Clinical context
    indication: Mapped[str] = mapped_column(String(500), default="")

    # Study details
    series_count: Mapped[int] = mapped_column(Integer, default=0)
    image_count: Mapped[int] = mapped_column(Integer, default=0)
    has_images: Mapped[bool] = mapped_column(Boolean, default=True)

    # Report status and content as JSONB
    report_status: Mapped[str] = mapped_column(String(50), default="pending")
    report: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Metadata
    meta_version_id: Mapped[str] = mapped_column(String(10), default="1")
    meta_last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
