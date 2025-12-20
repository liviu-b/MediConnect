"""
Doctor Tests
Tests for doctor CRUD operations and availability
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta


@pytest.mark.doctors
@pytest.mark.asyncio
class TestDoctorCreation:
    """Test doctor creation"""
    
    async def test_create_doctor_as_admin(
        self,
        client: AsyncClient,
        admin_headers,
        test_clinic
    ):
        """Test creating a doctor as admin"""
        doctor_data = {
            "name": "Dr. New Doctor",
            "email": "newdoctor@test.com",
            "phone": "0712345685",
            "specialty": "Pediatrics",
            "bio": "Experienced pediatrician",
            "consultation_duration": 30,
            "consultation_fee": 180.0,
            "currency": "RON"
        }
        
        response = await client.post(
            "/api/doctors",
            json=doctor_data,
            headers=admin_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == doctor_data["name"]
        assert data["email"] == doctor_data["email"]
        assert data["specialty"] == doctor_data["specialty"]
        assert "doctor_id" in data
    
    async def test_create_doctor_as_regular_user_fails(
        self,
        client: AsyncClient,
        auth_headers,
        sample_doctor_data
    ):
        """Test that regular users cannot create doctors"""
        response = await client.post(
            "/api/doctors",
            json=sample_doctor_data,
            headers=auth_headers
        )
        
        assert response.status_code == 403
    
    async def test_create_doctor_duplicate_email(
        self,
        client: AsyncClient,
        admin_headers,
        test_doctor
    ):
        """Test creating doctor with duplicate email fails"""
        doctor_data = {
            "name": "Dr. Duplicate",
            "email": test_doctor["email"],  # Same email
            "phone": "0712345686",
            "specialty": "Surgery",
            "consultation_duration": 30,
            "consultation_fee": 200.0,
            "currency": "RON"
        }
        
        response = await client.post(
            "/api/doctors",
            json=doctor_data,
            headers=admin_headers
        )
        
        assert response.status_code == 400
    
    async def test_create_doctor_with_availability_schedule(
        self,
        client: AsyncClient,
        admin_headers
    ):
        """Test creating doctor with custom availability schedule"""
        doctor_data = {
            "name": "Dr. Custom Schedule",
            "email": "custom@test.com",
            "phone": "0712345687",
            "specialty": "Dermatology",
            "consultation_duration": 45,
            "consultation_fee": 250.0,
            "currency": "RON",
            "availability_schedule": {
                "monday": [{"start": "10:00", "end": "14:00"}],
                "tuesday": [{"start": "10:00", "end": "14:00"}],
                "wednesday": [],
                "thursday": [{"start": "10:00", "end": "14:00"}],
                "friday": [{"start": "10:00", "end": "14:00"}],
                "saturday": [],
                "sunday": []
            }
        }
        
        response = await client.post(
            "/api/doctors",
            json=doctor_data,
            headers=admin_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "availability_schedule" in data
        assert data["availability_schedule"]["monday"][0]["start"] == "10:00"


@pytest.mark.doctors
@pytest.mark.asyncio
class TestDoctorRetrieval:
    """Test doctor retrieval operations"""
    
    async def test_get_all_doctors(
        self,
        client: AsyncClient,
        test_doctor
    ):
        """Test getting list of all doctors"""
        response = await client.get("/api/doctors")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(d["doctor_id"] == test_doctor["doctor_id"] for d in data)
    
    async def test_get_doctor_by_id(
        self,
        client: AsyncClient,
        test_doctor
    ):
        """Test getting specific doctor by ID"""
        response = await client.get(f"/api/doctors/{test_doctor['doctor_id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["doctor_id"] == test_doctor["doctor_id"]
        assert data["name"] == test_doctor["name"]
        assert data["specialty"] == test_doctor["specialty"]
    
    async def test_get_nonexistent_doctor(self, client: AsyncClient):
        """Test getting non-existent doctor returns 404"""
        response = await client.get("/api/doctors/nonexistent_id")
        
        assert response.status_code == 404
    
    async def test_get_doctors_by_clinic(
        self,
        client: AsyncClient,
        test_clinic,
        test_doctor
    ):
        """Test filtering doctors by clinic"""
        response = await client.get(
            f"/api/doctors?clinic_id={test_clinic['clinic_id']}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All doctors should belong to the specified clinic
        for doctor in data:
            assert doctor.get("clinic_id") == test_clinic["clinic_id"]
    
    async def test_doctor_response_includes_clinic_info(
        self,
        client: AsyncClient,
        test_doctor
    ):
        """Test that doctor response includes clinic information"""
        response = await client.get(f"/api/doctors/{test_doctor['doctor_id']}")
        
        assert response.status_code == 200
        data = response.json()
        # Should include clinic_name or clinic info
        assert "clinic_id" in data or "clinic_name" in data


@pytest.mark.doctors
@pytest.mark.asyncio
class TestDoctorUpdate:
    """Test doctor update operations"""
    
    async def test_update_doctor_as_admin(
        self,
        client: AsyncClient,
        admin_headers,
        test_doctor
    ):
        """Test updating doctor as admin"""
        update_data = {
            "bio": "Updated bio information",
            "consultation_fee": 250.0
        }
        
        response = await client.put(
            f"/api/doctors/{test_doctor['doctor_id']}",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == update_data["bio"]
        assert data["consultation_fee"] == update_data["consultation_fee"]
    
    async def test_update_doctor_as_regular_user_fails(
        self,
        client: AsyncClient,
        auth_headers,
        test_doctor
    ):
        """Test that regular users cannot update doctors"""
        update_data = {"bio": "Unauthorized update"}
        
        response = await client.put(
            f"/api/doctors/{test_doctor['doctor_id']}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 403
    
    async def test_update_nonexistent_doctor(
        self,
        client: AsyncClient,
        admin_headers
    ):
        """Test updating non-existent doctor returns 404"""
        update_data = {"bio": "Test"}
        
        response = await client.put(
            "/api/doctors/nonexistent_id",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == 404


@pytest.mark.doctors
@pytest.mark.asyncio
class TestDoctorAvailability:
    """Test doctor availability operations"""
    
    async def test_get_doctor_availability(
        self,
        client: AsyncClient,
        test_doctor
    ):
        """Test getting doctor availability for a specific date"""
        # Get availability for tomorrow
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
        
        response = await client.get(
            f"/api/doctors/{test_doctor['doctor_id']}/availability?date={tomorrow}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "available_slots" in data
        assert "duration" in data
        assert isinstance(data["available_slots"], list)
    
    async def test_availability_excludes_booked_slots(
        self,
        client: AsyncClient,
        test_doctor,
        test_appointment
    ):
        """Test that booked slots are excluded from availability"""
        # Get the appointment date
        appointment_date = datetime.fromisoformat(
            test_appointment["date_time"].replace("Z", "+00:00")
        ).strftime("%Y-%m-%d")
        
        response = await client.get(
            f"/api/doctors/{test_doctor['doctor_id']}/availability?date={appointment_date}"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # The booked time should not be in available slots
        appointment_time = datetime.fromisoformat(
            test_appointment["date_time"].replace("Z", "+00:00")
        ).strftime("%H:%M")
        
        available_times = [slot["time"] for slot in data["available_slots"]]
        assert appointment_time not in available_times
    
    async def test_update_doctor_availability(
        self,
        client: AsyncClient,
        admin_headers,
        test_doctor
    ):
        """Test updating doctor availability schedule"""
        new_schedule = {
            "availability_schedule": {
                "monday": [{"start": "08:00", "end": "12:00"}],
                "tuesday": [{"start": "08:00", "end": "12:00"}],
                "wednesday": [{"start": "08:00", "end": "12:00"}],
                "thursday": [{"start": "08:00", "end": "12:00"}],
                "friday": [{"start": "08:00", "end": "12:00"}],
                "saturday": [],
                "sunday": []
            }
        }
        
        response = await client.put(
            f"/api/doctors/{test_doctor['doctor_id']}/availability",
            json=new_schedule,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["availability_schedule"]["monday"][0]["start"] == "08:00"
    
    async def test_availability_invalid_date_format(
        self,
        client: AsyncClient,
        test_doctor
    ):
        """Test that invalid date format returns error"""
        response = await client.get(
            f"/api/doctors/{test_doctor['doctor_id']}/availability?date=invalid-date"
        )
        
        assert response.status_code == 400


@pytest.mark.doctors
@pytest.mark.asyncio
class TestDoctorDeletion:
    """Test doctor deletion (deactivation)"""
    
    async def test_delete_doctor_as_admin(
        self,
        client: AsyncClient,
        admin_headers,
        test_doctor
    ):
        """Test deleting (deactivating) doctor as admin"""
        response = await client.delete(
            f"/api/doctors/{test_doctor['doctor_id']}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        
        # Verify doctor is deactivated
        get_response = await client.get(f"/api/doctors/{test_doctor['doctor_id']}")
        # Should either return 404 or show is_active=False
        assert get_response.status_code in [404, 200]
        if get_response.status_code == 200:
            assert get_response.json().get("is_active") == False
    
    async def test_delete_doctor_as_regular_user_fails(
        self,
        client: AsyncClient,
        auth_headers,
        test_doctor
    ):
        """Test that regular users cannot delete doctors"""
        response = await client.delete(
            f"/api/doctors/{test_doctor['doctor_id']}",
            headers=auth_headers
        )
        
        assert response.status_code == 403


@pytest.mark.doctors
@pytest.mark.asyncio
class TestDoctorCaching:
    """Test doctor caching functionality"""
    
    async def test_doctor_cached_after_first_request(
        self,
        client: AsyncClient,
        test_doctor
    ):
        """Test that doctor data is cached after first request"""
        # First request
        response1 = await client.get(f"/api/doctors/{test_doctor['doctor_id']}")
        assert response1.status_code == 200
        
        # Second request (should be from cache)
        response2 = await client.get(f"/api/doctors/{test_doctor['doctor_id']}")
        assert response2.status_code == 200
        
        # Data should be identical
        assert response1.json() == response2.json()
    
    async def test_cache_invalidated_after_update(
        self,
        client: AsyncClient,
        admin_headers,
        test_doctor
    ):
        """Test that cache is invalidated after doctor update"""
        # Get doctor (cached)
        response1 = await client.get(f"/api/doctors/{test_doctor['doctor_id']}")
        original_bio = response1.json()["bio"]
        
        # Update doctor
        update_data = {"bio": "Updated bio for cache test"}
        await client.put(
            f"/api/doctors/{test_doctor['doctor_id']}",
            json=update_data,
            headers=admin_headers
        )
        
        # Get doctor again (should have new data)
        response2 = await client.get(f"/api/doctors/{test_doctor['doctor_id']}")
        new_bio = response2.json()["bio"]
        
        assert new_bio == update_data["bio"]
        assert new_bio != original_bio
