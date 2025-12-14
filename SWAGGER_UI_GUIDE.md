# Swagger UI Quick Reference Guide

## Accessing the API Documentation

### Swagger UI (Interactive)
**URL:** http://localhost:8000/docs

### ReDoc (Read-Only)
**URL:** http://localhost:8000/redoc

---

## Step-by-Step Testing Guide

### Step 1: Register a New User

1. Open http://localhost:8000/docs
2. Scroll to **POST /users/register**
3. Click **"Try it out"** button
4. Fill in the request body:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!"
}
```
5. Click **"Execute"**
6. Verify you receive a 201 response with user ID

---

### Step 2: Login and Get JWT Token

1. Scroll to **POST /users/login**
2. Click **"Try it out"**
3. Fill in the request body:
```json
{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```
4. Click **"Execute"**
5. Copy the `access_token` from the response

---

### Step 3: Authorize Your Requests

1. Look for the green **"Authorize"** button at the top of the Swagger page
2. Click it
3. In the dialog, select **"Bearer"** (if not already selected)
4. Paste your access token: `eyJhbGciOiJIUzI1NiIsIn...`
5. Click **"Authorize"**
6. Close the dialog

**Note:** All endpoints with a lock icon (🔒) now require this token

---

### Step 4: Get Your User Profile

1. Scroll to **GET /users/me**
2. Click **"Try it out"**
3. Click **"Execute"**
4. You should see your user profile with the correct username

---

### Step 5: Create a Calculation

1. Scroll to **POST /calculations**
2. Click **"Try it out"**
3. Fill in the request body:
```json
{
  "type": "addition",
  "inputs": [10, 5]
}
```
4. Click **"Execute"**
5. Verify the result is 15

**Available Types:**
- `"addition"` - Add all inputs
- `"subtraction"` - Subtract all inputs from first
- `"multiplication"` - Multiply all inputs
- `"division"` - Divide first input by all others

---

### Step 6: List Your Calculations

1. Scroll to **GET /calculations**
2. Click **"Try it out"**
3. Click **"Execute"**
4. See all calculations you've created

---

### Step 7: Get a Specific Calculation

1. Scroll to **GET /calculations/{calc_id}**
2. Click **"Try it out"**
3. Paste a calculation ID (from the list endpoint)
4. Click **"Execute"**
5. View details of that specific calculation

---

### Step 8: Update a Calculation

1. Scroll to **PUT /calculations/{calc_id}**
2. Click **"Try it out"**
3. Paste a calculation ID
4. Fill in the request body with new inputs:
```json
{
  "inputs": [20, 10]
}
```
5. Click **"Execute"**
6. The result should be recalculated (20 + 5 = 25 for addition)

---

### Step 9: Delete a Calculation

1. Scroll to **DELETE /calculations/{calc_id}**
2. Click **"Try it out"**
3. Paste a calculation ID
4. Click **"Execute"**
5. Verify you get a 204 (No Content) response

---

### Step 10: Update Your Profile

1. Scroll to **PUT /users/{user_id}**
2. Click **"Try it out"**
3. Paste your user ID (from /users/me endpoint)
4. Fill in new data:
```json
{
  "first_name": "Jane",
  "last_name": "Smith"
}
```
5. Click **"Execute"**
6. Verify the update was successful

---

## Testing Error Cases

### Division by Zero
1. Go to **POST /calculations**
2. Use request body:
```json
{
  "type": "division",
  "inputs": [10, 0]
}
```
3. Should receive 422 error with "Cannot divide by zero"

### Missing Required Fields
1. Go to **POST /users/register**
2. Omit a required field like `email`
3. Should receive 422 error with validation message

### Unauthenticated Request
1. Click the **"Authorize"** button
2. Click **"Logout"** to remove authorization
3. Try **GET /calculations**
4. Should receive 401 error

---

## Common Response Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | GET /users/me successful |
| 201 | Created | POST /users/register success |
| 204 | No Content | DELETE calculation success |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Calculation doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 500 | Server Error | Internal error |

---

## Schema Format Reference

### Calculation Request
```json
{
  "type": "addition|subtraction|multiplication|division",
  "inputs": [number, number, ...]  // Min 2 numbers
}
```

### Calculation Response
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "type": "addition|subtraction|multiplication|division",
  "inputs": [5.0, 3.0],
  "result": 8.0,
  "created_at": "2025-12-14T02:58:39.728342",
  "updated_at": "2025-12-14T02:58:39.728342"
}
```

### User Response
```json
{
  "id": "uuid",
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-12-14T03:01:03.427885Z",
  "updated_at": "2025-12-14T03:01:03.857374Z"
}
```

---

## Tips & Tricks

1. **Copy/Paste IDs:** Always copy the full UUID from responses when testing endpoints with ID parameters
2. **Token Expiration:** Tokens expire after 30 minutes - you'll need to login again
3. **Try Again:** If you get an error, check the response body for details
4. **Check Timestamps:** created_at never changes, updated_at changes on modifications
5. **Data Isolation:** You can only see your own calculations and user data

---

## Troubleshooting

**"Could not validate credentials"**
- Your token may be invalid or expired
- Click Authorize and login again

**"Username or email already exists"**
- Try a different username/email for registration

**"Calculation not found" (404)**
- The ID might be wrong or belong to another user
- Use GET /calculations to see valid IDs

**"Inactive user"**
- User account has been deactivated
- Contact administrator to reactivate

---

## API Performance Notes

- Average response time: <100ms
- Calculations are computed on-the-fly
- All user data is returned from database (real-time)
- No caching is implemented (fresh data always)

---

Last Updated: December 14, 2025
