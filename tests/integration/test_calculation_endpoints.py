# tests/integration/test_calculation_endpoints.py

"""
Integration tests for calculation endpoints (BREAD operations).

Tests for:
- Browse (GET /calculations) - List all calculations
- Read (GET /calculations/{id}) - Get specific calculation
- Edit (PUT /calculations/{id}) - Update calculation
- Add (POST /calculations) - Create calculation
- Delete (DELETE /calculations/{id}) - Delete calculation
"""

import pytest
from fastapi.testclient import TestClient
from uuid import UUID
from app.main import app
from app.models.user import User
from app.models.calculation import Calculation

client = TestClient(app)


@pytest.fixture
def authenticated_user(db):
    """Create an authenticated user and login."""
    # Register user
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!"
    }
    response = client.post("/users/register", json=user_data)
    user = response.json()
    
    # Login
    login_data = {
        "username": "testuser",
        "password": "TestPass123!"
    }
    login_response = client.post("/users/login", json=login_data)
    tokens = login_response.json()
    
    return {
        "user": user,
        "token": tokens["access_token"],
        "user_id": UUID(user["id"])
    }


class TestCalculationCreate:
    """Tests for calculation creation (Add)."""
    
    def test_create_add_calculation(self, authenticated_user):
        """Test creating an addition calculation."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        calc_data = {
            "type": "add",
            "inputs": {"a": 5, "b": 3}
        }
        
        response = client.post("/calculations", json=calc_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "add"
        assert data["inputs"] == {"a": 5, "b": 3}
        assert data["result"] == 8
        assert "id" in data
        assert data["user_id"] == str(authenticated_user["user_id"])
    
    def test_create_subtract_calculation(self, authenticated_user):
        """Test creating a subtraction calculation."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        calc_data = {
            "type": "subtract",
            "inputs": {"a": 10, "b": 4}
        }
        
        response = client.post("/calculations", json=calc_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "subtract"
        assert data["result"] == 6
    
    def test_create_multiply_calculation(self, authenticated_user):
        """Test creating a multiplication calculation."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        calc_data = {
            "type": "multiply",
            "inputs": {"a": 7, "b": 6}
        }
        
        response = client.post("/calculations", json=calc_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "multiply"
        assert data["result"] == 42
    
    def test_create_divide_calculation(self, authenticated_user):
        """Test creating a division calculation."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        calc_data = {
            "type": "divide",
            "inputs": {"a": 20, "b": 4}
        }
        
        response = client.post("/calculations", json=calc_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "divide"
        assert data["result"] == 5.0
    
    def test_create_calculation_division_by_zero(self, authenticated_user):
        """Test creating a division calculation with zero divisor."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        calc_data = {
            "type": "divide",
            "inputs": {"a": 10, "b": 0}
        }
        
        response = client.post("/calculations", json=calc_data, headers=headers)
        
        assert response.status_code == 400
        assert "Cannot divide by zero" in response.json()["detail"]
    
    def test_create_calculation_invalid_type(self, authenticated_user):
        """Test creating a calculation with invalid type."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        calc_data = {
            "type": "invalid_op",
            "inputs": {"a": 5, "b": 3}
        }
        
        response = client.post("/calculations", json=calc_data, headers=headers)
        
        assert response.status_code == 400
    
    def test_create_calculation_missing_auth(self):
        """Test creating a calculation without authentication."""
        calc_data = {
            "type": "add",
            "inputs": {"a": 5, "b": 3}
        }
        
        response = client.post("/calculations", json=calc_data)
        
        assert response.status_code == 403


class TestCalculationBrowse:
    """Tests for listing calculations (Browse)."""
    
    def test_list_empty_calculations(self, authenticated_user):
        """Test listing calculations when user has none."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        response = client.get("/calculations", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_list_multiple_calculations(self, authenticated_user):
        """Test listing multiple calculations."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        # Create multiple calculations
        calcs_data = [
            {"type": "add", "inputs": {"a": 5, "b": 3}},
            {"type": "subtract", "inputs": {"a": 10, "b": 4}},
            {"type": "multiply", "inputs": {"a": 7, "b": 6}}
        ]
        
        for calc_data in calcs_data:
            client.post("/calculations", json=calc_data, headers=headers)
        
        # List calculations
        response = client.get("/calculations", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(c["user_id"] == str(authenticated_user["user_id"]) for c in data)
    
    def test_list_calculations_missing_auth(self):
        """Test listing calculations without authentication."""
        response = client.get("/calculations")
        
        assert response.status_code == 403


class TestCalculationRead:
    """Tests for retrieving a specific calculation (Read)."""
    
    @pytest.fixture
    def created_calculation(self, authenticated_user):
        """Create a calculation for testing."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        calc_data = {
            "type": "add",
            "inputs": {"a": 5, "b": 3}
        }
        
        response = client.post("/calculations", json=calc_data, headers=headers)
        return {
            "calc": response.json(),
            "headers": headers,
            "user_token": authenticated_user['token']
        }
    
    def test_read_calculation(self, created_calculation):
        """Test retrieving a specific calculation."""
        calc_id = created_calculation["calc"]["id"]
        headers = created_calculation["headers"]
        
        response = client.get(f"/calculations/{calc_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == calc_id
        assert data["type"] == "add"
        assert data["result"] == 8
    
    def test_read_calculation_invalid_id(self, authenticated_user):
        """Test retrieving a calculation with invalid ID format."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        response = client.get("/calculations/not-a-uuid", headers=headers)
        
        assert response.status_code == 400
    
    def test_read_calculation_not_found(self, authenticated_user):
        """Test retrieving a non-existent calculation."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
        
        response = client.get(f"/calculations/{fake_uuid}", headers=headers)
        
        assert response.status_code == 404
    
    def test_read_other_users_calculation(self, created_calculation, db):
        """Test that users cannot read other users' calculations."""
        # Create another user
        other_user_data = {
            "first_name": "Other",
            "last_name": "User",
            "email": "other@example.com",
            "username": "otheruser",
            "password": "OtherPass123!",
            "confirm_password": "OtherPass123!"
        }
        client.post("/users/register", json=other_user_data)
        
        # Login as other user
        login_data = {
            "username": "otheruser",
            "password": "OtherPass123!"
        }
        login_response = client.post("/users/login", json=login_data)
        other_token = login_response.json()["access_token"]
        
        # Try to read first user's calculation
        calc_id = created_calculation["calc"]["id"]
        headers = {"Authorization": f"Bearer {other_token}"}
        
        response = client.get(f"/calculations/{calc_id}", headers=headers)
        
        assert response.status_code == 404


class TestCalculationEdit:
    """Tests for updating calculations (Edit)."""
    
    @pytest.fixture
    def created_calculation(self, authenticated_user):
        """Create a calculation for testing."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        calc_data = {
            "type": "add",
            "inputs": {"a": 5, "b": 3}
        }
        
        response = client.post("/calculations", json=calc_data, headers=headers)
        return {
            "calc": response.json(),
            "headers": headers
        }
    
    def test_update_calculation_inputs(self, created_calculation):
        """Test updating calculation inputs."""
        calc_id = created_calculation["calc"]["id"]
        headers = created_calculation["headers"]
        
        update_data = {
            "inputs": {"a": 10, "b": 5}
        }
        
        response = client.put(
            f"/calculations/{calc_id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["inputs"] == {"a": 10, "b": 5}
        assert data["result"] == 15
    
    def test_update_calculation_empty_update(self, created_calculation):
        """Test updating calculation with no changes."""
        calc_id = created_calculation["calc"]["id"]
        headers = created_calculation["headers"]
        original_data = created_calculation["calc"]
        
        update_data = {}
        
        response = client.put(
            f"/calculations/{calc_id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == original_data["result"]
    
    def test_update_calculation_invalid_id(self, authenticated_user):
        """Test updating a calculation with invalid ID format."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        update_data = {"inputs": {"a": 10, "b": 5}}
        
        response = client.put(
            "/calculations/not-a-uuid",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 400
    
    def test_update_calculation_not_found(self, authenticated_user):
        """Test updating a non-existent calculation."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
        
        update_data = {"inputs": {"a": 10, "b": 5}}
        
        response = client.put(
            f"/calculations/{fake_uuid}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 404


class TestCalculationDelete:
    """Tests for deleting calculations (Delete)."""
    
    @pytest.fixture
    def created_calculation(self, authenticated_user):
        """Create a calculation for testing."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        calc_data = {
            "type": "add",
            "inputs": {"a": 5, "b": 3}
        }
        
        response = client.post("/calculations", json=calc_data, headers=headers)
        return {
            "calc": response.json(),
            "headers": headers
        }
    
    def test_delete_calculation(self, created_calculation):
        """Test deleting a calculation."""
        calc_id = created_calculation["calc"]["id"]
        headers = created_calculation["headers"]
        
        response = client.delete(f"/calculations/{calc_id}", headers=headers)
        
        assert response.status_code == 204
        
        # Verify deletion
        verify_response = client.get(f"/calculations/{calc_id}", headers=headers)
        assert verify_response.status_code == 404
    
    def test_delete_calculation_invalid_id(self, authenticated_user):
        """Test deleting a calculation with invalid ID format."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        response = client.delete("/calculations/not-a-uuid", headers=headers)
        
        assert response.status_code == 400
    
    def test_delete_calculation_not_found(self, authenticated_user):
        """Test deleting a non-existent calculation."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
        
        response = client.delete(f"/calculations/{fake_uuid}", headers=headers)
        
        assert response.status_code == 404


class TestCalculationWorkflow:
    """Integration tests for complete calculation workflows."""
    
    def test_complete_calculation_workflow(self, authenticated_user):
        """Test a complete workflow: create, read, update, and delete."""
        headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
        
        # 1. Create calculation
        calc_data = {
            "type": "add",
            "inputs": {"a": 5, "b": 3}
        }
        create_response = client.post("/calculations", json=calc_data, headers=headers)
        assert create_response.status_code == 201
        calc_id = create_response.json()["id"]
        
        # 2. Browse calculations
        browse_response = client.get("/calculations", headers=headers)
        assert browse_response.status_code == 200
        assert len(browse_response.json()) >= 1
        
        # 3. Read calculation
        read_response = client.get(f"/calculations/{calc_id}", headers=headers)
        assert read_response.status_code == 200
        assert read_response.json()["result"] == 8
        
        # 4. Update calculation
        update_data = {"inputs": {"a": 20, "b": 5}}
        update_response = client.put(
            f"/calculations/{calc_id}",
            json=update_data,
            headers=headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["result"] == 25
        
        # 5. Delete calculation
        delete_response = client.delete(f"/calculations/{calc_id}", headers=headers)
        assert delete_response.status_code == 204
        
        # 6. Verify deletion
        verify_response = client.get(f"/calculations/{calc_id}", headers=headers)
        assert verify_response.status_code == 404
    
    def test_multiple_users_separate_calculations(self, db):
        """Test that multiple users' calculations are kept separate."""
        headers_list = []
        calc_ids = []
        
        # Create 2 users and calculations
        for i in range(2):
            user_data = {
                "first_name": f"User{i}",
                "last_name": "Test",
                "email": f"user{i}@example.com",
                "username": f"user{i}",
                "password": "TestPass123!",
                "confirm_password": "TestPass123!"
            }
            client.post("/users/register", json=user_data)
            
            login_response = client.post("/users/login", json={
                "username": f"user{i}",
                "password": "TestPass123!"
            })
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            headers_list.append(headers)
            
            # Create calculation
            calc_response = client.post("/calculations", json={
                "type": "add",
                "inputs": {"a": i+1, "b": i+1}
            }, headers=headers)
            calc_ids.append(calc_response.json()["id"])
        
        # Verify each user only sees their own calculations
        for i, headers in enumerate(headers_list):
            list_response = client.get("/calculations", headers=headers)
            calcs = list_response.json()
            assert len(calcs) == 1
            assert calcs[0]["id"] == calc_ids[i]
