"""
Comprehensive Integration Tests for FastAPI Calculator API

Tests include:
- User registration and authentication
- Database verification
- Calculation CRUD operations
- Error handling and validation
- Authorization and data isolation
"""

import pytest
import time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.main import app
from app.database import get_db
from app.models.user import User
from app.models.calculation import Calculation
from app.schemas.calculation import CalculationType


client = TestClient(app)


def get_unique_email():
    """Generate a unique email for testing."""
    return f"test{int(time.time() * 1000000)}@example.com"


def get_unique_username():
    """Generate a unique username for testing."""
    return f"user{int(time.time() * 1000000)}"


# ============================================================================
# USER INTEGRATION TESTS
# ============================================================================

class TestUserRegistrationIntegration:
    """Integration tests for user registration."""
    
    def test_register_user_and_verify_in_db(self, db_session: Session):
        """Test registration and verify user is correctly stored in database."""
        # Register user
        user_data = {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": get_unique_email(),
            "username": get_unique_username(),
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        
        response = client.post("/users/register", json=user_data)
        
        # Verify response
        assert response.status_code == 201
        response_data = response.json()
        user_id = response_data["id"]
        
        # Verify in database
        user_in_db = db_session.query(User).filter(User.id == user_id).first()
        assert user_in_db is not None
        assert user_in_db.username == user_data["username"]
        assert user_in_db.email == user_data["email"]
        assert user_in_db.first_name == "Alice"
        assert user_in_db.last_name == "Smith"
        assert user_in_db.is_active is True
        assert user_in_db.is_verified is False
        
        # Verify password is hashed (not stored in plain text)
        assert user_in_db.password != "SecurePass123!"
        
        # Verify timestamps exist
        assert isinstance(user_in_db.created_at, datetime)
        assert isinstance(user_in_db.updated_at, datetime)
    
    def test_register_user_password_validation(self):
        """Test registration fails with weak password."""
        user_data = {
            "first_name": "Bob",
            "last_name": "Jones",
            "email": get_unique_email(),
            "username": get_unique_username(),
            "password": "weak",
            "confirm_password": "weak"
        }
        
        response = client.post("/users/register", json=user_data)
        
        # Should fail with 422 (validation error)
        assert response.status_code == 422
        assert "error" in response.json() or "detail" in response.json()
    
    def test_register_user_password_mismatch(self):
        """Test registration fails when passwords don't match."""
        user_data = {
            "first_name": "Carol",
            "last_name": "Davis",
            "email": get_unique_email(),
            "username": get_unique_username(),
            "password": "SecurePass123!",
            "confirm_password": "DifferentPass123!"
        }
        
        response = client.post("/users/register", json=user_data)
        
        # Should fail with 422
        assert response.status_code == 422
    
    def test_register_duplicate_email(self, db_session: Session):
        """Test registration fails with duplicate email."""
        # Register first user
        email = get_unique_email()
        user_data_1 = {
            "first_name": "David",
            "last_name": "Wilson",
            "email": email,
            "username": get_unique_username(),
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        client.post("/users/register", json=user_data_1)
        
        # Try to register second user with same email
        user_data_2 = {
            "first_name": "David",
            "last_name": "Miller",
            "email": email,
            "username": get_unique_username(),
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        
        response = client.post("/users/register", json=user_data_2)
        
        # Should be 400 (Bad Request) or 422 (Unprocessable Entity)
        assert response.status_code in [400, 422]
        detail = str(response.json().get("detail", "")).lower()
        assert "already exists" in detail or "duplicate" in detail
    
    def test_register_duplicate_username(self, db_session: Session):
        """Test registration fails with duplicate username."""
        # Register first user
        username = get_unique_username()
        user_data_1 = {
            "first_name": "Eve",
            "last_name": "Taylor",
            "email": get_unique_email(),
            "username": username,
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        client.post("/users/register", json=user_data_1)
        
        # Try to register second user with same username
        user_data_2 = {
            "first_name": "Eve",
            "last_name": "Brown",
            "email": get_unique_email(),
            "username": username,
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        
        response = client.post("/users/register", json=user_data_2)
        
        # Should be 400 (Bad Request) or 422 (Unprocessable Entity)
        assert response.status_code in [400, 422]
        detail = str(response.json().get("detail", "")).lower()
        assert "already exists" in detail or "duplicate" in detail


class TestUserAuthenticationIntegration:
    """Integration tests for user authentication."""
    
    def test_login_success_and_get_token(self, db_session: Session):
        """Test successful login and token retrieval."""
        # Register user
        user_data = {
            "first_name": "Frank",
            "last_name": "Miller",
            "email": "frank@example.com",
            "username": "frankmiller",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        register_response = client.post("/users/register", json=user_data)
        user_id = register_response.json()["id"]
        
        # Login
        login_data = {
            "username": "frankmiller",
            "password": "SecurePass123!"
        }
        
        response = client.post("/users/login", json=login_data)
        
        # Verify response
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert "token_type" in token_data
        assert token_data["token_type"] == "bearer"
        
        # Verify JWT token format (3 parts separated by dots)
        token = token_data["access_token"]
        assert len(token.split(".")) == 3
        
        # Verify last_login is updated in database
        user_in_db = db_session.query(User).filter(User.id == user_id).first()
        assert user_in_db.last_login is not None
    
    def test_login_with_wrong_password(self, db_session: Session):
        """Test login fails with wrong password."""
        # Register user
        user_data = {
            "first_name": "Grace",
            "last_name": "Lee",
            "email": "grace@example.com",
            "username": "gracelee",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        client.post("/users/register", json=user_data)
        
        # Try to login with wrong password
        login_data = {
            "username": "gracelee",
            "password": "WrongPassword123!"
        }
        
        response = client.post("/users/login", json=login_data)
        
        # Should be 401 (Unauthorized)
        assert response.status_code == 401
        detail = str(response.json().get("detail", "")).lower()
        assert "invalid" in detail or "unauthorized" in detail
    
    def test_login_with_nonexistent_user(self):
        """Test login fails for non-existent user."""
        login_data = {
            "username": "nonexistent",
            "password": "SomePass123!"
        }
        
        response = client.post("/users/login", json=login_data)
        
        assert response.status_code == 401
    
    def test_get_current_user_with_valid_token(self, db_session: Session):
        """Test getting current user profile with valid token."""
        # Register and login user
        user_data = {
            "first_name": "Henry",
            "last_name": "Clark",
            "email": "henry@example.com",
            "username": "henryc",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        client.post("/users/register", json=user_data)
        
        login_response = client.post("/users/login", json={
            "username": "henryc",
            "password": "SecurePass123!"
        })
        token = login_response.json()["access_token"]
        
        # Get current user
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        user_profile = response.json()
        assert user_profile["username"] == "henryc"
        assert user_profile["email"] == "henry@example.com"
        assert user_profile["first_name"] == "Henry"
        assert user_profile["last_name"] == "Clark"
    
    def test_get_current_user_without_token(self):
        """Test getting current user fails without token."""
        response = client.get("/users/me")
        
        assert response.status_code == 401
    
    def test_get_current_user_with_invalid_token(self):
        """Test getting current user fails with invalid token."""
        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401


class TestUserProfileManagementIntegration:
    """Integration tests for user profile management."""
    
    @pytest.fixture
    def authenticated_user(self, db_session: Session):
        """Create and authenticate a user."""
        unique_username = get_unique_username()
        user_data = {
            "first_name": "Iris",
            "last_name": "Jones",
            "email": get_unique_email(),
            "username": unique_username,
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        register_response = client.post("/users/register", json=user_data)
        user_id = register_response.json()["id"]
        
        login_response = client.post("/users/login", json={
            "username": unique_username,
            "password": "SecurePass123!"
        })
        token = login_response.json()["access_token"]
        
        return user_id, token, unique_username
    
    def test_update_user_profile(self, authenticated_user, db_session: Session):
        """Test updating user profile."""
        user_id, token, _ = authenticated_user
        
        update_data = {
            "first_name": "Iris",
            "last_name": "Smith"
        }
        
        response = client.put(
            f"/users/{user_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["last_name"] == "Smith"
        
        # Verify in database
        user_in_db = db_session.query(User).filter(User.id == user_id).first()
        assert user_in_db.last_name == "Smith"
        assert user_in_db.updated_at is not None
    
    def test_change_password(self, authenticated_user, db_session: Session):
        """Test changing user password."""
        user_id, token, username = authenticated_user
        
        password_data = {
            "current_password": "SecurePass123!",
            "new_password": "NewSecurePass456!",
            "confirm_new_password": "NewSecurePass456!"
        }
        
        response = client.post(
            f"/users/{user_id}/change-password",
            json=password_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        
        # Verify old password no longer works
        old_login = client.post("/users/login", json={
            "username": username,
            "password": "SecurePass123!"
        })
        assert old_login.status_code == 401
        
        # Verify new password works
        new_login = client.post("/users/login", json={
            "username": username,
            "password": "NewSecurePass456!"
        })
        assert new_login.status_code == 200


# ============================================================================
# CALCULATION INTEGRATION TESTS
# ============================================================================

class TestCalculationCRUDIntegration:
    """Integration tests for calculation CRUD operations."""
    
    @pytest.fixture
    def authenticated_user(self, db_session: Session):
        """Create and authenticate a user for calculation tests."""
        unique_username = get_unique_username()
        user_data = {
            "first_name": "Jack",
            "last_name": "Ryan",
            "email": get_unique_email(),
            "username": unique_username,
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        register_response = client.post("/users/register", json=user_data)
        user_id = register_response.json()["id"]
        
        login_response = client.post("/users/login", json={
            "username": unique_username,
            "password": "SecurePass123!"
        })
        token = login_response.json()["access_token"]
        
        return user_id, token
    
    def test_create_addition_calculation(self, authenticated_user, db_session: Session):
        """Test creating an addition calculation."""
        user_id, token = authenticated_user
        
        calc_data = {
            "type": "addition",
            "inputs": [10, 5]
        }
        
        response = client.post(
            "/calculations",
            json=calc_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        calc = response.json()
        assert calc["type"] == "addition"
        assert calc["inputs"] == [10.0, 5.0]
        # Addition result should be 15.0
        assert calc["result"] == 15.0
        assert str(calc["user_id"]) == str(user_id)
        
        # Verify in database
        calc_id = calc["id"]
        calc_in_db = db_session.query(Calculation).filter(
            Calculation.id == calc_id
        ).first()
        assert calc_in_db is not None
        assert str(calc_in_db.user_id) == str(user_id)
        assert calc_in_db.result == 15.0
    
    def test_create_all_calculation_types(self, authenticated_user, db_session: Session):
        """Test creating calculations for all operation types."""
        user_id, token = authenticated_user
        
        test_cases = [
            {"type": "addition", "inputs": [10, 5], "expected": 15},
            {"type": "subtraction", "inputs": [10, 5], "expected": 5},
            {"type": "multiplication", "inputs": [10, 5], "expected": 50},
            {"type": "division", "inputs": [10, 5], "expected": 2},
        ]
        
        for test_case in test_cases:
            response = client.post(
                "/calculations",
                json={"type": test_case["type"], "inputs": test_case["inputs"]},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 201
            calc = response.json()
            assert calc["result"] == test_case["expected"]
    
    def test_read_calculation(self, authenticated_user, db_session: Session):
        """Test retrieving a specific calculation."""
        user_id, token = authenticated_user
        
        # Create calculation
        create_response = client.post(
            "/calculations",
            json={"type": "addition", "inputs": [20, 8]},
            headers={"Authorization": f"Bearer {token}"}
        )
        calc_id = create_response.json()["id"]
        
        # Retrieve calculation
        response = client.get(
            f"/calculations/{calc_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        calc = response.json()
        assert calc["id"] == calc_id
        assert calc["type"] == "addition"
        assert calc["result"] == 28.0
    
    def test_browse_calculations(self, authenticated_user, db_session: Session):
        """Test listing user's calculations."""
        user_id, token = authenticated_user
        
        # Create multiple calculations
        for i in range(3):
            client.post(
                "/calculations",
                json={"type": "addition", "inputs": [i, 1]},
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # Browse calculations
        response = client.get(
            "/calculations",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        calcs = response.json()
        assert len(calcs) == 3
        
        # Verify all belong to user
        for calc in calcs:
            assert str(calc["user_id"]) == str(user_id)
    
    def test_update_calculation(self, authenticated_user, db_session: Session):
        """Test updating a calculation."""
        user_id, token = authenticated_user
        
        # Create calculation
        create_response = client.post(
            "/calculations",
            json={"type": "addition", "inputs": [10, 5]},
            headers={"Authorization": f"Bearer {token}"}
        )
        calc_id = create_response.json()["id"]
        original_created_at = create_response.json()["created_at"]
        
        # Update calculation
        update_data = {"inputs": [20, 10]}
        response = client.put(
            f"/calculations/{calc_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        updated_calc = response.json()
        assert updated_calc["inputs"] == [20.0, 10.0]
        assert updated_calc["result"] == 30.0
        assert updated_calc["created_at"] == original_created_at
        
        # Verify in database
        calc_in_db = db_session.query(Calculation).filter(
            Calculation.id == calc_id
        ).first()
        assert calc_in_db.result == 30.0
    
    def test_delete_calculation(self, authenticated_user, db_session: Session):
        """Test deleting a calculation."""
        user_id, token = authenticated_user
        
        # Create calculation
        create_response = client.post(
            "/calculations",
            json={"type": "addition", "inputs": [10, 5]},
            headers={"Authorization": f"Bearer {token}"}
        )
        calc_id = create_response.json()["id"]
        
        # Delete calculation
        response = client.delete(
            f"/calculations/{calc_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 204
        
        # Verify deleted from database
        calc_in_db = db_session.query(Calculation).filter(
            Calculation.id == calc_id
        ).first()
        assert calc_in_db is None
        
        # Verify get returns 404
        get_response = client.get(
            f"/calculations/{calc_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 404


# ============================================================================
# CALCULATION ERROR HANDLING TESTS
# ============================================================================

class TestCalculationErrorHandling:
    """Integration tests for calculation error handling."""
    
    @pytest.fixture
    def authenticated_user(self, db_session: Session):
        """Create and authenticate a user."""
        unique_username = get_unique_username()
        user_data = {
            "first_name": "Karen",
            "last_name": "White",
            "email": get_unique_email(),
            "username": unique_username,
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        register_response = client.post("/users/register", json=user_data)
        user_id = register_response.json()["id"]
        
        login_response = client.post("/users/login", json={
            "username": unique_username,
            "password": "SecurePass123!"
        })
        token = login_response.json()["access_token"]
        
        return user_id, token
    
    def test_division_by_zero_error(self, authenticated_user):
        """Test division by zero returns proper error."""
        user_id, token = authenticated_user
        
        response = client.post(
            "/calculations",
            json={"type": "division", "inputs": [10, 0]},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
        assert "zero" in str(error_data["detail"]).lower()
    
    def test_invalid_calculation_type(self, authenticated_user):
        """Test invalid calculation type returns error."""
        user_id, token = authenticated_user
        
        response = client.post(
            "/calculations",
            json={"type": "invalid_op", "inputs": [10, 5]},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self, authenticated_user):
        """Test missing required fields returns validation error."""
        user_id, token = authenticated_user
        
        # Missing inputs
        response = client.post(
            "/calculations",
            json={"type": "addition"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 422
        
        # Missing type
        response = client.post(
            "/calculations",
            json={"inputs": [10, 5]},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 422
    
    def test_insufficient_inputs(self, authenticated_user):
        """Test calculation with insufficient inputs returns error."""
        user_id, token = authenticated_user
        
        response = client.post(
            "/calculations",
            json={"type": "addition", "inputs": [10]},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422
    
    def test_invalid_input_types(self, authenticated_user):
        """Test non-numeric inputs return validation error."""
        user_id, token = authenticated_user
        
        response = client.post(
            "/calculations",
            json={"type": "addition", "inputs": ["ten", "five"]},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422
    
    def test_get_nonexistent_calculation(self, authenticated_user):
        """Test getting non-existent calculation returns 404."""
        user_id, token = authenticated_user
        
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(
            f"/calculations/{fake_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
    
    def test_delete_nonexistent_calculation(self, authenticated_user):
        """Test deleting non-existent calculation returns 404."""
        user_id, token = authenticated_user
        
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(
            f"/calculations/{fake_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404


# ============================================================================
# AUTHORIZATION AND DATA ISOLATION TESTS
# ============================================================================

class TestDataIsolationIntegration:
    """Integration tests for data isolation and authorization."""
    
    @pytest.fixture
    def two_users(self, db_session: Session):
        """Create two authenticated users."""
        users = []
        
        for i, name in enumerate(["Leon", "Monica"]):
            unique_username = get_unique_username()
            user_data = {
                "first_name": name,
                "last_name": "Test",
                "email": get_unique_email(),
                "username": unique_username,
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!"
            }
            register_response = client.post("/users/register", json=user_data)
            user_id = register_response.json()["id"]
            
            login_response = client.post("/users/login", json={
                "username": unique_username,
                "password": "SecurePass123!"
            })
            token = login_response.json()["access_token"]
            
            users.append({"id": user_id, "token": token, "name": name})
        
        return users
    
    def test_user_cannot_access_other_users_calculations(self, two_users, db_session: Session):
        """Test that users cannot access other users' calculations."""
        user1, user2 = two_users
        
        # User1 creates a calculation
        response = client.post(
            "/calculations",
            json={"type": "addition", "inputs": [100, 50]},
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        calc_id = response.json()["id"]
        
        # User2 tries to access user1's calculation
        response = client.get(
            f"/calculations/{calc_id}",
            headers={"Authorization": f"Bearer {user2['token']}"}
        )
        
        # Should not be able to access
        assert response.status_code == 404
    
    def test_user_can_only_see_own_calculations(self, two_users, db_session: Session):
        """Test that users only see their own calculations."""
        user1, user2 = two_users
        
        # User1 creates 3 calculations
        for i in range(3):
            client.post(
                "/calculations",
                json={"type": "addition", "inputs": [i, 1]},
                headers={"Authorization": f"Bearer {user1['token']}"}
            )
        
        # User2 creates 2 calculations
        for i in range(2):
            client.post(
                "/calculations",
                json={"type": "subtraction", "inputs": [i, 1]},
                headers={"Authorization": f"Bearer {user2['token']}"}
            )
        
        # User1 lists calculations
        response = client.get(
            "/calculations",
            headers={"Authorization": f"Bearer {user1['token']}"}
        )
        user1_calcs = response.json()
        
        # User2 lists calculations
        response = client.get(
            "/calculations",
            headers={"Authorization": f"Bearer {user2['token']}"}
        )
        user2_calcs = response.json()
        
        # Verify counts
        assert len(user1_calcs) == 3
        assert len(user2_calcs) == 2
        
        # Verify types
        assert all(c["type"] == "addition" for c in user1_calcs)
        assert all(c["type"] == "subtraction" for c in user2_calcs)


# ============================================================================
# HEALTH CHECK TEST
# ============================================================================

class TestHealthCheckIntegration:
    """Integration test for health check endpoint."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
