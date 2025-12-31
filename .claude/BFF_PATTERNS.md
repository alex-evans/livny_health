# BFF Patterns and Conventions

BFFs (Backend for Frontend) orchestrate services and transform responses for specific frontends. This document defines how to build BFFs in Livny Health.

## Core Principle: BFFs Have No Business Logic

```python
# ✅ CORRECT - BFF orchestrates, services enforce rules
async def prescribe_medication(request: PrescribeRequest):
    # Get context from services
    allergies = await medication_service.get_allergies(patient_id)
    current_meds = await medication_service.get_active_medications(patient_id)
    
    # Check with CDS service
    alerts = await cds_service.check_prescription(drug_id, allergies, current_meds)
    
    # Create prescription (service enforces all business rules)
    prescription = await medication_service.create_prescription(request)
    
    # Transform response for frontend
    return transform_for_physician_ui(prescription, alerts)

# ❌ INCORRECT - BFF contains business logic
async def prescribe_medication(request: PrescribeRequest):
    # Validating dosage in BFF - this is business logic!
    if request.dosage > 1000:
        return {"error": "Dosage too high"}
    
    # Checking allergies in BFF - this is business logic!
    allergies = await medication_service.get_allergies(patient_id)
    for allergy in allergies:
        if allergy.allergen == "penicillin":
            return {"error": "Patient allergic"}
```

## BFF Responsibilities

### 1. Data Aggregation

Combine data from multiple services into a single response:

```python
# routers/encounter.py
@router.get("/encounters/{encounter_id}/context")
async def get_encounter_context(encounter_id: str):
    """
    Aggregate everything needed for encounter view.
    
    Single API call for frontend = better performance.
    """
    encounter = await clinical_doc_service.get_encounter(encounter_id)
    patient_id = encounter.patient_id
    
    # Fetch from multiple services in parallel
    async with httpx.AsyncClient() as client:
        patient_task = patient_service.get_patient(patient_id, client)
        meds_task = medication_service.get_active_medications(patient_id, client)
        allergies_task = medication_service.get_allergies(patient_id, client)
        labs_task = order_service.get_recent_labs(patient_id, client)
        problems_task = clinical_doc_service.get_active_problems(patient_id, client)
        
        # Wait for all to complete
        results = await asyncio.gather(
            patient_task,
            meds_task,
            allergies_task,
            labs_task,
            problems_task,
            return_exceptions=True  # Don't fail if one service is down
        )
    
    patient, meds, allergies, labs, problems = results
    
    # Handle partial failures gracefully
    if isinstance(meds, Exception):
        meds = []  # Degrade gracefully
    if isinstance(labs, Exception):
        labs = []
    
    # Transform for physician UI
    return {
        "patient": transform_patient_for_physician(patient),
        "medications": [transform_medication(m) for m in meds],
        "allergies": [transform_allergy(a) for a in allergies],
        "labs": transform_labs_summary(labs),
        "problems": problems,
        "encounter": encounter
    }
```

### 2. Response Transformation

Reshape service responses for specific frontend needs:

```python
# transforms/patient.py
def transform_patient_for_physician(patient: dict) -> dict:
    """
    Transform patient for physician chart view.
    
    Physicians need:
    - Quick demographics (name, age, MRN)
    - Photo if available
    - NOT insurance details, SSN, etc.
    """
    return {
        "id": patient["id"],
        "name": patient["full_name"],
        "age": calculate_age(patient["birth_date"]),
        "mrn": patient["mrn"],
        "sex": patient["sex"],
        "photo_url": patient.get("photo_url"),
    }

def transform_patient_for_registration(patient: dict) -> dict:
    """
    Transform patient for registration workflow.
    
    Registration needs:
    - Full demographics
    - Contact information
    - Insurance details
    - NOT clinical summary
    """
    return {
        "id": patient["id"],
        "full_name": patient["full_name"],
        "first_name": patient["first_name"],
        "last_name": patient["last_name"],
        "birth_date": patient["birth_date"],
        "ssn_last_four": patient["ssn"][-4:] if patient.get("ssn") else None,
        "address": format_address(patient["address"]),
        "phone": format_phone(patient["phone"]),
        "email": patient["email"],
        "insurance": patient["insurance_details"],
        "emergency_contact": patient.get("emergency_contact")
    }

def transform_patient_for_billing(patient: dict) -> dict:
    """
    Transform patient for billing workflow.
    
    Billing needs:
    - Identifiers (MRN, SSN)
    - Insurance info
    - NOT clinical data
    """
    return {
        "id": patient["id"],
        "name": patient["full_name"],
        "mrn": patient["mrn"],
        "ssn": patient["ssn"],
        "insurance": patient["insurance_details"],
        "guarantor": patient.get("guarantor")
    }
```

### 3. Workflow Orchestration

Coordinate complex multi-step workflows:

```python
# routers/medication.py
@router.post("/medications/prescribe")
async def prescribe_medication(request: PrescribeRequest, user: User = Depends(get_current_user)):
    """
    Orchestrate prescribing workflow:
    
    1. Gather patient context (allergies, meds, labs)
    2. Check clinical decision support
    3. If critical alerts, block prescription
    4. Create prescription (service enforces rules)
    5. Return aggregated response with alerts
    """
    
    # Step 1: Gather patient context for CDS
    async with httpx.AsyncClient() as client:
        context_tasks = [
            medication_service.get_allergies(request.patient_id, client),
            medication_service.get_active_medications(request.patient_id, client),
            order_service.get_recent_labs(request.patient_id, days=30, client)
        ]
        allergies, current_meds, labs = await asyncio.gather(*context_tasks)
    
    # Step 2: Check CDS for alerts
    cds_response = await cds_service.check_prescription(
        patient_id=request.patient_id,
        drug_id=request.drug_id,
        dosage=request.dosage,
        frequency=request.frequency,
        context={
            "allergies": allergies,
            "current_medications": current_meds,
            "recent_labs": labs,
            "workflow": "prescribing"
        }
    )
    
    # Step 3: Handle critical alerts
    critical_alerts = [a for a in cds_response.alerts if a.severity == "critical"]
    if critical_alerts and not request.override_reason:
        # Block prescription - return alerts for user to review
        return {
            "status": "blocked",
            "reason": "critical_alerts",
            "alerts": [transform_alert_for_physician(a) for a in critical_alerts],
            "message": "Critical safety alerts must be addressed before prescribing"
        }
    
    # Step 4: Create prescription (service handles all validation)
    try:
        prescription = await medication_service.create_prescription(
            patient_id=request.patient_id,
            drug_id=request.drug_id,
            dosage=request.dosage,
            frequency=request.frequency,
            duration_days=request.duration,
            instructions=request.instructions,
            indication=request.indication,
            prescriber_id=user.id,
            override_reason=request.override_reason
        )
    except httpx.HTTPStatusError as e:
        # Service rejected prescription - transform error for frontend
        error_detail = e.response.json()
        return {
            "status": "error",
            "error_code": error_detail.get("error"),
            "message": make_user_friendly(error_detail.get("message")),
            "ui_action": "show_error_modal"
        }
    
    # Step 5: Return success with any remaining alerts
    non_critical_alerts = [a for a in cds_response.alerts if a.severity != "critical"]
    
    return {
        "status": "success",
        "prescription": transform_prescription_for_physician(prescription),
        "alerts": [transform_alert_for_physician(a) for a in non_critical_alerts],
        "next_steps": [
            "Prescription will be transmitted to patient's pharmacy",
            "Patient will receive notification via patient portal"
        ]
    }
```

### 4. Configuration Resolution

Collapse configuration hierarchies into final settings:

```python
# routers/config.py
@router.get("/config/prescribing")
async def get_prescribing_config(user: User = Depends(get_current_user)):
    """
    Resolve prescribing configuration for this user.
    
    Configuration hierarchy (lowest to highest precedence):
    1. System defaults
    2. Facility settings
    3. Workflow settings
    4. User preferences
    """
    
    # Fetch all config layers
    config_tasks = [
        config_service.get_system_defaults(),
        config_service.get_facility_config(user.facility_id),
        config_service.get_workflow_config("prescribing"),
        config_service.get_user_preferences(user.id)
    ]
    
    system, facility, workflow, user_prefs = await asyncio.gather(*config_tasks)
    
    # Merge with precedence (user > workflow > facility > system)
    resolved = {
        **system,
        **facility,
        **workflow,
        **user_prefs
    }
    
    return {
        "cds_alerts": {
            "enabled": resolved.get("cds_alerts_enabled", True),
            "allergy_severity_threshold": resolved.get("allergy_threshold", "all"),
            "interaction_severity_threshold": resolved.get("interaction_threshold", "moderate"),
            "display_mode": resolved.get("alert_display_mode", "modal")
        },
        "defaults": {
            "drug_search_limit": resolved.get("drug_search_limit", 20),
            "default_duration_days": resolved.get("default_duration", 10),
            "show_generic_first": resolved.get("show_generic_first", True)
        },
        "ui": {
            "compact_mode": resolved.get("compact_mode", False),
            "auto_populate_dosing": resolved.get("auto_populate_dosing", True)
        }
    }
```

## Service Client Pattern

### Base Service Client

```python
# services/base.py
import httpx
from typing import Optional, Any
from config import settings

class BaseServiceClient:
    """
    Base class for service clients.
    
    Provides common functionality:
    - Timeout handling
    - Error handling
    - Retry logic
    - Logging
    """
    
    def __init__(self, base_url: str, service_name: str):
        self.base_url = base_url
        self.service_name = service_name
        self.timeout = 10.0  # Default timeout
    
    async def get(
        self,
        path: str,
        client: httpx.AsyncClient,
        params: Optional[dict] = None,
        timeout: Optional[float] = None
    ) -> Any:
        """Make GET request to service"""
        url = f"{self.base_url}{path}"
        
        try:
            response = await client.get(
                url,
                params=params,
                timeout=timeout or self.timeout
            )
            response.raise_for_status()
            return response.json()
        
        except httpx.TimeoutException:
            raise ServiceTimeoutError(f"{self.service_name} timed out")
        
        except httpx.HTTPStatusError as e:
            raise ServiceError(
                f"{self.service_name} returned error: {e.response.status_code}",
                status_code=e.response.status_code,
                detail=e.response.json()
            )
    
    async def post(
        self,
        path: str,
        client: httpx.AsyncClient,
        data: dict,
        timeout: Optional[float] = None
    ) -> Any:
        """Make POST request to service"""
        url = f"{self.base_url}{path}"
        
        try:
            response = await client.post(
                url,
                json=data,
                timeout=timeout or self.timeout
            )
            response.raise_for_status()
            return response.json()
        
        except httpx.TimeoutException:
            raise ServiceTimeoutError(f"{self.service_name} timed out")
        
        except httpx.HTTPStatusError as e:
            raise ServiceError(
                f"{self.service_name} returned error: {e.response.status_code}",
                status_code=e.response.status_code,
                detail=e.response.json()
            )

class ServiceError(Exception):
    """Service returned an error"""
    def __init__(self, message: str, status_code: int, detail: dict):
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)

class ServiceTimeoutError(Exception):
    """Service timed out"""
    pass
```

### Specific Service Client

```python
# services/medication_service.py
from services.base import BaseServiceClient
from config import settings
from typing import List, Optional

class MedicationServiceClient(BaseServiceClient):
    """Client for medication service"""
    
    def __init__(self):
        super().__init__(
            base_url=settings.medication_service_url,
            service_name="medication_service"
        )
    
    async def get_active_medications(
        self,
        patient_id: str,
        client: httpx.AsyncClient
    ) -> List[dict]:
        """Get patient's active medications"""
        return await self.get(
            f"/patients/{patient_id}/medications/active",
            client
        )
    
    async def get_allergies(
        self,
        patient_id: str,
        client: httpx.AsyncClient
    ) -> List[dict]:
        """Get patient's allergies"""
        return await self.get(
            f"/patients/{patient_id}/allergies",
            client
        )
    
    async def search_drugs(
        self,
        query: str,
        client: httpx.AsyncClient,
        limit: int = 20
    ) -> List[dict]:
        """Search drugs by name"""
        return await self.get(
            "/drugs/search",
            client,
            params={"query": query, "limit": limit}
        )
    
    async def create_prescription(
        self,
        patient_id: str,
        drug_id: str,
        dosage: str,
        frequency: str,
        duration_days: int,
        prescriber_id: str,
        instructions: Optional[str] = None,
        indication: Optional[str] = None,
        override_reason: Optional[str] = None
    ) -> dict:
        """Create a new prescription"""
        async with httpx.AsyncClient() as client:
            return await self.post(
                "/prescriptions",
                client,
                data={
                    "patient_id": patient_id,
                    "drug_id": drug_id,
                    "dosage": dosage,
                    "frequency": frequency,
                    "duration_days": duration_days,
                    "prescriber_id": prescriber_id,
                    "instructions": instructions,
                    "indication": indication,
                    "override_reason": override_reason
                }
            )

# Singleton instance
medication_service = MedicationServiceClient()
```

## Error Handling in BFF

### Transform Service Errors for Frontend

```python
# routers/medication.py
from fastapi import HTTPException

@router.post("/medications/prescribe")
async def prescribe_medication(request: PrescribeRequest):
    try:
        # Call services...
        return result
    
    except ServiceTimeoutError as e:
        # Service timed out
        raise HTTPException(
            status_code=503,
            detail={
                "error": "service_timeout",
                "message": "The request is taking longer than expected. Please try again.",
                "ui_action": "show_retry_button"
            }
        )
    
    except ServiceError as e:
        # Service returned error
        if e.status_code == 400:
            # Business rule violation
            raise HTTPException(
                status_code=400,
                detail={
                    "error": e.detail.get("error"),
                    "message": make_user_friendly(e.detail.get("message")),
                    "ui_action": "show_inline_error"
                }
            )
        elif e.status_code == 403:
            # Authorization error
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "unauthorized",
                    "message": "You don't have permission to perform this action.",
                    "ui_action": "show_permission_error"
                }
            )
        elif e.status_code == 404:
            # Not found
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "not_found",
                    "message": "The requested resource was not found.",
                    "ui_action": "redirect_to_search"
                }
            )
        else:
            # Other service error
            raise HTTPException(
                status_code=e.status_code,
                detail={
                    "error": "service_error",
                    "message": "An error occurred. Please try again.",
                    "ui_action": "show_error_toast"
                }
            )
    
    except Exception as e:
        # Unexpected error
        logger.exception("Unexpected error in prescribe endpoint")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "An unexpected error occurred. Please contact support if this persists.",
                "ui_action": "show_error_modal"
            }
        )

def make_user_friendly(technical_message: str) -> str:
    """Convert technical error messages to user-friendly ones"""
    error_map = {
        "Drug not found": "The selected medication is not available in our system.",
        "Patient not found": "We couldn't find the patient record. Please verify the patient ID.",
        "Invalid dosage": "The dosage you entered is not valid for this medication.",
        "Unauthorized prescriber": "You don't have permission to prescribe medications.",
        "DEA number required": "A DEA number is required to prescribe this controlled substance.",
        "Duplicate prescription": "This patient already has an active prescription for this medication."
    }
    
    return error_map.get(technical_message, technical_message)
```

## Transformation Helper Functions

```python
# transforms/helpers.py
from datetime import datetime

def calculate_age(birth_date: str) -> int:
    """Calculate age from birth date"""
    birth = datetime.fromisoformat(birth_date.replace('Z', '+00:00'))
    today = datetime.now()
    age = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1
    return age

def format_phone(phone: str) -> str:
    """Format phone number for display"""
    # Remove all non-digits
    digits = ''.join(c for c in phone if c.isdigit())
    
    # Format as (XXX) XXX-XXXX
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone

def format_address(address: dict) -> str:
    """Format address for display"""
    parts = [
        address.get("street"),
        address.get("city"),
        address.get("state"),
        address.get("zip")
    ]
    return ", ".join(p for p in parts if p)

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
```

## Testing BFF Orchestration

```python
# tests/test_medication_bff.py
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_prescribe_with_critical_alert_blocks(client: AsyncClient):
    """Test that critical alerts block prescription"""
    
    with patch('services.medication_service.get_allergies') as mock_allergies, \
         patch('services.cds_service.check_prescription') as mock_cds:
        
        # Setup: Patient has penicillin allergy
        mock_allergies.return_value = [
            {"allergen": "penicillin", "reaction": "anaphylaxis"}
        ]
        
        # CDS returns critical alert
        mock_cds.return_value = {
            "alerts": [
                {
                    "severity": "critical",
                    "type": "allergy",
                    "message": "Patient allergic to penicillin"
                }
            ]
        }
        
        # Attempt to prescribe amoxicillin (penicillin-based)
        response = await client.post("/medications/prescribe", json={
            "patient_id": "patient-123",
            "drug_id": "amox-500",
            "dosage": "500mg",
            "frequency": "TID",
            "duration": 10
        })
        
        # Should be blocked
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "blocked"
        assert "critical_alerts" in data["reason"]
        assert len(data["alerts"]) > 0

@pytest.mark.asyncio
async def test_prescribe_aggregates_context(client: AsyncClient):
    """Test that BFF properly aggregates context"""
    
    with patch('services.medication_service.get_allergies') as mock_allergies, \
         patch('services.medication_service.get_active_medications') as mock_meds, \
         patch('services.order_service.get_recent_labs') as mock_labs, \
         patch('services.cds_service.check_prescription') as mock_cds, \
         patch('services.medication_service.create_prescription') as mock_create:
        
        # Setup mocks
        mock_allergies.return_value = []
        mock_meds.return_value = []
        mock_labs.return_value = []
        mock_cds.return_value = {"alerts": []}
        mock_create.return_value = {"id": "rx-123"}
        
        # Make request
        response = await client.post("/medications/prescribe", json={
            "patient_id": "patient-123",
            "drug_id": "amox-500",
            "dosage": "500mg",
            "frequency": "TID",
            "duration": 10
        })
        
        # Verify all services were called
        assert mock_allergies.called
        assert mock_meds.called
        assert mock_labs.called
        assert mock_cds.called
        assert mock_create.called
        
        # Verify CDS received context
        cds_call_args = mock_cds.call_args[1]
        assert "allergies" in cds_call_args["context"]
        assert "current_medications" in cds_call_args["context"]
        assert "recent_labs" in cds_call_args["context"]
```

## Summary: BFF Checklist

When building BFF endpoints, ensure:

- [ ] No business logic in BFF (that's in services)
- [ ] Services called via service clients
- [ ] Responses transformed for specific frontend
- [ ] Errors transformed for user display
- [ ] Parallel requests where possible (asyncio.gather)
- [ ] Graceful degradation if service fails
- [ ] Timeouts configured
- [ ] Tests cover orchestration
- [ ] Configuration resolved if needed
