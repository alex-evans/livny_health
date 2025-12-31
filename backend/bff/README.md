# Livny Health - BFF Layer (Backend for Frontend)

> **Note for Claude Code**: Before working on BFFs, please review:
> - `.claude/BFF_PATTERNS.md` - BFF structure and orchestration patterns
> - `.claude/SERVICE_PATTERNS.md` - How to call services
> - Root `.claude/API_CONTRACTS.md` - Frontend-facing API contracts
> - Root `.claude/README.md` - Overall architecture

## What is the BFF Layer?

The BFF (Backend for Frontend) layer sits between frontends and services. It:
- **Aggregates** data from multiple services
- **Transforms** responses for specific frontend needs
- **Orchestrates** service calls in the right order
- **Resolves** configuration hierarchies
- **Applies** workflow context

**BFFs are frontend-specific, not user-role-specific.** We have:
- Physician BFF (web application for providers)
- Patient Portal BFF (patient-facing mobile/web)
- Integration BFF (for external systems via API)

## Architecture

```
Frontend (React) → BFF Layer → Services Layer → Database
                     ↓
              Orchestration
              Transformation
              Configuration
```

**Key principle**: BFFs have NO business logic. They orchestrate and transform, but services enforce rules.

## BFF Structure

Each BFF follows this pattern:

```
physician_bff/
├── __init__.py
├── main.py                 # FastAPI app, middleware, startup
├── config.py              # Configuration
├── routers/               # API endpoints (frontend-facing)
│   ├── __init__.py
│   ├── encounter.py       # Encounter/chart endpoints
│   ├── medication.py      # Medication/prescribing endpoints
│   └── documentation.py   # Documentation endpoints
├── services/              # Service clients (call services layer)
│   ├── __init__.py
│   ├── patient_service.py
│   ├── medication_service.py
│   ├── cds_service.py
│   └── base.py           # Base service client
├── transforms/            # Response transformations
│   ├── __init__.py
│   ├── patient.py
│   ├── medication.py
│   └── alert.py
├── models/                # Pydantic models (request/response)
│   ├── __init__.py
│   ├── requests.py
│   └── responses.py
├── middleware/            # Custom middleware
│   ├── __init__.py
│   └── auth.py
├── tests/
├── requirements.txt
└── Dockerfile
```

## Core Responsibilities

### 1. Data Aggregation

BFFs combine data from multiple services into a single response:

```python
# routers/encounter.py
@router.get("/encounters/{encounter_id}/context")
async def get_encounter_context(
    encounter_id: str,
    user: User = Depends(get_current_user)
):
    """
    Aggregate data from multiple services for encounter view.
    This is BFF responsibility - not service responsibility.
    """
    # Get encounter to find patient_id
    encounter = await clinical_doc_service.get_encounter(encounter_id)
    patient_id = encounter.patient_id
    
    # Parallel fetch from multiple services
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            patient_service.get_patient(patient_id, client),
            medication_service.get_active_medications(patient_id, client),
            medication_service.get_allergies(patient_id, client),
            order_service.get_recent_labs(patient_id, days=90, client),
            clinical_doc_service.get_active_problems(patient_id, client)
        )
    
    patient, medications, allergies, labs, problems = results
    
    # Transform for frontend
    return {
        "patient": transform_patient_for_physician(patient),
        "medications": [transform_medication(m) for m in medications],
        "allergies": [transform_allergy(a) for a in allergies],
        "labs": transform_labs_summary(labs),
        "problems": problems,
        "encounter": encounter
    }
```

### 2. Response Transformation

BFFs reshape service responses for frontend needs:

```python
# transforms/patient.py
def transform_patient_for_physician(patient: dict) -> dict:
    """
    Transform patient data for physician UI.
    Physicians need different fields than registration clerks.
    """
    return {
        "id": patient["id"],
        "name": patient["full_name"],
        "age": calculate_age(patient["birth_date"]),
        "mrn": patient["mrn"],
        "photo_url": patient.get("photo_url"),
        # Physician doesn't need SSN, insurance details in chart header
    }

def transform_patient_for_registration(patient: dict) -> dict:
    """
    Transform patient data for registration UI.
    Registration needs demographics and insurance.
    """
    return {
        "id": patient["id"],
        "full_name": patient["full_name"],
        "birth_date": patient["birth_date"],
        "ssn_last_four": patient["ssn"][-4:],
        "address": patient["address"],
        "phone": patient["phone"],
        "insurance": patient["insurance_details"],
        # Registration doesn't need clinical summary
    }
```

### 3. Orchestration

BFFs coordinate complex workflows across services:

```python
# routers/medication.py
@router.post("/medications/prescribe")
async def prescribe_medication(
    request: PrescribeRequest,
    user: User = Depends(get_current_user)
):
    """
    Orchestrate prescription workflow:
    1. Get patient context for CDS
    2. Check with CDS service for alerts
    3. If safe, create prescription via medication service
    4. Return aggregated response
    """
    # Step 1: Get patient context
    async with httpx.AsyncClient() as client:
        allergies = await medication_service.get_allergies(request.patient_id, client)
        current_meds = await medication_service.get_active_medications(
            request.patient_id, client
        )
        recent_labs = await order_service.get_recent_labs(
            request.patient_id, days=30, client
        )
    
    # Step 2: Check with CDS
    cds_response = await cds_service.check_prescription(
        patient_id=request.patient_id,
        drug_id=request.drug_id,
        dosage=request.dosage,
        context={
            "allergies": allergies,
            "current_medications": current_meds,
            "recent_labs": recent_labs
        }
    )
    
    # Step 3: If critical alerts, block prescription
    has_critical = any(a.severity == "critical" for a in cds_response.alerts)
    if has_critical and not request.override_reason:
        return {
            "status": "blocked",
            "alerts": [transform_alert_for_physician(a) for a in cds_response.alerts]
        }
    
    # Step 4: Create prescription (service enforces business rules)
    prescription = await medication_service.create_prescription(
        patient_id=request.patient_id,
        drug_id=request.drug_id,
        dosage=request.dosage,
        frequency=request.frequency,
        duration_days=request.duration,
        prescriber_id=user.id,
        override_reason=request.override_reason
    )
    
    # Step 5: Return aggregated response
    return {
        "status": "success",
        "prescription": transform_prescription_for_physician(prescription),
        "alerts": [transform_alert_for_physician(a) for a in cds_response.alerts 
                   if a.severity != "critical"]
    }
```

### 4. Configuration Resolution

BFFs collapse configuration hierarchies:

```python
# routers/medication.py
async def get_prescribing_context(
    patient_id: str,
    user: User = Depends(get_current_user)
):
    """
    Resolve configuration for prescribing workflow.
    BFF collapses: system → facility → workflow → user preferences
    """
    # Get all config layers
    system_config = await config_service.get_system_defaults()
    facility_config = await config_service.get_facility_config(user.facility_id)
    workflow_config = await config_service.get_workflow_config("prescribing")
    user_prefs = await config_service.get_user_preferences(user.id)
    
    # Merge with precedence (user > workflow > facility > system)
    resolved_config = {
        **system_config,
        **facility_config,
        **workflow_config,
        **user_prefs
    }
    
    return resolved_config
```

## Service Client Pattern

BFFs use service clients to call backend services:

```python
# services/medication_service.py
import httpx
from typing import List, Optional

class MedicationServiceClient:
    """Client for calling medication service"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    async def get_active_medications(
        self,
        patient_id: str,
        client: httpx.AsyncClient
    ) -> List[dict]:
        """Get patient's active medications"""
        response = await client.get(
            f"{self.base_url}/patients/{patient_id}/medications/active",
            timeout=5.0  # Timeout for resilience
        )
        response.raise_for_status()
        return response.json()
    
    async def create_prescription(
        self,
        patient_id: str,
        drug_id: str,
        dosage: str,
        frequency: str,
        duration_days: int,
        prescriber_id: str,
        override_reason: Optional[str] = None
    ) -> dict:
        """Create a new prescription"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/prescriptions",
                json={
                    "patient_id": patient_id,
                    "drug_id": drug_id,
                    "dosage": dosage,
                    "frequency": frequency,
                    "duration_days": duration_days,
                    "prescriber_id": prescriber_id,
                    "override_reason": override_reason
                },
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
```

## Request/Response Models

BFFs define frontend-facing contracts:

```python
# models/requests.py
from pydantic import BaseModel, Field
from typing import Optional

class PrescribeRequest(BaseModel):
    """Request from frontend to prescribe medication"""
    patient_id: str = Field(..., description="Patient identifier")
    drug_id: str = Field(..., description="Drug identifier")
    dosage: str = Field(..., description="Dosage (e.g., '500mg')")
    frequency: str = Field(..., description="Frequency (QD, BID, TID, QID)")
    duration: int = Field(..., ge=1, le=365, description="Duration in days")
    instructions: Optional[str] = Field(None, description="Patient instructions")
    indication: Optional[str] = Field(None, description="Reason for prescription")
    override_reason: Optional[str] = Field(None, description="Reason for overriding alerts")

# models/responses.py
class PrescriptionResponse(BaseModel):
    """Response to frontend after prescribing"""
    status: str = Field(..., description="success, error, or blocked")
    prescription: Optional[dict] = Field(None, description="Prescription details")
    alerts: List[dict] = Field(default_factory=list, description="Clinical alerts")
    next_steps: Optional[List[str]] = Field(None, description="What happens next")
```

## Error Handling

BFFs transform service errors for frontend consumption:

```python
@router.post("/medications/prescribe")
async def prescribe_medication(request: PrescribeRequest):
    try:
        # Call services...
        return result
    
    except httpx.HTTPStatusError as e:
        # Service returned error - transform for frontend
        if e.response.status_code == 400:
            error_detail = e.response.json()
            raise HTTPException(
                status_code=400,
                detail={
                    "error": error_detail.get("error"),
                    "message": make_user_friendly(error_detail.get("message")),
                    "ui_action": "show_error_toast"
                }
            )
        elif e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "not_found",
                    "message": "The requested resource was not found",
                    "ui_action": "redirect_to_home"
                }
            )
    
    except httpx.TimeoutException:
        # Service timeout - tell frontend to retry
        raise HTTPException(
            status_code=503,
            detail={
                "error": "service_timeout",
                "message": "The request timed out. Please try again.",
                "ui_action": "show_retry_button"
            }
        )
    
    except Exception as e:
        # Unexpected error
        logger.exception("Unexpected error in prescribe endpoint")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": "An unexpected error occurred. Please try again.",
                "ui_action": "show_error_modal"
            }
        )

def make_user_friendly(message: str) -> str:
    """Transform technical error messages for users"""
    mapping = {
        "Drug not found": "The selected medication is not available.",
        "Patient not found": "Patient record not found. Please verify the patient ID.",
        "Invalid dosage": "The dosage entered is not valid for this medication.",
    }
    return mapping.get(message, message)
```

## Middleware

BFFs handle cross-cutting concerns:

```python
# middleware/auth.py
from fastapi import Request, HTTPException
from jose import jwt

async def auth_middleware(request: Request, call_next):
    """Verify JWT token and attach user to request"""
    
    # Skip auth for health check
    if request.url.path == "/health":
        return await call_next(request)
    
    # Get token from header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = auth_header.split(" ")[1]
    
    try:
        # Verify token (replace with actual verification)
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = {
            "id": payload["user_id"],
            "name": payload["name"],
            "role": payload["role"]
        }
        request.state.user = user
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return await call_next(request)
```

## CORS Configuration

BFFs configure CORS for frontend access:

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Physician BFF", version="1.0.0")

# CORS - restrict to frontend domain in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://app.livnyhealth.com"  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing BFFs

BFFs test orchestration, not business logic:

```python
# tests/test_medication_bff.py
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_prescribe_with_alerts(client: AsyncClient):
    """Test that BFF properly handles CDS alerts"""
    
    # Mock service responses
    with patch('services.medication_service.get_allergies') as mock_allergies, \
         patch('services.cds_service.check_prescription') as mock_cds, \
         patch('services.medication_service.create_prescription') as mock_create:
        
        # Setup mocks
        mock_allergies.return_value = [{"allergen": "penicillin"}]
        mock_cds.return_value = {
            "alerts": [
                {"severity": "warning", "message": "Drug interaction"}
            ]
        }
        mock_create.return_value = {"id": "rx-123"}
        
        # Make request
        response = await client.post("/medications/prescribe", json={
            "patient_id": "patient-123",
            "drug_id": "amox-500",
            "dosage": "500mg",
            "frequency": "TID",
            "duration": 10
        })
        
        # Verify orchestration
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["alerts"]) == 1
        assert mock_allergies.called
        assert mock_cds.called
        assert mock_create.called
```

## Environment Variables

```bash
# .env
# Service URLs
PATIENT_SERVICE_URL=http://patient_service:8001
MEDICATION_SERVICE_URL=http://medication_service:8002
CDS_SERVICE_URL=http://cds_service:8003

# Auth
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# CORS
CORS_ORIGINS=http://localhost:3000,https://app.livnyhealth.com

# Logging
LOG_LEVEL=INFO
```

## Health Check

```python
@app.get("/health")
async def health_check():
    """
    Health check that verifies dependencies.
    BFF checks if services are healthy.
    """
    health_status = {
        "status": "healthy",
        "service": "physician_bff",
        "version": "1.0.0",
        "dependencies": {}
    }
    
    # Check each service
    services = {
        "patient_service": PATIENT_SERVICE_URL,
        "medication_service": MEDICATION_SERVICE_URL,
        "cds_service": CDS_SERVICE_URL
    }
    
    async with httpx.AsyncClient() as client:
        for name, url in services.items():
            try:
                response = await client.get(f"{url}/health", timeout=2.0)
                health_status["dependencies"][name] = "healthy" if response.status_code == 200 else "unhealthy"
            except:
                health_status["dependencies"][name] = "unreachable"
    
    # Overall status is unhealthy if any dependency is down
    if any(status != "healthy" for status in health_status["dependencies"].values()):
        health_status["status"] = "degraded"
    
    return health_status
```

## BFF Directory

| BFF | Port | Frontend |
|-----|------|----------|
| physician_bff | 8000 | Physician web application |
| patient_portal_bff | 8100 | Patient mobile/web portal |
| integration_bff | 8200 | External API consumers |

## Key Principles Review

### ✅ DO in BFFs:
- Aggregate data from multiple services
- Transform responses for specific frontends
- Orchestrate service calls
- Resolve configuration
- Handle frontend-specific concerns
- Transform errors for user display

### ❌ DON'T in BFFs:
- Implement business logic (that's services)
- Directly access databases (call services)
- Duplicate business rules from services
- Call other BFFs
- Store state (BFFs are stateless)

## Next Steps

1. Review `.claude/BFF_PATTERNS.md` for detailed orchestration patterns
2. Start with physician_bff (most critical for MVP)
3. Build endpoints as you need them (don't build all upfront)
4. Test orchestration logic thoroughly
5. Monitor service call performance~
