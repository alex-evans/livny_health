
FAKE_MEDICATIONS = [
    {"id": "amox-250", "name": "Amoxicillin 250mg capsule", "strength": "250mg", "form": "capsule", "commonDosing": ["250mg TID", "250mg BID"], "isControlled": False},
    {"id": "amox-500", "name": "Amoxicillin 500mg capsule", "strength": "500mg", "form": "capsule", "commonDosing": ["500mg TID", "500mg BID"], "isControlled": False},
    {"id": "amox-875", "name": "Amoxicillin 875mg tablet", "strength": "875mg", "form": "tablet", "commonDosing": ["875mg BID"], "isControlled": False},
    {"id": "lisinopril-5", "name": "Lisinopril 5mg tablet", "strength": "5mg", "form": "tablet", "commonDosing": ["5mg daily"], "isControlled": False},
    {"id": "lisinopril-10", "name": "Lisinopril 10mg tablet", "strength": "10mg", "form": "tablet", "commonDosing": ["10mg daily"], "isControlled": False},
    {"id": "lisinopril-20", "name": "Lisinopril 20mg tablet", "strength": "20mg", "form": "tablet", "commonDosing": ["20mg daily"], "isControlled": False},
    {"id": "metformin-500", "name": "Metformin 500mg tablet", "strength": "500mg", "form": "tablet", "commonDosing": ["500mg BID", "500mg daily"], "isControlled": False},
    {"id": "metformin-850", "name": "Metformin 850mg tablet", "strength": "850mg", "form": "tablet", "commonDosing": ["850mg BID"], "isControlled": False},
    {"id": "metformin-1000", "name": "Metformin 1000mg tablet", "strength": "1000mg", "form": "tablet", "commonDosing": ["1000mg BID"], "isControlled": False},
    {"id": "atorvastatin-10", "name": "Atorvastatin 10mg tablet", "strength": "10mg", "form": "tablet", "commonDosing": ["10mg daily at bedtime"], "isControlled": False},
    {"id": "atorvastatin-20", "name": "Atorvastatin 20mg tablet", "strength": "20mg", "form": "tablet", "commonDosing": ["20mg daily at bedtime"], "isControlled": False},
    {"id": "atorvastatin-40", "name": "Atorvastatin 40mg tablet", "strength": "40mg", "form": "tablet", "commonDosing": ["40mg daily at bedtime"], "isControlled": False},
    {"id": "omeprazole-20", "name": "Omeprazole 20mg capsule", "strength": "20mg", "form": "capsule", "commonDosing": ["20mg daily before breakfast"], "isControlled": False},
    {"id": "omeprazole-40", "name": "Omeprazole 40mg capsule", "strength": "40mg", "form": "capsule", "commonDosing": ["40mg daily before breakfast"], "isControlled": False},
    {"id": "amlodipine-5", "name": "Amlodipine 5mg tablet", "strength": "5mg", "form": "tablet", "commonDosing": ["5mg daily"], "isControlled": False},
    {"id": "amlodipine-10", "name": "Amlodipine 10mg tablet", "strength": "10mg", "form": "tablet", "commonDosing": ["10mg daily"], "isControlled": False},
    {"id": "hydrocodone-5-325", "name": "Hydrocodone/APAP 5/325mg tablet", "strength": "5/325mg", "form": "tablet", "commonDosing": ["1-2 tablets every 4-6 hours PRN"], "isControlled": True},
    {"id": "oxycodone-5", "name": "Oxycodone 5mg tablet", "strength": "5mg", "form": "tablet", "commonDosing": ["5mg every 4-6 hours PRN"], "isControlled": True},
    {"id": "gabapentin-100", "name": "Gabapentin 100mg capsule", "strength": "100mg", "form": "capsule", "commonDosing": ["100mg TID"], "isControlled": False},
    {"id": "gabapentin-300", "name": "Gabapentin 300mg capsule", "strength": "300mg", "form": "capsule", "commonDosing": ["300mg TID"], "isControlled": False},
    {"id": "prednisone-5", "name": "Prednisone 5mg tablet", "strength": "5mg", "form": "tablet", "commonDosing": ["5mg daily", "Taper per instructions"], "isControlled": False},
    {"id": "prednisone-10", "name": "Prednisone 10mg tablet", "strength": "10mg", "form": "tablet", "commonDosing": ["10mg daily", "Taper per instructions"], "isControlled": False},
    {"id": "azithromycin-250", "name": "Azithromycin 250mg tablet", "strength": "250mg", "form": "tablet", "commonDosing": ["500mg day 1, then 250mg days 2-5"], "isControlled": False},
    {"id": "ciprofloxacin-500", "name": "Ciprofloxacin 500mg tablet", "strength": "500mg", "form": "tablet", "commonDosing": ["500mg BID"], "isControlled": False},
    {"id": "albuterol-inhaler", "name": "Albuterol 90mcg inhaler", "strength": "90mcg/actuation", "form": "inhaler", "commonDosing": ["2 puffs every 4-6 hours PRN"], "isControlled": False},
]

FAKE_PATIENTS = [
    {
        "id": "patient-001",
        "name": "Sarah Johnson",
        "dateOfBirth": "1985-03-15",
        "mrn": "MRN-10001",
        "allergies": [
            {
                "id": "allergy-1",
                "allergen": "Penicillin",
                "reaction": "Anaphylaxis",
                "severity": "severe",
                "documented": "2020-01-15",
            },
            {
                "id": "allergy-2",
                "allergen": "Sulfa",
                "reaction": "Rash",
                "severity": "moderate",
                "documented": "2019-06-20",
            },
        ],
        "activeMedications": [
            {
                "id": "med-1",
                "name": "Lisinopril",
                "dosage": "10mg",
                "frequency": "daily",
                "started": "2023-06-15",
            },
            {
                "id": "med-2",
                "name": "Metformin",
                "dosage": "500mg",
                "frequency": "twice daily",
                "started": "2022-03-10",
            },
            {
                "id": "med-3",
                "name": "Atorvastatin",
                "dosage": "20mg",
                "frequency": "at bedtime",
                "started": "2023-01-05",
            },
        ],
    },
    {
        "id": "patient-002",
        "name": "Michael Chen",
        "dateOfBirth": "1972-08-22",
        "mrn": "MRN-10002",
        "allergies": [
            {
                "id": "allergy-3",
                "allergen": "Aspirin",
                "reaction": "Hives",
                "severity": "mild",
                "documented": "2018-04-10",
            },
        ],
        "activeMedications": [
            {
                "id": "med-4",
                "name": "Omeprazole",
                "dosage": "20mg",
                "frequency": "daily before breakfast",
                "started": "2024-01-20",
            },
        ],
    },
    {
        "id": "patient-003",
        "name": "Emily Rodriguez",
        "dateOfBirth": "1990-11-08",
        "mrn": "MRN-10003",
        "allergies": [],
        "activeMedications": [
            {
                "id": "med-5",
                "name": "Albuterol inhaler",
                "dosage": "90mcg",
                "frequency": "as needed",
                "started": "2023-09-01",
            },
        ],
    },
    {
        "id": "patient-004",
        "name": "James Williams",
        "dateOfBirth": "1968-05-30",
        "mrn": "MRN-10004",
        "allergies": [
            {
                "id": "allergy-4",
                "allergen": "Codeine",
                "reaction": "Nausea and vomiting",
                "severity": "moderate",
                "documented": "2015-08-22",
            },
            {
                "id": "allergy-5",
                "allergen": "Latex",
                "reaction": "Contact dermatitis",
                "severity": "mild",
                "documented": "2010-03-15",
            },
        ],
        "activeMedications": [
            {
                "id": "med-6",
                "name": "Amlodipine",
                "dosage": "5mg",
                "frequency": "daily",
                "started": "2021-11-30",
            },
            {
                "id": "med-7",
                "name": "Gabapentin",
                "dosage": "300mg",
                "frequency": "three times daily",
                "started": "2023-04-15",
            },
        ],
    },
    {
        "id": "patient-005",
        "name": "Maria Garcia",
        "dateOfBirth": "1995-01-17",
        "mrn": "MRN-10005",
        "allergies": [],
        "activeMedications": [],
    },
]


