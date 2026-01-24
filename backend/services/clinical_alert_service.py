"""
Clinical Alert Service.

Orchestrates alert generation, retrieval, acknowledgment, and dismissal.
Alerts are generated on-demand when a patient chart is opened.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from resources import (
    ClinicalAlert,
    ClinicalAlertRepository,
    AlertSummary,
    AlertStatus,
)
from services.alert_generators import AlertGenerator


@dataclass
class AlertsResponse:
    """Response containing alerts for a patient."""
    alerts: list[ClinicalAlert]
    summary: AlertSummary

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "alerts": [a.to_dict() for a in self.alerts],
            "summary": self.summary.to_dict(),
        }


class ClinicalAlertService:
    """
    Service for managing clinical alerts.

    Coordinates alert generation from multiple sources and manages
    alert lifecycle (active -> acknowledged/dismissed).
    """

    def __init__(
        self,
        alert_repo: ClinicalAlertRepository,
        generators: list[AlertGenerator],
    ):
        """
        Initialize the clinical alert service.

        Args:
            alert_repo: Repository for storing alert state
            generators: List of alert generators for different alert types
        """
        self.alert_repo = alert_repo
        self.generators = generators

    async def get_patient_alerts(
        self,
        patient_id: str,
        status: AlertStatus | list[AlertStatus] | None = "active",
        regenerate: bool = True,
    ) -> AlertsResponse:
        """
        Get alerts for a patient.

        Args:
            patient_id: The patient ID
            status: Filter by status (default: active only)
            regenerate: Whether to regenerate alerts from source data

        Returns:
            AlertsResponse with alerts and summary
        """
        if regenerate:
            await self._regenerate_alerts(patient_id)

        alerts = await self.alert_repo.get_by_patient(patient_id, status=status)
        summary = await self.alert_repo.get_alert_summary(patient_id)

        return AlertsResponse(alerts=alerts, summary=summary)

    async def get_alert_summary(self, patient_id: str) -> AlertSummary:
        """
        Get summary counts of active alerts for a patient.

        Args:
            patient_id: The patient ID

        Returns:
            AlertSummary with counts by severity
        """
        # Regenerate to ensure counts are current
        await self._regenerate_alerts(patient_id)
        return await self.alert_repo.get_alert_summary(patient_id)

    async def acknowledge_alert(
        self,
        patient_id: str,
        alert_id: str,
        by: str,
        note: str | None = None,
    ) -> ClinicalAlert | None:
        """
        Acknowledge an alert.

        Args:
            patient_id: The patient ID (for validation)
            alert_id: The alert ID to acknowledge
            by: Who is acknowledging (provider ID or name)
            note: Optional acknowledgment note

        Returns:
            Updated ClinicalAlert or None if not found
        """
        alert = await self.alert_repo.get(alert_id)
        if alert is None or alert.patient_id != patient_id:
            return None

        return await self.alert_repo.acknowledge(alert_id, by=by, note=note)

    async def dismiss_alert(
        self,
        patient_id: str,
        alert_id: str,
        by: str,
        reason: str | None = None,
    ) -> ClinicalAlert | None:
        """
        Dismiss an alert.

        Args:
            patient_id: The patient ID (for validation)
            alert_id: The alert ID to dismiss
            by: Who is dismissing (provider ID or name)
            reason: Optional dismissal reason

        Returns:
            Updated ClinicalAlert or None if not found
        """
        alert = await self.alert_repo.get(alert_id)
        if alert is None or alert.patient_id != patient_id:
            return None

        return await self.alert_repo.dismiss(alert_id, by=by, reason=reason)

    async def _regenerate_alerts(self, patient_id: str) -> None:
        """
        Regenerate alerts from source data.

        This runs all generators and upserts the results,
        preserving acknowledged/dismissed states.
        """
        for generator in self.generators:
            try:
                alerts = await generator.generate_alerts(patient_id)
                for alert in alerts:
                    await self.alert_repo.upsert_alert(alert)
            except Exception as e:
                # Log error but don't fail - other generators can still run
                print(f"Error in alert generator {generator.__class__.__name__}: {e}")


class ClinicalAlertServiceBuilder:
    """Builder for creating ClinicalAlertService with all generators wired."""

    @staticmethod
    def build(
        alert_repo: ClinicalAlertRepository,
        lab_result_repo=None,
        vitals_repo=None,
        imaging_repo=None,
        patient_repo=None,
        medication_request_repo=None,
    ) -> ClinicalAlertService:
        """
        Build a ClinicalAlertService with appropriate generators.

        Args:
            alert_repo: Repository for alert state
            lab_result_repo: Optional lab result repository
            vitals_repo: Optional vitals repository
            imaging_repo: Optional imaging repository
            patient_repo: Optional patient repository
            medication_request_repo: Optional medication request repository

        Returns:
            Configured ClinicalAlertService
        """
        from services.alert_generators import (
            LabAlertGenerator,
            VitalAlertGenerator,
            ImagingAlertGenerator,
            ScreeningAlertGenerator,
            ChronicDiseaseAlertGenerator,
        )

        generators: list[AlertGenerator] = []

        if lab_result_repo:
            generators.append(LabAlertGenerator(lab_result_repo))

        if vitals_repo:
            generators.append(VitalAlertGenerator(vitals_repo))

        if imaging_repo:
            generators.append(ImagingAlertGenerator(imaging_repo))

        if patient_repo:
            generators.append(ScreeningAlertGenerator(patient_repo))

            if lab_result_repo:
                generators.append(
                    ChronicDiseaseAlertGenerator(patient_repo, lab_result_repo)
                )

        return ClinicalAlertService(alert_repo=alert_repo, generators=generators)
