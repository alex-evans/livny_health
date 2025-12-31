# Livny Health - Services Layer

> **Note for Claude Code**: Before working on services, please review:
> - `.claude/SERVICE_PATTERNS.md` - Service structure and conventions
> - `.claude/DOMAIN_LOGIC.md` - Business rules and domain logic patterns
> - `.claude/DATABASE_CONVENTIONS.md` - Database models and queries
> - Root `.claude/README.md` - Overall architecture

## Architecture Overview

The Services Layer contains the **business logic** of Livny Health. This is where domain rules, data validation, and business processes live.

```
Services Layer (Business Logic)
├── patient_service/      - Patient demographics, identifiers
├── medication_service/   - Prescriptions, drugs, allergies
├── cds_service/         - Clinical decision support rules
├── order_service/       - Lab/imaging orders and results
├── clinical_doc_service/ - Visit notes, documentation
├── billing_service/     - Charges, coding, claims
└── shared/              - Shared utilities, models
```

## Key Principles

### 1. Services Own Their Domain
- **patient_service** owns patient demographics - no other service stores this
- **medication_service** owns prescriptions and allergies - single source of truth
- Services expose clean APIs but keep business logic internal

### 2. Business Logic Lives Here
```python
# ✅ Business logic in service
async def create_prescription(drug_id: str, dosage: str) -> Prescription:
    # Business rule: Validate dosage is within range
    if not is_valid_dosage(drug_id, dosage):
        raise InvalidDosageError()
    
    # Business rule: Calculate quantity based on frequency
    quantity = calculate_quantity(dosage, frequency, duration)
    
    return save_prescription(...)

# ❌ Business logic in BFF or Frontend
# Never put validation, calculations, or rules outside services
```

### 3. Services are Role-Agnostic
Services don't know about "physicians" vs "nurses" - they enforce business rules for everyone:

```python
# ✅ Good - role-agnostic
async def create_prescription(
    drug_id: str,
    prescriber_id: str,
    patient_id: str
):
    # Service checks if prescriber CAN prescribe (business rule)
    prescriber = await get_user(prescriber_id)
    if not prescriber.can_prescribe:
        raise UnauthorizedError("User cannot prescribe")
    
    # Business logic proceeds...

# ❌ Bad - role-aware
async def physician_create_prescription(...):
    # Don't create role-specific service endpoints
```

### 4. Services Communicate via Events
Services don't call each other directly for side effects - they publish events:

```python
# ✅ Good - event-driven
async def create_prescription(...):
    prescription = save_prescription(...)
    
    # Publish event - other services can react
    await event_bus.publish("prescription.created", {
        "prescription_id": prescription.id,
        "patient_id": prescription.patient_id
    })
    
    return prescription

# In billing_service (separate service)
@event_handler("prescription.created")
async def create_billing_charge(event):
    # React to event asynchronously
    await create_charge(event.data)

# ❌ Bad - tight coupling
async def create_prescription(...):
    prescription = save_prescription(...)
    # Don't call other services directly for side effects
    await billing_service.create_charge(prescription)
```

## Service Structure

Each service follows this pattern:

```
medication_service/
├── __init__.py
├── main.py                 # FastAPI app, startup/shutdown
├── config.py              # Configuration, environment variables
├── database.py            # Database connection, session management
├── routers/               # API endpoints (thin layer)
│   ├── __init__.py
│   ├── prescriptions.py   # Prescription endpoints
│   ├── drugs.py          # Drug search endpoints
│   └── allergies.py      # Allergy endpoints
├── domain/                # Business logic (thick layer)
│   ├── __init__.py
│   ├── prescription.py    # Prescription business logic
│   ├── drug_validation.py # Drug dosing rules
│   └── rules.py          # Business rules
├── models/                # Database models (SQLAlchemy)
│   ├── __init__.py
│   ├── prescription.py
│   ├── drug.py
│   └── allergy.py
├── schemas/               # Pydantic schemas (API contracts)
│   ├── __init__.py
│   ├── prescription.py
│   └── drug.py
├── tests/                 # Unit and integration tests
│   ├── test_prescription.py
│   └── test_domain_rules.py
├── requirements.txt       # Python dependencies
└── Dockerfile            # Container definition
```

## Technology Stack

- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+ (via SQLAlchemy 2.0)
- **Validation**: Pydantic v2
- **Testing**: pytest + pytest-asyncio
- **Async**: asyncio + asyncpg
- **Migrations**: Alembic

## Getting Started

### Setting Up a New Service

```bash
# Navigate to services directory
cd backend/services

# Create new service
mkdir patient_service
cd patient_service

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy asyncpg pydantic alembic pytest

# Create directory structure
mkdir routers domain models schemas tests
touch main.py config.py database.py requirements.txt

# Freeze dependencies
pip freeze > requirements.txt
```

### Running a Service Locally

```bash
cd backend/services/medication_service
source venv/bin/activate
uvicorn main:app --reload --port 8002
```

Service will be available at `http://localhost:8002`

### Running All Services with Docker Compose

```bash
# From project root
docker-compose up

# Services will be available at:
# - patient_service: http://localhost:8001
# - medication_service: http://localhost:8002
# - cds_service: http://localhost:8003
```

## Code Conventions

### 1. Endpoint Structure (Routers)

Routers are **thin** - they handle HTTP concerns only:

```python
# routers/prescriptions.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from domain.prescription import PrescriptionDomain
from schemas.prescription import PrescriptionCreate, PrescriptionResponse

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])

@router.post("/", response_model=PrescriptionResponse)
async def create_prescription(
    prescription: PrescriptionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new prescription.
    Router handles HTTP - domain handles business logic.
    """
    try:
        domain = PrescriptionDomain(db)
        result = await domain.create_prescription(
            patient_id=prescription.patient_id,
            drug_id=prescription.drug_id,
            dosage=prescription.dosage,
            frequency=prescription.frequency,
            duration_days=prescription.duration_days,
            prescriber_id=prescription.prescriber_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 2. Domain Logic (Business Rules)

Domain layer is **thick** - all business logic lives here:

```python
# domain/prescription.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import List

from models.prescription import Prescription
from models.drug import Drug

class PrescriptionDomain:
    """
    Business logic for prescriptions.
    All rules, validations, and calculations happen here.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_prescription(
        self,
        patient_id: str,
        drug_id: str,
        dosage: str,
        frequency: str,
        duration_days: int,
        prescriber_id: str
    ) -> Prescription:
        """
        Create prescription with business rules applied.
        """
        # Business rule: Validate drug exists
        drug = await self._get_drug(drug_id)
        if not drug:
            raise ValueError(f"Drug {drug_id} not found")
        
        # Business rule: Validate dosage is within range
        if not self._is_valid_dosage(drug, dosage):
            raise ValueError(f"Dosage {dosage} invalid for {drug.name}")
        
        # Business rule: Validate prescriber can prescribe
        prescriber = await self._get_user(prescriber_id)
        if not prescriber.can_prescribe:
            raise ValueError("User not authorized to prescribe")
        
        # Business rule: Controlled substances need DEA
        if drug.is_controlled and not prescriber.has_dea_number:
            raise ValueError("DEA number required for controlled substances")
        
        # Business logic: Calculate dates
        start_date = datetime.now()
        end_date = start_date + timedelta(days=duration_days)
        
        # Business logic: Calculate quantity
        quantity = self._calculate_quantity(frequency, duration_days)
        
        # Create prescription
        prescription = Prescription(
            patient_id=patient_id,
            drug_id=drug_id,
            dosage=dosage,
            frequency=frequency,
            start_date=start_date,
            end_date=end_date,
            quantity=quantity,
            prescriber_id=prescriber_id,
            status="active"
        )
        
        self.db.add(prescription)
        await self.db.commit()
        await self.db.refresh(prescription)
        
        # Publish event for other services
        await self._publish_event("prescription.created", prescription)
        
        return prescription
    
    def _is_valid_dosage(self, drug: Drug, dosage: str) -> bool:
        """Business rule: Validate dosage"""
        amount = float(dosage.rstrip('mg'))
        return drug.min_dose <= amount <= drug.max_dose
    
    def _calculate_quantity(self, frequency: str, duration_days: int) -> int:
        """Business logic: Calculate quantity"""
        frequency_map = {"QD": 1, "BID": 2, "TID": 3, "QID": 4}
        times_per_day = frequency_map.get(frequency, 1)
        return times_per_day * duration_days
```

### 3. Database Models

```python
# models/prescription.py
from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Prescription(Base):
    __tablename__ = "prescriptions"
    
    id = Column(String, primary_key=True)
    patient_id = Column(String, nullable=False, index=True)
    drug_id = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    prescriber_id = Column(String, nullable=False)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
```

### 4. Pydantic Schemas (API Contracts)

```python
# schemas/prescription.py
from pydantic import BaseModel, Field
from datetime import datetime

class PrescriptionCreate(BaseModel):
    """Request schema for creating prescription"""
    patient_id: str = Field(..., description="Patient identifier")
    drug_id: str = Field(..., description="Drug identifier")
    dosage: str = Field(..., description="Dosage (e.g., '500mg')")
    frequency: str = Field(..., description="Frequency (QD, BID, TID, QID)")
    duration_days: int = Field(..., ge=1, le=365, description="Duration in days")
    prescriber_id: str = Field(..., description="Prescriber identifier")

class PrescriptionResponse(BaseModel):
    """Response schema for prescription"""
    id: str
    patient_id: str
    drug_id: str
    drug_name: str
    dosage: str
    frequency: str
    quantity: int
    start_date: datetime
    end_date: datetime
    prescriber_id: str
    status: str
    
    class Config:
        from_attributes = True
```

## Testing

### Unit Tests (Domain Logic)

```python
# tests/test_prescription_domain.py
import pytest
from domain.prescription import PrescriptionDomain

@pytest.mark.asyncio
async def test_validate_dosage():
    """Test business rule: dosage validation"""
    domain = PrescriptionDomain(mock_db)
    
    # Valid dosage
    assert domain._is_valid_dosage(drug, "500mg") == True
    
    # Invalid dosage (too high)
    assert domain._is_valid_dosage(drug, "5000mg") == False

@pytest.mark.asyncio
async def test_controlled_substance_requires_dea():
    """Test business rule: DEA required for controlled substances"""
    domain = PrescriptionDomain(mock_db)
    
    with pytest.raises(ValueError, match="DEA number required"):
        await domain.create_prescription(
            drug_id="schedule_ii_drug",
            prescriber_id="prescriber_without_dea",
            ...
        )
```

### Integration Tests (Full Flow)

```python
# tests/test_prescription_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_prescription_endpoint(client: AsyncClient):
    """Test full prescription creation flow"""
    response = await client.post("/prescriptions", json={
        "patient_id": "patient-123",
        "drug_id": "amox-500",
        "dosage": "500mg",
        "frequency": "TID",
        "duration_days": 10,
        "prescriber_id": "dr-emily"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 30  # 3 times daily * 10 days
```

## Database Migrations

Use Alembic for database schema changes:

```bash
# Create migration
alembic revision --autogenerate -m "Add prescriptions table"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Environment Variables

Each service uses these environment variables:

```bash
# .env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/livny_dev
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
EVENT_BUS_URL=redis://localhost:6379
```

## Health Checks

Every service must implement a health check:

```python
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "medication_service",
        "version": "1.0.0"
    }
```

## Error Handling

Services return structured errors:

```python
class BusinessRuleViolation(Exception):
    """Raised when business rule is violated"""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message

# In router
try:
    result = await domain.create_prescription(...)
except BusinessRuleViolation as e:
    raise HTTPException(
        status_code=400,
        detail={
            "error": e.code,
            "message": e.message
        }
    )
```

## Deployment

Services are deployed as Docker containers:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Service Directory

| Service | Port | Responsibility |
|---------|------|----------------|
| patient_service | 8001 | Patient demographics, identifiers |
| medication_service | 8002 | Prescriptions, drugs, allergies |
| cds_service | 8003 | Clinical decision support rules |
| order_service | 8004 | Lab/imaging orders and results |
| clinical_doc_service | 8005 | Visit notes, documentation |
| billing_service | 8006 | Charges, billing codes, claims |

## Next Steps

1. Review `.claude/SERVICE_PATTERNS.md` for detailed patterns
2. Review `.claude/DOMAIN_LOGIC.md` for business rule examples
3. Start with medication_service (most critical for prescribing workflow)
4. Add tests as you build domain logic
5. Use event bus for cross-service communication
