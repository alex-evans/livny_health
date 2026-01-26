"""
ImagingStudy mapper for domain <-> ORM conversion.
"""

from datetime import datetime

from mappers.base import Mapper
from db.models.imaging_study import ImagingStudyORM
from resources.imaging_study import (
    ImagingStudy,
    RadiologyReport,
    ComparisonStudy,
    MODALITY_NAMES,
)


class ImagingStudyMapper(Mapper[ImagingStudy, ImagingStudyORM]):
    """Mapper for ImagingStudy <-> ImagingStudyORM conversion."""

    def to_orm(self, domain: ImagingStudy) -> ImagingStudyORM:
        """Convert ImagingStudy domain model to ORM."""
        return ImagingStudyORM(
            id=domain.id,
            patient_id=domain.patient_id,
            accession_number=domain.accession_number,
            modality=domain.modality,
            modality_name=domain.modality_name,
            body_part=domain.body_part,
            study_date=domain.study_date,
            facility=domain.facility,
            ordering_provider=domain.ordering_provider,
            reading_radiologist=domain.reading_radiologist,
            indication=domain.indication,
            series_count=domain.series_count,
            image_count=domain.image_count,
            has_images=domain.has_images,
            report_status=domain.report_status,
            report=self._report_to_dict(domain.report) if domain.report else None,
            meta_version_id=domain.meta_version_id,
            meta_last_updated=domain.meta_last_updated,
        )

    def to_domain(self, orm: ImagingStudyORM) -> ImagingStudy:
        """Convert ImagingStudyORM to ImagingStudy domain model."""
        return ImagingStudy(
            id=orm.id,
            patient_id=orm.patient_id,
            accession_number=orm.accession_number,
            modality=orm.modality,
            modality_name=orm.modality_name
            or MODALITY_NAMES.get(orm.modality, orm.modality),
            body_part=orm.body_part,
            study_date=orm.study_date,
            facility=orm.facility,
            ordering_provider=orm.ordering_provider,
            reading_radiologist=orm.reading_radiologist,
            indication=orm.indication,
            series_count=orm.series_count,
            image_count=orm.image_count,
            has_images=orm.has_images,
            report_status=orm.report_status,
            report=self._dict_to_report(orm.report) if orm.report else None,
            meta_version_id=orm.meta_version_id,
            meta_last_updated=orm.meta_last_updated,
        )

    def _report_to_dict(self, r: RadiologyReport) -> dict:
        return {
            "clinical_indication": r.clinical_indication,
            "technique": r.technique,
            "findings": r.findings,
            "impression": r.impression,
            "comparison_studies": [
                {
                    "study_id": cs.study_id,
                    "date": cs.date.isoformat(),
                    "modality": cs.modality,
                    "body_part": cs.body_part,
                }
                for cs in r.comparison_studies
            ],
            "critical_finding": r.critical_finding,
            "addendum": r.addendum,
        }

    def _dict_to_report(self, d: dict) -> RadiologyReport:
        comparison_studies = []
        for cs in d.get("comparison_studies", []):
            comparison_studies.append(
                ComparisonStudy(
                    study_id=cs["study_id"],
                    date=datetime.fromisoformat(cs["date"]),
                    modality=cs["modality"],
                    body_part=cs["body_part"],
                )
            )
        return RadiologyReport(
            clinical_indication=d.get("clinical_indication", ""),
            technique=d.get("technique", ""),
            findings=d.get("findings", ""),
            impression=d.get("impression", ""),
            comparison_studies=comparison_studies,
            critical_finding=d.get("critical_finding", False),
            addendum=d.get("addendum"),
        )
