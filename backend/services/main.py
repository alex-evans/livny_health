from fastapi import FastAPI

app = FastAPI(title="Livny Health Services", version="0.1.0")

FAKE_PATIENTS = [
    {
        "id": "patient-001",
        "name": "Sarah Johnson",
        "dateOfBirth": "1985-03-15",
        "mrn": "MRN-10001",
    },
    {
        "id": "patient-002",
        "name": "Michael Chen",
        "dateOfBirth": "1972-08-22",
        "mrn": "MRN-10002",
    },
    {
        "id": "patient-003",
        "name": "Emily Rodriguez",
        "dateOfBirth": "1990-11-08",
        "mrn": "MRN-10003",
    },
    {
        "id": "patient-004",
        "name": "James Williams",
        "dateOfBirth": "1968-05-30",
        "mrn": "MRN-10004",
    },
    {
        "id": "patient-005",
        "name": "Maria Garcia",
        "dateOfBirth": "1995-01-17",
        "mrn": "MRN-10005",
    },
]


@app.get("/patients")
async def get_patients():
    return FAKE_PATIENTS
