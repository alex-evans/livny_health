"""
This module provides functions to manage patient data.
"""

from .fake_data import FAKE_PATIENTS


def find_patient(patient_id: str):
    for patient in FAKE_PATIENTS:
        if patient["id"] == patient_id:
            return patient
    return None


