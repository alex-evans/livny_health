"""
Imaging Study resource model.

Represents radiology studies and reports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Literal

from resources.core import DomainResource, Reference


ImagingModality = Literal["CT", "MRI", "XR", "US", "NM", "PET", "FLUORO", "MAMMO"]
ReportStatus = Literal["final", "preliminary", "pending", "addendum"]


# Full names for modalities
MODALITY_NAMES: dict[ImagingModality, str] = {
    "CT": "Computed Tomography",
    "MRI": "Magnetic Resonance Imaging",
    "XR": "X-Ray",
    "US": "Ultrasound",
    "NM": "Nuclear Medicine",
    "PET": "Positron Emission Tomography",
    "FLUORO": "Fluoroscopy",
    "MAMMO": "Mammography",
}


@dataclass
class ComparisonStudy:
    """Reference to a prior study used for comparison."""
    study_id: str
    date: datetime
    modality: ImagingModality
    body_part: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "studyId": self.study_id,
            "date": self.date.isoformat(),
            "modality": self.modality,
            "bodyPart": self.body_part,
        }


@dataclass
class RadiologyReport:
    """Structured radiology report with FHIR-style sections."""
    clinical_indication: str
    technique: str
    findings: str
    impression: str
    comparison_studies: list[ComparisonStudy] = field(default_factory=list)
    critical_finding: bool = False
    addendum: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "clinicalIndication": self.clinical_indication,
            "technique": self.technique,
            "findings": self.findings,
            "impression": self.impression,
            "comparisonStudies": [c.to_dict() for c in self.comparison_studies],
            "criticalFinding": self.critical_finding,
            "addendum": self.addendum,
        }


@dataclass
class ImagingStudy(DomainResource):
    """
    A radiology imaging study.

    Represents a single imaging study (e.g., CT scan, MRI, X-ray)
    with its associated report.
    """
    resource_type: ClassVar[str] = "ImagingStudy"

    # Study identification
    patient_id: str = ""
    accession_number: str | None = None

    # What type of study
    modality: ImagingModality = "XR"
    modality_name: str = ""
    body_part: str = ""

    # When and where
    study_date: datetime = field(default_factory=datetime.utcnow)
    facility: str = ""

    # Who ordered/read
    ordering_provider: str = ""
    reading_radiologist: str | None = None

    # Clinical context
    indication: str = ""

    # Study details
    series_count: int = 0
    image_count: int = 0
    has_images: bool = True

    # Report
    report_status: ReportStatus = "pending"
    report: RadiologyReport | None = None

    def __post_init__(self):
        """Set modality_name if not provided."""
        if not self.modality_name and self.modality:
            self.modality_name = MODALITY_NAMES.get(self.modality, self.modality)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "resourceType": self.resource_type,
            "patientId": self.patient_id,
            "accessionNumber": self.accession_number,
            "modality": self.modality,
            "modalityName": self.modality_name,
            "bodyPart": self.body_part,
            "studyDate": self.study_date.isoformat(),
            "facility": self.facility,
            "orderingProvider": self.ordering_provider,
            "readingRadiologist": self.reading_radiologist,
            "indication": self.indication,
            "seriesCount": self.series_count,
            "imageCount": self.image_count,
            "hasImages": self.has_images,
            "reportStatus": self.report_status,
            "report": self.report.to_dict() if self.report else None,
        }

    def to_bff_dict(self) -> dict:
        """Convert to BFF-friendly format."""
        return self.to_dict()
