# BREAD Calculation Endpoints - Quick Start Guide

## Overview

This guide provides quick examples for using the BREAD (Browse, Read, Edit, Add, Delete) calculation endpoints.

## Prerequisites

- FastAPI application running (see README.md)
- Valid JWT access token (obtain by registering and logging in)
- cURL or Postman for testing

## Getting Your Access Token

First, register and login to get an access token:

```bash
# 1. Register
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!",
    "confirm_password": "TestPass123!"
  }'

# 2. Login to get token
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }'

# Copy the "access_token" from the response
```

---

## Quick Examples

### 1. Add (Create) a Calculation

**Create an Addition Calculation:**
```bash
curl -X POST http://localhost:8000/calculations \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "add",
    "inputs": {"a": 5, "b": 3}
  }'
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "add",
  "inputs": {"a": 5, "b": 3},
  "result": 8,
  "created_at": "2025-12-13T10:30:00Z",
  "updated_at": "2025-12-13T10:30:00Z"
}
```

**Supported Operations:**
```bash
# Addition
{"type": "add", "inputs": {"a": 5, "b": 3}}        # Result: 8

# Subtraction
{"type": "subtract", "inputs": {"a": 10, "b": 4}}  # Result: 6

# Multiplication
{"type": "multiply", "inputs": {"a": 7, "b": 6}}   # Result: 42

# Division
{"type": "divide", "inputs": {"a": 20, "b": 4}}    # Result: 5.0
```

**Using Python:**
```python
import requests

token = "YOUR_ACCESS_TOKEN_HERE"
headers = {"Authorization": f"Bearer {token}"}

calc_data = {
    "type": "add",
    "inputs": {"a": 5, "b": 3}
}

response = requests.post(
    "http://localhost:8000/calculations",
    json=calc_data,
    headers=headers
)

calculation = response.json()
print(f"Calculation ID: {calculation['id']}")
print(f"Result: {calculation['result']}")  # Output: 8
```

---

### 2. Browse (List) All Calculations

**Using cURL:**
```bash
curl -X GET http://localhost:8000/calculations \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "type": "add",
    "inputs": {"a": 5, "b": 3},
    "result": 8,
    "created_at": "2025-12-13T10:30:00Z",
    "updated_at": "2025-12-13T10:30:00Z"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "type": "multiply",
    "inputs": {"a": 7, "b": 6},
    "result": 42,
    "created_at": "2025-12-13T10:35:00Z",
    "updated_at": "2025-12-13T10:35:00Z"
  }
]
```

**Using Python:**
```python
import requests

token = "YOUR_ACCESS_TOKEN_HERE"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(
    "http://localhost:8000/calculations",
    headers=headers
)

calculations = response.json()
print(f"Total calculations: {len(calculations)}")

for calc in calculations:
    print(f"{calc['type']}: {calc['inputs']} = {calc['result']}")
```

---

### 3. Read (Get) a Specific Calculation

**Using cURL:**
```bash
curl -X GET http://localhost:8000/calculations/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "add",
  "inputs": {"a": 5, "b": 3},
  "result": 8,
  "created_at": "2025-12-13T10:30:00Z",
  "updated_at": "2025-12-13T10:30:00Z"
}
```

**Using Python:**
```python
import requests

token = "YOUR_ACCESS_TOKEN_HERE"
calc_id = "550e8400-e29b-41d4-a716-446655440000"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(
    f"http://localhost:8000/calculations/{calc_id}",
    headers=headers
)

calc = response.json()
print(f"Type: {calc['type']}")
print(f"Inputs: {calc['inputs']}")
print(f"Result: {calc['result']}")
```

---

### 4. Edit (Update) a Calculation

**Update Calculation Inputs:**
```bash
curl -X PUT http://localhost:8000/calculations/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {"a": 20, "b": 5}
  }'
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "add",
  "inputs": {"a": 20, "b": 5},
  "result": 25,
  "created_at": "2025-12-13T10:30:00Z",
  "updated_at": "2025-12-13T10:40:00Z"
}
```

**Using Python:**
```python
import requests

token = "YOUR_ACCESS_TOKEN_HERE"
calc_id = "550e8400-e29b-41d4-a716-446655440000"
headers = {"Authorization": f"Bearer {token}"}

update_data = {
    "inputs": {"a": 100, "b": 50}
}

response = requests.put(
    f"http://localhost:8000/calculations/{calc_id}",
    json=update_data,
    headers=headers
)

updated_calc = response.json()
print(f"New result: {updated_calc['result']}")  # Output: 150
```

---

### 5. Delete a Calculation

**Using cURL:**
```bash
curl -X DELETE http://localhost:8000/calculations/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (204 No Content)**

**Using Python:**
```python
import requests

token = "YOUR_ACCESS_TOKEN_HERE"
calc_id = "550e8400-e29b-41d4-a716-446655440000"
headers = {"Authorization": f"Bearer {token}"}

response = requests.delete(
    f"http://localhost:8000/calculations/{calc_id}",
    headers=headers
)

if response.status_code == 204:
    print("Calculation deleted successfully!")
```

---

## Complete Workflow Example

### Python Script - Full CRUD Workflow

```python
import requests

BASE_URL = "http://localhost:8000"
TOKEN = "YOUR_ACCESS_TOKEN_HERE"
headers = {"Authorization": f"Bearer {TOKEN}"}

print("=== BREAD Calculation Workflow ===\n")

# 1. ADD - Create a new calculation
print("1. ADD: Creating calculation (5 + 3)...")
create_response = requests.post(
    f"{BASE_URL}/calculations",
    json={"type": "add", "inputs": {"a": 5, "b": 3}},
    headers=headers
)
calc = create_response.json()
calc_id = calc["id"]
print(f"   ✓ Created: Result = {calc['result']}")

# 2. BROWSE - List all calculations
print("\n2. BROWSE: Listing all calculations...")
list_response = requests.get(
    f"{BASE_URL}/calculations",
    headers=headers
)
calculations = list_response.json()
print(f"   ✓ Found {len(calculations)} calculation(s)")

# 3. READ - Get specific calculation
print(f"\n3. READ: Getting calculation {calc_id}...")
read_response = requests.get(
    f"{BASE_URL}/calculations/{calc_id}",
    headers=headers
)
calc = read_response.json()
print(f"   ✓ Retrieved: {calc['type']} {calc['inputs']} = {calc['result']}")

# 4. EDIT - Update the calculation
print("\n4. EDIT: Updating inputs to (20 + 5)...")
update_response = requests.put(
    f"{BASE_URL}/calculations/{calc_id}",
    json={"inputs": {"a": 20, "b": 5}},
    headers=headers
)
calc = update_response.json()
print(f"   ✓ Updated: Result = {calc['result']}")

# 5. DELETE - Remove the calculation
print(f"\n5. DELETE: Deleting calculation {calc_id}...")
delete_response = requests.delete(
    f"{BASE_URL}/calculations/{calc_id}",
    headers=headers
)
if delete_response.status_code == 204:
    print("   ✓ Deleted successfully")

print("\n✓ Workflow complete!")
```

---

## Error Handling Examples

### Division by Zero

```bash
curl -X POST http://localhost:8000/calculations \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "divide",
    "inputs": {"a": 10, "b": 0}
  }'

# Response: 400 Bad Request
# Detail: "Cannot divide by zero!"
```

### Invalid Calculation Type

```bash
curl -X POST http://localhost:8000/calculations \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "invalid_op",
    "inputs": {"a": 5, "b": 3}
  }'

# Response: 400 Bad Request
```

### Invalid UUID Format

```bash
curl -X GET http://localhost:8000/calculations/not-a-uuid \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response: 400 Bad Request
# Detail: "Invalid calculation ID format (must be UUID)"
```

### Non-existent Calculation

```bash
curl -X GET http://localhost:8000/calculations/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response: 404 Not Found
# Detail: "Calculation with ID 550e8400-e29b-41d4-a716-446655440000 not found or access denied"
```

### Missing Authentication

```bash
curl -X GET http://localhost:8000/calculations

# Response: 403 Forbidden
# Detail: "Not authenticated"
```

---

## Testing in Swagger UI

1. **Start the application:**
   ```bash
   docker-compose up -d
   ```

2. **Open Swagger UI:**
   - Visit: `http://localhost:8000/docs`

3. **Authorize:**
   - Click the "Authorize" button
   - Paste your JWT access token
   - Click "Authorize"

4. **Test Endpoints:**
   - Expand any calculation endpoint
   - Click "Try it out"
   - Enter request parameters
   - Click "Execute"
   - View response

---

## Running Integration Tests

```bash
# Run all calculation tests
pytest tests/integration/test_calculation_endpoints.py -v

# Run specific test class
pytest tests/integration/test_calculation_endpoints.py::TestCalculationCreate -v

# Run with coverage
pytest tests/integration/test_calculation_endpoints.py --cov=app --cov-report=html

# Run all tests
pytest tests/integration/ -v
```

---

## Calculation Formulas

### Addition
$$\text{result} = a + b$$

### Subtraction
$$\text{result} = a - b$$

### Multiplication
$$\text{result} = a \times b$$

### Division
$$\text{result} = \frac{a}{b}, \quad \text{where } b \neq 0$$

---

## Data Structure

### Calculation Response
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "add",
  "inputs": {"a": 5, "b": 3},
  "result": 8,
  "created_at": "2025-12-13T10:30:00Z",
  "updated_at": "2025-12-13T10:30:00Z"
}
```

**Fields:**
- `id` - Unique identifier (UUID)
- `user_id` - Owner's user ID
- `type` - Calculation type (add, subtract, multiply, divide)
- `inputs` - Input parameters as JSON object
- `result` - Computed result
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

---

## Common Issues & Troubleshooting

### "Could not validate credentials"
- Ensure token is included: `Authorization: Bearer <token>`
- Token may be expired; get a new one by logging in
- Check token is copied exactly from login response

### "Calculation not found"
- Verify the calculation UUID is correct
- Ensure it belongs to your account
- Try listing all calculations to see available IDs

### "Cannot divide by zero"
- Check that divisor (b value) is not 0
- Update inputs and retry

### "Invalid calculation id format"
- Ensure calc_id is a valid UUID
- Format: `550e8400-e29b-41d4-a716-446655440000`

---

## Quick Reference Table

| Operation | Method | Endpoint | Auth | Status |
|-----------|--------|----------|------|--------|
| Add | POST | `/calculations` | Yes | 201 |
| Browse | GET | `/calculations` | Yes | 200 |
| Read | GET | `/calculations/{id}` | Yes | 200 |
| Edit | PUT | `/calculations/{id}` | Yes | 200 |
| Delete | DELETE | `/calculations/{id}` | Yes | 204 |

---

## Next Steps

1. **Read Full Documentation:** [CALCULATION_ENDPOINTS_DOCUMENTATION.md](CALCULATION_ENDPOINTS_DOCUMENTATION.md)
2. **View Implementation Details:** [CALCULATION_IMPLEMENTATION_SUMMARY.md](CALCULATION_IMPLEMENTATION_SUMMARY.md)
3. **Run Tests:** `pytest tests/integration/test_calculation_endpoints.py -v`
4. **Explore Swagger UI:** `http://localhost:8000/docs`

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [HTTP Status Codes](https://httpwg.org/specs/rfc7231.html#status.codes)
- [JWT Documentation](https://tools.ietf.org/html/rfc7519)
