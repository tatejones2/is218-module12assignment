# tests/integration/test_user_endpoints.py

"""
Integration tests for user endpoints.

Tests for:
- User registration (POST /users/register)
- User login (POST /users/login)
- Get current user (GET /users/me)
- Get user by ID (GET /users/{user_id})
- Update user profile (PUT /users/{user_id})
- Change password (POST /users/{user_id}/change-password)
- Deactivate user (POST /users/{user_id}/deactivate)
- Delete user (DELETE /users/{user_id})
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db
from app.models.user import User

client = TestClient(app)


@pytest.fixture
def db_session(db):
    """Provide a database session for tests."""
    return db


class TestUserRegistration:
    """Tests for user registration endpoint."""
    
    def test_register_new_user_success(self, db_session):
        """Test successful user registration."""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "username": "johndoe",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        
        response = client.post("/users/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "johndoe"
        assert data["email"] == "john.doe@example.com"
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert "id" in data
        assert "password" not in data  # Password should not be returned
    
    def test_register_duplicate_username(self, db_session):
        """Test registration with duplicate username."""
        # Create first user
        user_data_1 = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "username": "johndoe",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        client.post("/users/register", json=user_data_1)
        
        # Try to create second user with same username
        user_data_2 = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "username": "johndoe",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        response = client.post("/users/register", json=user_data_2)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_register_duplicate_email(self, db_session):
        """Test registration with duplicate email."""
        # Create first user
        user_data_1 = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "username": "johndoe",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        client.post("/users/register", json=user_data_1)
        
        # Try to create second user with same email
        user_data_2 = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "john.doe@example.com",
            "username": "janesmith",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        response = client.post("/users/register", json=user_data_2)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_register_password_mismatch(self, db_session):
        """Test registration with mismatched passwords."""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "username": "johndoe",
            "password": "SecurePass123!",
            "confirm_password": "DifferentPass123!"
        }
        
        response = client.post("/users/register", json=user_data)
        
        assert response.status_code == 422
        assert "match" in response.json()["detail"][0]["msg"].lower()
    
    def test_register_weak_password(self, db_session):
        """Test registration with weak password."""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "username": "johndoe",
            "password": "weak",
            "confirm_password": "weak"
        }
        
        response = client.post("/users/register", json=user_data)
        
        assert response.status_code == 422


class TestUserLogin:
    """Tests for user login endpoint."""
    
    @pytest.fixture
    def registered_user(self, db_session):
        """Create a registered user for testing."""
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "username": "johndoe",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        response = client.post("/users/register", json=user_data)
        return response.json()
    
    def test_login_with_username(self, registered_user):
        """Test login with username."""
        login_data = {
            "username": "johndoe",
            "password": "SecurePass123!"
        }
        
        response = client.post("/users/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == "johndoe"
        assert data["email"] == "john.doe@example.com"
    
    def test_login_with_email(self, registered_user):
        """Test login with email."""
        login_data = {
            "username": "john.doe@example.com",
            "password": "SecurePass123!"
        }
        
        response = client.post("/users/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_login_invalid_credentials(self, registered_user):
        """Test login with invalid credentials."""
        login_data = {
            "username": "johndoe",
            "password": "WrongPassword123!"
        }
        
        response = client.post("/users/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid" in response.json()["detail"]
    
    def test_login_nonexistent_user(self):
        """Test login with nonexistent user."""
        login_data = {
            "username": "nonexistent",
            "password": "SecurePass123!"
        }
        
        response = client.post("/users/login", json=login_data)
        
        assert response.status_code == 401


class TestAuthenticatedUserEndpoints:
    """Tests for authenticated user endpoints."""
    
    @pytest.fixture
    def authenticated_client(self, db_session):
        """Create an authenticated client."""
        # Register user
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "username": "johndoe",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        client.post("/users/register", json=user_data)
        
        # Login
        login_data = {
            "username": "johndoe",
            "password": "SecurePass123!"
        }
        login_response = client.post("/users/login", json=login_data)
        token = login_response.json()["access_token"]
        
        return token, login_response.json()
    
    def test_get_current_user(self, authenticated_client):
        """Test retrieving current user profile."""
        token, login_data = authenticated_client
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "johndoe"
        assert data["email"] == "john.doe@example.com"
    
    def test_get_user_by_id(self, authenticated_client):
        """Test retrieving user by ID."""
        token, login_data = authenticated_client
        user_id = login_data["user_id"]
        
        response = client.get(f"/users/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "johndoe"
    
    def test_update_user_profile(self, authenticated_client):
        """Test updating user profile."""
        token, login_data = authenticated_client
        user_id = login_data["user_id"]
        
        update_data = {
            "first_name": "Jane",
            "last_name": "Smith"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put(f"/users/{user_id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Smith"
    
    def test_change_password(self, authenticated_client):
        """Test changing user password."""
        token, login_data = authenticated_client
        user_id = login_data["user_id"]
        
        password_data = {
            "current_password": "SecurePass123!",
            "new_password": "NewSecurePass123!",
            "confirm_new_password": "NewSecurePass123!"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            f"/users/{user_id}/change-password",
            json=password_data,
            headers=headers
        )
        
        assert response.status_code == 200
        
        # Verify old password doesn't work
        login_data_old = {
            "username": "johndoe",
            "password": "SecurePass123!"
        }
        login_response = client.post("/users/login", json=login_data_old)
        assert login_response.status_code == 401
        
        # Verify new password works
        login_data_new = {
            "username": "johndoe",
            "password": "NewSecurePass123!"
        }
        login_response = client.post("/users/login", json=login_data_new)
        assert login_response.status_code == 200
    
    def test_deactivate_user(self, authenticated_client):
        """Test deactivating user account."""
        token, login_data = authenticated_client
        user_id = login_data["user_id"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(f"/users/{user_id}/deactivate", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
    
    def test_delete_user(self, authenticated_client):
        """Test deleting user account."""
        token, login_data = authenticated_client
        user_id = login_data["user_id"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete(f"/users/{user_id}", headers=headers)
        
        assert response.status_code == 204
        
        # Verify user is deleted
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 404
    
    def test_cannot_update_other_users_profile(self, authenticated_client, db_session):
        """Test that users cannot update other users' profiles."""
        token, login_data = authenticated_client
        
        # Create another user
        other_user_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "username": "janesmith",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        other_user_response = client.post("/users/register", json=other_user_data)
        other_user_id = other_user_response.json()["id"]
        
        # Try to update other user's profile
        update_data = {
            "first_name": "Hacked"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put(f"/users/{other_user_id}", json=update_data, headers=headers)
        
        assert response.status_code == 403
        assert "only update your own" in response.json()["detail"].lower()
