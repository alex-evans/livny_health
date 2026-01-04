# API Contracts - Physician BFF

Base URL: `http://localhost:8000` (dev)

## Authentication
All requests require `Authorization: Bearer <token>` header.

## Endpoints

### Get Encounter Context
```
GET /encounters/{encounter_id}/context
```

**Response:**
```json
{
  "patient": {
    "id": "12345",
    "name": "John Doe",
    "age": 45,
    "mrn": "123456",
    "photo_url": "/photos/12345.jpg"
  },
  "medications": [
    {
      "id": "med-1",
      "name": "Lisinopril 10mg",
      "dosage": "10mg",
      "frequency": "daily",
      "started": "2023-06-15T00:00:00Z"
    }
  ],
  "allergies": [
    {
      "id": "allergy-1",
      "allergen": "Penicillin",
      "reaction": "Anaphylaxis",
      "severity": "severe",
      "documented": "2020-01-01T00:00:00Z"
    }
  ],
  "encounter": {
    "id": "67890",
    "date": "2024-01-15T14:30:00Z",
    "type": "office_visit",
    "status": "in_progress"
  }
}
```

### Search Medications
```
POST /medications/search
```

**Request:**
```json
{
  "query": "amox",
  "limit": 20
}
```

**Response:**
```json
[
  {
    "id": "amox-500",
    "name": "Amoxicillin 500mg capsule",
    "strength": "500mg",
    "form": "capsule",
    "common_dosing": ["500mg TID", "500mg BID"],
    "is_controlled": false
  }
]
```

### Check Drug Interactions
```
POST /patients/{patient_id}/check-interactions
```

Checks if a medication interacts with the patient's current active medications.

**Request:**
```json
{
  "medication_name": "Amoxicillin"
}
```

**Response (with interactions):**
```json
{
  "hasInteractions": true,
  "interactions": [
    {
      "interactingDrug": "Warfarin",
      "severity": "moderate",
      "description": "May increase warfarin effects - monitor INR"
    }
  ]
}
```

**Response (no interactions):**
```json
{
  "hasInteractions": false,
  "interactions": []
}
```

**Severity levels:**
- `major` - Serious interaction, avoid combination or use extreme caution
- `moderate` - Monitor patient closely
- `minor` - Minimal clinical significance

### Prescribe Medication
```
POST /medications/prescribe
```

**Request:**
```json
{
  "patient_id": "12345",
  "drug_id": "amox-500",
  "dosage": "500mg",
  "frequency": "TID",
  "duration": 10,
  "instructions": "Take with food",
  "indication": "Suspected strep throat",
  "override_reason": null
}
```

**Response:**
```json
{
  "status": "success",
  "prescription": {
    "id": "rx-789",
    "drug_name": "Amoxicillin 500mg capsule",
    "dosage": "500mg",
    "frequency": "TID",
    "duration_days": 10,
    "start_date": "2024-01-15T00:00:00Z",
    "end_date": "2024-01-25T00:00:00Z"
  },
  "alerts": []
}
```

## Error Responses

All errors follow this format:
```json
{
  "error": "error_code",
  "message": "Human readable message",
  "details": {}
}
```

Common error codes:
- `patient_not_found`
- `drug_not_found`
- `critical_alerts` - when alerts block prescription
- `unauthorized`
- `validation_error`
