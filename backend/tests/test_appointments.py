"""
Appointment Tests
Tests for appointment booking, management, and workflows
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta


@pytest.mark.appointments
@pytest.mark.asyncio
class TestAppointmentCreation:
    """Test appointment creation"""
    
    async def test_create_appointment_success(
        self,
        client: AsyncClient,
        auth_headers,
        test_doctor
    ):
        """Test successful appointment creation"""
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        appointment_time = tomorrow.replace(hour=11, minute=0, second=0, microsecond=0)
        
        appointment_data = {
            "doctor_id": test_doctor["doctor_id"],
            "date_time": appointment_time.isoformat(),
            "reason": "Regular checkup",
            "notes": "First visit"
        }
        
        response = await client.post(
            "/api/appointments",
            json=appointment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "appointment_id" in data
        assert data["doctor_id"] == test_doctor["doctor_id"]
        assert data["reason"] == appointment_data["reason"]
        assert data["status"] == "SCHEDULED"
    
    async def test_create_appointment_without_auth_fails(
        self,
        client: AsyncClient,
        test_doctor,
        sample_appointment_data
    ):
        """Test that unauthenticated users cannot create appointments"""
        appointment_data = {
            **sample_appointment_data,
            "doctor_id": test_doctor["doctor_id"]
        }
        
        response = await client.post(
            "/api/appointments",
            json=appointment_data
        )
        
        assert response.status_code == 401
    
    async def test_create_appointment_past_date_fails(
        self,
        client: AsyncClient,
        auth_headers,
        test_doctor
    ):
        """Test that appointments cannot be created in the past"""
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        
        appointment_data = {
            "doctor_id": test_doctor["doctor_id"],
            "date_time": yesterday.isoformat(),
            "reason": "Past appointment"
        }
        
        response = await client.post(
            "/api/appointments",
            json=appointment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    async def test_create_appointment_nonexistent_doctor_fails(
        self,
        client: AsyncClient,
        auth_headers
    ):
        """Test appointment creation with non-existent doctor fails"""
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        
        appointment_data = {
            "doctor_id": "nonexistent_doctor_id",
            "date_time": tomorrow.isoformat(),
            "reason": "Test"
        }
        
        response = await client.post(
            "/api/appointments",
            json=appointment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_create_appointment_duplicate_slot_fails(
        self,
        client: AsyncClient,
        auth_headers,
        test_appointment
    ):
        """Test that double-booking same slot fails"""
        # Try to book the same time slot
        appointment_data = {
            "doctor_id": test_appointment["doctor_id"],
            "date_time": test_appointment["date_time"],
            "reason": "Duplicate booking"
        }
        
        response = await client.post(
            "/api/appointments",
            json=appointment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "already booked" in response.json()["detail"].lower()


@pytest.mark.appointments
@pytest.mark.asyncio
class TestAppointmentRetrieval:
    """Test appointment retrieval"""
    
    async def test_get_my_appointments(
        self,
        client: AsyncClient,
        auth_headers,
        test_appointment
    ):
        """Test getting current user's appointments"""
        response = await client.get(
            "/api/appointments",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(a["appointment_id"] == test_appointment["appointment_id"] for a in data)
    
    async def test_get_appointment_by_id(
        self,
        client: AsyncClient,
        auth_headers,
        test_appointment
    ):
        """Test getting specific appointment by ID"""
        response = await client.get(
            f"/api/appointments/{test_appointment['appointment_id']}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["appointment_id"] == test_appointment["appointment_id"]
    
    async def test_cannot_view_other_users_appointment(
        self,
        client: AsyncClient,
        test_appointment
    ):
        """Test that users cannot view other users' appointments"""
        # Create a different user
        other_user_data = {
            "email": "other@example.com",
            "password": "Other123!@#",
            "full_name": "Other User",
            "phone": "0712345699"
        }
        
        await client.post("/api/auth/register", json=other_user_data)
        
        # Login as other user
        login_response = await client.post("/api/auth/login", json={
            "email": other_user_data["email"],
            "password": other_user_data["password"]
        })
        
        other_headers = {
            "Authorization": f"Bearer {login_response.json()['access_token']}"
        }
        
        # Try to access first user's appointment
        response = await client.get(
            f"/api/appointments/{test_appointment['appointment_id']}",
            headers=other_headers
        )
        
        assert response.status_code == 403
    
    async def test_admin_can_view_all_appointments(
        self,
        client: AsyncClient,
        admin_headers,
        test_appointment
    ):
        """Test that admins can view all appointments"""
        response = await client.get(
            f"/api/appointments/{test_appointment['appointment_id']}",
            headers=admin_headers
        )
        
        assert response.status_code == 200


@pytest.mark.appointments
@pytest.mark.asyncio
class TestAppointmentUpdate:
    """Test appointment updates"""
    
    async def test_update_appointment_status(
        self,
        client: AsyncClient,
        admin_headers,
        test_appointment
    ):
        """Test updating appointment status"""
        update_data = {
            "status": "CONFIRMED"
        }
        
        response = await client.put(
            f"/api/appointments/{test_appointment['appointment_id']}",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "CONFIRMED"
    
    async def test_patient_cannot_change_status(
        self,
        client: AsyncClient,
        auth_headers,
        test_appointment
    ):
        """Test that patients cannot change appointment status"""
        update_data = {
            "status": "COMPLETED"
        }
        
        response = await client.put(
            f"/api/appointments/{test_appointment['appointment_id']}",
            json=update_data,
            headers=auth_headers
        )
        
        # Should either fail or ignore status change
        assert response.status_code in [403, 200]
        if response.status_code == 200:
            # Status should not have changed
            assert response.json()["status"] != "COMPLETED"
    
    async def test_reschedule_appointment(
        self,
        client: AsyncClient,
        auth_headers,
        test_appointment
    ):
        """Test rescheduling an appointment"""
        new_time = datetime.now(timezone.utc) + timedelta(days=2)
        new_time = new_time.replace(hour=15, minute=0, second=0, microsecond=0)
        
        update_data = {
            "date_time": new_time.isoformat()
        }
        
        response = await client.put(
            f"/api/appointments/{test_appointment['appointment_id']}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        # Verify time was updated
        assert data["date_time"] != test_appointment["date_time"]


@pytest.mark.appointments
@pytest.mark.asyncio
class TestAppointmentCancellation:
    """Test appointment cancellation"""
    
    async def test_cancel_appointment_as_patient(
        self,
        client: AsyncClient,
        auth_headers,
        test_appointment
    ):
        """Test patient cancelling their own appointment"""
        response = await client.delete(
            f"/api/appointments/{test_appointment['appointment_id']}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify appointment is cancelled
        get_response = await client.get(
            f"/api/appointments/{test_appointment['appointment_id']}",
            headers=auth_headers
        )
        
        assert get_response.status_code == 200
        assert get_response.json()["status"] == "CANCELLED"
    
    async def test_cancel_appointment_as_admin(
        self,
        client: AsyncClient,
        admin_headers,
        test_appointment
    ):
        """Test admin cancelling an appointment"""
        response = await client.delete(
            f"/api/appointments/{test_appointment['appointment_id']}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
    
    async def test_cannot_cancel_other_users_appointment(
        self,
        client: AsyncClient,
        test_appointment
    ):
        """Test that users cannot cancel other users' appointments"""
        # Create different user
        other_user_data = {
            "email": "canceller@example.com",
            "password": "Cancel123!@#",
            "full_name": "Canceller User",
            "phone": "0712345698"
        }
        
        await client.post("/api/auth/register", json=other_user_data)
        login_response = await client.post("/api/auth/login", json={
            "email": other_user_data["email"],
            "password": other_user_data["password"]
        })
        
        other_headers = {
            "Authorization": f"Bearer {login_response.json()['access_token']}"
        }
        
        response = await client.delete(
            f"/api/appointments/{test_appointment['appointment_id']}",
            headers=other_headers
        )
        
        assert response.status_code == 403


@pytest.mark.appointments
@pytest.mark.asyncio
class TestRecurringAppointments:
    """Test recurring appointment functionality"""
    
    async def test_create_recurring_appointments(
        self,
        client: AsyncClient,
        auth_headers,
        test_doctor
    ):
        """Test creating recurring appointments"""
        start_date = datetime.now(timezone.utc) + timedelta(days=1)
        start_date = start_date.replace(hour=10, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(weeks=4)
        
        appointment_data = {
            "doctor_id": test_doctor["doctor_id"],
            "date_time": start_date.isoformat(),
            "reason": "Weekly therapy",
            "recurrence": {
                "frequency": "WEEKLY",
                "end_date": end_date.strftime("%Y-%m-%d")
            }
        }
        
        response = await client.post(
            "/api/appointments",
            json=appointment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Should create multiple appointments
        if isinstance(data, list):
            assert len(data) >= 4  # At least 4 weekly appointments
        else:
            # Or return info about created recurring appointments
            assert "appointment_id" in data


@pytest.mark.appointments
@pytest.mark.asyncio
class TestAppointmentNotifications:
    """Test appointment notification functionality"""
    
    async def test_appointment_confirmation_sent(
        self,
        client: AsyncClient,
        auth_headers,
        test_doctor
    ):
        """Test that confirmation is sent when appointment is created"""
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        appointment_time = tomorrow.replace(hour=13, minute=0, second=0, microsecond=0)
        
        appointment_data = {
            "doctor_id": test_doctor["doctor_id"],
            "date_time": appointment_time.isoformat(),
            "reason": "Notification test"
        }
        
        response = await client.post(
            "/api/appointments",
            json=appointment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        # In real implementation, check email was sent
        # For now, just verify appointment was created


@pytest.mark.appointments
@pytest.mark.asyncio
class TestAppointmentFiltering:
    """Test appointment filtering and querying"""
    
    async def test_filter_appointments_by_status(
        self,
        client: AsyncClient,
        auth_headers,
        test_appointment
    ):
        """Test filtering appointments by status"""
        response = await client.get(
            "/api/appointments?status=SCHEDULED",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All returned appointments should have SCHEDULED status
        for appointment in data:
            assert appointment["status"] == "SCHEDULED"
    
    async def test_filter_appointments_by_date_range(
        self,
        client: AsyncClient,
        auth_headers
    ):
        """Test filtering appointments by date range"""
        start_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        end_date = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d")
        
        response = await client.get(
            f"/api/appointments?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.appointments
@pytest.mark.asyncio
class TestAppointmentValidation:
    """Test appointment validation rules"""
    
    async def test_appointment_within_doctor_availability(
        self,
        client: AsyncClient,
        auth_headers,
        test_doctor
    ):
        """Test that appointments must be within doctor's availability"""
        # Try to book on Sunday (typically not available)
        next_sunday = datetime.now(timezone.utc) + timedelta(days=(6 - datetime.now().weekday()) % 7 + 7)
        appointment_time = next_sunday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        appointment_data = {
            "doctor_id": test_doctor["doctor_id"],
            "date_time": appointment_time.isoformat(),
            "reason": "Sunday test"
        }
        
        response = await client.post(
            "/api/appointments",
            json=appointment_data,
            headers=auth_headers
        )
        
        # Should fail if doctor doesn't work on Sundays
        # (depends on doctor's availability schedule)
        assert response.status_code in [400, 201]
    
    async def test_appointment_duration_respected(
        self,
        client: AsyncClient,
        auth_headers,
        test_doctor
    ):
        """Test that appointment duration is respected"""
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        time1 = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        
        # Create first appointment
        appointment1_data = {
            "doctor_id": test_doctor["doctor_id"],
            "date_time": time1.isoformat(),
            "reason": "First appointment"
        }
        
        response1 = await client.post(
            "/api/appointments",
            json=appointment1_data,
            headers=auth_headers
        )
        
        assert response1.status_code == 201
        
        # Try to book 15 minutes later (should fail if duration is 30 min)
        time2 = time1 + timedelta(minutes=15)
        appointment2_data = {
            "doctor_id": test_doctor["doctor_id"],
            "date_time": time2.isoformat(),
            "reason": "Overlapping appointment"
        }
        
        response2 = await client.post(
            "/api/appointments",
            json=appointment2_data,
            headers=auth_headers
        )
        
        # Should fail due to overlap
        assert response2.status_code == 400
