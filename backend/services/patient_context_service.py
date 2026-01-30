"""
Patient Context Service.

Provides comprehensive patient context for clinical workflow with:
- Vital sign trends and abnormal detection
- High-alert medication flagging
- Medication categorization
- Allergy severity ordering
- Mode-aware filtering (review vs documentation)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Literal

from resources import (
    PatientRepository,
    AllergyIntoleranceRepository,
    MedicationRequestRepository,
    VitalSignRepository,
    LabResultRepository,
    VisitNoteRepository,
    VitalSign,
    MedicationRequest,
    AllergyIntolerance,
    LabResult,
    VisitNote,
)


# ISMP High-Alert Medications list (common examples)
HIGH_ALERT_DRUG_CLASSES = {
    "anticoagulant",
    "thrombolytic",
    "insulin",
    "opioid",
    "neuromuscular blocking agent",
    "chemotherapy",
    "iv potassium",
    "iv magnesium",
    "epidural",
    "intrathecal",
    "dialysis",
}

HIGH_ALERT_MEDICATIONS = {
    "warfarin",
    "heparin",
    "enoxaparin",
    "rivaroxaban",
    "apixaban",
    "dabigatran",
    "insulin",
    "morphine",
    "hydromorphone",
    "fentanyl",
    "oxycodone",
    "methadone",
    "potassium chloride",
    "digoxin",
    "amiodarone",
    "methotrexate",
    "vincristine",
    "epinephrine",
    "norepinephrine",
    "propofol",
    "ketamine",
}

# Medication category mappings
DRUG_CLASS_CATEGORIES = {
    "ace inhibitor": "Cardiovascular",
    "arb": "Cardiovascular",
    "beta blocker": "Cardiovascular",
    "calcium channel blocker": "Cardiovascular",
    "diuretic": "Cardiovascular",
    "statin": "Cardiovascular",
    "antiplatelet": "Cardiovascular",
    "anticoagulant": "Cardiovascular",
    "biguanide": "Diabetes",
    "sulfonylurea": "Diabetes",
    "sglt2 inhibitor": "Diabetes",
    "glp-1 agonist": "Diabetes",
    "dpp-4 inhibitor": "Diabetes",
    "insulin": "Diabetes",
    "ssri": "Mental Health",
    "snri": "Mental Health",
    "benzodiazepine": "Mental Health",
    "antipsychotic": "Mental Health",
    "mood stabilizer": "Mental Health",
    "ppi": "Gastrointestinal",
    "h2 blocker": "Gastrointestinal",
    "antibiotic": "Infectious Disease",
    "antiviral": "Infectious Disease",
    "antifungal": "Infectious Disease",
    "bronchodilator": "Respiratory",
    "inhaled corticosteroid": "Respiratory",
    "nsaid": "Pain/Inflammation",
    "opioid": "Pain/Inflammation",
    "analgesic": "Pain/Inflammation",
    "antihistamine": "Allergy",
    "thyroid hormone": "Endocrine",
    "corticosteroid": "Endocrine",
}

# Vital sign clinical thresholds
VITAL_THRESHOLDS = {
    "blood_pressure_systolic": {"low": 90, "high": 140, "critical_low": 80, "critical_high": 180},
    "blood_pressure_diastolic": {"low": 60, "high": 90, "critical_low": 50, "critical_high": 120},
    "heart_rate": {"low": 60, "high": 100, "critical_low": 40, "critical_high": 150},
    "respiratory_rate": {"low": 12, "high": 20, "critical_low": 8, "critical_high": 30},
    "temperature": {"low": 97.0, "high": 99.5, "critical_low": 95.0, "critical_high": 103.0},
    "oxygen_saturation": {"low": 95, "critical_low": 90},
    "weight": {},  # No standard thresholds
    "height": {},  # No standard thresholds
    "bmi": {"high": 30, "critical_high": 40},
}


@dataclass
class EnrichedVital:
    """Vital sign with trend and status information."""
    id: str
    vital_type: str
    display_name: str
    value: float
    unit: str
    display_value: str
    status: Literal["normal", "abnormal", "critical"]
    trend: Literal["improving", "worsening", "stable"] | None
    previous_value: float | None
    previous_date: str | None
    recorded_at: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "vitalType": self.vital_type,
            "displayName": self.display_name,
            "value": self.value,
            "unit": self.unit,
            "displayValue": self.display_value,
            "status": self.status,
            "trend": self.trend,
            "previousValue": self.previous_value,
            "previousDate": self.previous_date,
            "recordedAt": self.recorded_at,
        }


@dataclass
class EnrichedMedication:
    """Medication with category and alert flags."""
    id: str
    name: str
    generic_name: str | None
    dosage: str
    frequency: str
    route: str
    category: str
    is_high_alert: bool
    is_recently_started: bool
    start_date: str | None
    prescriber: str | None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "genericName": self.generic_name,
            "dosage": self.dosage,
            "frequency": self.frequency,
            "route": self.route,
            "category": self.category,
            "isHighAlert": self.is_high_alert,
            "isRecentlyStarted": self.is_recently_started,
            "startDate": self.start_date,
            "prescriber": self.prescriber,
        }


@dataclass
class DiscontinuedMedication:
    """Recently discontinued medication."""
    id: str
    name: str
    dosage: str
    discontinued_date: str
    reason: str | None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "dosage": self.dosage,
            "discontinuedDate": self.discontinued_date,
            "reason": self.reason,
        }


@dataclass
class EnrichedAllergy:
    """Allergy with full details and ordering info."""
    id: str
    allergen: str
    reaction: str
    severity: Literal["critical", "moderate", "mild"]
    status: Literal["confirmed", "suspected", "reported"]
    is_anaphylaxis: bool
    onset_date: str | None
    notes: str | None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "allergen": self.allergen,
            "reaction": self.reaction,
            "severity": self.severity,
            "status": self.status,
            "isAnaphylaxis": self.is_anaphylaxis,
            "onsetDate": self.onset_date,
            "notes": self.notes,
        }


@dataclass
class EnrichedProblem:
    """Problem with ICD-10 and status."""
    id: str
    description: str
    icd10_code: str
    status: Literal["active", "inactive", "resolved"]
    problem_type: Literal["chronic", "acute"]
    onset_date: str | None
    is_primary: bool

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "icd10Code": self.icd10_code,
            "status": self.status,
            "type": self.problem_type,
            "onsetDate": self.onset_date,
            "isPrimary": self.is_primary,
        }


@dataclass
class EnrichedLab:
    """Lab result with reference ranges and flags."""
    id: str
    name: str
    value: str
    unit: str
    reference_range: str
    status: Literal["normal", "high", "low", "critical"]
    date: str
    is_pending: bool

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "referenceRange": self.reference_range,
            "status": self.status,
            "date": self.date,
            "isPending": self.is_pending,
        }


@dataclass
class EnrichedVisit:
    """Visit with summary and days ago calculation."""
    id: str
    date: str
    visit_type: str
    chief_complaint: str
    provider: str
    days_ago: int
    summary: str | None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date,
            "type": self.visit_type,
            "chiefComplaint": self.chief_complaint,
            "provider": self.provider,
            "daysAgo": self.days_ago,
            "summary": self.summary,
        }


@dataclass
class QuickContextSummary:
    """Quick context bar summary data."""
    primary_vital: dict | None  # {label, value, trend}
    medication_names: list[str]
    critical_allergies: list[str]
    key_lab: dict | None  # {name, value}
    problem_count: int

    def to_dict(self) -> dict:
        return {
            "primaryVital": self.primary_vital,
            "medicationNames": self.medication_names,
            "criticalAllergies": self.critical_allergies,
            "keyLab": self.key_lab,
            "problemCount": self.problem_count,
        }


@dataclass
class PatientContextResponse:
    """Full patient context response."""
    patient_id: str
    generated_at: str
    medications: dict  # {active, recentlyDiscontinued, totalActive}
    allergies: list[EnrichedAllergy]
    problems: dict  # {active, totalActive}
    vitals: dict  # {mostRecent, recordedAt}
    recent_visits: list[EnrichedVisit]
    recent_labs: dict  # {results, pending}
    quick_summary: QuickContextSummary

    def to_dict(self) -> dict:
        return {
            "patientId": self.patient_id,
            "generatedAt": self.generated_at,
            "medications": {
                "active": [m.to_dict() for m in self.medications["active"]],
                "recentlyDiscontinued": [m.to_dict() for m in self.medications["recentlyDiscontinued"]],
                "totalActive": self.medications["totalActive"],
            },
            "allergies": [a.to_dict() for a in self.allergies],
            "problems": {
                "active": [p.to_dict() for p in self.problems["active"]],
                "totalActive": self.problems["totalActive"],
            },
            "vitals": {
                "mostRecent": {k: v.to_dict() for k, v in self.vitals["mostRecent"].items()},
                "recordedAt": self.vitals.get("recordedAt"),
            },
            "recentVisits": [v.to_dict() for v in self.recent_visits],
            "recentLabs": {
                "results": [l.to_dict() for l in self.recent_labs["results"]],
                "pending": self.recent_labs["pending"],
            },
            "quickSummary": self.quick_summary.to_dict(),
        }


class PatientContextService:
    """
    Service for building comprehensive patient context.

    All business logic for:
    - Vital trend calculation
    - High-alert medication detection
    - Medication categorization
    - Recently started/discontinued detection
    - Allergy severity ordering
    - Quick summary generation
    - Mode-aware filtering
    """

    def __init__(
        self,
        patient_repo: PatientRepository,
        allergy_repo: AllergyIntoleranceRepository,
        medication_request_repo: MedicationRequestRepository,
        vitals_repo: VitalSignRepository,
        lab_result_repo: LabResultRepository,
        visit_note_repo: VisitNoteRepository,
    ):
        self.patient_repo = patient_repo
        self.allergy_repo = allergy_repo
        self.medication_request_repo = medication_request_repo
        self.vitals_repo = vitals_repo
        self.lab_result_repo = lab_result_repo
        self.visit_note_repo = visit_note_repo

    async def get_patient_context(
        self,
        patient_id: str,
        encounter_id: str | None = None,
        mode: Literal["review", "documentation"] = "review",
    ) -> PatientContextResponse:
        """
        Get comprehensive patient context.

        Args:
            patient_id: The patient ID
            encounter_id: Optional encounter ID for context
            mode: 'review' for full history, 'documentation' for today-focused

        Returns:
            PatientContextResponse with all enriched context data
        """
        # Fetch raw data from repositories
        patient = await self.patient_repo.get(patient_id)
        if not patient:
            raise PatientNotFoundError(f"Patient {patient_id} not found")

        # Get all data in parallel-ish
        vitals = await self.vitals_repo.list(patient_id=patient_id, days_back=90)
        medications = await self.medication_request_repo.list(patient_id=patient_id)
        allergies = await self.allergy_repo.list(patient_id=patient_id)
        labs = await self.lab_result_repo.list(patient_id=patient_id, days_back=90)
        visits = await self.visit_note_repo.list(patient_id=patient_id, days_back=180)

        # Process vitals with trends
        enriched_vitals = self._process_vitals(vitals, mode)

        # Process medications with categories and flags
        active_meds, discontinued_meds = self._process_medications(medications, mode)

        # Process allergies with severity ordering
        enriched_allergies = self._process_allergies(allergies)

        # Process problems from patient
        enriched_problems = self._process_problems(patient)

        # Process labs
        enriched_labs, pending_labs = self._process_labs(labs, mode)

        # Process visits with days ago
        enriched_visits = self._process_visits(visits, mode)

        # Generate quick summary
        quick_summary = self._generate_quick_summary(
            enriched_vitals,
            active_meds,
            enriched_allergies,
            enriched_labs,
            enriched_problems,
        )

        return PatientContextResponse(
            patient_id=patient_id,
            generated_at=datetime.utcnow().isoformat(),
            medications={
                "active": active_meds,
                "recentlyDiscontinued": discontinued_meds,
                "totalActive": len(active_meds),
            },
            allergies=enriched_allergies,
            problems={
                "active": enriched_problems,
                "totalActive": len(enriched_problems),
            },
            vitals={
                "mostRecent": enriched_vitals,
                "recordedAt": vitals[0].recorded_at.isoformat() if vitals else None,
            },
            recent_visits=enriched_visits,
            recent_labs={
                "results": enriched_labs,
                "pending": pending_labs,
            },
            quick_summary=quick_summary,
        )

    async def get_quick_context_summary(
        self, patient_id: str
    ) -> QuickContextSummary:
        """Get just the quick summary for the context bar."""
        context = await self.get_patient_context(patient_id, mode="documentation")
        return context.quick_summary

    def _process_vitals(
        self, vitals: list[VitalSign], mode: str
    ) -> dict[str, EnrichedVital]:
        """Process vitals with trend calculation."""
        if not vitals:
            return {}

        # Group by vital type
        vitals_by_type: dict[str, list[VitalSign]] = {}
        for v in vitals:
            vital_type = v.vital_type.value if hasattr(v.vital_type, 'value') else str(v.vital_type)
            if vital_type not in vitals_by_type:
                vitals_by_type[vital_type] = []
            vitals_by_type[vital_type].append(v)

        # Sort each group by date descending
        for vital_type in vitals_by_type:
            vitals_by_type[vital_type].sort(
                key=lambda x: x.recorded_at, reverse=True
            )

        result = {}
        for vital_type, vital_list in vitals_by_type.items():
            current = vital_list[0]
            previous = vital_list[1] if len(vital_list) > 1 else None

            trend = self._calculate_vital_trend(vital_type, current, previous)
            status = self._get_vital_status(vital_type, current.value)

            result[vital_type] = EnrichedVital(
                id=current.id,
                vital_type=vital_type,
                display_name=self._get_vital_display_name(vital_type),
                value=current.value,
                unit=current.unit,
                display_value=f"{current.value} {current.unit}",
                status=status,
                trend=trend,
                previous_value=previous.value if previous else None,
                previous_date=previous.recorded_at.isoformat() if previous else None,
                recorded_at=current.recorded_at.isoformat(),
            )

        return result

    def _calculate_vital_trend(
        self, vital_type: str, current: VitalSign, previous: VitalSign | None
    ) -> Literal["improving", "worsening", "stable"] | None:
        """Calculate trend based on vital type and direction."""
        if not previous:
            return None

        diff = current.value - previous.value
        threshold = abs(previous.value * 0.05)  # 5% change threshold

        if abs(diff) < threshold:
            return "stable"

        # For most vitals, lower is better when high, higher is better when low
        current_status = self._get_vital_status(vital_type, current.value)

        # Oxygen saturation: higher is always better
        if vital_type == "oxygen_saturation":
            return "improving" if diff > 0 else "worsening"

        # For blood pressure and heart rate: depends on current level
        if current_status == "normal":
            return "stable"  # Already normal, any small change is stable
        elif current_status in ("abnormal", "critical"):
            # Check if moving toward normal
            thresholds = VITAL_THRESHOLDS.get(vital_type, {})
            if thresholds:
                low = thresholds.get("low", 0)
                high = thresholds.get("high", float("inf"))

                if current.value > high:
                    return "improving" if diff < 0 else "worsening"
                elif current.value < low:
                    return "improving" if diff > 0 else "worsening"

        return "stable"

    def _get_vital_status(
        self, vital_type: str, value: float
    ) -> Literal["normal", "abnormal", "critical"]:
        """Determine vital sign status based on clinical thresholds."""
        thresholds = VITAL_THRESHOLDS.get(vital_type, {})
        if not thresholds:
            return "normal"

        critical_low = thresholds.get("critical_low", float("-inf"))
        critical_high = thresholds.get("critical_high", float("inf"))
        low = thresholds.get("low", critical_low)
        high = thresholds.get("high", critical_high)

        if value <= critical_low or value >= critical_high:
            return "critical"
        elif value < low or value > high:
            return "abnormal"
        return "normal"

    def _get_vital_display_name(self, vital_type: str) -> str:
        """Get display name for vital type."""
        names = {
            "blood_pressure_systolic": "BP Systolic",
            "blood_pressure_diastolic": "BP Diastolic",
            "heart_rate": "Heart Rate",
            "respiratory_rate": "Resp Rate",
            "temperature": "Temp",
            "oxygen_saturation": "SpO2",
            "weight": "Weight",
            "height": "Height",
            "bmi": "BMI",
        }
        return names.get(vital_type, vital_type.replace("_", " ").title())

    def _process_medications(
        self, medications: list[MedicationRequest], mode: str
    ) -> tuple[list[EnrichedMedication], list[DiscontinuedMedication]]:
        """Process medications with categories and flags."""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active = []
        discontinued = []

        for med in medications:
            status = med.status.value if hasattr(med.status, 'value') else str(med.status)

            # Extract dosage info from dosage_instruction
            primary_dosage = med.primary_dosage
            dosage_str = med.strength or ""
            frequency_str = ""
            route_str = ""
            if primary_dosage:
                dosage_str = primary_dosage.dose or med.strength or ""
                frequency_str = primary_dosage.frequency or ""
                route_str = primary_dosage.route or ""

            if status == "active":
                is_high_alert = self._is_high_alert_medication(med)
                category = self._categorize_medication(med)
                is_recently_started = self._is_recently_started(med, thirty_days_ago)

                # Get prescriber name from requester reference
                prescriber_name = None
                if med.requester and med.requester.display:
                    prescriber_name = med.requester.display

                active.append(EnrichedMedication(
                    id=med.id,
                    name=med.medication_name,
                    generic_name=med.brand_name,  # brand_name is closest to generic
                    dosage=dosage_str,
                    frequency=frequency_str,
                    route=route_str,
                    category=category,
                    is_high_alert=is_high_alert,
                    is_recently_started=is_recently_started,
                    start_date=med.authored_on.isoformat() if med.authored_on else None,
                    prescriber=prescriber_name,
                ))
            elif status in ("stopped", "cancelled"):
                # Check if recently discontinued - use authored_on as fallback
                # since MedicationRequest doesn't have an end_date field
                discontinued.append(DiscontinuedMedication(
                    id=med.id,
                    name=med.medication_name,
                    dosage=dosage_str,
                    discontinued_date=med.authored_on.isoformat() if med.authored_on else "",
                    reason=med.status_reason,
                ))

        # Sort active medications: high-alert first, then recently started
        active.sort(key=lambda m: (not m.is_high_alert, not m.is_recently_started, m.name))

        # In documentation mode, limit to most relevant
        if mode == "documentation":
            active = active[:10]
            discontinued = discontinued[:5]

        return active, discontinued

    def _is_high_alert_medication(self, medication: MedicationRequest) -> bool:
        """Check if medication is on ISMP high-alert list."""
        med_name = medication.medication_name.lower()
        drug_class = getattr(medication, 'drug_class', '') or ""
        drug_class = drug_class.lower()

        # Check medication name
        for high_alert in HIGH_ALERT_MEDICATIONS:
            if high_alert in med_name:
                return True

        # Check drug class
        for high_alert_class in HIGH_ALERT_DRUG_CLASSES:
            if high_alert_class in drug_class:
                return True

        return False

    def _categorize_medication(self, medication: MedicationRequest) -> str:
        """Categorize medication by drug class."""
        drug_class = getattr(medication, 'drug_class', '') or ""
        drug_class_lower = drug_class.lower()

        for class_key, category in DRUG_CLASS_CATEGORIES.items():
            if class_key in drug_class_lower:
                return category

        return "Other"

    def _is_recently_started(
        self, medication: MedicationRequest, threshold: datetime
    ) -> bool:
        """Check if medication was started within threshold."""
        if not medication.authored_on:
            return False
        return medication.authored_on >= threshold

    def _process_allergies(
        self, allergies: list[AllergyIntolerance]
    ) -> list[EnrichedAllergy]:
        """Process allergies with severity ordering."""
        enriched = []

        for allergy in allergies:
            severity = getattr(allergy, 'severity', 'moderate')
            if hasattr(severity, 'value'):
                severity = severity.value

            # Normalize severity
            if severity in ('severe', 'high', 'critical'):
                normalized_severity = "critical"
            elif severity in ('mild', 'low'):
                normalized_severity = "mild"
            else:
                normalized_severity = "moderate"

            clinical_status = getattr(allergy, 'clinical_status', 'confirmed')
            if hasattr(clinical_status, 'value'):
                clinical_status = clinical_status.value

            # Normalize status
            if clinical_status in ('confirmed', 'active'):
                normalized_status = "confirmed"
            elif clinical_status in ('suspected', 'unconfirmed'):
                normalized_status = "suspected"
            else:
                normalized_status = "reported"

            enriched.append(EnrichedAllergy(
                id=allergy.id,
                allergen=allergy.allergen,
                reaction=allergy.reaction or "",
                severity=normalized_severity,
                status=normalized_status,
                is_anaphylaxis=allergy.is_anaphylaxis,
                onset_date=allergy.recorded_date.isoformat() if allergy.recorded_date else None,
                notes=allergy.notes,
            ))

        # Sort by severity (critical first), then anaphylaxis, then alphabetically
        severity_order = {"critical": 0, "moderate": 1, "mild": 2}
        enriched.sort(
            key=lambda a: (
                severity_order.get(a.severity, 2),
                not a.is_anaphylaxis,
                a.allergen.lower(),
            )
        )

        return enriched

    def _process_problems(self, patient) -> list[EnrichedProblem]:
        """Process problems from patient."""
        if not patient or not patient.problem_list:
            return []

        enriched = []
        for idx, problem in enumerate(patient.problem_list):
            status = problem.status.value if hasattr(problem.status, 'value') else str(problem.status)

            # Only include active problems
            if status != "active":
                continue

            problem_type = "chronic"  # Default
            if hasattr(problem, 'priority'):
                priority = problem.priority.value if hasattr(problem.priority, 'value') else str(problem.priority)
                if priority in ('acute', 'urgent'):
                    problem_type = "acute"

            enriched.append(EnrichedProblem(
                id=f"problem-{idx}",
                description=problem.name,
                icd10_code=problem.icd10_code or "",
                status="active",
                problem_type=problem_type,
                onset_date=problem.onset_date.isoformat() if hasattr(problem, 'onset_date') and problem.onset_date else None,
                is_primary=idx == 0 or getattr(problem, 'is_critical', False),
            ))

        return enriched

    def _process_labs(
        self, labs: list[LabResult], mode: str
    ) -> tuple[list[EnrichedLab], list[dict]]:
        """Process lab results."""
        enriched = []
        pending = []

        for lab in labs:
            lab_status = lab.status if isinstance(lab.status, str) else str(lab.status)

            if lab_status == "pending" or lab_status == "in_progress":
                pending.append({
                    "name": lab.test_name,
                    "orderedDate": lab.collection_date.isoformat() if lab.collection_date else None,
                })
                continue

            # Map lab status to our enriched status
            # LabResultStatus = "normal" | "abnormal" | "critical" | "pending" | "in_progress"
            result_status: Literal["normal", "high", "low", "critical"] = "normal"
            if lab_status == "critical":
                result_status = "critical"
            elif lab_status == "abnormal":
                result_status = "high"  # Default abnormal to high

            enriched.append(EnrichedLab(
                id=lab.id,
                name=lab.test_name,
                value=str(lab.value),
                unit=lab.unit or "",
                reference_range=lab.reference_range or "",
                status=result_status,
                date=lab.collection_date.isoformat() if lab.collection_date else "",
                is_pending=False,
            ))

        # Sort by date descending
        enriched.sort(key=lambda l: l.date, reverse=True)

        # Limit in documentation mode
        if mode == "documentation":
            enriched = enriched[:5]
            pending = pending[:3]
        else:
            enriched = enriched[:10]

        return enriched, pending

    def _process_visits(
        self, visits: list[VisitNote], mode: str
    ) -> list[EnrichedVisit]:
        """Process visits with days ago calculation."""
        now = datetime.utcnow()
        enriched = []

        for visit in visits:
            visit_date = visit.date
            if not visit_date:
                continue

            days_ago = (now - visit_date).days

            # Get provider name from provider object if available
            provider_name = ""
            if visit.provider:
                provider_name = visit.provider.name

            enriched.append(EnrichedVisit(
                id=visit.id,
                date=visit_date.isoformat(),
                visit_type=visit.visit_type or "Office Visit",
                chief_complaint=visit.chief_complaint or "",
                provider=provider_name,
                days_ago=days_ago,
                summary=visit.notes,
            ))

        # Sort by date descending
        enriched.sort(key=lambda v: v.date, reverse=True)

        # Limit based on mode
        max_visits = 3 if mode == "documentation" else 5
        return enriched[:max_visits]

    def _generate_quick_summary(
        self,
        vitals: dict[str, EnrichedVital],
        medications: list[EnrichedMedication],
        allergies: list[EnrichedAllergy],
        labs: list[EnrichedLab],
        problems: list[EnrichedProblem],
    ) -> QuickContextSummary:
        """Generate quick summary for context bar."""
        # Primary vital: prefer BP, then HR
        primary_vital = None
        for vital_type in ["blood_pressure_systolic", "heart_rate", "oxygen_saturation"]:
            if vital_type in vitals:
                v = vitals[vital_type]
                trend_symbol = ""
                if v.trend == "improving":
                    trend_symbol = " \u2193"  # Down arrow for improving BP
                elif v.trend == "worsening":
                    trend_symbol = " \u2191"  # Up arrow for worsening BP

                primary_vital = {
                    "label": v.display_name,
                    "value": v.display_value,
                    "trend": v.trend,
                }
                break

        # Top 3 medication names (high-alert first)
        med_names = [m.name for m in medications[:3]]

        # Critical allergies
        critical_allergies = [
            a.allergen for a in allergies
            if a.severity == "critical" or a.is_anaphylaxis
        ]

        # Key lab (most recent abnormal, or most recent)
        key_lab = None
        for lab in labs:
            if lab.status in ("high", "low", "critical"):
                key_lab = {"name": lab.name, "value": f"{lab.value} {lab.unit}".strip()}
                break
        if not key_lab and labs:
            key_lab = {"name": labs[0].name, "value": f"{labs[0].value} {labs[0].unit}".strip()}

        return QuickContextSummary(
            primary_vital=primary_vital,
            medication_names=med_names,
            critical_allergies=critical_allergies,
            key_lab=key_lab,
            problem_count=len(problems),
        )


class PatientNotFoundError(Exception):
    """Raised when patient is not found."""
    pass
