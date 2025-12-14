# User Endpoints Quick Start Guide

## Overview

This guide provides quick examples for using the user registration and login endpoints.

## Prerequisites

- FastAPI application running (see README.md)
- Docker and Docker Compose (for local development)
- cURL or Postman for testing

## Starting the Application

### Using Docker Compose
```bash
cd /home/tatejones/is218/module12_is601
docker-compose up -d
```

The API will be available at `http://localhost:8000`

### Swagger UI Documentation
Once running, visit: `http://localhost:8000/docs`

---

## Quick Examples

### 1. Register a New User

**Using cURL:**
```bash
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "username": "johndoe",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!"
  }'
```

**Response (201 Created):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "johndoe",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-12-13T10:30:00Z",
  "updated_at": "2025-12-13T10:30:00Z"
}
```

**Using Python:**
```python
import requests

url = "http://localhost:8000/users/register"
data = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "username": "johndoe",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!"
}

response = requests.post(url, json=data)
user = response.json()
print(f"User created: {user['username']}")
```

---

### 2. Login User (Get Tokens)

**Using cURL:**
```bash
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123!"
  }'
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjNlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQwMDAiLCJleHAiOjE3MzI5Nzc0MDB9.signature",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjNlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQwMDAiLCJleHAiOjE3MzMwNjM4MDB9.signature",
  "token_type": "bearer",
  "expires_at": "2025-12-13T11:00:00Z",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "johndoe",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false
}
```

**Using Python:**
```python
import requests

url = "http://localhost:8000/users/login"
data = {
    "username": "johndoe",
    "password": "SecurePass123!"
}

response = requests.post(url, json=data)
tokens = response.json()
access_token = tokens["access_token"]
print(f"Login successful, token: {access_token[:20]}...")
```

---

### 3. Get Current User Profile

**Using cURL:**
```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Replace `YOUR_ACCESS_TOKEN` with the token from login response.

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "johndoe",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-12-13T10:30:00Z",
  "updated_at": "2025-12-13T10:30:00Z"
}
```

**Using Python:**
```python
import requests

access_token = "YOUR_ACCESS_TOKEN_HERE"
headers = {"Authorization": f"Bearer {access_token}"}

response = requests.get("http://localhost:8000/users/me", headers=headers)
user = response.json()
print(f"Current user: {user['username']} ({user['email']})")
```

---

### 4. Update User Profile

**Using cURL:**
```bash
curl -X PUT http://localhost:8000/users/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith"
  }'
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "johndoe",
  "email": "john.doe@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-12-13T10:30:00Z",
  "updated_at": "2025-12-13T10:35:00Z"
}
```

**Using Python:**
```python
import requests

access_token = "YOUR_ACCESS_TOKEN_HERE"
user_id = "123e4567-e89b-12d3-a456-426614174000"
headers = {"Authorization": f"Bearer {access_token}"}

update_data = {
    "first_name": "Jane",
    "last_name": "Smith"
}

response = requests.put(
    f"http://localhost:8000/users/{user_id}",
    json=update_data,
    headers=headers
)
updated_user = response.json()
print(f"Profile updated: {updated_user['first_name']} {updated_user['last_name']}")
```

---

### 5. Change Password

**Using cURL:**
```bash
curl -X POST http://localhost:8000/users/123e4567-e89b-12d3-a456-426614174000/change-password \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "SecurePass123!",
    "new_password": "NewSecurePass123!",
    "confirm_new_password": "NewSecurePass123!"
  }'
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "johndoe",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-12-13T10:30:00Z",
  "updated_at": "2025-12-13T10:40:00Z"
}
```

**Using Python:**
```python
import requests

access_token = "YOUR_ACCESS_TOKEN_HERE"
user_id = "123e4567-e89b-12d3-a456-426614174000"
headers = {"Authorization": f"Bearer {access_token}"}

password_data = {
    "current_password": "SecurePass123!",
    "new_password": "NewSecurePass123!",
    "confirm_new_password": "NewSecurePass123!"
}

response = requests.post(
    f"http://localhost:8000/users/{user_id}/change-password",
    json=password_data,
    headers=headers
)

if response.status_code == 200:
    print("Password changed successfully!")
else:
    print(f"Error: {response.json()['detail']}")
```

---

### 6. Deactivate Account

**Using cURL:**
```bash
curl -X POST http://localhost:8000/users/123e4567-e89b-12d3-a456-426614174000/deactivate \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "johndoe",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": false,
  "is_verified": false,
  "created_at": "2025-12-13T10:30:00Z",
  "updated_at": "2025-12-13T10:45:00Z"
}
```

---

### 7. Delete Account

**Using cURL:**
```bash
curl -X DELETE http://localhost:8000/users/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (204 No Content)**

---

## Complete Workflow Example

### Python Script
```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Register
print("1. Registering user...")
register_response = requests.post(
    f"{BASE_URL}/users/register",
    json={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "username": "johndoe",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }
)
user = register_response.json()
user_id = user["id"]
print(f"   ✓ User registered: {user['username']}")

# 2. Login
print("\n2. Logging in...")
login_response = requests.post(
    f"{BASE_URL}/users/login",
    json={
        "username": "johndoe",
        "password": "SecurePass123!"
    }
)
tokens = login_response.json()
access_token = tokens["access_token"]
print(f"   ✓ Logged in, token: {access_token[:20]}...")

# 3. Get Profile
print("\n3. Getting profile...")
headers = {"Authorization": f"Bearer {access_token}"}
profile_response = requests.get(f"{BASE_URL}/users/me", headers=headers)
profile = profile_response.json()
print(f"   ✓ Profile: {profile['first_name']} {profile['last_name']}")

# 4. Update Profile
print("\n4. Updating profile...")
update_response = requests.put(
    f"{BASE_URL}/users/{user_id}",
    json={"first_name": "Jane"},
    headers=headers
)
updated_user = update_response.json()
print(f"   ✓ Updated: {updated_user['first_name']}")

# 5. Change Password
print("\n5. Changing password...")
password_response = requests.post(
    f"{BASE_URL}/users/{user_id}/change-password",
    json={
        "current_password": "SecurePass123!",
        "new_password": "NewSecurePass123!",
        "confirm_new_password": "NewSecurePass123!"
    },
    headers=headers
)
if password_response.status_code == 200:
    print("   ✓ Password changed")

print("\n✓ All operations completed successfully!")
```

---

## Error Handling

### Registration Errors

```bash
# Password too weak
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "username": "john",
    "password": "weak",
    "confirm_password": "weak"
  }'

# Response: 422 Unprocessable Entity
```

### Login Errors

```bash
# Invalid credentials
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "wrong"}'

# Response: 401 Unauthorized
# Detail: "Invalid username or password"
```

### Authorization Errors

```bash
# Missing token
curl -X GET http://localhost:8000/users/me

# Response: 403 Forbidden
# Detail: "Not authenticated"

# Updating other user's profile
curl -X PUT http://localhost:8000/users/OTHER_USER_ID \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Hacked"}'

# Response: 403 Forbidden
# Detail: "You can only update your own profile"
```

---

## Testing in Swagger UI

1. Visit: `http://localhost:8000/docs`
2. Try the endpoints interactively
3. For authenticated endpoints:
   - Click "Authorize" button
   - Paste your access token
   - Click "Authorize"
   - Use endpoints normally

---

## Common Issues

### "User already exists"
- Check that username is unique
- Try with a different email/username

### "Invalid credentials"
- Verify you're using correct password
- Check username/email spelling
- Passwords are case-sensitive

### "Could not validate credentials"
- Token may be expired (get new token with login)
- Token format should be: `Authorization: Bearer <token>`
- Token must be copied exactly from login response

### "You can only update your own profile"
- Ensure you're updating your own user ID
- Get your user ID from login response's `user_id` field

---

## Password Requirements

Must contain:
- ✓ Minimum 8 characters
- ✓ At least 1 uppercase letter (A-Z)
- ✓ At least 1 lowercase letter (a-z)
- ✓ At least 1 digit (0-9)
- ✓ At least 1 special character (!@#$%^&*)

**Example of strong password:** `MyPass123!`

---

## Next Steps

1. See [USER_ENDPOINTS_DOCUMENTATION.md](USER_ENDPOINTS_DOCUMENTATION.md) for complete API reference
2. See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for technical details
3. Run tests: `pytest tests/integration/test_user_endpoints.py -v`
4. Check Swagger UI: `http://localhost:8000/docs`

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [JWT Documentation](https://tools.ietf.org/html/rfc7519)
