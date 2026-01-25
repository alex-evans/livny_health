"""
Clinical Alert Thresholds Configuration.

Defines critical thresholds for lab values, vitals, and screening intervals.
These thresholds trigger clinical alerts when exceeded.
"""

from typing import TypedDict


class LabThreshold(TypedDict, total=False):
    """Threshold configuration for a lab value."""
    critical_high: float
    critical_low: float
    high: float
    low: float


class VitalThreshold(TypedDict, total=False):
    """Threshold configuration for a vital sign."""
    critical_high: float
    critical_low: float


class ScreeningInterval(TypedDict, total=False):
    """Screening interval configuration."""
    interval_days: int
    min_age: int
    max_age: int | None
    gender: str | None  # "male", "female", or None for all


# Critical lab value thresholds
CRITICAL_LAB_THRESHOLDS: dict[str, LabThreshold] = {
    # Electrolytes
    "Potassium": {"critical_high": 6.0, "critical_low": 2.5, "high": 5.5, "low": 3.0},
    "Sodium": {"critical_high": 160, "critical_low": 120, "high": 150, "low": 130},
    "Calcium": {"critical_high": 14.0, "critical_low": 6.0},
    "Magnesium": {"critical_high": 4.0, "critical_low": 1.0},
    "Phosphorus": {"critical_high": 9.0, "critical_low": 1.0},

    # Glucose/Metabolic
    "Glucose": {"critical_high": 500, "critical_low": 40, "high": 200, "low": 60},
    "HbA1c": {"critical_high": 14.0, "high": 9.0},

    # Renal
    "Creatinine": {"critical_high": 10.0, "high": 2.0},
    "BUN": {"critical_high": 100, "high": 30},
    "eGFR": {"critical_low": 15, "low": 30},

    # Hematology
    "Hemoglobin": {"critical_high": 20.0, "critical_low": 7.0, "high": 18.0, "low": 10.0},
    "Hematocrit": {"critical_high": 60, "critical_low": 20, "high": 52, "low": 30},
    "Platelets": {"critical_high": 1000, "critical_low": 20, "high": 450, "low": 100},
    "WBC": {"critical_high": 30, "critical_low": 1.0, "high": 15, "low": 3.5},

    # Cardiac
    "Troponin I": {"critical_high": 0.04},  # Any elevation is critical
    "Troponin T": {"critical_high": 0.01},
    "BNP": {"critical_high": 1000, "high": 400},
    "NT-proBNP": {"critical_high": 5000, "high": 900},

    # Coagulation
    "INR": {"critical_high": 5.0, "critical_low": 0.5, "high": 4.0},
    "PTT": {"critical_high": 100},
    "D-dimer": {"critical_high": 10.0, "high": 0.5},

    # Liver
    "AST": {"critical_high": 1000, "high": 120},
    "ALT": {"critical_high": 1000, "high": 120},
    "Bilirubin": {"critical_high": 15.0, "high": 3.0},
    "Ammonia": {"critical_high": 100},

    # Blood Gas
    "pH": {"critical_high": 7.55, "critical_low": 7.20},
    "pCO2": {"critical_high": 70, "critical_low": 20},
    "pO2": {"critical_low": 50},
    "Lactate": {"critical_high": 4.0, "high": 2.0},

    # Lipids (for trending, not usually critical)
    "LDL": {"high": 190},
    "Total Cholesterol": {"high": 240},
    "Triglycerides": {"critical_high": 1000, "high": 500},
}


# Critical vital sign thresholds
CRITICAL_VITAL_THRESHOLDS: dict[str, VitalThreshold] = {
    "blood_pressure_systolic": {"critical_high": 180, "critical_low": 80},
    "blood_pressure_diastolic": {"critical_high": 120, "critical_low": 50},
    "heart_rate": {"critical_high": 150, "critical_low": 40},
    "temperature": {"critical_high": 104.0, "critical_low": 95.0},  # Fahrenheit
    "oxygen_saturation": {"critical_low": 90},
    "respiratory_rate": {"critical_high": 30, "critical_low": 8},
}


# Preventive screening intervals
SCREENING_INTERVALS: dict[str, ScreeningInterval] = {
    # Cancer screenings
    "colonoscopy": {"interval_days": 3650, "min_age": 45, "max_age": 75},  # 10 years
    "mammogram": {"interval_days": 730, "min_age": 40, "max_age": 74, "gender": "female"},  # 2 years
    "pap_smear": {"interval_days": 1095, "min_age": 21, "max_age": 65, "gender": "female"},  # 3 years
    "lung_cancer_ct": {"interval_days": 365, "min_age": 50, "max_age": 80},  # Annual for smokers

    # Chronic disease screenings
    "diabetes_screen": {"interval_days": 1095, "min_age": 35},  # 3 years for prediabetes
    "lipid_panel": {"interval_days": 1825, "min_age": 40},  # 5 years baseline

    # Other preventive care
    "bone_density": {"interval_days": 730, "min_age": 65, "gender": "female"},  # 2 years
    "aaa_screen": {"interval_days": 0, "min_age": 65, "max_age": 75, "gender": "male"},  # One-time
    "eye_exam": {"interval_days": 365, "min_age": 60},  # Annual for diabetics/elderly
}


# Chronic disease monitoring thresholds (for worsening trends)
CHRONIC_DISEASE_THRESHOLDS = {
    "diabetes": {
        "hba1c_target": 7.0,
        "hba1c_concern": 8.0,
        "fasting_glucose_target": 130,
    },
    "hypertension": {
        "systolic_target": 130,
        "diastolic_target": 80,
    },
    "ckd": {
        "egfr_stage_3a": 45,
        "egfr_stage_3b": 30,
        "egfr_stage_4": 15,
    },
    "heart_failure": {
        "bnp_concern": 400,
        "weight_gain_lbs": 3,  # In 1-2 days
    },
}


def get_lab_severity(test_name: str, value: float) -> str | None:
    """
    Determine alert severity for a lab value.

    Returns:
        "critical", "high", or None if within normal range
    """
    thresholds = CRITICAL_LAB_THRESHOLDS.get(test_name)
    if not thresholds:
        return None

    # Check critical thresholds first
    if "critical_high" in thresholds and value >= thresholds["critical_high"]:
        return "critical"
    if "critical_low" in thresholds and value <= thresholds["critical_low"]:
        return "critical"

    # Check high/low thresholds
    if "high" in thresholds and value >= thresholds["high"]:
        return "high"
    if "low" in thresholds and value <= thresholds["low"]:
        return "high"

    return None


def get_vital_severity(vital_type: str, value: float) -> str | None:
    """
    Determine alert severity for a vital sign value.

    Returns:
        "critical" or None if within acceptable range
    """
    thresholds = CRITICAL_VITAL_THRESHOLDS.get(vital_type)
    if not thresholds:
        return None

    if "critical_high" in thresholds and value >= thresholds["critical_high"]:
        return "critical"
    if "critical_low" in thresholds and value <= thresholds["critical_low"]:
        return "critical"

    return None
