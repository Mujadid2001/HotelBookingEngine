# 🏨 Hotel Booking Engine - API Routes Guide

## 📋 Overview

This guide provides a comprehensive overview of the redesigned API routes for the Hotel Booking Engine. The new structure follows REST conventions and provides intuitive, user-friendly endpoints.

---

## 🔗 Base URLs

### Production API
- **Base URL**: `https://your-domain.com/api/v1/`
- **Documentation**: `https://your-domain.com/api/v1/docs/`
- **Admin Panel**: `https://your-domain.com/admin/`

### Development API
- **Base URL**: `http://127.0.0.1:8000/api/v1/`
- **Documentation**: `http://127.0.0.1:8000/api/v1/docs/`
- **Admin Panel**: `http://127.0.0.1:8000/admin/`

---

## 🚀 Quick Start Examples

### 1. API Root Discovery
```bash
GET /api/v1/
```
Returns API navigation and quick start links.

### 2. Authentication Flow
```bash
# Register new user
POST /api/v1/auth/register/

# Login
POST /api/v1/auth/login/

# Refresh token
POST /api/v1/auth/refresh/

# Logout
POST /api/v1/auth/logout/
```

### 3. Hotel Discovery
```bash
# List all hotels
GET /api/v1/hotels/

# Search hotels
GET /api/v1/hotels/search/?location=Miami&checkin=2025-08-01&checkout=2025-08-05

# Get hotel details
GET /api/v1/hotels/{hotel_id}/

# Check availability
GET /api/v1/hotels/{hotel_id}/availability/?checkin=2025-08-01&checkout=2025-08-05
```

### 4. Booking Management
```bash
# Create booking
POST /api/v1/bookings/create/

# List user bookings
GET /api/v1/bookings/

# Get booking details
GET /api/v1/bookings/{booking_reference}/

# Cancel booking
POST /api/v1/bookings/{booking_reference}/cancel/
```

---

## 🔐 Authentication Endpoints (`/api/v1/auth/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/register/` | Register new user account | ❌ |
| `POST` | `/login/` | User login with credentials | ❌ |
| `POST` | `/logout/` | Logout and invalidate tokens | ✅ |
| `POST` | `/refresh/` | Refresh access token | ❌ |
| `GET` | `/verify/{token}/` | Verify email address | ❌ |
| `POST` | `/password/reset/` | Request password reset | ❌ |
| `POST` | `/password/confirm/{token}/` | Confirm password reset | ❌ |

### Example: User Registration
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "newuser",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'
```

---

## 👤 User Management (`/api/v1/user/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | Get user profile | ✅ |
| `PUT` | `/update/` | Update user profile | ✅ |
| `POST` | `/avatar/` | Upload profile avatar | ✅ |
| `PUT` | `/password/change/` | Change password | ✅ |
| `GET` | `/settings/` | Get user settings | ✅ |
| `GET` | `/bookings/` | Get user's bookings | ✅ |
| `GET` | `/notifications/` | Get user notifications | ✅ |
| `DELETE` | `/delete/` | Delete user account | ✅ |

### Example: Get User Profile
```bash
curl -X GET http://127.0.0.1:8000/api/v1/user/ \
  -H "Authorization: Bearer {access_token}"
```

---

## 🏨 Hotels & Rooms (`/api/v1/hotels/`)

### Hotel Discovery
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | List all hotels | ❌ |
| `GET` | `/search/` | Search hotels with filters | ❌ |
| `GET` | `/search-availability/` | **NEW**: Search with dates & capacity | ❌ |
| `GET` | `/search-capacity/` | **NEW**: Quick search by capacity only | ❌ |
| `GET` | `/featured/` | Get featured hotels | ❌ |

### Individual Hotel
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/{hotel_id}/` | Get hotel details | ❌ |
| `GET` | `/{hotel_id}/gallery/` | Get hotel image gallery | ❌ |
| `GET` | `/{hotel_id}/reviews/` | Get hotel reviews | ❌ |
| `GET` | `/{hotel_id}/policies/` | Get hotel policies | ❌ |

### Rooms & Availability
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/{hotel_id}/rooms/` | List hotel rooms | ❌ |
| `GET` | `/{hotel_id}/room-types/` | Get room types | ❌ |
| `GET` | `/{hotel_id}/rooms/{room_id}/` | Get room details | ❌ |
| `GET` | `/{hotel_id}/availability/` | Check availability | ❌ |
| `GET` | `/{hotel_id}/availability/calendar/` | Get availability calendar | ❌ |
| `GET` | `/{hotel_id}/pricing/` | Get pricing information | ❌ |

### Services & Amenities
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/{hotel_id}/amenities/` | Get hotel amenities | ❌ |
| `GET` | `/{hotel_id}/services/` | Get hotel services | ❌ |
| `GET` | `/{hotel_id}/extras/` | Get additional services | ❌ |
| `GET` | `/{hotel_id}/dining/` | Get dining options | ❌ |

### Example: Search Hotels
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/hotels/search/?location=Miami&checkin=2025-08-01&checkout=2025-08-05&guests=2&rooms=1"
```

### Example: Check Availability
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/hotels/123e4567-e89b-12d3-a456-426614174000/availability/?checkin=2025-08-01&checkout=2025-08-05&guests=2"
```

### 🔥 NEW: Advanced Hotel Search with Availability
Search hotels based on availability dates and guest capacity:

```bash
# Search all hotels for specific dates and capacity
curl -X GET "http://127.0.0.1:8000/api/v1/hotels/search-availability/?check_in=2024-12-25&check_out=2024-12-27&capacity=2"

# Search specific hotel
curl -X GET "http://127.0.0.1:8000/api/v1/hotels/search-availability/?check_in=2024-12-25&check_out=2024-12-27&capacity=3&hotel_id=abc123"

# Search without capacity filter (any room size)
curl -X GET "http://127.0.0.1:8000/api/v1/hotels/search-availability/?check_in=2024-12-25&check_out=2024-12-27"
```

**Query Parameters:**
- `check_in` (required): Check-in date in YYYY-MM-DD format
- `check_out` (required): Check-out date in YYYY-MM-DD format
- `capacity` (optional): Number of guests (1-10). Returns rooms with capacity >= this value
- `hotel_id` (optional): Filter to specific hotel UUID

**Response includes:**
- Available hotels with room types
- Real-time room availability count
- Pricing per night and total cost
- Room amenities and features
- Booking-ready information

### 🚀 NEW: Quick Hotel Search by Capacity Only
Search hotels by guest capacity without date requirements:

```bash
# Search hotels that can accommodate 2 guests
curl -X GET "http://127.0.0.1:8000/api/v1/hotels/search-capacity/?capacity=2"

# Search specific hotel for capacity
curl -X GET "http://127.0.0.1:8000/api/v1/hotels/search-capacity/?capacity=4&hotel_id=abc123"
```

**Query Parameters:**
- `capacity` (required): Number of guests (1-10). Returns hotels with rooms that can accommodate this capacity
- `hotel_id` (optional): Filter to specific hotel UUID

**Response includes:**
- Hotels with suitable room types
- All rooms that meet capacity requirements
- Room details (number, floor, pricing, view type)
- Total available rooms per room type
- No date-based availability filtering

---

## 🎯 Booking Management (`/api/v1/bookings/`)

### Booking Operations
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | List user bookings | ✅ |
| `POST` | `/create/` | Create new booking | ✅ |
| `POST` | `/quote/` | Get booking quote | ❌ |
| `POST` | `/draft/` | Save booking draft | ✅ |

### Individual Booking
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/{reference}/` | Get booking details | ✅ |
| `PUT` | `/{reference}/update/` | Update booking | ✅ |
| `POST` | `/{reference}/cancel/` | Cancel booking | ✅ |
| `POST` | `/{reference}/confirm/` | Confirm booking | ✅ |

### Booking Modifications
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/{reference}/modify/` | Modify booking | ✅ |
| `PUT` | `/{reference}/modify/dates/` | Change dates | ✅ |
| `PUT` | `/{reference}/modify/guests/` | Change guest count | ✅ |
| `PUT` | `/{reference}/modify/room/` | Change room type | ✅ |

### Services & Extras
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/{reference}/services/` | Get booking services | ✅ |
| `POST` | `/{reference}/services/add/` | Add service | ✅ |
| `DELETE` | `/{reference}/services/{id}/remove/` | Remove service | ✅ |
| `GET` | `/{reference}/extras/` | Get booking extras | ✅ |

### Check-in/Check-out
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/{reference}/checkin/` | Check-in guest | ✅ Staff |
| `POST` | `/{reference}/checkout/` | Check-out guest | ✅ Staff |
| `POST` | `/{reference}/early-checkin/` | Request early check-in | ✅ |
| `POST` | `/{reference}/late-checkout/` | Request late check-out | ✅ |

### Billing & Payment
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/{reference}/invoice/` | Get invoice | ✅ |
| `GET` | `/{reference}/receipt/` | Get receipt | ✅ |
| `POST` | `/{reference}/payment/process/` | Process payment | ✅ |
| `POST` | `/{reference}/payment/refund/` | Request refund | ✅ |

### Example: Create Booking
```bash
curl -X POST http://127.0.0.1:8000/api/v1/bookings/create/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "hotel_id": "123e4567-e89b-12d3-a456-426614174000",
    "room_type": "deluxe",
    "check_in_date": "2025-08-01",
    "check_out_date": "2025-08-05",
    "guests": 2,
    "rooms": 1,
    "special_requests": "Late check-in",
    "extras": [1, 2]
  }'
```

---

## 🛡️ Staff Operations (`/api/v1/bookings/staff/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | List all bookings | ✅ Staff |
| `GET` | `/dashboard/` | Staff dashboard | ✅ Staff |
| `GET` | `/today/` | Today's bookings | ✅ Staff |
| `GET` | `/arrivals/` | Today's arrivals | ✅ Staff |
| `GET` | `/departures/` | Today's departures | ✅ Staff |

### Management & Reports
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/management/occupancy/` | Occupancy report | ✅ Manager |
| `GET` | `/management/revenue/` | Revenue report | ✅ Manager |
| `GET` | `/management/analytics/` | Booking analytics | ✅ Manager |
| `POST` | `/management/export/` | Export bookings | ✅ Manager |

---

## 📊 API Response Formats

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation completed successfully",
  "pagination": {
    "count": 100,
    "next": "http://api.example.com/api/v1/hotels/?page=2",
    "previous": null,
    "page_size": 20
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request data is invalid",
    "details": {
      "email": ["This field is required"],
      "password": ["Password must be at least 8 characters"]
    }
  }
}
```

---

## 🔧 Request Headers

### Authentication
```
Authorization: Bearer {access_token}
```

### Content Type
```
Content-Type: application/json
```

### API Version (Optional)
```
API-Version: v1
```

---

## 📖 Interactive Documentation

### Swagger UI
Visit `http://127.0.0.1:8000/api/v1/docs/` for interactive API documentation where you can:
- Explore all endpoints
- Test API calls directly
- View request/response schemas
- See authentication requirements

### ReDoc
Visit `http://127.0.0.1:8000/api/v1/redoc/` for alternative documentation format.

### API Browser
Visit `http://127.0.0.1:8000/api/v1/` for Django REST Framework's browsable API.

---

## 🆕 What's New in v1 API

### ✅ Improvements
1. **RESTful Design**: Consistent resource-based URLs
2. **Logical Hierarchy**: hotels → rooms → availability → bookings
3. **Self-Documenting**: Clear, descriptive endpoint names
4. **Versioning**: `/api/v1/` prefix for future compatibility
5. **Interactive Docs**: Swagger UI and ReDoc integration
6. **Enhanced Search**: Advanced filtering and search capabilities
7. **Bulk Operations**: Bulk booking management for staff
8. **Real-time**: Live availability and pricing updates
9. **Analytics**: Comprehensive reporting endpoints
10. **User Experience**: Intuitive navigation and discovery

### 🔄 Migration from Legacy API
The new API maintains backward compatibility:
- Legacy endpoints still work: `/api/accounts/`, `/api/core/`, `/api/bookings/`
- Gradually migrate to v1 endpoints
- No breaking changes to existing integrations

---

## 🎯 Best Practices

### 1. Use Appropriate HTTP Methods
- `GET`: Retrieve data
- `POST`: Create new resources
- `PUT`: Update entire resource
- `PATCH`: Partial updates
- `DELETE`: Remove resources

### 2. Handle Pagination
```javascript
// JavaScript example
const response = await fetch('/api/v1/hotels/?page=2&page_size=10');
const data = await response.json();
console.log(data.pagination.next); // Next page URL
```

### 3. Error Handling
```javascript
// JavaScript example
try {
  const response = await fetch('/api/v1/bookings/create/', options);
  if (!response.ok) {
    const error = await response.json();
    console.error('API Error:', error.error.message);
  }
} catch (error) {
  console.error('Network Error:', error);
}
```

### 4. Authentication
```javascript
// JavaScript example
const headers = {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json'
};
```

---

## 🔗 Related Resources

- **Complete API Documentation**: `API_DOCUMENTATION.md`
- **Setup Guide**: `HowTo_RUN.md`
- **Project README**: `README.md`
- **Live API**: `http://127.0.0.1:8000/api/v1/`

---

**Happy Coding! 🚀**

*Last Updated: July 27, 2025*  
*API Version: 1.0*
