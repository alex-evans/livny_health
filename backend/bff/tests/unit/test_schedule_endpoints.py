"""
Unit tests for schedule-related endpoints.

These tests verify the API contract and response structure
for scheduling functionality.
"""
from datetime import date
from fastapi import status
import pytest


@pytest.mark.unit
class TestGetSchedule:
    """Tests for GET /schedule endpoint"""

    def test_get_schedule_returns_200(self, client, mock_services):
        """Should return 200 OK status"""
        today = date.today().isoformat()
        response = client.get(f"/schedule?date={today}")
        assert response.status_code == status.HTTP_200_OK

    def test_get_schedule_structure(self, client, mock_services):
        """Schedule should have required fields"""
        today = date.today().isoformat()
        response = client.get(f"/schedule?date={today}")
        data = response.json()

        assert "date" in data
        assert "provider" in data
        assert "appointments" in data

    def test_get_schedule_provider_structure(self, client, mock_services):
        """Provider should have id and name"""
        today = date.today().isoformat()
        response = client.get(f"/schedule?date={today}")
        data = response.json()

        assert "id" in data["provider"]
        assert "name" in data["provider"]

    def test_get_schedule_appointments_is_list(self, client, mock_services):
        """Appointments should be a list"""
        today = date.today().isoformat()
        response = client.get(f"/schedule?date={today}")
        data = response.json()

        assert isinstance(data["appointments"], list)

    def test_get_schedule_returns_seeded_appointments(self, client, mock_services):
        """Should return seeded appointments for today"""
        today = date.today().isoformat()
        response = client.get(f"/schedule?date={today}")
        data = response.json()

        # Seeded data includes appointments for today
        assert len(data["appointments"]) > 0

    def test_get_schedule_date_required(self, client, mock_services):
        """Should return 422 when date is missing"""
        response = client.get("/schedule")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_schedule_invalid_date_format(self, client, mock_services):
        """Should return 400 for invalid date format"""
        response = client.get("/schedule?date=invalid-date")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_schedule_with_provider_id(self, client, mock_services):
        """Should accept provider_id parameter"""
        today = date.today().isoformat()
        response = client.get(f"/schedule?date={today}&provider_id=provider-001")
        assert response.status_code == status.HTTP_200_OK

    def test_get_schedule_unknown_provider(self, client, mock_services):
        """Should return 404 for unknown provider"""
        today = date.today().isoformat()
        response = client.get(f"/schedule?date={today}&provider_id=unknown-provider")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.unit
class TestCreateAppointment:
    """Tests for POST /schedule/appointments endpoint"""

    def test_create_appointment_returns_200(self, client, mock_services):
        """Should return 200 OK status for valid request"""
        response = client.post(
            "/schedule/appointments",
            json={
                "date": date.today().isoformat(),
                "patient_id": "patient-001",
                "time": "15:00",
                "duration_minutes": 30,
                "visit_type": "Follow-up",
                "chief_complaint": "Test appointment",
            },
        )
        assert response.status_code == status.HTTP_200_OK

    def test_create_appointment_structure(self, client, mock_services):
        """Response should have success and appointment fields"""
        response = client.post(
            "/schedule/appointments",
            json={
                "date": date.today().isoformat(),
                "patient_id": "patient-002",
                "time": "16:00",
            },
        )
        data = response.json()

        assert "success" in data
        assert data["success"] is True
        assert "appointment" in data

    def test_create_appointment_with_defaults(self, client, mock_services):
        """Should use default values for optional fields"""
        response = client.post(
            "/schedule/appointments",
            json={
                "date": date.today().isoformat(),
                "patient_id": "patient-003",
                "time": "17:00",
            },
        )
        data = response.json()

        assert data["success"] is True
        assert "appointment" in data

    def test_create_appointment_missing_required_fields(self, client, mock_services):
        """Should return 422 for missing required fields"""
        response = client.post(
            "/schedule/appointments",
            json={
                "date": date.today().isoformat(),
                # Missing patient_id and time
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_appointment_invalid_date(self, client, mock_services):
        """Should return 400 for invalid date format"""
        response = client.post(
            "/schedule/appointments",
            json={
                "date": "not-a-date",
                "patient_id": "patient-001",
                "time": "10:00",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.unit
class TestClearAppointments:
    """Tests for DELETE /schedule/schedule/appointments endpoint"""

    def test_clear_appointments_returns_200(self, client, mock_services):
        """Should return 200 OK status"""
        response = client.delete("/schedule/schedule/appointments")
        assert response.status_code == status.HTTP_200_OK

    def test_clear_appointments_response_structure(self, client, mock_services):
        """Response should have success and message fields"""
        response = client.delete("/schedule/schedule/appointments")
        data = response.json()

        assert "success" in data
        assert data["success"] is True
        assert "message" in data


@pytest.mark.unit
class TestScheduleEdgeCases:
    """Additional edge case tests for schedule endpoints"""

    def test_get_schedule_future_date(self, client, mock_services):
        """Should return empty schedule for future date with no appointments"""
        from datetime import timedelta
        future_date = (date.today() + timedelta(days=30)).isoformat()
        response = client.get(f"/schedule?date={future_date}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["appointments"] == []

    def test_get_schedule_past_date(self, client, mock_services):
        """Should return schedule for past date"""
        from datetime import timedelta
        past_date = (date.today() - timedelta(days=7)).isoformat()
        response = client.get(f"/schedule?date={past_date}")
        assert response.status_code == status.HTTP_200_OK

    def test_create_appointment_all_fields(self, client, mock_services):
        """Should create appointment with all fields"""
        response = client.post(
            "/schedule/appointments",
            json={
                "date": date.today().isoformat(),
                "patient_id": "patient-004",
                "time": "14:30",
                "duration_minutes": 45,
                "visit_type": "Annual Physical",
                "chief_complaint": "Yearly checkup",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["appointment"]["visitType"] == "Annual Physical"

    def test_create_appointment_patient_not_found(self, client, mock_services):
        """Should return 400 for unknown patient"""
        response = client.post(
            "/schedule/appointments",
            json={
                "date": date.today().isoformat(),
                "patient_id": "nonexistent-patient",
                "time": "10:00",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_schedule_appointment_includes_patient_data(self, client, mock_services):
        """Appointments should include patient data"""
        today = date.today().isoformat()
        response = client.get(f"/schedule?date={today}")
        data = response.json()

        # At least one appointment should have patient data
        appointments_with_patient = [
            a for a in data["appointments"] if a.get("patient")
        ]
        assert len(appointments_with_patient) > 0
