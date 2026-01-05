"""
Fake schedule data. Will go away when we have a real database.
"""

from datetime import datetime, timedelta

# Reference to patients from patients module
FAKE_PATIENT_DATA = {
    "patient-001": {
        "id": "patient-001",
        "name": "Sarah Johnson",
        "dateOfBirth": "1985-03-15",
        "gender": "Female",
        "mrn": "MRN-10001",
    },
    "patient-002": {
        "id": "patient-002",
        "name": "Michael Chen",
        "dateOfBirth": "1972-08-22",
        "gender": "Male",
        "mrn": "MRN-10002",
    },
    "patient-003": {
        "id": "patient-003",
        "name": "Emily Rodriguez",
        "dateOfBirth": "1990-11-08",
        "gender": "Female",
        "mrn": "MRN-10003",
    },
    "patient-004": {
        "id": "patient-004",
        "name": "James Williams",
        "dateOfBirth": "1968-05-30",
        "gender": "Male",
        "mrn": "MRN-10004",
    },
    "patient-005": {
        "id": "patient-005",
        "name": "Maria Garcia",
        "dateOfBirth": "1995-01-17",
        "gender": "Female",
        "mrn": "MRN-10005",
    },
    "patient-006": {
        "id": "patient-006",
        "name": "Robert Thompson",
        "dateOfBirth": "1958-07-12",
        "gender": "Male",
        "mrn": "MRN-10006",
    },
    "patient-007": {
        "id": "patient-007",
        "name": "Patricia Martinez",
        "dateOfBirth": "1965-09-23",
        "gender": "Female",
        "mrn": "MRN-10007",
    },
}


def generate_appointments_for_date(date_str: str) -> list[dict]:
    """
    Generate fake appointments for a given date.
    The appointments vary based on the date to simulate different schedules.
    """
    base_date = datetime.strptime(date_str, "%Y-%m-%d")

    # Seed based on date for consistent results
    day_of_week = base_date.weekday()
    day_of_month = base_date.day

    # Define appointment templates
    templates = [
        {
            "patient_id": "patient-001",
            "time_offset": 0,  # 8:00 AM
            "duration": 30,
            "visit_type": "Follow-up",
            "chief_complaint": "Blood pressure check",
            "flags": [{"type": "critical_lab", "message": "A1C elevated at 8.2%"}],
        },
        {
            "patient_id": "patient-002",
            "time_offset": 30,  # 8:30 AM
            "duration": 45,
            "visit_type": "Office Visit",
            "chief_complaint": "Persistent heartburn",
            "flags": [],
        },
        {
            "patient_id": "patient-003",
            "time_offset": 75,  # 9:15 AM
            "duration": 30,
            "visit_type": "Follow-up",
            "chief_complaint": "Asthma follow-up",
            "flags": [{"type": "overdue_screening", "message": "Overdue for cervical cancer screening"}],
        },
        {
            "patient_id": "patient-004",
            "time_offset": 120,  # 10:00 AM
            "duration": 60,
            "visit_type": "Annual Physical",
            "chief_complaint": None,
            "flags": [{"type": "special_needs", "message": "Latex allergy - use nitrile gloves"}],
        },
        {
            "patient_id": "patient-005",
            "time_offset": 180,  # 11:00 AM
            "duration": 30,
            "visit_type": "New Patient",
            "chief_complaint": "Establish care, general wellness",
            "flags": [{"type": "new_patient", "message": "New patient - allow extra time"}],
        },
        {
            "patient_id": "patient-006",
            "time_offset": 240,  # 12:00 PM - lunch usually
            "duration": 30,
            "visit_type": "Urgent",
            "chief_complaint": "Chest pain - stable, for evaluation",
            "flags": [{"type": "critical_lab", "message": "INR out of range at 4.1"}],
        },
        {
            "patient_id": "patient-007",
            "time_offset": 300,  # 1:00 PM
            "duration": 30,
            "visit_type": "Follow-up",
            "chief_complaint": "Medication review",
            "flags": [],
        },
        {
            "patient_id": "patient-001",  # Double-booked example
            "time_offset": 300,  # 1:00 PM (same as above)
            "duration": 15,
            "visit_type": "Procedure",
            "chief_complaint": "Blood draw",
            "flags": [],
            "is_double_booked": True,
        },
        {
            "patient_id": "patient-002",
            "time_offset": 330,  # 1:30 PM
            "duration": 30,
            "visit_type": "Follow-up",
            "chief_complaint": "Review endoscopy results",
            "flags": [],
        },
        {
            "patient_id": "patient-003",
            "time_offset": 360,  # 2:00 PM
            "duration": 30,
            "visit_type": "Office Visit",
            "chief_complaint": "Shortness of breath with exercise",
            "flags": [],
        },
        {
            "patient_id": "patient-004",
            "time_offset": 390,  # 2:30 PM
            "duration": 45,
            "visit_type": "Follow-up",
            "chief_complaint": "Pain management review",
            "flags": [],
        },
        {
            "patient_id": "patient-005",
            "time_offset": 450,  # 3:30 PM
            "duration": 30,
            "visit_type": "Office Visit",
            "chief_complaint": "Fatigue and low energy",
            "flags": [],
        },
    ]

    # Generate appointments based on templates
    appointments = []
    start_time = base_date.replace(hour=8, minute=0, second=0, microsecond=0)
    now = datetime.now()

    for idx, template in enumerate(templates):
        # Skip some appointments on certain days for variety
        if day_of_week == 0 and idx > 8:  # Lighter Monday
            continue
        if day_of_week == 4 and idx in [5, 7]:  # Skip some on Friday
            continue

        appt_start = start_time + timedelta(minutes=template["time_offset"])
        appt_end = appt_start + timedelta(minutes=template["duration"])

        # Determine status based on current time
        if base_date.date() < now.date():
            # Past days - all completed
            status = "completed"
        elif base_date.date() > now.date():
            # Future days - all scheduled
            status = "scheduled"
        else:
            # Today - determine based on time
            if appt_end < now:
                status = "completed"
            elif appt_start <= now < appt_end:
                status = "in_progress"
            else:
                status = "scheduled"

        # Add some variety to past appointments
        if status == "completed" and idx == 3:
            status = "no_show"
        if status == "scheduled" and idx == 6 and day_of_week == 2:
            status = "canceled"

        # Check-in status for upcoming appointments (30 min before)
        if status == "scheduled" and base_date.date() == now.date():
            if now >= appt_start - timedelta(minutes=30):
                status = "checked_in"

        patient = FAKE_PATIENT_DATA[template["patient_id"]]

        appointment = {
            "id": f"appt-{date_str}-{idx:03d}",
            "patient": {
                "id": patient["id"],
                "name": patient["name"],
                "dateOfBirth": patient["dateOfBirth"],
                "gender": patient["gender"],
                "mrn": patient["mrn"],
            },
            "appointmentTime": appt_start.isoformat(),
            "endTime": appt_end.isoformat(),
            "durationMinutes": template["duration"],
            "visitType": template["visit_type"],
            "chiefComplaint": template["chief_complaint"],
            "status": status,
            "flags": template["flags"],
            "isDoubleBooked": template.get("is_double_booked", False),
        }
        appointments.append(appointment)

    return appointments


# Provider data
FAKE_PROVIDERS = {
    "provider-001": {
        "id": "provider-001",
        "name": "Dr. Elizabeth Frost",
    },
}
