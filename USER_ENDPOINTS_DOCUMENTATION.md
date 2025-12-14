# User Endpoints Implementation Documentation

## Overview

This document describes the implementation of user endpoints for the FastAPI Calculator application. The endpoints include user registration, login, profile management, and account management.

## Architecture

### File Structure

```
app/
├── operations/
│   ├── __init__.py              # Updated with UserOperations import
│   └── users.py                 # NEW: User operations business logic
├── main.py                      # Updated with comprehensive user endpoints
└── [existing files unchanged]
```

### Components

#### 1. **User Operations Module** (`app/operations/users.py`)

A new module containing the `UserOperations` class with static methods for all user-related database operations:

- `register_user(db, user_data)` - Create a new user account
- `authenticate_user(db, username_or_email, password)` - Authenticate user and generate tokens
- `get_user_by_id(db, user_id)` - Retrieve user by UUID
- `get_user_by_username(db, username)` - Retrieve user by username
- `get_user_by_email(db, email)` - Retrieve user by email
- `update_user(db, user_id, update_data)` - Update user profile
- `change_password(db, user_id, password_data)` - Change user password
- `deactivate_user(db, user_id)` - Deactivate account
- `activate_user(db, user_id)` - Activate account
- `delete_user(db, user_id)` - Permanently delete account

#### 2. **Main Application** (`app/main.py`)

Updated FastAPI application with comprehensive user endpoints organized into sections:

- **User Endpoints** (new primary endpoints)
- **Legacy Auth Endpoints** (backward compatibility)

## API Endpoints

### User Management Endpoints

#### 1. Register User
**POST** `/users/register`

Creates a new user account.

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!"
}
```

**Response:** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
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

**Error Responses:**
- `400 Bad Request` - Username or email already exists, password mismatch, weak password
- `422 Unprocessable Entity` - Invalid request data

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

---

#### 2. Login User
**POST** `/users/login`

Authenticates a user and returns JWT tokens.

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_at": "2025-12-13T10:45:00Z",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "johndoe",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid username or password

**Notes:**
- Username or email can be used for login
- Access token expires based on `ACCESS_TOKEN_EXPIRE_MINUTES` setting
- Refresh token expires based on `REFRESH_TOKEN_EXPIRE_DAYS` setting
- `last_login` timestamp is updated on successful authentication

---

#### 3. Get Current User Profile
**GET** `/users/me`

Retrieves the authenticated user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
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

**Error Responses:**
- `401 Unauthorized` - Missing or invalid token

---

#### 4. Get User by ID
**GET** `/users/{user_id}`

Retrieves a user's public profile by UUID.

**Parameters:**
- `user_id` (path): User's UUID

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
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

**Error Responses:**
- `404 Not Found` - User not found

---

#### 5. Update User Profile
**PUT** `/users/{user_id}`

Updates the authenticated user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Parameters:**
- `user_id` (path): User's UUID (must match authenticated user's ID)

**Request Body:** (all fields optional)
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@example.com",
  "username": "janesmith"
}
```

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "janesmith",
  "email": "jane.smith@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-12-13T10:30:00Z",
  "updated_at": "2025-12-13T10:35:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Username or email already exists
- `403 Forbidden` - User can only update their own profile
- `404 Not Found` - User not found
- `401 Unauthorized` - Missing or invalid token

---

#### 6. Change Password
**POST** `/users/{user_id}/change-password`

Changes the authenticated user's password.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Parameters:**
- `user_id` (path): User's UUID (must match authenticated user's ID)

**Request Body:**
```json
{
  "current_password": "SecurePass123!",
  "new_password": "NewSecurePass123!",
  "confirm_new_password": "NewSecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "johndoe",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-12-13T10:30:00Z",
  "updated_at": "2025-12-13T10:36:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Current password incorrect, new password doesn't meet requirements
- `403 Forbidden` - User can only change their own password
- `404 Not Found` - User not found
- `401 Unauthorized` - Missing or invalid token

---

#### 7. Deactivate User Account
**POST** `/users/{user_id}/deactivate`

Deactivates the authenticated user's account.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Parameters:**
- `user_id` (path): User's UUID (must match authenticated user's ID)

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "johndoe",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": false,
  "is_verified": false,
  "created_at": "2025-12-13T10:30:00Z",
  "updated_at": "2025-12-13T10:37:00Z"
}
```

**Error Responses:**
- `403 Forbidden` - User can only deactivate their own account
- `404 Not Found` - User not found
- `401 Unauthorized` - Missing or invalid token

---

#### 8. Delete User Account
**DELETE** `/users/{user_id}`

Permanently deletes the authenticated user's account.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Parameters:**
- `user_id` (path): User's UUID (must match authenticated user's ID)

**Response:** `204 No Content`

**Error Responses:**
- `403 Forbidden` - User can only delete their own account
- `404 Not Found` - User not found
- `401 Unauthorized` - Missing or invalid token

**Notes:**
- This action is permanent and cannot be undone
- All user data including calculations is deleted (cascade delete)

---

## Security Features

### Password Hashing
- Uses bcrypt with configurable rounds (default: 12)
- Passwords are hashed before storage
- Implemented in `User.hash_password()` and verified in `User.verify_password()`

### JWT Authentication
- Access tokens and refresh tokens are generated on login
- Tokens are verified on protected endpoints
- Token expiration is configurable via environment variables

### Authorization
- Users can only access/modify their own data
- Endpoints check that the authenticated user's ID matches the requested user ID
- Returns `403 Forbidden` when authorization fails

### Input Validation
- Email validation using Pydantic's `EmailStr`
- Password strength requirements enforced at schema level
- Username and email uniqueness enforced at database level

---

## Authentication Flow

### Registration Flow
1. User submits registration with credentials
2. System validates password strength and confirmation
3. System checks for duplicate username/email
4. Password is hashed using bcrypt
5. User record is created in database
6. User response is returned (without password)

### Login Flow
1. User submits username/email and password
2. System finds user by username or email
3. System verifies hashed password
4. System updates `last_login` timestamp
5. System generates JWT access and refresh tokens
6. Tokens and user info are returned to client

### Authenticated Request Flow
1. Client sends request with `Authorization: Bearer <token>` header
2. `OAuth2PasswordBearer` dependency extracts token
3. `get_current_active_user` dependency verifies token
4. Token payload is decoded to get user ID
5. User data is retrieved and returned
6. Endpoint accesses `current_user` parameter

---

## Database Schema

### User Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIMEZONE,
    updated_at TIMESTAMP WITH TIMEZONE,
    last_login TIMESTAMP WITH TIMEZONE
);
```

---

## Error Handling

### Validation Errors (422)
- Invalid email format
- Password too short
- Password doesn't match confirmation
- Password missing required character types
- Username too short

### Not Found Errors (404)
- User not found by ID
- User not found by username or email

### Conflict Errors (400)
- Username already exists
- Email already exists
- New password same as current password

### Authentication Errors (401)
- Missing authorization header
- Invalid token format
- Expired token
- Invalid credentials (wrong password)

### Authorization Errors (403)
- User attempting to modify another user's profile
- User attempting to change another user's password
- User attempting to delete another user's account

---

## Testing

Comprehensive integration tests are provided in `tests/integration/test_user_endpoints.py`:

### Test Classes
1. **TestUserRegistration** - Registration endpoint tests
2. **TestUserLogin** - Login endpoint tests
3. **TestAuthenticatedUserEndpoints** - Protected endpoint tests

### Test Coverage
- Successful registration with valid data
- Duplicate username/email detection
- Password validation (mismatch, weakness)
- Login with username and email
- Invalid credentials handling
- Current user profile retrieval
- User profile updates
- Password changes
- Account deactivation and deletion
- Authorization checks

### Running Tests
```bash
# Run all user endpoint tests
pytest tests/integration/test_user_endpoints.py -v

# Run specific test class
pytest tests/integration/test_user_endpoints.py::TestUserRegistration -v

# Run specific test
pytest tests/integration/test_user_endpoints.py::TestUserRegistration::test_register_new_user_success -v

# Run with coverage
pytest tests/integration/test_user_endpoints.py --cov=app --cov-report=html
```

---

## Environment Variables

Configure the following environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
JWT_REFRESH_SECRET_KEY=your-super-refresh-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Password Hashing
BCRYPT_ROUNDS=12
```

---

## Usage Examples

### cURL Examples

#### Register User
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

#### Login User
```bash
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123!"
  }'
```

#### Get Current User
```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Update Profile
```bash
curl -X PUT http://localhost:8000/users/YOUR_USER_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane"
  }'
```

---

## Future Enhancements

1. **Email Verification** - Send verification emails on registration
2. **Password Reset** - Implement forgot password functionality
3. **Two-Factor Authentication** - Add 2FA support
4. **User Roles** - Implement role-based access control (RBAC)
5. **Account Locking** - Lock account after failed login attempts
6. **Audit Logging** - Log all user actions for security
7. **Token Refresh** - Implement refresh token endpoint
8. **User Profile Picture** - Support user avatars
9. **User Preferences** - Store user settings (theme, language, etc.)
10. **Social Login** - OAuth2 integration (Google, GitHub, etc.)

---

## Troubleshooting

### "User already exists" error on registration
- Ensure the username and email are unique
- Check the database for existing users with same credentials

### "Invalid credentials" on login
- Verify username/email and password are correct
- Ensure the user account is active (`is_active=true`)
- Check password strength requirements were met during registration

### "Could not validate credentials" on authenticated endpoints
- Verify the token is included in the Authorization header
- Ensure token format is correct: `Authorization: Bearer <token>`
- Check token hasn't expired
- Try logging in again to get a fresh token

### "You can only update your own profile" error
- Verify you're updating your own user ID
- Obtain the correct user ID from the login response or `/users/me` endpoint

---

## Related Files

- `app/models/user.py` - User model with authentication methods
- `app/schemas/user.py` - Pydantic schemas for user endpoints
- `app/auth/jwt.py` - JWT token creation and verification
- `app/auth/dependencies.py` - Authentication dependency functions
- `app/database.py` - Database configuration and session management
- `tests/integration/test_user_endpoints.py` - Integration tests
