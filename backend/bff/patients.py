'''
API endpoints for managing patients
'''

from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel
from typing import Literal

from bff import dependencies


router = APIRouter(prefix='/patients', tags=['patients'])


def get_mock_recent_labs():
    """Return mock lab data for demonstration with trend indicators and data completeness."""
    today = datetime.now()

    return {
        "panels": [
            {
                "id": "panel-1",
                "panelName": "Basic Metabolic Panel",
                "collectionDate": (today - timedelta(days=1)).isoformat(),
                "lastUpdated": (today - timedelta(hours=22)).isoformat(),
                "results": [
                    {
                        "id": "lab-1",
                        "testName": "Glucose",
                        "value": "98",
                        "unit": "mg/dL",
                        "referenceRange": "70-100",
                        "status": "normal",
                        "collectionDate": (today - timedelta(days=1)).isoformat(),
                        "lastUpdated": (today - timedelta(hours=22)).isoformat(),
                        "acknowledged": True,
                        "acknowledgedBy": "dr-smith",
                        "acknowledgedAt": (today - timedelta(hours=20)).isoformat(),
                        "previousValue": {
                            "value": "110",
                            "collectionDate": (today - timedelta(days=90)).isoformat()
                        }
                    },
                    {
                        "id": "lab-2",
                        "testName": "BUN",
                        "value": "18",
                        "unit": "mg/dL",
                        "referenceRange": "7-20",
                        "status": "normal",
                        "collectionDate": (today - timedelta(days=1)).isoformat(),
                        "lastUpdated": (today - timedelta(hours=22)).isoformat(),
                        "acknowledged": True,
                        "acknowledgedBy": "dr-smith",
                        "acknowledgedAt": (today - timedelta(hours=20)).isoformat(),
                        "previousValue": {
                            "value": "17",
                            "collectionDate": (today - timedelta(days=90)).isoformat()
                        }
                    },
                    {
                        "id": "lab-3",
                        "testName": "Creatinine",
                        "value": "1.4",
                        "unit": "mg/dL",
                        "referenceRange": "0.7-1.3",
                        "status": "abnormal",
                        "collectionDate": (today - timedelta(days=1)).isoformat(),
                        "lastUpdated": (today - timedelta(hours=22)).isoformat(),
                        "acknowledged": True,
                        "acknowledgedBy": "dr-smith",
                        "acknowledgedAt": (today - timedelta(hours=20)).isoformat(),
                        "previousValue": {
                            "value": "1.1",
                            "collectionDate": (today - timedelta(days=90)).isoformat()
                        }
                    },
                    {
                        "id": "lab-4",
                        "testName": "Sodium",
                        "value": "140",
                        "unit": "mEq/L",
                        "referenceRange": "136-145",
                        "status": "normal",
                        "collectionDate": (today - timedelta(days=1)).isoformat(),
                        "lastUpdated": (today - timedelta(hours=22)).isoformat(),
                        "acknowledged": True,
                        "acknowledgedBy": "dr-smith",
                        "acknowledgedAt": (today - timedelta(hours=20)).isoformat(),
                        "previousValue": {
                            "value": "139",
                            "collectionDate": (today - timedelta(days=90)).isoformat()
                        }
                    },
                    {
                        "id": "lab-5",
                        "testName": "Potassium",
                        "value": "5.8",
                        "unit": "mEq/L",
                        "referenceRange": "3.5-5.0",
                        "status": "critical",
                        "collectionDate": (today - timedelta(days=1)).isoformat(),
                        "lastUpdated": (today - timedelta(hours=22)).isoformat(),
                        "acknowledged": False,
                        "acknowledgedBy": None,
                        "acknowledgedAt": None,
                        "previousValue": {
                            "value": "4.5",
                            "collectionDate": (today - timedelta(days=90)).isoformat()
                        }
                    },
                    {
                        "id": "lab-6",
                        "testName": "Chloride",
                        "value": "102",
                        "unit": "mEq/L",
                        "referenceRange": "98-106",
                        "status": "normal",
                        "collectionDate": (today - timedelta(days=1)).isoformat(),
                        "lastUpdated": (today - timedelta(hours=22)).isoformat(),
                        "acknowledged": True,
                        "acknowledgedBy": "dr-smith",
                        "acknowledgedAt": (today - timedelta(hours=20)).isoformat()
                    },
                    {
                        "id": "lab-7",
                        "testName": "CO2",
                        "value": "24",
                        "unit": "mEq/L",
                        "referenceRange": "23-29",
                        "status": "normal",
                        "collectionDate": (today - timedelta(days=1)).isoformat(),
                        "lastUpdated": (today - timedelta(hours=22)).isoformat(),
                        "acknowledged": True,
                        "acknowledgedBy": "dr-smith",
                        "acknowledgedAt": (today - timedelta(hours=20)).isoformat()
                    }
                ]
            },
            {
                "id": "panel-2",
                "panelName": "Lipid Panel",
                "collectionDate": (today - timedelta(days=45)).isoformat(),
                "lastUpdated": (today - timedelta(days=44)).isoformat(),
                "results": [
                    {
                        "id": "lab-8",
                        "testName": "Total Cholesterol",
                        "value": "210",
                        "unit": "mg/dL",
                        "referenceRange": "<200",
                        "status": "abnormal",
                        "collectionDate": (today - timedelta(days=45)).isoformat(),
                        "lastUpdated": (today - timedelta(days=44)).isoformat(),
                        "acknowledged": True,
                        "acknowledgedBy": "dr-jones",
                        "acknowledgedAt": (today - timedelta(days=44)).isoformat(),
                        "previousValue": {
                            "value": "225",
                            "collectionDate": (today - timedelta(days=180)).isoformat()
                        }
                    },
                    {
                        "id": "lab-9",
                        "testName": "HDL",
                        "value": "55",
                        "unit": "mg/dL",
                        "referenceRange": ">40",
                        "status": "normal",
                        "collectionDate": (today - timedelta(days=45)).isoformat(),
                        "lastUpdated": (today - timedelta(days=44)).isoformat(),
                        "acknowledged": True,
                        "acknowledgedBy": "dr-jones",
                        "acknowledgedAt": (today - timedelta(days=44)).isoformat(),
                        "previousValue": {
                            "value": "48",
                            "collectionDate": (today - timedelta(days=180)).isoformat()
                        }
                    },
                    {
                        "id": "lab-10",
                        "testName": "LDL",
                        "value": "135",
                        "unit": "mg/dL",
                        "referenceRange": "<100",
                        "status": "abnormal",
                        "collectionDate": (today - timedelta(days=45)).isoformat(),
                        "lastUpdated": (today - timedelta(days=44)).isoformat(),
                        "acknowledged": True,
                        "acknowledgedBy": "dr-jones",
                        "acknowledgedAt": (today - timedelta(days=44)).isoformat(),
                        "previousValue": {
                            "value": "125",
                            "collectionDate": (today - timedelta(days=180)).isoformat()
                        }
                    },
                    {
                        "id": "lab-11",
                        "testName": "Triglycerides",
                        "value": "150",
                        "unit": "mg/dL",
                        "referenceRange": "<150",
                        "status": "normal",
                        "collectionDate": (today - timedelta(days=45)).isoformat(),
                        "lastUpdated": (today - timedelta(days=44)).isoformat(),
                        "acknowledged": True,
                        "acknowledgedBy": "dr-jones",
                        "acknowledgedAt": (today - timedelta(days=44)).isoformat(),
                        "previousValue": {
                            "value": "165",
                            "collectionDate": (today - timedelta(days=180)).isoformat()
                        }
                    }
                ]
            },
            {
                "id": "panel-3",
                "panelName": "Complete Blood Count",
                "collectionDate": (today - timedelta(days=60)).isoformat(),
                "lastUpdated": (today - timedelta(days=59)).isoformat(),
                "results": [
                    {
                        "id": "lab-12",
                        "testName": "WBC",
                        "value": "7.5",
                        "unit": "K/uL",
                        "referenceRange": "4.5-11.0",
                        "status": "normal",
                        "collectionDate": (today - timedelta(days=60)).isoformat(),
                        "lastUpdated": (today - timedelta(days=59)).isoformat(),
                        "acknowledged": True,
                        "acknowledgedBy": "dr-smith",
                        "acknowledgedAt": (today - timedelta(days=59)).isoformat(),
                        "previousValue": {
                            "value": "7.3",
                            "collectionDate": (today - timedelta(days=200)).isoformat()
                        }
                    },
                    {
                        "id": "lab-13",
                        "testName": "RBC",
                        "value": "4.8",
                        "unit": "M/uL",
                        "referenceRange": "4.5-5.5",
                        "status": "normal",
                        "collectionDate": (today - timedelta(days=60)).isoformat(),
                        "lastUpdated": (today - timedelta(days=59)).isoformat(),
                        "acknowledged": True,
                        "acknowledgedBy": "dr-smith",
                        "acknowledgedAt": (today - timedelta(days=59)).isoformat()
                    },
                    {
                        "id": "lab-14",
                        "testName": "Hemoglobin",
                        "value": "14.2",
                        "unit": "g/dL",
                        "referenceRange": "13.5-17.5",
                        "status": "normal",
                        "collectionDate": (today - timedelta(days=60)).isoformat(),
                        "lastUpdated": (today - timedelta(days=59)).isoformat(),
                        "acknowledged": True,
                        "acknowledgedBy": "dr-smith",
                        "acknowledgedAt": (today - timedelta(days=59)).isoformat(),
                        "previousValue": {
                            "value": "13.8",
                            "collectionDate": (today - timedelta(days=200)).isoformat()
                        }
                    },
                    {
                        "id": "lab-15",
                        "testName": "Hematocrit",
                        "value": "42",
                        "unit": "%",
                        "referenceRange": "38-50",
                        "status": "normal",
                        "collectionDate": (today - timedelta(days=60)).isoformat(),
                        "lastUpdated": (today - timedelta(days=59)).isoformat(),
                        "acknowledged": True,
                        "acknowledgedBy": "dr-smith",
                        "acknowledgedAt": (today - timedelta(days=59)).isoformat()
                    },
                    {
                        "id": "lab-16",
                        "testName": "Platelets",
                        "value": "250",
                        "unit": "K/uL",
                        "referenceRange": "150-400",
                        "status": "normal",
                        "collectionDate": (today - timedelta(days=60)).isoformat(),
                        "lastUpdated": (today - timedelta(days=59)).isoformat(),
                        "acknowledged": True,
                        "acknowledgedBy": "dr-smith",
                        "acknowledgedAt": (today - timedelta(days=59)).isoformat()
                    }
                ]
            },
            {
                "id": "panel-pending-1",
                "panelName": "Thyroid Panel",
                "collectionDate": (today - timedelta(hours=4)).isoformat(),
                "lastUpdated": (today - timedelta(hours=2)).isoformat(),
                "results": [
                    {
                        "id": "lab-pending-1",
                        "testName": "TSH",
                        "value": "",
                        "unit": "mIU/L",
                        "referenceRange": "0.4-4.0",
                        "status": "in_progress",
                        "collectionDate": (today - timedelta(hours=4)).isoformat(),
                        "lastUpdated": (today - timedelta(hours=2)).isoformat(),
                        "acknowledged": False,
                        "acknowledgedBy": None,
                        "acknowledgedAt": None
                    },
                    {
                        "id": "lab-pending-2",
                        "testName": "Free T4",
                        "value": "",
                        "unit": "ng/dL",
                        "referenceRange": "0.8-1.8",
                        "status": "in_progress",
                        "collectionDate": (today - timedelta(hours=4)).isoformat(),
                        "lastUpdated": (today - timedelta(hours=2)).isoformat(),
                        "acknowledged": False,
                        "acknowledgedBy": None,
                        "acknowledgedAt": None
                    }
                ]
            }
        ],
        "ungroupedResults": [
            {
                "id": "lab-17",
                "testName": "HbA1c",
                "value": "6.8",
                "unit": "%",
                "referenceRange": "<5.7",
                "status": "abnormal",
                "collectionDate": (today - timedelta(days=30)).isoformat(),
                "lastUpdated": (today - timedelta(days=29)).isoformat(),
                "acknowledged": True,
                "acknowledgedBy": "dr-smith",
                "acknowledgedAt": (today - timedelta(days=29)).isoformat(),
                "previousValue": {
                    "value": "6.2",
                    "collectionDate": (today - timedelta(days=120)).isoformat()
                }
            },
            {
                "id": "lab-19",
                "testName": "Vitamin D, 25-Hydroxy",
                "value": "28",
                "unit": "ng/mL",
                "referenceRange": "30-100",
                "status": "abnormal",
                "collectionDate": (today - timedelta(days=120)).isoformat(),
                "lastUpdated": (today - timedelta(days=119)).isoformat(),
                "acknowledged": True,
                "acknowledgedBy": "dr-jones",
                "acknowledgedAt": (today - timedelta(days=118)).isoformat()
            },
            {
                "id": "lab-20",
                "testName": "eGFR",
                "value": "65",
                "unit": "mL/min/1.73m²",
                "referenceRange": ">60",
                "status": "normal",
                "collectionDate": (today - timedelta(days=1)).isoformat(),
                "lastUpdated": (today - timedelta(hours=22)).isoformat(),
                "acknowledged": True,
                "acknowledgedBy": "dr-smith",
                "acknowledgedAt": (today - timedelta(hours=20)).isoformat(),
                "previousValue": {
                    "value": "72",
                    "collectionDate": (today - timedelta(days=90)).isoformat()
                }
            },
            {
                "id": "lab-critical-1",
                "testName": "Troponin I",
                "value": "0.85",
                "unit": "ng/mL",
                "referenceRange": "<0.04",
                "status": "critical",
                "collectionDate": (today - timedelta(hours=2)).isoformat(),
                "lastUpdated": (today - timedelta(hours=1)).isoformat(),
                "acknowledged": False,
                "acknowledgedBy": None,
                "acknowledgedAt": None
            },
            {
                "id": "lab-pending-3",
                "testName": "Urinalysis",
                "value": "",
                "unit": "",
                "referenceRange": "",
                "status": "pending",
                "collectionDate": (today - timedelta(hours=6)).isoformat(),
                "lastUpdated": (today - timedelta(hours=6)).isoformat(),
                "acknowledged": False,
                "acknowledgedBy": None,
                "acknowledgedAt": None
            }
        ]
    }


@router.get("/")
async def get_patients():
    """Get all patients."""
    patient_repo = dependencies.get_patient_repo()
    patients = await patient_repo.list()
    return [p.to_bff_dict() for p in patients]


@router.get("/{patient_id}")
async def get_patient(patient_id: str = Path(..., description="The patient ID")):
    """Get a single patient with their allergies, active medications, and next appointment."""
    patient_repo = dependencies.get_patient_repo()
    allergy_repo = dependencies.get_allergy_repo()
    medication_request_repo = dependencies.get_medication_request_repo()
    appointment_repo = dependencies.get_appointment_repo()

    patient = await patient_repo.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get all allergies (including inactive) for the toggle view
    all_allergies = await allergy_repo.get_all_by_patient(patient_id)
    medications = await medication_request_repo.get_active_for_patient(patient_id)
    upcoming_appointments = await appointment_repo.get_upcoming_for_patient(patient_id)

    result = patient.to_bff_dict()
    result["allergies"] = [a.to_bff_dict() for a in all_allergies]
    result["activeMedications"] = [m.to_bff_dict() for m in medications]

    # Add next appointment if available
    if upcoming_appointments:
        next_appt = upcoming_appointments[0]
        result["nextAppointment"] = {
            "date": next_appt.start.strftime("%m/%d/%Y"),
            "time": next_appt.start.strftime("%I:%M %p").lstrip("0"),
            "reason": next_appt.reason or next_appt.visit_type,
        }

    # Add mock recent labs
    result["recentLabs"] = get_mock_recent_labs()

    return result


@router.get("/{patient_id}/visits")
async def get_visit_history(
    patient_id: str = Path(..., description="The patient ID"),
    days_back: int = Query(365, ge=1, le=3650, description="Number of days of history to retrieve"),
    include_all: bool = Query(False, description="Include cancelled and no-show visits"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of visits to return"),
    offset: int = Query(0, ge=0, description="Number of visits to skip for pagination"),
    visit_type: str | None = Query(None, description="Filter by visit type (e.g., office_visit, telehealth)"),
    provider_id: str | None = Query(None, description="Filter by provider ID"),
    diagnosis_code: str | None = Query(None, description="Filter by ICD-10 diagnosis code (partial match)"),
    search_query: str | None = Query(None, description="Full-text search in SOAP notes, chief complaint, diagnoses"),
    date_from: str | None = Query(None, description="Filter visits on or after this date (ISO format)"),
    date_to: str | None = Query(None, description="Filter visits on or before this date (ISO format)"),
):
    """
    Get visit history for a patient with SOAP notes, vitals, medications, and orders.

    Supports filtering by:
    - Visit type (office_visit, telehealth, urgent_care, etc.)
    - Provider
    - Diagnosis code (ICD-10, partial match supported)
    - Full-text search across SOAP notes, chief complaint, and diagnoses
    - Date range

    Returns visit notes including:
    - Chief complaint and diagnoses
    - SOAP note (Subjective, Objective, Assessment, Plan)
    - Vital signs recorded during the visit
    - Medications prescribed or modified
    - Orders placed (labs, imaging, referrals) with status
    """
    # Verify patient exists
    patient_repo = dependencies.get_patient_repo()
    patient = await patient_repo.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Parse date filters
    parsed_date_from = None
    parsed_date_to = None
    if date_from:
        try:
            parsed_date_from = datetime.fromisoformat(date_from.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_from format. Use ISO format.")

    if date_to:
        try:
            parsed_date_to = datetime.fromisoformat(date_to.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_to format. Use ISO format.")

    # Get visit history
    visit_history_service = dependencies.get_visit_history_service()
    history_response = await visit_history_service.get_visit_history(
        patient_id=patient_id,
        days_back=days_back,
        include_all=include_all,
        limit=limit,
        offset=offset,
        visit_type=visit_type,
        provider_id=provider_id,
        diagnosis_code=diagnosis_code,
        search_query=search_query,
        date_from=parsed_date_from,
        date_to=parsed_date_to,
    )

    return history_response.to_dict()


@router.get("/{patient_id}/visits/providers")
async def get_visit_providers(
    patient_id: str = Path(..., description="The patient ID"),
):
    """
    Get all unique providers who have treated a patient.

    Returns a list of providers with their ID, name, role, and specialty.
    Useful for populating provider filter dropdowns.
    """
    # Verify patient exists
    patient_repo = dependencies.get_patient_repo()
    patient = await patient_repo.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get providers
    visit_history_service = dependencies.get_visit_history_service()
    providers = await visit_history_service.get_providers_for_patient(patient_id)

    return {"providers": providers}


@router.get("/{patient_id}/problems/resolved")
async def get_resolved_problems(
    patient_id: str = Path(..., description="The patient ID"),
):
    """
    Get all resolved problems for a patient.

    Returns problems sorted by resolved date (most recently resolved first).
    Useful for viewing historical problems that are no longer active.
    """
    # Verify patient exists
    patient_repo = dependencies.get_patient_repo()
    patient = await patient_repo.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    problem_list_service = dependencies.get_problem_list_service()
    resolved_problems = await problem_list_service.get_resolved_problems(patient_id)

    return {
        "problems": [p.to_bff_dict() for p in resolved_problems],
        "count": len(resolved_problems),
    }


@router.get("/{patient_id}/problems/{icd10_code}")
async def get_problem_detail(
    patient_id: str = Path(..., description="The patient ID"),
    icd10_code: str = Path(..., description="The ICD-10 code of the problem"),
):
    """
    Get detailed information for a specific problem.

    Returns:
    - Problem details with all fields
    - History timeline (onset, progression, visits, status changes)
    - Treatment history with outcomes
    - Last addressed date
    - Current treatment
    """
    # Verify patient exists
    patient_repo = dependencies.get_patient_repo()
    patient = await patient_repo.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get problem detail
    problem_detail_service = dependencies.get_problem_detail_service()
    detail_response = await problem_detail_service.get_problem_detail(
        patient_id=patient_id,
        icd10_code=icd10_code,
    )

    if not detail_response:
        raise HTTPException(
            status_code=404,
            detail=f"Problem with ICD-10 code '{icd10_code}' not found"
        )

    return detail_response.to_dict()


@router.get("/{patient_id}/labs/{test_name}/history")
async def get_lab_history(
    patient_id: str = Path(..., description="The patient ID"),
    test_name: str = Path(..., description="The lab test name"),
    days_back: int = Query(365, ge=1, le=3650, description="Number of days of history to retrieve"),
):
    """
    Get historical lab results for a specific test.

    Returns history entries and trend analysis for the specified test.
    """
    # Verify patient exists
    patient_repo = dependencies.get_patient_repo()
    patient = await patient_repo.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get lab history
    lab_history_service = dependencies.get_lab_history_service()
    history_response = await lab_history_service.get_lab_history(
        patient_id=patient_id,
        test_name=test_name,
        days_back=days_back,
    )

    if not history_response:
        raise HTTPException(
            status_code=404,
            detail=f"No lab history found for test '{test_name}'"
        )

    return history_response.to_dict()


# Request models for problem status management
class UpdateProblemStatusRequest(BaseModel):
    """Request body for updating problem status."""
    status: Literal["active", "inactive", "resolved", "rule_out"]
    providerName: str


class ResolveProblemRequest(BaseModel):
    """Request body for resolving a problem."""
    providerName: str


class ReactivateProblemRequest(BaseModel):
    """Request body for reactivating a problem."""
    providerName: str


@router.patch("/{patient_id}/problems/{icd10_code}/status")
async def update_problem_status(
    request: UpdateProblemStatusRequest,
    patient_id: str = Path(..., description="The patient ID"),
    icd10_code: str = Path(..., description="The ICD-10 code of the problem"),
):
    """
    Update the status of a problem.

    Supports changing status to active, inactive, resolved, or rule_out.
    When marking as resolved, automatically sets resolved_date and resolved_by_provider.
    When reactivating, clears the resolution fields.
    """
    from resources import ProblemStatus

    # Map string status to enum
    status_map = {
        "active": ProblemStatus.ACTIVE,
        "inactive": ProblemStatus.INACTIVE,
        "resolved": ProblemStatus.RESOLVED,
        "rule_out": ProblemStatus.RULE_OUT,
    }
    new_status = status_map[request.status]

    problem_list_service = dependencies.get_problem_list_service()
    updated_problem = await problem_list_service.update_problem_status(
        patient_id=patient_id,
        icd10_code=icd10_code,
        new_status=new_status,
        provider_name=request.providerName,
    )

    if not updated_problem:
        raise HTTPException(
            status_code=404,
            detail=f"Problem with ICD-10 code '{icd10_code}' not found"
        )

    return updated_problem.to_bff_dict()


@router.post("/{patient_id}/problems/{icd10_code}/resolve")
async def resolve_problem(
    request: ResolveProblemRequest,
    patient_id: str = Path(..., description="The patient ID"),
    icd10_code: str = Path(..., description="The ICD-10 code of the problem"),
):
    """
    Mark a problem as resolved.

    Sets status to RESOLVED and records the resolution date and provider.
    """
    problem_list_service = dependencies.get_problem_list_service()
    updated_problem = await problem_list_service.resolve_problem(
        patient_id=patient_id,
        icd10_code=icd10_code,
        provider_name=request.providerName,
    )

    if not updated_problem:
        raise HTTPException(
            status_code=404,
            detail=f"Problem with ICD-10 code '{icd10_code}' not found"
        )

    return updated_problem.to_bff_dict()


@router.post("/{patient_id}/problems/{icd10_code}/reactivate")
async def reactivate_problem(
    request: ReactivateProblemRequest,
    patient_id: str = Path(..., description="The patient ID"),
    icd10_code: str = Path(..., description="The ICD-10 code of the problem"),
):
    """
    Reactivate a resolved or inactive problem.

    Sets status back to ACTIVE and clears resolution tracking fields.
    Useful when a previously resolved condition recurs.
    """
    problem_list_service = dependencies.get_problem_list_service()
    updated_problem = await problem_list_service.reactivate_problem(
        patient_id=patient_id,
        icd10_code=icd10_code,
        provider_name=request.providerName,
    )

    if not updated_problem:
        raise HTTPException(
            status_code=404,
            detail=f"Problem with ICD-10 code '{icd10_code}' not found"
        )

    return updated_problem.to_bff_dict()
