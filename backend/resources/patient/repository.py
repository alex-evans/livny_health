"""
Patient repository - data access layer.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from resources.core import InMemoryRepository, Reference
from .model import Patient, AllergyReviewStatus


class PatientRepository(InMemoryRepository[Patient]):
    """
    Repository for Patient resources.
    Currently uses in-memory storage, can be swapped for database later.
    """

    async def list(self, **filters: Any) -> list[Patient]:
        """
        List patients with optional filters.

        Supported filters:
        - active: bool - Filter by active status
        - name: str - Filter by name (partial match)
        - mrn: str - Filter by MRN (exact match)
        """
        results = list(self._store.values())

        if "active" in filters:
            results = [p for p in results if p.active == filters["active"]]

        if "name" in filters:
            name_filter = filters["name"].lower()
            results = [p for p in results if name_filter in p.display_name.lower()]

        if "mrn" in filters:
            results = [p for p in results if p.mrn == filters["mrn"]]

        return results

    async def get_by_mrn(self, mrn: str) -> Patient | None:
        """Find a patient by MRN."""
        for patient in self._store.values():
            if patient.mrn == mrn:
                return patient
        return None

    async def mark_allergies_reviewed(
        self,
        patient_id: str,
        reviewer_id: str | None = None,
        reviewer_name: str | None = None,
    ) -> Patient | None:
        """
        Mark a patient's allergy history as reviewed.

        Args:
            patient_id: The patient ID
            reviewer_id: Optional practitioner ID who reviewed
            reviewer_name: Optional practitioner name for display

        Returns:
            Updated Patient or None if not found
        """
        patient = await self.get(patient_id)
        if not patient:
            return None

        reviewer_ref = None
        if reviewer_id:
            reviewer_ref = Reference.to("Practitioner", reviewer_id, reviewer_name)

        patient.allergy_review_status = AllergyReviewStatus(
            reviewed_at=datetime.now(),
            reviewed_by=reviewer_ref,
        )

        return patient
