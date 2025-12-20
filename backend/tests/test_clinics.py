"""
Clinic Tests
Tests for clinic CRUD operations and management
"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestClinicCreation:
    """Test clinic creation"""
    
    async def test_create_clinic_as_admin(
        self,
        client: AsyncClient,
        admin_headers
    ):
        """Test creating a clinic as admin"""
        clinic_data = {
            "name": "New Medical Center",
            "address": "Main Street 123",
            "county": "București",
            "city": "București",
            "phone": "0212345670",
            "email": "new@clinic.com",
            "description": "Modern medical center",
            "working_hours": {
                "monday": {"start": "08:00", "end": "18:00"},
                "tuesday": {"start": "08:00", "end": "18:00"},
                "wednesday": {"start": "08:00", "end": "18:00"},
                "thursday": {"start": "08:00", "end": "18:00"},
                "friday": {"start": "08:00", "end": "18:00"},
                "saturday": {"start": "09:00", "end": "13:00"},
                "sunday": None
            }
        }
        
        response = await client.post(
            "/api/clinics",
            json=clinic_data,
            headers=admin_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == clinic_data["name"]
        assert data["address"] == clinic_data["address"]
        assert "clinic_id" in data
    
    async def test_create_clinic_as_regular_user_fails(
        self,
        client: AsyncClient,
        auth_headers
    ):
        """Test that regular users cannot create clinics"""
        clinic_data = {
            "name": "Unauthorized Clinic",
            "address": "Test Address",
            "county": "București",
            "city": "București",
            "phone": "0212345671",
            "email": "unauthorized@clinic.com"
        }
        
        response = await client.post(
            "/api/clinics",
            json=clinic_data,
            headers=auth_headers
        )
        
        assert response.status_code == 403
    
    async def test_create_clinic_missing_required_fields(
        self,
        client: AsyncClient,
        admin_headers
    ):
        """Test clinic creation with missing required fields"""
        clinic_data = {
            "name": "Incomplete Clinic"
            # Missing address, county, city, phone, email
        }
        
        response = await client.post(
            "/api/clinics",
            json=clinic_data,
            headers=admin_headers
        )
        
        assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.asyncio
class TestClinicRetrieval:
    """Test clinic retrieval"""
    
    async def test_get_all_clinics(
        self,
        client: AsyncClient,
        test_clinic
    ):
        """Test getting list of all clinics"""
        response = await client.get("/api/clinics")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    async def test_get_clinic_by_id(
        self,
        client: AsyncClient,
        test_clinic
    ):
        """Test getting specific clinic by ID"""
        response = await client.get(f"/api/clinics/{test_clinic['clinic_id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["clinic_id"] == test_clinic["clinic_id"]
        assert data["name"] == test_clinic["name"]
    
    async def test_search_clinics_by_county(
        self,
        client: AsyncClient,
        test_clinic
    ):
        """Test searching clinics by county"""
        response = await client.get(
            f"/api/clinics?county={test_clinic['county']}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for clinic in data:
            assert clinic["county"] == test_clinic["county"]
    
    async def test_search_clinics_by_city(
        self,
        client: AsyncClient,
        test_clinic
    ):
        """Test searching clinics by city"""
        response = await client.get(
            f"/api/clinics?city={test_clinic['city']}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for clinic in data:
            assert clinic["city"] == test_clinic["city"]


@pytest.mark.integration
@pytest.mark.asyncio
class TestClinicUpdate:
    """Test clinic updates"""
    
    async def test_update_clinic_as_admin(
        self,
        client: AsyncClient,
        admin_headers,
        test_clinic
    ):
        """Test updating clinic as admin"""
        update_data = {
            "description": "Updated description",
            "phone": "0212345699"
        }
        
        response = await client.put(
            f"/api/clinics/{test_clinic['clinic_id']}",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == update_data["description"]
        assert data["phone"] == update_data["phone"]
    
    async def test_update_clinic_working_hours(
        self,
        client: AsyncClient,
        admin_headers,
        test_clinic
    ):
        """Test updating clinic working hours"""
        update_data = {
            "working_hours": {
                "monday": {"start": "07:00", "end": "19:00"},
                "tuesday": {"start": "07:00", "end": "19:00"},
                "wednesday": {"start": "07:00", "end": "19:00"},
                "thursday": {"start": "07:00", "end": "19:00"},
                "friday": {"start": "07:00", "end": "19:00"},
                "saturday": {"start": "08:00", "end": "14:00"},
                "sunday": None
            }
        }
        
        response = await client.put(
            f"/api/clinics/{test_clinic['clinic_id']}",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["working_hours"]["monday"]["start"] == "07:00"


@pytest.mark.integration
@pytest.mark.asyncio
class TestClinicDoctors:
    """Test clinic-doctor relationships"""
    
    async def test_get_clinic_doctors(
        self,
        client: AsyncClient,
        test_clinic,
        test_doctor
    ):
        """Test getting all doctors for a clinic"""
        response = await client.get(
            f"/api/clinics/{test_clinic['clinic_id']}/doctors"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_clinic_includes_doctor_count(
        self,
        client: AsyncClient,
        test_clinic,
        test_doctor
    ):
        """Test that clinic response includes doctor count"""
        response = await client.get(f"/api/clinics/{test_clinic['clinic_id']}")
        
        assert response.status_code == 200
        data = response.json()
        # Should include doctor_count or doctors array
        assert "doctor_count" in data or "doctors" in data


@pytest.mark.integration
@pytest.mark.asyncio
class TestClinicServices:
    """Test clinic services"""
    
    async def test_add_service_to_clinic(
        self,
        client: AsyncClient,
        admin_headers,
        test_clinic
    ):
        """Test adding a service to clinic"""
        service_data = {
            "name": "General Consultation",
            "description": "Standard medical consultation",
            "price": 150.0,
            "currency": "RON",
            "duration": 30
        }
        
        response = await client.post(
            f"/api/clinics/{test_clinic['clinic_id']}/services",
            json=service_data,
            headers=admin_headers
        )
        
        assert response.status_code in [201, 200]
    
    async def test_get_clinic_services(
        self,
        client: AsyncClient,
        test_clinic
    ):
        """Test getting all services for a clinic"""
        response = await client.get(
            f"/api/clinics/{test_clinic['clinic_id']}/services"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
