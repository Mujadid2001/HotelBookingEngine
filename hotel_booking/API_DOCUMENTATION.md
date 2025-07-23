# Hotel Booking Engine - API Documentation

## Overview
This is a Django REST API backend for a hotel booking system. The frontend will be separate, and this backend provides all the necessary endpoints for user management and authentication.

## Base URL
```
http://127.0.0.1:8000/api/accounts/
```

## API Endpoints

### 1. User Registration
**POST** `/register/`

Register a new user account.

**Request Body:**
```json
{
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe", 
    "password": "password123",
    "password_confirm": "password123"
}
```

**Response (201 Created):**
```json
{
    "message": "Registration successful! Please check your email to verify your account.",
    "user": {
        "id": "uuid-here",
        "email": "user@example.com",
        "username": "username",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        // ... other user fields
    }
}
```

**PowerShell Example:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/accounts/register/" -Method POST -ContentType "application/json" -Body '{"email": "test@example.com", "username": "testuser", "first_name": "Test", "last_name": "User", "password": "testpass123", "password_confirm": "testpass123"}'
```

### 2. User Login
**POST** `/login/`

Authenticate user and get JWT tokens.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**Response (200 OK):**
```json
{
    "message": "Welcome back, John!",
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

**PowerShell Example:**
```powershell
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/accounts/login/" -Method POST -ContentType "application/json" -Body '{"email": "test@example.com", "password": "testpass123"}'
$token = $response.tokens.access
```

### 3. Get User Profile
**GET** `/profile/`

Get the current user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": "uuid-here",
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone_number": "",
    "date_of_birth": null,
    "gender": "",
    "user_type": "guest",
    "address_line_1": "",
    "city": "",
    "country": "United States",
    "is_active": true,
    "is_verified": false,
    "date_joined": "2025-07-23T15:20:27.572580Z",
    "profile": {
        "emergency_contact_name": "",
        "preferred_room_type": "",
        "dietary_restrictions": "",
        "total_bookings": 0,
        "total_spent": "0.00"
    }
}
```

**PowerShell Example:**
```powershell
$headers = @{"Authorization" = "Bearer $token"}
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/accounts/profile/" -Method GET -Headers $headers
```

### 4. Update User Profile
**PUT** `/profile/update/`

Update the current user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Smith",
    "phone_number": "+1234567890",
    "bio": "Updated bio",
    "city": "New York",
    "profile": {
        "preferred_room_type": "deluxe",
        "dietary_restrictions": "vegetarian",
        "special_requests": "Late check-in"
    }
}
```

**PowerShell Example:**
```powershell
$headers = @{"Authorization" = "Bearer $token"}
$data = '{"bio": "Updated bio", "city": "Test City", "profile": {"preferred_room_type": "deluxe", "dietary_restrictions": "vegetarian"}}'
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/accounts/profile/update/" -Method PUT -ContentType "application/json" -Body $data -Headers $headers
```

### 5. Password Reset Request
**POST** `/password/reset/`

Request a password reset email.

**Request Body:**
```json
{
    "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
    "message": "If the email exists, a password reset link has been sent."
}
```

**PowerShell Example:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/accounts/password/reset/" -Method POST -ContentType "application/json" -Body '{"email": "test@example.com"}'
```

### 6. Token Refresh
**POST** `/token/refresh/`

Refresh JWT access token using refresh token.

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 7. User Logout
**POST** `/logout/`

Logout user and blacklist JWT tokens to prevent reuse.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "message": "Successfully logged out. Token has been blacklisted."
}
```

**PowerShell Example:**
```powershell
$headers = @{"Authorization" = "Bearer $token"}
$data = '{"refresh": "' + $refresh_token + '"}'
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/accounts/logout/" -Method POST -ContentType "application/json" -Body $data -Headers $headers
```

**Note:** After logout, both the access and refresh tokens are added to a blacklist. Any subsequent requests using these tokens will be rejected with a 401 error.

## Token Blacklisting & Security

This API implements **industry-standard JWT token blacklisting** for enhanced security:

### How It Works
1. **Upon Logout**: Both access and refresh tokens are added to a server-side blacklist
2. **Middleware Check**: Every API request checks if the token has been blacklisted
3. **Automatic Rejection**: Blacklisted tokens are automatically rejected with 401 Unauthorized

### Security Benefits
- **Immediate Token Invalidation**: Tokens become unusable the moment user logs out
- **Prevents Token Reuse**: Protects against stolen or compromised tokens
- **Server-Side Control**: Complete control over token validity regardless of client actions

### Database Implementation
- Custom blacklist table: `simple_token_blacklist`
- Stores JTI (JWT ID) of blacklisted tokens
- Middleware: `TokenBlacklistMiddleware` automatically checks all protected endpoints

## Authentication
This API uses JWT (JSON Web Tokens) for authentication. After logging in, you'll receive:
- **Access Token**: Short-lived token (1 hour) for API requests
- **Refresh Token**: Long-lived token (7 days) for getting new access tokens

Include the access token in the `Authorization` header for protected endpoints:
```
Authorization: Bearer <access_token>
```

## Error Responses
The API returns standard HTTP status codes:
- **200**: Success
- **201**: Created successfully 
- **400**: Bad request (validation errors)
- **401**: Unauthorized (invalid/missing token)
- **404**: Not found
- **500**: Internal server error

## Running the API
1. Start the Django development server:
   ```bash
   python manage.py runserver
   ```

2. The API will be available at: `http://127.0.0.1:8000/api/accounts/`

3. Run the test suite to verify everything works:
   ```bash
   python api_tests.py
   ```

## Notes
- All endpoints return JSON responses
- Email verification and password reset emails are logged to console (not actually sent)
- User profiles are automatically created when users register
- The API is designed to be frontend-agnostic and can work with any client application
