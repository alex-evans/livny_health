"""
Alert Generators for Clinical Alerts.

Each generator is responsible for detecting specific types of clinical alerts
from source data (labs, vitals, imaging, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any

from resources import (
    ClinicalAlert,
    LabResultRepository,
    VitalSignRepository,
    ImagingStudyRepository,
    PatientRepository,
    MedicationRequestRepository,
)
from resources.core import generate_id
from services.alert_thresholds import (
    CRITICAL_LAB_THRESHOLDS,
    CRITICAL_VITAL_THRESHOLDS,
    get_lab_severity,
    get_vital_severity,
)


class AlertGenerator(ABC):
    """Base class for alert generators."""

    @abstractmethod
    async def generate_alerts(self, patient_id: str) -> list[ClinicalAlert]:
        """
        Generate alerts for a patient.

        Args:
            patient_id: The patient ID to check

        Returns:
            List of generated ClinicalAlert objects
        """
        ...


class LabAlertGenerator(AlertGenerator):
    """Generates alerts for critical/abnormal lab values."""

    def __init__(self, lab_result_repo: LabResultRepository):
        self.lab_result_repo = lab_result_repo

    async def generate_alerts(self, patient_id: str) -> list[ClinicalAlert]:
        """Generate alerts for critical lab values."""
        alerts = []

        # Get recent lab results (last 7 days)
        results = await self.lab_result_repo.list(
            patient_id=patient_id,
            days_back=7,
        )

        # Group by test name and get most recent for each
        latest_by_test: dict[str, Any] = {}
        for result in results:
            if result.test_name not in latest_by_test:
                latest_by_test[result.test_name] = result
            elif result.collection_date > latest_by_test[result.test_name].collection_date:
                latest_by_test[result.test_name] = result

        for test_name, result in latest_by_test.items():
            # Skip pending/in-progress results
            if result.status in ("pending", "in_progress"):
                continue

            # Get numeric value
            numeric_value = result.numeric_value
            if numeric_value is None:
                continue

            severity = get_lab_severity(test_name, numeric_value)
            if severity:
                thresholds = CRITICAL_LAB_THRESHOLDS.get(test_name, {})
                description = self._build_description(test_name, result, thresholds)
                actions = self._get_recommended_actions(test_name, severity)

                alert = ClinicalAlert(
                    id=generate_id("alert"),
                    patient_id=patient_id,
                    alert_type="critical_lab",
                    severity=severity,
                    status="active",
                    title=f"{'Critical' if severity == 'critical' else 'Abnormal'} {test_name}",
                    description=description,
                    generated_at=datetime.utcnow(),
                    source="Lab Result",
                    source_id=result.id,
                    source_link=f"/patients/{patient_id}/labs/{result.id}",
                    context={
                        "testName": test_name,
                        "value": result.value,
                        "unit": result.unit,
                        "referenceRange": result.reference_range,
                        "collectionDate": result.collection_date.isoformat(),
                    },
                    recommended_actions=actions,
                )
                alerts.append(alert)

        return alerts

    def _build_description(self, test_name: str, result: Any, thresholds: dict) -> str:
        """Build a descriptive message for the lab alert."""
        value = result.value
        unit = result.unit
        ref_range = result.reference_range

        parts = [f"{test_name} is {value} {unit}"]

        if ref_range:
            parts.append(f"(reference: {ref_range})")

        numeric = result.numeric_value
        if numeric is not None:
            if thresholds.get("critical_high") and numeric >= thresholds["critical_high"]:
                parts.append("- critically elevated")
            elif thresholds.get("critical_low") and numeric <= thresholds["critical_low"]:
                parts.append("- critically low")
            elif thresholds.get("high") and numeric >= thresholds["high"]:
                parts.append("- elevated")
            elif thresholds.get("low") and numeric <= thresholds["low"]:
                parts.append("- low")

        return " ".join(parts)

    def _get_recommended_actions(self, test_name: str, severity: str) -> list[str]:
        """Get recommended actions for a lab alert."""
        actions: dict[str, list[str]] = {
            "Potassium": [
                "Repeat stat potassium level",
                "Review EKG for peaked T waves",
                "Consider calcium gluconate if critically high",
            ],
            "Troponin I": [
                "Obtain serial troponins q3h x 3",
                "Obtain 12-lead EKG",
                "Consider cardiology consult",
            ],
            "Troponin T": [
                "Obtain serial troponins q3h x 3",
                "Obtain 12-lead EKG",
                "Consider cardiology consult",
            ],
            "Glucose": [
                "Check for ketones if elevated",
                "Assess hydration status",
                "Review insulin/medication regimen",
            ],
            "Hemoglobin": [
                "Type and screen",
                "Consider transfusion if symptomatic",
                "Identify source of blood loss",
            ],
            "Creatinine": [
                "Review medication list for nephrotoxins",
                "Assess volume status",
                "Consider nephrology consult",
            ],
            "INR": [
                "Hold warfarin",
                "Consider vitamin K if bleeding",
                "Recheck INR in 24-48 hours",
            ],
        }

        default_actions = [
            f"Review result and clinical context",
            f"Repeat {test_name} if clinically indicated",
        ]

        return actions.get(test_name, default_actions)


class VitalAlertGenerator(AlertGenerator):
    """Generates alerts for critical vital signs."""

    def __init__(self, vitals_repo: VitalSignRepository):
        self.vitals_repo = vitals_repo

    async def generate_alerts(self, patient_id: str) -> list[ClinicalAlert]:
        """Generate alerts for critical vital signs."""
        alerts = []

        # Get current vitals (most recent for each type)
        current_vitals = await self.vitals_repo.get_current_vitals(patient_id)

        for vital_type, vital in current_vitals.items():
            # Only check vitals from last 24 hours
            if datetime.utcnow() - vital.recorded_at > timedelta(hours=24):
                continue

            severity = get_vital_severity(vital_type, vital.value)
            if severity:
                description = self._build_description(vital)
                actions = self._get_recommended_actions(vital_type, vital.value)

                alert = ClinicalAlert(
                    id=generate_id("alert"),
                    patient_id=patient_id,
                    alert_type="critical_vital",
                    severity=severity,
                    status="active",
                    title=self._get_title(vital_type, vital.value),
                    description=description,
                    generated_at=datetime.utcnow(),
                    source="Vital Signs",
                    source_id=vital.id,
                    source_link=f"/patients/{patient_id}/vitals",
                    context={
                        "vitalType": vital_type,
                        "value": vital.value,
                        "unit": vital.unit,
                        "recordedAt": vital.recorded_at.isoformat(),
                    },
                    recommended_actions=actions,
                )
                alerts.append(alert)

        return alerts

    def _get_title(self, vital_type: str, value: float) -> str:
        """Get alert title for vital sign."""
        titles = {
            "blood_pressure_systolic": f"Hypertensive Urgency" if value >= 180 else "Hypotension",
            "blood_pressure_diastolic": f"Elevated Diastolic BP",
            "heart_rate": "Tachycardia" if value >= 150 else "Bradycardia",
            "temperature": "Hyperthermia" if value >= 104 else "Hypothermia",
            "oxygen_saturation": "Hypoxemia",
            "respiratory_rate": "Tachypnea" if value >= 30 else "Bradypnea",
        }
        return titles.get(vital_type, f"Critical {vital_type.replace('_', ' ').title()}")

    def _build_description(self, vital: Any) -> str:
        """Build description for vital alert."""
        vital_type = vital.vital_type.replace("_", " ").title()
        return f"{vital_type} is {vital.value} {vital.unit} (recorded {vital.recorded_at.strftime('%m/%d %H:%M')})"

    def _get_recommended_actions(self, vital_type: str, value: float) -> list[str]:
        """Get recommended actions for a vital alert."""
        actions: dict[str, list[str]] = {
            "blood_pressure_systolic": [
                "Assess for symptoms (headache, chest pain, vision changes)",
                "Consider oral antihypertensive",
                "Recheck BP in 15-30 minutes",
            ],
            "heart_rate": [
                "Obtain 12-lead EKG",
                "Check electrolytes",
                "Assess for symptoms (palpitations, lightheadedness)",
            ],
            "oxygen_saturation": [
                "Apply supplemental oxygen",
                "Assess respiratory effort",
                "Consider ABG if not improving",
            ],
            "temperature": [
                "Blood cultures if febrile",
                "Administer antipyretic",
                "Cooling/warming measures as appropriate",
            ],
        }

        return actions.get(vital_type, ["Assess patient and recheck vital"])


class ImagingAlertGenerator(AlertGenerator):
    """Generates alerts for critical imaging findings."""

    def __init__(self, imaging_repo: ImagingStudyRepository):
        self.imaging_repo = imaging_repo

    async def generate_alerts(self, patient_id: str) -> list[ClinicalAlert]:
        """Generate alerts for critical imaging findings."""
        alerts = []

        # Get recent imaging studies
        studies = await self.imaging_repo.list(patient_id=patient_id)

        for study in studies:
            # Check for critical findings in report
            if study.report and study.report.findings:
                findings_lower = study.report.findings.lower()
                is_critical = any(term in findings_lower for term in [
                    "critical",
                    "emergent",
                    "urgent",
                    "immediate",
                    "pulmonary embolism",
                    "aortic dissection",
                    "intracranial hemorrhage",
                    "pneumothorax",
                    "bowel obstruction",
                ])

                if is_critical:
                    alert = ClinicalAlert(
                        id=generate_id("alert"),
                        patient_id=patient_id,
                        alert_type="critical_imaging",
                        severity="critical",
                        status="active",
                        title=f"Critical Finding on {study.modality}",
                        description=f"Critical finding reported: {study.report.impression or study.report.findings[:200]}",
                        generated_at=datetime.utcnow(),
                        source="Imaging Study",
                        source_id=study.id,
                        source_link=f"/patients/{patient_id}/imaging/{study.id}",
                        context={
                            "modality": study.modality,
                            "studyDate": study.study_date.isoformat(),
                            "impression": study.report.impression,
                        },
                        recommended_actions=[
                            "Review imaging findings",
                            "Contact ordering provider",
                            "Initiate appropriate treatment",
                        ],
                    )
                    alerts.append(alert)

        return alerts


class ScreeningAlertGenerator(AlertGenerator):
    """Generates alerts for overdue preventive screenings."""

    def __init__(self, patient_repo: PatientRepository):
        self.patient_repo = patient_repo

    async def generate_alerts(self, patient_id: str) -> list[ClinicalAlert]:
        """Generate alerts for overdue screenings."""
        alerts = []

        patient = await self.patient_repo.get(patient_id)
        if not patient:
            return alerts

        # Calculate age
        today = datetime.now().date()
        age = today.year - patient.birth_date.year
        if (today.month, today.day) < (patient.birth_date.month, patient.birth_date.day):
            age -= 1

        # Check colonoscopy for patients 45-75
        if 45 <= age <= 75:
            # For demo, assume no colonoscopy if age > 50
            if age > 50:
                alert = ClinicalAlert(
                    id=generate_id("alert"),
                    patient_id=patient_id,
                    alert_type="overdue_screening",
                    severity="medium",
                    status="active",
                    title="Overdue Colonoscopy Screening",
                    description=f"Patient is {age} years old with no documented colonoscopy in recommended interval",
                    generated_at=datetime.utcnow(),
                    source="Preventive Care",
                    source_id="screening-colonoscopy",
                    context={
                        "screeningType": "colonoscopy",
                        "patientAge": age,
                        "recommendedInterval": "10 years",
                    },
                    recommended_actions=[
                        "Discuss colorectal cancer screening options",
                        "Order colonoscopy or alternative screening",
                        "Document patient preferences if declined",
                    ],
                )
                alerts.append(alert)

        return alerts


class ChronicDiseaseAlertGenerator(AlertGenerator):
    """Generates alerts for chronic disease management concerns."""

    def __init__(
        self,
        patient_repo: PatientRepository,
        lab_result_repo: LabResultRepository,
    ):
        self.patient_repo = patient_repo
        self.lab_result_repo = lab_result_repo

    async def generate_alerts(self, patient_id: str) -> list[ClinicalAlert]:
        """Generate alerts for chronic disease concerns."""
        alerts = []

        patient = await self.patient_repo.get(patient_id)
        if not patient:
            return alerts

        # Check for diabetes management
        has_diabetes = any(
            "diabetes" in p.name.lower()
            for p in patient.problems if p.status == "active"
        )

        if has_diabetes:
            # Get recent HbA1c
            hba1c_results = await self.lab_result_repo.list(
                patient_id=patient_id,
                test_name="HbA1c",
                days_back=180,
            )

            if hba1c_results:
                latest = max(hba1c_results, key=lambda r: r.collection_date)
                value = latest.numeric_value

                if value and value >= 9.0:
                    alert = ClinicalAlert(
                        id=generate_id("alert"),
                        patient_id=patient_id,
                        alert_type="chronic_disease",
                        severity="high",
                        status="active",
                        title="Uncontrolled Diabetes",
                        description=f"HbA1c is {value}% indicating poor glycemic control (goal <7%)",
                        generated_at=datetime.utcnow(),
                        source="Chronic Disease Management",
                        source_id=latest.id,
                        source_link=f"/patients/{patient_id}/labs/{latest.id}",
                        context={
                            "condition": "Diabetes",
                            "hba1c": value,
                            "goal": 7.0,
                            "collectionDate": latest.collection_date.isoformat(),
                        },
                        recommended_actions=[
                            "Review current diabetes regimen",
                            "Consider medication intensification",
                            "Reinforce lifestyle modifications",
                            "Consider endocrinology referral",
                        ],
                    )
                    alerts.append(alert)

        return alerts
