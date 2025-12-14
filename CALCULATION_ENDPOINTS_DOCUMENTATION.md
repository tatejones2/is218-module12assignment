# Calculation Endpoints Implementation

## Overview

This document describes the implementation of BREAD (Browse, Read, Edit, Add, Delete) calculation endpoints for the FastAPI Calculator application.

## Architecture

### Components

#### 1. **Calculation Operations Module** (`app/operations/calculations.py`)

New module containing the `CalculationOperations` class with static methods for all calculation-related database operations:

- `create_calculation()` - Create and compute a new calculation
- `list_user_calculations()` - Get all calculations for a user
- `get_calculation_by_id()` - Retrieve a specific calculation
- `update_calculation()` - Update calculation inputs and result
- `delete_calculation()` - Delete a calculation
- `get_calculation_count()` - Count user's calculations
- `get_calculation_by_type()` - Filter calculations by type
- `clear_user_calculations()` - Delete all user's calculations

#### 2. **Enhanced Main Application** (`app/main.py`)

Updated FastAPI application with well-documented BREAD endpoints:

- All endpoints use `CalculationOperations` for business logic
- Comprehensive error handling
- Full docstrings with examples
- Type hints and validation

---

## API Endpoints

### BREAD Operations

#### 1. Add (Create) Calculation
**POST** `/calculations`

Creates and computes a new calculation for the authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "type": "add",
  "inputs": {"a": 5, "b": 3}
}
```

**Response:** `201 Created`
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

**Supported Calculation Types:**
- `add` - Addition: $a + b$
- `subtract` - Subtraction: $a - b$
- `multiply` - Multiplication: $a \times b$
- `divide` - Division: $\frac{a}{b}$ (raises error if $b = 0$)

**Error Responses:**
- `400 Bad Request` - Invalid calculation type, missing inputs, division by zero
- `401 Unauthorized` - Missing or invalid token
- `422 Unprocessable Entity` - Invalid request body

---

#### 2. Browse (List) Calculations
**GET** `/calculations`

Lists all calculations created by the authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
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

**Query Parameters:**
- None currently, but extensible for filtering (by type, date range, etc.)

**Error Responses:**
- `401 Unauthorized` - Missing or invalid token

**Notes:**
- Returns empty list if user has no calculations
- Only returns calculations owned by the authenticated user

---

#### 3. Read (Get) a Specific Calculation
**GET** `/calculations/{calc_id}`

Retrieves a specific calculation by its UUID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Parameters:**
- `calc_id` (path): Calculation's UUID

**Response:** `200 OK`
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

**Error Responses:**
- `400 Bad Request` - Invalid UUID format
- `401 Unauthorized` - Missing or invalid token
- `404 Not Found` - Calculation not found or user is not the owner

---

#### 4. Edit (Update) a Calculation
**PUT** `/calculations/{calc_id}`

Updates a calculation's inputs and recomputes the result.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Parameters:**
- `calc_id` (path): Calculation's UUID

**Request Body:**
```json
{
  "inputs": {"a": 20, "b": 5}
}
```

**Response:** `200 OK`
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

**Error Responses:**
- `400 Bad Request` - Invalid UUID format, invalid inputs, computation error (e.g., division by zero)
- `401 Unauthorized` - Missing or invalid token
- `404 Not Found` - Calculation not found or user is not the owner

**Notes:**
- `updated_at` timestamp is automatically refreshed
- Result is automatically recomputed when inputs change
- Type cannot be changed via update endpoint

---

#### 5. Delete a Calculation
**DELETE** `/calculations/{calc_id}`

Permanently deletes a calculation.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Parameters:**
- `calc_id` (path): Calculation's UUID

**Response:** `204 No Content`

**Error Responses:**
- `400 Bad Request` - Invalid UUID format
- `401 Unauthorized` - Missing or invalid token
- `404 Not Found` - Calculation not found or user is not the owner

**Notes:**
- This action cannot be undone
- User can only delete their own calculations

---

## Security Features

### Authentication
- All endpoints require valid JWT access token
- Token must be passed in `Authorization: Bearer <token>` header
- Token is verified on every request

### Authorization
- Users can only access and modify their own calculations
- Endpoints check that `user_id` from token matches calculation owner
- Returns `404 Not Found` if user attempts unauthorized access

### Input Validation
- Calculation type must be valid (add, subtract, multiply, divide)
- Inputs must be valid numeric values
- Division by zero is explicitly handled and rejected

### Data Isolation
- Database queries filtered by user ID
- User cannot see other users' calculations
- Cascading delete ensures data consistency

---

## Database Schema

### Calculation Table
```sql
CREATE TABLE calculations (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL FOREIGN KEY REFERENCES users(id),
    type VARCHAR(50) NOT NULL,
    inputs JSONB NOT NULL,
    result FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIMEZONE,
    updated_at TIMESTAMP WITH TIMEZONE
);
```

### Indexes
- Primary key on `id`
- Foreign key on `user_id`
- Composite index on `(user_id, created_at)` for efficient queries

---

## Error Handling

### Validation Errors (422)
- Missing required fields (type, inputs)
- Invalid JSON structure
- Type field has invalid calculation type

### Bad Request Errors (400)
- Invalid UUID format for calc_id
- Division by zero
- Missing required input parameters

### Not Found Errors (404)
- Calculation ID does not exist
- User is not the owner of the calculation

### Authentication Errors (401)
- Missing Authorization header
- Invalid or expired token

---

## Calculation Types Details

### Addition (`add`)
$$\text{result} = a + b$$

Example:
```json
{
  "type": "add",
  "inputs": {"a": 5, "b": 3}
}
// Result: 8
```

### Subtraction (`subtract`)
$$\text{result} = a - b$$

Example:
```json
{
  "type": "subtract",
  "inputs": {"a": 10, "b": 4}
}
// Result: 6
```

### Multiplication (`multiply`)
$$\text{result} = a \times b$$

Example:
```json
{
  "type": "multiply",
  "inputs": {"a": 7, "b": 6}
}
// Result: 42
```

### Division (`divide`)
$$\text{result} = \frac{a}{b} \text{ (where } b \neq 0\text{)}$$

Example:
```json
{
  "type": "divide",
  "inputs": {"a": 20, "b": 4}
}
// Result: 5.0
```

Error case:
```json
{
  "type": "divide",
  "inputs": {"a": 10, "b": 0}
}
// Error: Cannot divide by zero!
```

---

## Testing

Comprehensive integration tests are provided in `tests/integration/test_calculation_endpoints.py`:

### Test Classes
1. **TestCalculationCreate** - Creation and validation tests
2. **TestCalculationBrowse** - List and filtering tests
3. **TestCalculationRead** - Retrieval tests
4. **TestCalculationEdit** - Update tests
5. **TestCalculationDelete** - Deletion tests
6. **TestCalculationWorkflow** - End-to-end scenarios

### Test Coverage
- All calculation types (add, subtract, multiply, divide)
- Error cases (division by zero, invalid types, missing auth)
- Authorization enforcement (users can't access others' data)
- CRUD operations completeness
- Data isolation between users

### Running Tests
```bash
# Run all calculation endpoint tests
pytest tests/integration/test_calculation_endpoints.py -v

# Run specific test class
pytest tests/integration/test_calculation_endpoints.py::TestCalculationCreate -v

# Run specific test
pytest tests/integration/test_calculation_endpoints.py::TestCalculationCreate::test_create_add_calculation -v

# Run with coverage
pytest tests/integration/test_calculation_endpoints.py --cov=app --cov-report=html
```

---

## Usage Examples

### cURL Examples

#### Create Addition Calculation
```bash
curl -X POST http://localhost:8000/calculations \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "add",
    "inputs": {"a": 5, "b": 3}
  }'
```

#### List All Calculations
```bash
curl -X GET http://localhost:8000/calculations \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Get Specific Calculation
```bash
curl -X GET http://localhost:8000/calculations/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Update Calculation
```bash
curl -X PUT http://localhost:8000/calculations/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {"a": 20, "b": 5}
  }'
```

#### Delete Calculation
```bash
curl -X DELETE http://localhost:8000/calculations/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Python Examples

#### Create Calculation
```python
import requests

access_token = "YOUR_ACCESS_TOKEN_HERE"
headers = {"Authorization": f"Bearer {access_token}"}

calc_data = {
    "type": "multiply",
    "inputs": {"a": 7, "b": 6}
}

response = requests.post(
    "http://localhost:8000/calculations",
    json=calc_data,
    headers=headers
)

if response.status_code == 201:
    calculation = response.json()
    print(f"Created calculation: {calculation['id']}")
    print(f"Result: {calculation['result']}")
```

#### List Calculations
```python
import requests

access_token = "YOUR_ACCESS_TOKEN_HERE"
headers = {"Authorization": f"Bearer {access_token}"}

response = requests.get(
    "http://localhost:8000/calculations",
    headers=headers
)

calculations = response.json()
for calc in calculations:
    print(f"{calc['type']}: {calc['inputs']} = {calc['result']}")
```

#### Update Calculation
```python
import requests

access_token = "YOUR_ACCESS_TOKEN_HERE"
calc_id = "550e8400-e29b-41d4-a716-446655440000"
headers = {"Authorization": f"Bearer {access_token}"}

update_data = {
    "inputs": {"a": 100, "b": 50}
}

response = requests.put(
    f"http://localhost:8000/calculations/{calc_id}",
    json=update_data,
    headers=headers
)

if response.status_code == 200:
    updated_calc = response.json()
    print(f"Updated result: {updated_calc['result']}")
```

---

## Integration with User Endpoints

Calculations are automatically associated with the authenticated user:

1. When creating a calculation, the user's ID from the JWT token is used
2. When listing/reading/updating/deleting, the endpoint verifies ownership
3. When a user is deleted, all their calculations are also deleted (cascade delete)

This ensures complete data isolation between users.

---

## Performance Considerations

### Database Optimization
- Calculations indexed by user_id for efficient filtering
- UUID primary keys for distributed systems
- JSONB column for flexible input storage

### Query Efficiency
- All queries filtered by user_id (prevents full table scans)
- Results cached in response for subsequent accesses
- Minimal computation overhead

### Scalability
- Stateless endpoints allow horizontal scaling
- No session state stored in endpoints
- Database handles concurrency with transactions

---

## Future Enhancements

1. **Batch Operations** - Create/delete multiple calculations at once
2. **Calculation History** - Track all changes to calculations
3. **Advanced Filtering** - Filter by date range, type, result range
4. **Export Functionality** - Export calculations as CSV/JSON
5. **Calculation Templates** - Save and reuse calculation patterns
6. **Calculation Groups** - Organize calculations by project/category
7. **Sharing** - Share calculations with other users
8. **Notifications** - Alert users of calculation errors
9. **Analytics** - Statistics on calculation usage patterns
10. **Undo/Redo** - Restore previous calculation states

---

## Troubleshooting

### "Could not validate credentials"
- Verify the access token is included in the Authorization header
- Ensure token format is correct: `Authorization: Bearer <token>`
- Token may be expired; get a new one by logging in

### "Calculation not found"
- Verify the calculation UUID is correct
- Ensure the calculation belongs to the authenticated user
- Try listing all calculations to see available IDs

### "Cannot divide by zero"
- Check that the divisor (b value) is not 0
- Modify inputs and retry the update

### "Invalid calculation id format"
- Ensure the calc_id is a valid UUID
- Format should be: `550e8400-e29b-41d4-a716-446655440000`

---

## Related Files

- `app/models/calculation.py` - Calculation model with factory methods
- `app/schemas/calculation.py` - Pydantic schemas for validation
- `app/operations/calculations.py` - Business logic operations
- `tests/integration/test_calculation_endpoints.py` - Integration tests
- `app/main.py` - FastAPI endpoint definitions

---

**Last Updated:** December 13, 2025
**Status:** ✅ Complete - All BREAD endpoints fully implemented with comprehensive documentation and tests
