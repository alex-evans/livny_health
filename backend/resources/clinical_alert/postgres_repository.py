"""
PostgreSQL repository for ClinicalAlert resources.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from resources.core.postgres_repository import PostgresRepository
from resources.clinical_alert.model import ClinicalAlert, AlertStatus, AlertSummary
from db.models.clinical_alert import ClinicalAlertORM
from mappers.clinical_alert import ClinicalAlertMapper


class PostgresClinicalAlertRepository(
    PostgresRepository[ClinicalAlert, ClinicalAlertORM]
):
    """PostgreSQL repository for ClinicalAlert resources."""

    orm_class = ClinicalAlertORM
    mapper = ClinicalAlertMapper()

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__(session_factory)

    def _apply_filters(self, stmt, **filters: Any):
        """Apply ClinicalAlert-specific filters."""
        if filters.get("patient_id"):
            stmt = stmt.where(ClinicalAlertORM.patient_id == filters["patient_id"])
        if filters.get("status"):
            stmt = stmt.where(ClinicalAlertORM.status == filters["status"])
        if filters.get("severity"):
            stmt = stmt.where(ClinicalAlertORM.severity == filters["severity"])
        if filters.get("alert_type"):
            stmt = stmt.where(ClinicalAlertORM.alert_type == filters["alert_type"])
        return stmt.order_by(
            ClinicalAlertORM.severity.desc(), ClinicalAlertORM.generated_at.desc()
        )

    async def get_by_patient(
        self,
        patient_id: str,
        status: AlertStatus | list[AlertStatus] | None = None,
    ) -> list[ClinicalAlert]:
        """
        Get alerts for a specific patient.

        Args:
            patient_id: The patient ID
            status: Optional status filter (single status or list of statuses)

        Returns:
            List of ClinicalAlert objects sorted by severity (critical first) then date
        """
        filters: dict[str, Any] = {"patient_id": patient_id}
        if status is not None:
            filters["status"] = status

        results = await self.list(**filters)

        # Sort by severity (critical > high > medium) then by generated_at (newest first)
        severity_order = {"critical": 0, "high": 1, "medium": 2}
        results.sort(
            key=lambda a: (severity_order.get(a.severity, 3), -a.generated_at.timestamp())
        )

        return results

    async def acknowledge(
        self,
        alert_id: str,
        by: str,
        note: str | None = None,
    ) -> ClinicalAlert | None:
        """
        Mark an alert as acknowledged.

        Args:
            alert_id: The alert ID
            by: Who is acknowledging (provider ID or name)
            note: Optional acknowledgment note

        Returns:
            Updated ClinicalAlert or None if not found
        """
        alert = await self.get(alert_id)
        if alert is None:
            return None

        alert.acknowledge(by=by, note=note)
        await self.update(alert_id, alert)
        return alert

    async def dismiss(
        self,
        alert_id: str,
        by: str,
        reason: str | None = None,
    ) -> ClinicalAlert | None:
        """
        Mark an alert as dismissed.

        Args:
            alert_id: The alert ID
            by: Who is dismissing (provider ID or name)
            reason: Optional dismissal reason

        Returns:
            Updated ClinicalAlert or None if not found
        """
        alert = await self.get(alert_id)
        if alert is None:
            return None

        alert.dismiss(by=by, reason=reason)
        await self.update(alert_id, alert)
        return alert

    async def get_alert_summary(self, patient_id: str) -> AlertSummary:
        """
        Get summary counts of active alerts for a patient.

        Args:
            patient_id: The patient ID

        Returns:
            AlertSummary with counts by severity
        """
        active_alerts = await self.get_by_patient(patient_id, status="active")

        summary = AlertSummary()
        for alert in active_alerts:
            if alert.severity == "critical":
                summary.critical_count += 1
            elif alert.severity == "high":
                summary.high_count += 1
            elif alert.severity == "medium":
                summary.medium_count += 1

        return summary

    async def upsert_alert(self, alert: ClinicalAlert) -> ClinicalAlert:
        """
        Insert or update an alert.

        If an alert with the same source_id and alert_type exists for the patient,
        it updates that alert. Otherwise, it creates a new one.

        Args:
            alert: The alert to upsert

        Returns:
            The upserted alert
        """
        # Check if alert already exists for this source
        existing_alerts = await self.list(
            patient_id=alert.patient_id,
            alert_type=alert.alert_type,
        )

        for existing in existing_alerts:
            if existing.source_id == alert.source_id:
                # Preserve acknowledgment/dismissal state if already handled
                if existing.status != "active":
                    return existing
                # Update existing alert
                alert.id = existing.id
                await self.update(existing.id, alert)
                return alert

        # Create new alert
        await self.create(alert)
        return alert

    async def clear_patient_alerts(self, patient_id: str) -> int:
        """
        Remove all alerts for a patient.

        Used when regenerating alerts from source data.

        Args:
            patient_id: The patient ID

        Returns:
            Number of alerts removed
        """
        alerts = await self.get_by_patient(patient_id)
        count = 0
        for alert in alerts:
            if alert.status == "active":
                await self.delete(alert.id)
                count += 1
        return count
