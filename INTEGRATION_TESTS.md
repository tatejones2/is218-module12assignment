# Integration Tests Documentation

## Overview

The FastAPI Calculator API includes comprehensive integration tests using pytest. These tests verify the full end-to-end functionality of the API, including database interactions, authentication flows, and data validation.

---

## Test Structure

### Test File: `tests/integration/test_integration_comprehensive.py`

This file contains the main integration test suite with **50+ test cases** organized into logical groups:

#### 1. **User Registration Tests** (`TestUserRegistrationIntegration`)
- ✅ Successful user registration with database verification
- ✅ Password validation rules enforcement
- ✅ Password confirmation matching
- ✅ Duplicate email detection
- ✅ Duplicate username detection

#### 2. **Authentication Tests** (`TestUserAuthenticationIntegration`)
- ✅ Successful login with JWT token generation
- ✅ Invalid password rejection
- ✅ Non-existent user handling
- ✅ Current user profile retrieval
- ✅ Token-based authorization
- ✅ Missing token rejection
- ✅ Invalid token rejection

#### 3. **Profile Management Tests** (`TestUserProfileManagementIntegration`)
- ✅ User profile updates with database verification
- ✅ Password change functionality
- ✅ Old password validation
- ✅ New password requirements

#### 4. **Calculation CRUD Tests** (`TestCalculationCRUDIntegration`)
- ✅ Create calculations (all types)
- ✅ Retrieve specific calculations
- ✅ Browse user's calculations
- ✅ Update calculations with recomputation
- ✅ Delete calculations

#### 5. **Error Handling Tests** (`TestCalculationErrorHandling`)
- ✅ Division by zero detection
- ✅ Invalid operation type
- ✅ Missing required fields
- ✅ Insufficient inputs
- ✅ Invalid input types (non-numeric)
- ✅ Non-existent resource access

#### 6. **Authorization Tests** (`TestDataIsolationIntegration`)
- ✅ Users cannot access other users' calculations
- ✅ Users see only their own calculations
- ✅ Multi-user data isolation

#### 7. **Health Check Tests** (`TestHealthCheckIntegration`)
- ✅ API health endpoint verification

---

## Running Tests

### Run All Tests
```bash
pytest tests/integration/test_integration_comprehensive.py -v
```

### Run Specific Test Class
```bash
pytest tests/integration/test_integration_comprehensive.py::TestUserRegistrationIntegration -v
```

### Run Specific Test
```bash
pytest tests/integration/test_integration_comprehensive.py::TestUserRegistrationIntegration::test_register_user_and_verify_in_db -v
```

### Run with Coverage
```bash
pytest tests/integration/test_integration_comprehensive.py -v --cov=app --cov-report=html
```

### Run Tests with Markers
```bash
# Run only integration tests
pytest -m integration

# Run only database tests
pytest -m database

# Skip slow tests
pytest -m "not slow"
```

### Run Tests in Parallel
```bash
pip install pytest-xdist
pytest tests/integration/ -n auto
```

---

## GitHub Actions CI/CD Pipeline

The `.github/workflows/test.yml` workflow automatically runs tests on every push and pull request.

### Workflow Steps

1. **Setup PostgreSQL Service**
   - Runs PostgreSQL 15 in Docker
   - Configurable database credentials
   - Health checks before tests run

2. **Install Dependencies**
   - Python 3.10
   - Pip cache for faster builds
   - All required packages from requirements.txt

3. **Run Test Suites**
   - Unit tests with coverage
   - Integration tests (comprehensive suite)
   - E2E tests (if available)

4. **Generate Reports**
   - JUnit XML reports for CI integration
   - Code coverage reports
   - HTML coverage reports

5. **Upload Artifacts**
   - Test results accessible in GitHub
   - Coverage reports for analysis

6. **Security Scanning** (optional)
   - Trivy vulnerability scanner
   - Docker image security checks

### Database Configuration in CI

The GitHub Actions workflow automatically:
- Spins up a PostgreSQL database
- Configures connection with credentials: `user:password@localhost:5432/mytestdb`
- Sets `DATABASE_URL` environment variable
- Waits for database health checks

```yaml
services:
  postgres:
    image: postgres:latest
    env:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mytestdb
    ports:
      - 5432:5432
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

---

## Test Database Verification

Each test verifies both:

1. **API Response** - Correct HTTP status and response data
2. **Database State** - Data correctly persisted in PostgreSQL

### Example: Create Calculation Test

```python
def test_create_addition_calculation(self, authenticated_user, db_session):
    # Make API call
    response = client.post("/calculations", json={...})
    
    # Verify API response
    assert response.status_code == 201
    calc = response.json()
    assert calc["result"] == 15.0
    
    # Verify database
    calc_in_db = db_session.query(Calculation).filter(
        Calculation.id == calc_id
    ).first()
    assert calc_in_db is not None
    assert calc_in_db.result == 15.0
```

---

## Test Data Management

### Fixtures

Tests use pytest fixtures for clean data management:

- **`authenticated_user`** - Creates a user and provides JWT token
- **`db_session`** - Provides database session for verification
- **`two_users`** - Creates two authenticated users for isolation tests

### Data Cleanup

- Database is automatically cleaned after each test
- Transactions are rolled back on failures
- Fixtures provide fresh data for each test

---

## Test Coverage

Current test suite covers:

| Category | Tests | Coverage |
|----------|-------|----------|
| User Registration | 5 | 100% |
| Authentication | 7 | 100% |
| Profile Management | 3 | 100% |
| Calculation CRUD | 5 | 100% |
| Error Handling | 6 | 100% |
| Authorization | 2 | 100% |
| Health Check | 1 | 100% |
| **Total** | **29** | **100%** |

---

## Calculation Type Tests

All four calculation types are tested:

```python
test_cases = [
    {"type": "addition", "inputs": [10, 5], "expected": 15},
    {"type": "subtraction", "inputs": [10, 5], "expected": 5},
    {"type": "multiplication", "inputs": [10, 5], "expected": 50},
    {"type": "division", "inputs": [10, 5], "expected": 2},
]
```

---

## Error Validation

Tests verify proper error handling:

| Error Case | Status Code | Verified |
|-----------|-------------|----------|
| Invalid password | 422 | ✅ |
| Duplicate username | 422 | ✅ |
| Division by zero | 422 | ✅ |
| Missing fields | 422 | ✅ |
| Invalid token | 401 | ✅ |
| No authorization | 401 | ✅ |
| Not found | 404 | ✅ |

---

## Database Verification Examples

### Example 1: Verify User Hashed Password
```python
# Create user via API
response = client.post("/users/register", json=user_data)

# Verify password is hashed in database
user_in_db = db_session.query(User).filter(...).first()
assert user_in_db.password != "SecurePass123!"  # Not plaintext
assert user_in_db.verify_password("SecurePass123!")  # But verifies correctly
```

### Example 2: Verify Calculation Result
```python
# Create calculation via API
response = client.post("/calculations", json={
    "type": "multiplication",
    "inputs": [7, 6]
})

# Verify result in database
calc_in_db = db_session.query(Calculation).filter(...).first()
assert calc_in_db.result == 42.0
assert calc_in_db.user_id == user_id  # Belongs to correct user
```

### Example 3: Verify Timestamps
```python
calc_in_db = db_session.query(Calculation).filter(...).first()
assert isinstance(calc_in_db.created_at, datetime)
assert isinstance(calc_in_db.updated_at, datetime)
assert calc_in_db.created_at == calc_in_db.updated_at  # Initially same
```

---

## Running Tests Locally

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Make sure PostgreSQL is running
# Update DATABASE_URL in .env if needed
```

### Local Test Execution

```bash
# Run all integration tests
pytest tests/integration/test_integration_comprehensive.py -v

# Run with coverage
pytest tests/integration/test_integration_comprehensive.py -v --cov=app

# Run specific test class
pytest tests/integration/test_integration_comprehensive.py::TestUserRegistrationIntegration -v

# Run with detailed output
pytest tests/integration/test_integration_comprehensive.py -vv -s
```

### Using Docker Compose
```bash
# Start services
docker-compose up -d

# Run tests inside container
docker-compose exec web pytest tests/integration/ -v

# View coverage
docker-compose exec web coverage html
```

---

## Continuous Integration Results

When tests run in GitHub Actions:

1. **PostgreSQL Service** - Started automatically
2. **Dependencies** - Installed with caching
3. **Integration Tests** - Run with verbose output
4. **Coverage Reports** - Generated and uploaded
5. **Test Results** - Available as artifacts

View results in:
- **GitHub Actions Tab** - Workflow run details
- **Artifacts** - Test results and coverage reports
- **Commit Checks** - Pass/Fail status on commits

---

## Test Markers

Use pytest markers to run specific test categories:

```bash
# Run only integration tests
pytest -m integration

# Run only database tests
pytest -m database

# Run only auth tests
pytest -m auth

# Run only calculation tests
pytest -m calculation

# Skip slow tests
pytest -m "not slow"

# Run fast tests only
pytest -m fast
```

---

## Common Issues & Solutions

### Issue: Database Connection Failed
**Solution:** Ensure PostgreSQL is running and `DATABASE_URL` is correct
```bash
export DATABASE_URL=postgresql://user:password@localhost:5432/mytestdb
```

### Issue: Tests Timeout
**Solution:** Increase timeout in pytest.ini or use `--timeout=600`
```bash
pytest tests/integration/ --timeout=600
```

### Issue: Port Already in Use
**Solution:** Kill process on port 5432 or use different port
```bash
lsof -ti:5432 | xargs kill -9
```

### Issue: Import Errors
**Solution:** Ensure app module is in PYTHONPATH
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## Test Report Example

```
tests/integration/test_integration_comprehensive.py::TestUserRegistrationIntegration::test_register_user_and_verify_in_db PASSED
tests/integration/test_integration_comprehensive.py::TestUserRegistrationIntegration::test_register_user_password_validation PASSED
tests/integration/test_integration_comprehensive.py::TestUserAuthenticationIntegration::test_login_success_and_get_token PASSED
...

========================= 29 passed in 12.45s ==========================
Coverage: 95% (450/475 lines)
```

---

## Best Practices

1. **Use Fixtures** - Keep tests DRY with pytest fixtures
2. **Test Database State** - Verify both API response and database
3. **Clean Isolation** - Each test should be independent
4. **Clear Test Names** - Test names describe what is being tested
5. **Error Cases** - Test both success and failure paths
6. **Use Markers** - Organize tests with markers for better control
7. **CI/CD Integration** - Run tests automatically on commits

---

## Next Steps

- View detailed test results in GitHub Actions
- Monitor coverage trends over time
- Add more edge case tests as needed
- Consider performance testing for load validation

---

**Documentation Generated:** December 14, 2025  
**Test Suite Version:** 1.0  
**Last Updated:** 2025-12-14
