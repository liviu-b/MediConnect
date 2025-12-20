"""
Authentication Tests
Tests for user registration, login, and authentication flows
"""

import pytest
from httpx import AsyncClient


@pytest.mark.auth
class TestUserRegistration:
    """Test user registration flow"""
    
    @pytest.mark.asyncio
    async def test_register_new_user_success(self, client: AsyncClient):
        """Test successful user registration"""
        user_data = {
            "email": "newuser@example.com",
            "password": "NewUser123!@#",
            "full_name": "New User",
            "phone": "0712345690"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "password" not in data  # Password should not be returned
    
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Test registration with duplicate email fails"""
        user_data = {
            "email": test_user["email"],  # Same email as test_user
            "password": "Another123!@#",
            "full_name": "Another User",
            "phone": "0712345691"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email format"""
        user_data = {
            "email": "invalid-email",
            "password": "Test123!@#",
            "full_name": "Test User",
            "phone": "0712345692"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error
    
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password"""
        user_data = {
            "email": "weak@example.com",
            "password": "123",  # Too weak
            "full_name": "Weak Password User",
            "phone": "0712345693"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code in [400, 422]
    
    async def test_register_missing_required_fields(self, client: AsyncClient):
        """Test registration with missing required fields"""
        user_data = {
            "email": "incomplete@example.com"
            # Missing password, full_name, phone
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 422


@pytest.mark.auth
@pytest.mark.asyncio
class TestUserLogin:
    """Test user login flow"""
    
    async def test_login_success(self, client: AsyncClient, test_user):
        """Test successful login"""
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        response = await client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Test login with wrong password"""
        login_data = {
            "email": test_user["email"],
            "password": "WrongPassword123!@#"
        }
        
        response = await client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent email"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "Test123!@#"
        }
        
        response = await client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
    
    async def test_login_case_insensitive_email(self, client: AsyncClient, test_user):
        """Test login with different email case"""
        login_data = {
            "email": test_user["email"].upper(),  # Uppercase email
            "password": test_user["password"]
        }
        
        response = await client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200


@pytest.mark.auth
@pytest.mark.asyncio
class TestAuthenticatedRequests:
    """Test authenticated API requests"""
    
    async def test_get_current_user(self, client: AsyncClient, auth_headers, test_user):
        """Test getting current user info"""
        response = await client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["email"]
        assert data["full_name"] == test_user["full_name"]
        assert "password" not in data
    
    async def test_access_protected_route_without_token(self, client: AsyncClient):
        """Test accessing protected route without authentication"""
        response = await client.get("/api/auth/me")
        
        assert response.status_code == 401
    
    async def test_access_protected_route_invalid_token(self, client: AsyncClient):
        """Test accessing protected route with invalid token"""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = await client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    async def test_token_contains_user_info(self, client: AsyncClient, test_user):
        """Test that JWT token contains correct user information"""
        # Login
        login_response = await client.post("/api/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        
        token = login_response.json()["access_token"]
        
        # Decode token (without verification for testing)
        import jwt
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        assert "sub" in decoded  # Subject (user_id)
        assert "email" in decoded
        assert decoded["email"] == test_user["email"]


@pytest.mark.auth
@pytest.mark.asyncio
class TestPasswordSecurity:
    """Test password security measures"""
    
    async def test_password_hashed_in_database(self, client: AsyncClient, test_user):
        """Test that passwords are hashed in database"""
        from app.db import db
        
        user = await db.users.find_one({"email": test_user["email"]})
        
        assert user is not None
        assert "hashed_password" in user
        assert user["hashed_password"] != test_user["password"]
        assert len(user["hashed_password"]) > 50  # Bcrypt hash length
    
    async def test_password_not_returned_in_api(self, client: AsyncClient, auth_headers):
        """Test that password is never returned in API responses"""
        response = await client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "password" not in data
        assert "hashed_password" not in data


@pytest.mark.auth
@pytest.mark.asyncio
class TestRoleBasedAccess:
    """Test role-based access control"""
    
    async def test_regular_user_cannot_create_clinic(
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
            "phone": "0212345678",
            "email": "test@clinic.com"
        }
        
        response = await client.post(
            "/api/clinics",
            json=clinic_data,
            headers=auth_headers
        )
        
        assert response.status_code == 403  # Forbidden
    
    async def test_admin_can_create_clinic(
        self,
        client: AsyncClient,
        admin_headers
    ):
        """Test that admin users can create clinics"""
        clinic_data = {
            "name": "Admin Clinic",
            "address": "Admin Address",
            "county": "București",
            "city": "București",
            "phone": "0212345679",
            "email": "admin@clinic.com",
            "description": "Admin clinic"
        }
        
        response = await client.post(
            "/api/clinics",
            json=clinic_data,
            headers=admin_headers
        )
        
        assert response.status_code == 201


@pytest.mark.auth
@pytest.mark.asyncio
class TestTokenExpiration:
    """Test JWT token expiration"""
    
    async def test_token_has_expiration(self, client: AsyncClient, test_user):
        """Test that JWT tokens have expiration time"""
        login_response = await client.post("/api/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        
        token = login_response.json()["access_token"]
        
        # Decode token
        import jwt
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        assert "exp" in decoded  # Expiration time
        assert decoded["exp"] > decoded.get("iat", 0)  # Expires after issued
