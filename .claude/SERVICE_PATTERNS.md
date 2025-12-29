# Service Patterns and Conventions

This document defines how to build services in Livny Health. Services contain the **business logic** - all domain rules, validations, and business processes.

## Core Principle: Services Own Business Logic

```python
# ✅ CORRECT - Business logic in service
# medication_service/domain/prescription.py
async def create_prescription(drug_id: str, dosage: str, patient_id: str):
    # Business rule: Validate dosage range
    if not is_within_dosage_range(drug_id, dosage):
        raise InvalidDosageError()
    
    # Business rule: Check for duplicate active prescriptions
    if await has_active_prescription(patient_id, drug_id):
        raise DuplicatePrescriptionError()
    
    # Business logic: Calculate quantity
    quantity = calculate_quantity(dosage, frequency, duration)
    
    return save_prescription(...)

# ❌ INCORRECT - Business logic in BFF or Frontend
# This should NEVER happen
async def bff_create_prescription(request):
    if int(request.dosage.rstrip('mg')) > 1000:  # Business rule leak!
        return {"error": "Dosage too high"}
    
    return await medication_service.create_prescription(request)
```

## Service Structure

Every service follows this pattern:

```
medication_service/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration management
├── database.py          # Database connection & session
│
├── routers/             # HTTP endpoints (THIN layer)
│   ├── prescriptions.py # /prescriptions routes
│   └── drugs.py         # /drugs routes
│
├── domain/              # Business logic (THICK layer)
│   ├── prescription.py  # Prescription domain logic
│   ├── drug_validation.py
│   └── rules.py         # Business rules
│
├── models/              # SQLAlchemy database models
│   ├── prescription.py
│   └── drug.py
│
├── schemas/             # Pydantic API schemas
│   ├── prescription.py
│   └── drug.py
│
└── tests/
    ├── test_domain_prescription.py
    └── test_api_prescriptions.py
```

## Layer Responsibilities

### 1. Routers (Thin Layer)

Routers handle HTTP concerns only:
- Parse request
- Call domain layer
- Return response
- Handle HTTP errors

```python
# routers/prescriptions.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from domain.prescription import PrescriptionDomain
from schemas.prescription import PrescriptionCreate, PrescriptionResponse

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])

@router.post("/", response_model=PrescriptionResponse, status_code=201)
async def create_prescription(
    prescription: PrescriptionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new prescription.
    
    Router responsibilities:
    - Parse HTTP request
    - Validate request schema (Pydantic does this)
    - Call domain layer
    - Return HTTP response
    
    Router does NOT:
    - Validate business rules (domain does this)
    - Calculate quantities (domain does this)
    - Check drug interactions (CDS service does this)
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
        # Business rule violation
        raise HTTPException(status_code=400, detail=str(e))
    
    except PermissionError as e:
        # Authorization failure
        raise HTTPException(status_code=403, detail=str(e))
    
    except Exception as e:
        # Unexpected error
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 2. Domain Layer (Thick Layer)

Domain contains all business logic:

```python
# domain/prescription.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional

from models.prescription import Prescription
from models.drug import Drug
from models.user import User

class PrescriptionDomain:
    """
    Business logic for prescriptions.
    
    All rules, validations, calculations happen here.
    This is the heart of the service.
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
        Create prescription with all business rules applied.
        
        Business rules enforced:
        1. Drug must exist
        2. Dosage must be within valid range
        3. Prescriber must have authority
        4. Controlled substances require DEA
        5. No duplicate active prescriptions
        """
        
        # Business rule: Validate drug exists
        drug = await self._get_drug(drug_id)
        if not drug:
            raise ValueError(f"Drug {drug_id} not found")
        
        # Business rule: Validate dosage is within range
        if not self._is_valid_dosage(drug, dosage):
            raise ValueError(
                f"Dosage {dosage} is not valid for {drug.name}. "
                f"Valid range: {drug.min_dose}mg - {drug.max_dose}mg"
            )
        
        # Business rule: Validate prescriber authority
        prescriber = await self._get_user(prescriber_id)
        if not prescriber.can_prescribe:
            raise PermissionError(
                f"User {prescriber.name} is not authorized to prescribe"
            )
        
        # Business rule: Controlled substances require DEA
        if drug.is_controlled and not prescriber.has_dea_number:
            raise PermissionError(
                f"DEA number required to prescribe {drug.name} "
                f"(Schedule {drug.schedule})"
            )
        
        # Business rule: Check for duplicate active prescriptions
        if await self._has_active_prescription(patient_id, drug_id):
            raise ValueError(
                f"Patient already has an active prescription for {drug.name}"
            )
        
        # Business logic: Calculate dates
        start_date = datetime.now()
        end_date = start_date + timedelta(days=duration_days)
        
        # Business logic: Calculate quantity based on frequency
        quantity = self._calculate_quantity(frequency, duration_days)
        
        # Create prescription
        prescription = Prescription(
            patient_id=patient_id,
            drug_id=drug_id,
            drug_name=drug.name,  # Denormalized for performance
            dosage=dosage,
            frequency=frequency,
            start_date=start_date,
            end_date=end_date,
            quantity=quantity,
            prescriber_id=prescriber_id,
            prescriber_name=prescriber.name,  # Denormalized
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save to database
        self.db.add(prescription)
        await self.db.commit()
        await self.db.refresh(prescription)
        
        # Publish event for other services
        await self._publish_event("prescription.created", {
            "prescription_id": prescription.id,
            "patient_id": patient_id,
            "drug_id": drug_id,
            "prescriber_id": prescriber_id
        })
        
        return prescription
    
    def _is_valid_dosage(self, drug: Drug, dosage: str) -> bool:
        """
        Business rule: Validate dosage is within acceptable range.
        
        Args:
            drug: Drug object with min/max dosage
            dosage: Dosage string like "500mg"
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # Parse dosage (e.g., "500mg" -> 500.0)
            amount = float(dosage.rstrip('mg'))
        except ValueError:
            return False
        
        # Check against drug's valid range
        return drug.min_dose <= amount <= drug.max_dose
    
    def _calculate_quantity(self, frequency: str, duration_days: int) -> int:
        """
        Business logic: Calculate total quantity needed.
        
        Args:
            frequency: QD (once daily), BID (twice daily), TID (3x), QID (4x)
            duration_days: Treatment duration in days
        
        Returns:
            Total pills/doses needed
        """
        frequency_map = {
            "QD": 1,
            "BID": 2,
            "TID": 3,
            "QID": 4
        }
        
        times_per_day = frequency_map.get(frequency.upper(), 1)
        return times_per_day * duration_days
    
    async def _has_active_prescription(
        self, 
        patient_id: str, 
        drug_id: str
    ) -> bool:
        """
        Business rule: Check if patient already has active prescription.
        
        This prevents duplicate prescriptions for the same drug.
        """
        query = select(Prescription).where(
            Prescription.patient_id == patient_id,
            Prescription.drug_id == drug_id,
            Prescription.status == "active",
            Prescription.end_date >= datetime.now()
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def _get_drug(self, drug_id: str) -> Optional[Drug]:
        """Get drug from database"""
        query = select(Drug).where(Drug.id == drug_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_user(self, user_id: str) -> Optional[User]:
        """Get user from database"""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _publish_event(self, event_type: str, data: dict):
        """
        Publish event to event bus for other services.
        
        This is how services communicate asynchronously.
        """
        # TODO: Implement with Redis or message queue
        pass
```

## Business Rules Pattern

Separate complex business rules into dedicated modules:

```python
# domain/rules.py
from typing import List
from models.prescription import Prescription
from models.allergy import Allergy
from models.drug import Drug

class PrescriptionRules:
    """
    Business rules for prescription validation.
    
    Separate rules make them:
    - Testable in isolation
    - Reusable across different flows
    - Documented in one place
    """
    
    @staticmethod
    def can_prescribe_with_allergy(
        drug: Drug,
        allergies: List[Allergy]
    ) -> tuple[bool, str]:
        """
        Business rule: Determine if drug can be prescribed given allergies.
        
        Returns:
            (can_prescribe, reason)
        """
        for allergy in allergies:
            # Check direct match
            if drug.generic_name.lower() == allergy.allergen.lower():
                return False, f"Patient allergic to {allergy.allergen}"
            
            # Check cross-reactivity (e.g., penicillin allergy → amoxicillin)
            if PrescriptionRules._is_cross_reactive(drug, allergy):
                return False, (
                    f"Cross-reactivity: Patient allergic to {allergy.allergen}, "
                    f"{drug.name} is in same class"
                )
        
        return True, ""
    
    @staticmethod
    def _is_cross_reactive(drug: Drug, allergy: Allergy) -> bool:
        """
        Business rule: Check if drug is cross-reactive with allergen.
        
        This is clinical knowledge encoded as business logic.
        """
        cross_reactivity_map = {
            "penicillin": ["amoxicillin", "ampicillin", "penicillin"],
            "sulfa": ["sulfamethoxazole", "sulfasalazine"],
            "cephalosporin": ["cephalexin", "cefazolin", "ceftriaxone"]
        }
        
        allergen = allergy.allergen.lower()
        if allergen in cross_reactivity_map:
            return drug.generic_name.lower() in cross_reactivity_map[allergen]
        
        return False
    
    @staticmethod
    def requires_renal_adjustment(
        drug: Drug,
        creatinine_clearance: float
    ) -> tuple[bool, Optional[str]]:
        """
        Business rule: Determine if renal dose adjustment needed.
        
        Args:
            drug: Drug being prescribed
            creatinine_clearance: Patient's CrCl in mL/min
        
        Returns:
            (needs_adjustment, recommended_dose)
        """
        if not drug.requires_renal_adjustment:
            return False, None
        
        # Moderate renal impairment (30-60 mL/min)
        if 30 <= creatinine_clearance < 60:
            return True, drug.moderate_renal_dose
        
        # Severe renal impairment (<30 mL/min)
        if creatinine_clearance < 30:
            return True, drug.severe_renal_dose
        
        return False, None
```

## Database Models

Models define database schema:

```python
# models/prescription.py
from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, Index
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Prescription(Base):
    """
    Prescription database model.
    
    Represents an active medication order for a patient.
    """
    __tablename__ = "prescriptions"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys (no actual FKs to allow service independence)
    patient_id = Column(String, nullable=False, index=True)
    drug_id = Column(String, nullable=False)
    prescriber_id = Column(String, nullable=False)
    
    # Prescription details
    drug_name = Column(String, nullable=False)  # Denormalized for performance
    dosage = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    route = Column(String, default="PO")
    instructions = Column(String, nullable=True)
    indication = Column(String, nullable=True)
    
    # Dates
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # Status
    status = Column(String, nullable=False, default="active")  # active, completed, discontinued
    
    # Refills
    refills_allowed = Column(Integer, default=0)
    refills_remaining = Column(Integer, default=0)
    
    # Prescriber info (denormalized)
    prescriber_name = Column(String, nullable=False)
    
    # Override tracking (for critical alerts)
    override_reason = Column(String, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_prescriptions_patient_status', 'patient_id', 'status'),
        Index('ix_prescriptions_prescriber', 'prescriber_id'),
        Index('ix_prescriptions_dates', 'start_date', 'end_date'),
    )
```

## Pydantic Schemas

Schemas define API contracts:

```python
# schemas/prescription.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class PrescriptionCreate(BaseModel):
    """Request schema for creating a prescription"""
    
    patient_id: str = Field(..., description="Patient identifier")
    drug_id: str = Field(..., description="Drug identifier")
    dosage: str = Field(..., description="Dosage (e.g., '500mg')")
    frequency: str = Field(..., description="Frequency (QD, BID, TID, QID)")
    duration_days: int = Field(..., ge=1, le=365, description="Duration in days")
    route: str = Field(default="PO", description="Route of administration")
    instructions: Optional[str] = Field(None, description="Patient instructions")
    indication: Optional[str] = Field(None, description="Reason for prescription")
    prescriber_id: str = Field(..., description="Prescriber identifier")
    override_reason: Optional[str] = Field(None, description="Reason for alert override")
    
    @validator('frequency')
    def validate_frequency(cls, v):
        """Validate frequency is one of accepted values"""
        valid = ['QD', 'BID', 'TID', 'QID']
        if v.upper() not in valid:
            raise ValueError(f"Frequency must be one of: {', '.join(valid)}")
        return v.upper()
    
    @validator('dosage')
    def validate_dosage_format(cls, v):
        """Validate dosage format"""
        if not v.endswith('mg'):
            raise ValueError("Dosage must end with 'mg'")
        try:
            float(v.rstrip('mg'))
        except ValueError:
            raise ValueError("Dosage must be a number followed by 'mg'")
        return v

class PrescriptionResponse(BaseModel):
    """Response schema for prescription"""
    
    id: str
    patient_id: str
    drug_id: str
    drug_name: str
    dosage: str
    frequency: str
    quantity: int
    route: str
    instructions: Optional[str]
    indication: Optional[str]
    start_date: datetime
    end_date: datetime
    prescriber_id: str
    prescriber_name: str
    status: str
    refills_allowed: int
    refills_remaining: int
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allows creation from SQLAlchemy models
```

## Database Connection

```python
# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://livny:dev_password@localhost:5432/livny_dev"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    future=True
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session.
    
    Usage in FastAPI:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

## Service-to-Service Communication

### Synchronous (HTTP) - Use Sparingly

Only for queries that need immediate response:

```python
# domain/prescription.py
async def verify_patient_exists(patient_id: str) -> bool:
    """
    Check if patient exists in patient service.
    
    This is OK because we need immediate answer.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{PATIENT_SERVICE_URL}/patients/{patient_id}",
                timeout=2.0
            )
            return response.status_code == 200
        except httpx.TimeoutException:
            raise ServiceUnavailableError("Patient service unavailable")
```

### Asynchronous (Events) - Preferred

For notifications and side effects:

```python
# Event publishing (in domain layer)
async def create_prescription(...):
    prescription = save_prescription(...)
    
    # Publish event - don't wait for consumers
    await event_bus.publish("prescription.created", {
        "prescription_id": prescription.id,
        "patient_id": prescription.patient_id,
        "drug_id": prescription.drug_id,
        "prescriber_id": prescription.prescriber_id,
        "created_at": prescription.created_at.isoformat()
    })
    
    return prescription

# Event handling (in other service)
# billing_service/events.py
@event_handler("prescription.created")
async def handle_prescription_created(event: dict):
    """
    React to prescription creation.
    
    This runs asynchronously - prescription service doesn't wait.
    """
    prescription_id = event["prescription_id"]
    
    # Create billing charge
    await billing_domain.create_charge(
        patient_id=event["patient_id"],
        service_type="prescription",
        reference_id=prescription_id
    )
```

## Error Handling

Define domain-specific exceptions:

```python
# domain/exceptions.py
class DomainException(Exception):
    """Base exception for domain errors"""
    pass

class BusinessRuleViolation(DomainException):
    """Raised when business rule is violated"""
    def __init__(self, rule: str, message: str):
        self.rule = rule
        self.message = message
        super().__init__(message)

class InvalidDosageError(BusinessRuleViolation):
    """Dosage outside acceptable range"""
    def __init__(self, drug_name: str, dosage: str, valid_range: str):
        super().__init__(
            "invalid_dosage",
            f"Dosage {dosage} invalid for {drug_name}. Valid range: {valid_range}"
        )

class UnauthorizedPrescriber(BusinessRuleViolation):
    """User not authorized to prescribe"""
    def __init__(self, user_name: str):
        super().__init__(
            "unauthorized_prescriber",
            f"User {user_name} is not authorized to prescribe medications"
        )
```

## Testing Domain Logic

Focus tests on business rules:

```python
# tests/test_prescription_domain.py
import pytest
from domain.prescription import PrescriptionDomain
from domain.exceptions import InvalidDosageError, UnauthorizedPrescriber

@pytest.mark.asyncio
async def test_valid_dosage_accepted(db_session):
    """Test that valid dosage is accepted"""
    domain = PrescriptionDomain(db_session)
    
    # Should not raise
    prescription = await domain.create_prescription(
        patient_id="patient-123",
        drug_id="amox-500",
        dosage="500mg",  # Valid dosage
        frequency="TID",
        duration_days=10,
        prescriber_id="dr-emily"
    )
    
    assert prescription.dosage == "500mg"
    assert prescription.quantity == 30  # 3 times daily * 10 days

@pytest.mark.asyncio
async def test_invalid_dosage_rejected(db_session):
    """Test that invalid dosage is rejected"""
    domain = PrescriptionDomain(db_session)
    
    with pytest.raises(InvalidDosageError):
        await domain.create_prescription(
            patient_id="patient-123",
            drug_id="amox-500",
            dosage="5000mg",  # Too high
            frequency="TID",
            duration_days=10,
            prescriber_id="dr-emily"
        )

@pytest.mark.asyncio
async def test_unauthorized_prescriber_rejected(db_session):
    """Test that non-prescriber cannot create prescription"""
    domain = PrescriptionDomain(db_session)
    
    with pytest.raises(UnauthorizedPrescriber):
        await domain.create_prescription(
            patient_id="patient-123",
            drug_id="amox-500",
            dosage="500mg",
            frequency="TID",
            duration_days=10,
            prescriber_id="nurse-without-privileges"
        )

@pytest.mark.asyncio
async def test_controlled_substance_requires_dea(db_session):
    """Test that controlled substances require DEA number"""
    domain = PrescriptionDomain(db_session)
    
    with pytest.raises(BusinessRuleViolation, match="DEA number required"):
        await domain.create_prescription(
            drug_id="oxycodone-5",  # Schedule II controlled substance
            prescriber_id="dr-without-dea",
            ...
        )
```

## Configuration

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Service configuration"""
    
    # Database
    database_url: str = "postgresql+asyncpg://livny:password@localhost/livny_dev"
    
    # Service URLs (for service-to-service calls)
    patient_service_url: str = "http://patient_service:8001"
    cds_service_url: str = "http://cds_service:8003"
    
    # Event bus
    event_bus_url: str = "redis://localhost:6379"
    
    # Logging
    log_level: str = "INFO"
    
    # Service info
    service_name: str = "medication_service"
    service_version: str = "1.0.0"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Summary: Service Checklist

When building a service, ensure:

- [ ] Business logic lives in domain layer
- [ ] Routers are thin (just HTTP handling)
- [ ] All business rules are validated
- [ ] Domain logic is testable
- [ ] Database models use proper indexes
- [ ] Pydantic schemas validate input
- [ ] Errors are domain-specific
- [ ] Events published for side effects
- [ ] Health check endpoint exists
- [ ] Tests cover business rules
