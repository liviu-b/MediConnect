"""
Pytest Configuration and Fixtures
Shared fixtures for all tests
"""

import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
import sys
from pathlib import Path

# Enable pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set test environment BEFORE importing app
os.environ["TESTING"] = "true"
os.environ["REDIS_ENABLED"] = "false"  # Disable Redis for tests
os.environ["RATE_LIMIT_ENABLED"] = "false"  # Disable rate limiting for tests
os.environ["MONGO_URL"] = os.getenv("MONGO_URL", "mongodb://localhost:27017")

# Now import app modules
from app.main import app
from app.db import db
from app.config import MONGO_URL


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    """Create test client"""
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(client):
    """Create a test user"""
    user_data = {
        "email": "test@example.com",
        "password": "Test123!@#",
        "full_name": "Test User",
        "phone": "0712345678"
    }
    
    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    
    return {
        **user_data,
        "user_id": response.json()["user_id"]
    }


@pytest.fixture
async def auth_headers(client, test_user):
    """Get authentication headers for test user"""
    response = await client.post("/api/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_user(client):
    """Create an admin user"""
    admin_data = {
        "email": "admin@example.com",
        "password": "Admin123!@#",
        "full_name": "Admin User",
        "phone": "0712345679",
        "role": "CLINIC_ADMIN"
    }
    
    # Register admin
    response = await client.post("/api/auth/register", json=admin_data)
    assert response.status_code == 201
    
    # Update role in database (normally done by super admin)
    from app.db import db
    await db.users.update_one(
        {"email": admin_data["email"]},
        {"$set": {"role": "CLINIC_ADMIN"}}
    )
    
    return {
        **admin_data,
        "user_id": response.json()["user_id"]
    }


@pytest.fixture
async def admin_headers(client, admin_user):
    """Get authentication headers for admin user"""
    response = await client.post("/api/auth/login", json={
        "email": admin_user["email"],
        "password": admin_user["password"]
    })
    
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_clinic(client, admin_headers):
    """Create a test clinic"""
    clinic_data = {
        "name": "Test Clinic",
        "address": "Test Address 123",
        "county": "București",
        "city": "București",
        "phone": "0212345678",
        "email": "clinic@test.com",
        "description": "Test clinic description",
        "working_hours": {
            "monday": {"start": "09:00", "end": "17:00"},
            "tuesday": {"start": "09:00", "end": "17:00"},
            "wednesday": {"start": "09:00", "end": "17:00"},
            "thursday": {"start": "09:00", "end": "17:00"},
            "friday": {"start": "09:00", "end": "17:00"},
            "saturday": {"start": "10:00", "end": "14:00"},
            "sunday": None
        }
    }
    
    response = await client.post(
        "/api/clinics",
        json=clinic_data,
        headers=admin_headers
    )
    
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def test_doctor(client, admin_headers, test_clinic):
    """Create a test doctor"""
    doctor_data = {
        "name": "Dr. Test Doctor",
        "email": "doctor@test.com",
        "phone": "0712345680",
        "specialty": "Cardiology",
        "bio": "Test doctor bio",
        "consultation_duration": 30,
        "consultation_fee": 200.0,
        "currency": "RON"
    }
    
    response = await client.post(
        "/api/doctors",
        json=doctor_data,
        headers=admin_headers
    )
    
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def test_appointment(client, auth_headers, test_doctor):
    """Create a test appointment"""
    from datetime import datetime, timedelta
    
    # Schedule appointment for tomorrow at 10:00
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    appointment_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    
    appointment_data = {
        "doctor_id": test_doctor["doctor_id"],
        "date_time": appointment_time.isoformat(),
        "reason": "Test consultation",
        "notes": "Test notes"
    }
    
    response = await client.post(
        "/api/appointments",
        json=appointment_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "sample@example.com",
        "password": "Sample123!@#",
        "full_name": "Sample User",
        "phone": "0712345681"
    }


@pytest.fixture
def sample_doctor_data():
    """Sample doctor data for testing"""
    return {
        "name": "Dr. Sample Doctor",
        "email": "sample.doctor@test.com",
        "phone": "0712345682",
        "specialty": "General Medicine",
        "bio": "Sample doctor bio",
        "consultation_duration": 30,
        "consultation_fee": 150.0,
        "currency": "RON"
    }


@pytest.fixture
def sample_appointment_data():
    """Sample appointment data for testing"""
    from datetime import datetime, timedelta
    
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    appointment_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    
    return {
        "date_time": appointment_time.isoformat(),
        "reason": "Sample consultation",
        "notes": "Sample notes"
    }


# Helper functions for tests
def assert_valid_uuid(value: str):
    """Assert that value is a valid UUID"""
    import uuid
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def assert_valid_datetime(value: str):
    """Assert that value is a valid ISO datetime"""
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False
