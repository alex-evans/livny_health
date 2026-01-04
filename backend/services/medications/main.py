
from . import dosing_data
from . import rxnorm


def get_patient_active_medications(patient: dict) -> list:
    """
    Get the active medications for a patient.
    """
    return patient.get("activeMedications", [])


def search(query: str) -> list:
    """
    Search for medications.
    """
    return rxnorm.search(query)


def get_default_duration(medication_name: str) -> dict:
    """
    Get default prescription values for a medication.
    """
    return dosing_data.get_default_duration(medication_name)

