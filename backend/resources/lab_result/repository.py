"""
Lab Result repository - data access layer.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from resources.core import InMemoryRepository, generate_id, Reference
from .model import LabResult, LabResultHistory


class LabResultRepository(InMemoryRepository[LabResult]):
    """
    Repository for LabResult resources.
    Currently uses in-memory storage with mock data.
    """

    def __init__(self):
        super().__init__()
        self._seed_mock_data()

    def _seed_mock_data(self):
        """Seed the repository with mock historical lab data."""
        today = datetime.now()

        # Mock patient ID for demo
        patient_id = "patient-001"

        # Glucose history (showing improvement then slight increase)
        # Note: Most recent result is acknowledged; older results too
        glucose_history = [
            ("130", "abnormal", 365, True, "dr-smith", 360),
            ("125", "abnormal", 300, True, "dr-smith", 295),
            ("118", "abnormal", 240, True, "dr-jones", 235),
            ("110", "abnormal", 180, True, "dr-smith", 175),
            ("105", "normal", 120, True, "dr-smith", 115),
            ("98", "normal", 14, True, "dr-smith", 13),
        ]

        for i, (value, status, days_ago, acked, acked_by, acked_days_ago) in enumerate(glucose_history):
            collection_date = today - timedelta(days=days_ago)
            result = LabResult(
                id=f"glucose-{i}",
                test_name="Glucose",
                test_code="2339-0",
                value=value,
                unit="mg/dL",
                reference_range="70-100",
                status=status,
                subject=Reference(reference=f"Patient/{patient_id}"),
                collection_date=collection_date,
                performing_lab="Quest Diagnostics",
                panel_id="bmp" if days_ago <= 180 else None,
                last_updated=collection_date + timedelta(hours=2),
                acknowledged=acked,
                acknowledged_by=acked_by if acked else None,
                acknowledged_at=today - timedelta(days=acked_days_ago) if acked else None,
            )
            self._store[result.id] = result

        # Creatinine history (showing worsening trend)
        creatinine_history = [
            ("0.9", "normal", 365, True, "dr-smith", 360),
            ("1.0", "normal", 300, True, "dr-smith", 295),
            ("1.1", "normal", 240, True, "dr-jones", 235),
            ("1.1", "normal", 180, True, "dr-smith", 175),
            ("1.2", "normal", 90, True, "dr-smith", 85),
            ("1.4", "abnormal", 14, True, "dr-smith", 13),
        ]

        for i, (value, status, days_ago, acked, acked_by, acked_days_ago) in enumerate(creatinine_history):
            collection_date = today - timedelta(days=days_ago)
            result = LabResult(
                id=f"creatinine-{i}",
                test_name="Creatinine",
                test_code="2160-0",
                value=value,
                unit="mg/dL",
                reference_range="0.7-1.3",
                status=status,
                subject=Reference(reference=f"Patient/{patient_id}"),
                collection_date=collection_date,
                performing_lab="Quest Diagnostics",
                panel_id="bmp",
                last_updated=collection_date + timedelta(hours=3),
                acknowledged=acked,
                acknowledged_by=acked_by if acked else None,
                acknowledged_at=today - timedelta(days=acked_days_ago) if acked else None,
            )
            self._store[result.id] = result

        # Potassium history (showing sudden spike - critical, most recent UNACKNOWLEDGED)
        potassium_history = [
            ("4.2", "normal", 365, True, "dr-smith", 360),
            ("4.3", "normal", 270, True, "dr-smith", 265),
            ("4.1", "normal", 180, True, "dr-jones", 175),
            ("4.5", "normal", 120, True, "dr-smith", 115),
            ("4.8", "normal", 90, True, "dr-smith", 85),
            ("5.8", "critical", 1, False, None, None),  # Critical and NOT acknowledged!
        ]

        for i, (value, status, days_ago, acked, acked_by, acked_days_ago) in enumerate(potassium_history):
            collection_date = today - timedelta(days=days_ago)
            result = LabResult(
                id=f"potassium-{i}",
                test_name="Potassium",
                test_code="2823-3",
                value=value,
                unit="mEq/L",
                reference_range="3.5-5.0",
                status=status,
                subject=Reference(reference=f"Patient/{patient_id}"),
                collection_date=collection_date,
                performing_lab="Quest Diagnostics",
                panel_id="bmp",
                last_updated=collection_date + timedelta(hours=1),
                acknowledged=acked,
                acknowledged_by=acked_by,
                acknowledged_at=today - timedelta(days=acked_days_ago) if acked_days_ago else None,
            )
            self._store[result.id] = result

        # HbA1c history (showing worsening control)
        hba1c_history = [
            ("5.8", "abnormal", 365, True, "dr-smith", 360),
            ("6.0", "abnormal", 270, True, "dr-smith", 265),
            ("6.2", "abnormal", 180, True, "dr-jones", 175),
            ("6.5", "abnormal", 120, True, "dr-smith", 115),
            ("6.8", "abnormal", 30, True, "dr-smith", 28),
        ]

        for i, (value, status, days_ago, acked, acked_by, acked_days_ago) in enumerate(hba1c_history):
            collection_date = today - timedelta(days=days_ago)
            result = LabResult(
                id=f"hba1c-{i}",
                test_name="HbA1c",
                test_code="4548-4",
                value=value,
                unit="%",
                reference_range="<5.7",
                status=status,
                subject=Reference(reference=f"Patient/{patient_id}"),
                collection_date=collection_date,
                performing_lab="LabCorp",
                last_updated=collection_date + timedelta(days=1),
                acknowledged=acked,
                acknowledged_by=acked_by if acked else None,
                acknowledged_at=today - timedelta(days=acked_days_ago) if acked else None,
            )
            self._store[result.id] = result

        # LDL history (showing improvement with treatment)
        ldl_history = [
            ("165", "abnormal", 365, True, "dr-smith", 360),
            ("155", "abnormal", 270, True, "dr-smith", 265),
            ("145", "abnormal", 180, True, "dr-jones", 175),
            ("135", "abnormal", 45, True, "dr-smith", 43),
        ]

        for i, (value, status, days_ago, acked, acked_by, acked_days_ago) in enumerate(ldl_history):
            collection_date = today - timedelta(days=days_ago)
            result = LabResult(
                id=f"ldl-{i}",
                test_name="LDL",
                test_code="2089-1",
                value=value,
                unit="mg/dL",
                reference_range="<100",
                status=status,
                subject=Reference(reference=f"Patient/{patient_id}"),
                collection_date=collection_date,
                performing_lab="Quest Diagnostics",
                panel_id="lipid",
                last_updated=collection_date + timedelta(hours=4),
                acknowledged=acked,
                acknowledged_by=acked_by if acked else None,
                acknowledged_at=today - timedelta(days=acked_days_ago) if acked else None,
            )
            self._store[result.id] = result

        # eGFR history (showing gradual decline)
        egfr_history = [
            ("85", "normal", 365, True, "dr-smith", 360),
            ("80", "normal", 270, True, "dr-smith", 265),
            ("75", "normal", 180, True, "dr-jones", 175),
            ("72", "normal", 90, True, "dr-smith", 85),
            ("65", "normal", 14, True, "dr-smith", 13),
        ]

        for i, (value, status, days_ago, acked, acked_by, acked_days_ago) in enumerate(egfr_history):
            collection_date = today - timedelta(days=days_ago)
            result = LabResult(
                id=f"egfr-{i}",
                test_name="eGFR",
                test_code="33914-3",
                value=value,
                unit="mL/min/1.73m²",
                reference_range=">60",
                status=status,
                subject=Reference(reference=f"Patient/{patient_id}"),
                collection_date=collection_date,
                performing_lab="Quest Diagnostics",
                last_updated=collection_date + timedelta(hours=2),
                acknowledged=acked,
                acknowledged_by=acked_by if acked else None,
                acknowledged_at=today - timedelta(days=acked_days_ago) if acked else None,
            )
            self._store[result.id] = result

        # CBC - Pending results (ordered but not yet complete)
        cbc_pending = LabResult(
            id="cbc-pending-1",
            test_name="CBC",
            test_code="58410-2",
            value="",
            unit="",
            reference_range="",
            status="pending",
            subject=Reference(reference=f"Patient/{patient_id}"),
            collection_date=today - timedelta(hours=6),
            performing_lab="Quest Diagnostics",
            panel_id="cbc",
            last_updated=today - timedelta(hours=6),
            acknowledged=False,
        )
        self._store[cbc_pending.id] = cbc_pending

        # TSH - In Progress (sample received, processing)
        tsh_in_progress = LabResult(
            id="tsh-inprogress-1",
            test_name="TSH",
            test_code="3016-3",
            value="",
            unit="mIU/L",
            reference_range="0.4-4.0",
            status="in_progress",
            subject=Reference(reference=f"Patient/{patient_id}"),
            collection_date=today - timedelta(hours=4),
            performing_lab="LabCorp",
            last_updated=today - timedelta(hours=2),
            acknowledged=False,
        )
        self._store[tsh_in_progress.id] = tsh_in_progress

        # Troponin - Critical and UNACKNOWLEDGED (urgent alert scenario)
        troponin_critical = LabResult(
            id="troponin-critical-1",
            test_name="Troponin I",
            test_code="10839-9",
            value="0.85",
            unit="ng/mL",
            reference_range="<0.04",
            status="critical",
            subject=Reference(reference=f"Patient/{patient_id}"),
            collection_date=today - timedelta(hours=2),
            performing_lab="Quest Diagnostics",
            last_updated=today - timedelta(hours=1),
            acknowledged=False,  # Critical and NOT acknowledged!
        )
        self._store[troponin_critical.id] = troponin_critical

    async def list(self, **filters: Any) -> list[LabResult]:
        """
        List lab results with optional filters.

        Supported filters:
        - patient_id: str - Filter by patient ID
        - test_name: str - Filter by test name (case-insensitive)
        - status: str | list[str] - Filter by status(es)
        - days_back: int - Filter to results within N days
        """
        results = list(self._store.values())

        if "patient_id" in filters:
            patient_ref = f"Patient/{filters['patient_id']}"
            results = [r for r in results if r.subject.reference == patient_ref]

        if "test_name" in filters:
            test_name_lower = filters["test_name"].lower()
            results = [r for r in results if r.test_name.lower() == test_name_lower]

        if "status" in filters:
            status_filter = filters["status"]
            if isinstance(status_filter, str):
                status_filter = [status_filter]
            results = [r for r in results if r.status in status_filter]

        if "days_back" in filters:
            cutoff = datetime.now() - timedelta(days=filters["days_back"])
            results = [r for r in results if r.collection_date >= cutoff]

        return results

    async def get_history(
        self,
        patient_id: str,
        test_name: str,
        limit: int = 10,
        days_back: int | None = None,
    ) -> list[LabResultHistory]:
        """
        Get historical results for a specific test.

        Args:
            patient_id: The patient ID
            test_name: The test name to look up
            limit: Maximum number of results to return
            days_back: Optional limit to results within N days

        Returns:
            List of LabResultHistory entries, sorted by date (most recent first)
        """
        filters: dict[str, Any] = {
            "patient_id": patient_id,
            "test_name": test_name,
        }
        if days_back is not None:
            filters["days_back"] = days_back

        results = await self.list(**filters)

        # Sort by collection date (most recent first)
        results.sort(key=lambda r: r.collection_date, reverse=True)

        # Limit results
        results = results[:limit]

        # Convert to history entries
        return [r.to_history_entry() for r in results]

    async def get_by_patient(self, patient_id: str) -> list[LabResult]:
        """Get all lab results for a patient."""
        return await self.list(patient_id=patient_id)

    async def get_available_tests(self, patient_id: str) -> list[str]:
        """Get list of unique test names for a patient."""
        results = await self.get_by_patient(patient_id)
        return list(set(r.test_name for r in results))
