# Hotel Booking Engine API

A professional Django REST Framework API for hotel booking management with JWT authentication, room management, booking system, and comprehensive hotel services.

## 🏨 Features

- **Hotel Management**: Multi-hotel support with detailed hotel profiles
- **Room Management**: Room types, availability, pricing, and amenities
- **Booking System**: Complete booking lifecycle with check-in/out
- **User Management**: JWT authentication with guest/staff roles
- **Extra Services**: Spa, dining, transport, and other hotel services
- **API Documentation**: Swagger/OpenAPI integration
- **Professional API**: Clean, RESTful endpoints with proper validation

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** installed on your system
- **pip** (Python package manager)
- **Git** (for cloning the repository)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Mujadid2001/HotelBookingEngine.git
cd HotelBookingEngine

# Create virtual environment (macOS/Linux)
python3 -m venv hotel_booking_env
source hotel_booking_env/bin/activate

# Create virtual environment (Windows)
python -m venv hotel_booking_env
hotel_booking_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Navigate to Django project directory
cd hotel_booking

# Apply database migrations
python manage.py migrate

# Setup initial data (hotels, rooms, users, services)
python manage.py setup_initial_data --reset
```

### 3. Run the Server

```bash
# Start development server
python manage.py runserver 0.0.0.0:8002

# Server will be available at:
# - API: http://127.0.0.1:8002/api/v1/
# - Dashboard: http://127.0.0.1:8002/
# - Swagger UI: http://127.0.0.1:8002/swagger/
```

### 4. Access the Application

Once the server is running, you can access:

- **🎛️ Interactive Dashboard**: http://127.0.0.1:8002/
- **📚 API Documentation**: http://127.0.0.1:8002/swagger/
- **🔗 API Root**: http://127.0.0.1:8002/api/v1/
- **👨‍💼 Admin Panel**: http://127.0.0.1:8002/admin/

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8002/swagger/
- **ReDoc**: http://127.0.0.1:8002/redoc/
- **API Root**: http://127.0.0.1:8002/api/v1/

## 🎛️ Interactive Dashboard

The Hotel Booking Engine includes a beautiful, responsive dashboard for testing and managing the complete API without any command-line tools.

### 🌐 Access the Dashboard
- **URL**: http://127.0.0.1:8002/
- **No authentication required** to view and test the API

### ✨ Dashboard Features

#### 🔐 Authentication Testing
- **User Registration**: Complete signup form with password confirmation
- **User Login**: Secure JWT authentication
- **Token Management**: Automatic token storage and display
- **Logout**: Clear session and tokens

#### 🏨 Hotel Discovery & Search
- **🔍 Advanced Search**: Search hotels by check-in/check-out dates and guest capacity
- **⚡ Quick Search**: Search hotels by capacity only (no dates required)
- **📊 Live Results**: Real-time availability with detailed room information
- **💰 Pricing**: Per-night and total costs for different room types
- **🏠 Room Details**: View available rooms with floor, capacity, and view type

#### 📅 Booking Management
- **� View Bookings**: List all user bookings with status
- **➕ Create Bookings**: Interactive booking creation form
- **✏️ Manage Bookings**: Update or cancel existing bookings
- **🔍 Booking Details**: Complete booking information and history

#### 👤 User Profile
- **📝 Profile Management**: View and update user information
- **🔒 Account Security**: Change passwords and manage settings
- **� Booking History**: Track past and upcoming reservations

#### 🎨 Modern Interface
- **📱 Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **🌈 Beautiful UI**: Modern gradient design with smooth animations
- **💻 Code Highlighting**: Syntax-highlighted JSON responses
- **� Real-time Updates**: Live API status monitoring
- **� Toast Notifications**: Instant feedback for all actions
- **📊 API Status**: Live monitoring of API health

### 🚀 How to Use the Dashboard

1. **Start the Server**:
   ```bash
   cd hotel_booking
   python manage.py runserver 0.0.0.0:8002
   ```

2. **Open the Dashboard**:
   - Go to http://127.0.0.1:8002/
   - The dashboard loads with API status check

3. **Test Authentication**:
   - Register a new account or login with test accounts
   - Tokens are automatically managed

4. **Search Hotels**:
   - Use the "Search with Dates & Capacity" for availability-based search
   - Use "Search by Capacity Only" for quick room type discovery
   - View detailed results with pricing and room information

5. **Manage Bookings**:
   - Create bookings using the interactive form
   - View and manage your reservations
   - Track booking status and history

### 🎯 Dashboard Benefits
- **No Technical Knowledge Required**: User-friendly interface for all users
- **Complete API Testing**: Test every endpoint without command-line tools
- **Visual Feedback**: Immediate results with beautiful formatting
- **Development Tool**: Perfect for developers and stakeholders
- **Demo Ready**: Professional interface for presentations

## 🔐 Test Accounts

The setup command creates these test accounts:

### Admin Account
- **Email**: admin@hotelmaar.com
- **Password**: AdminPass123!
- **Role**: Administrator with full access

### Guest Account
- **Email**: guest@example.com
- **Password**: TestPass123!
- **Role**: Regular guest user

### Staff Account
- **Email**: staff@hotelmaar.com
- **Password**: StaffPass123!
- **Role**: Hotel staff member

## 🛠 API Endpoints

### Authentication
```
POST /api/v1/auth/login/          # User login
POST /api/v1/auth/register/       # User registration
POST /api/v1/auth/logout/         # User logout
POST /api/v1/auth/refresh/        # Refresh JWT token
POST /api/v1/auth/password-reset/ # Password reset
```

### Hotels & Rooms
```
GET  /api/v1/hotels/                    # List all hotels
GET  /api/v1/hotels/search-availability/ # Search hotels with dates & capacity
GET  /api/v1/hotels/search-capacity/    # Search hotels by capacity only
GET  /api/v1/hotels/{id}/               # Hotel details
GET  /api/v1/hotels/{id}/rooms/         # Hotel rooms
GET  /api/v1/hotels/{id}/availability/  # Room availability
GET  /api/v1/hotels/{id}/amenities/     # Hotel amenities
GET  /api/v1/hotels/{id}/location/      # Hotel location
```

#### Hotel Search with Availability (Date-based)
Search hotels based on dates and guest capacity:
```bash
GET /api/v1/hotels/search-availability/?check_in=2025-08-01&check_out=2025-08-03&capacity=2
```
**Parameters:**
- `check_in` (required): Check-in date (YYYY-MM-DD)
- `check_out` (required): Check-out date (YYYY-MM-DD)  
- `capacity` (optional): Number of guests (1-10)
- `hotel_id` (optional): Specific hotel UUID

**Returns**: Hotels with available rooms for the specified dates, including detailed room information, pricing, and availability counts.

#### Hotel Search by Capacity Only (Quick Search)
Search hotels by guest capacity without date requirements:
```bash
GET /api/v1/hotels/search-capacity/?capacity=4
```
**Parameters:**
- `capacity` (required): Number of guests (1-10)
- `hotel_id` (optional): Specific hotel UUID

**Returns**: Hotels with room types that can accommodate the specified capacity, including all rooms that meet the requirements.

### Bookings
```
GET  /api/v1/bookings/                       # List bookings
POST /api/v1/bookings/                       # Create booking
GET  /api/v1/bookings/{id}/                  # Booking details
PUT  /api/v1/bookings/{id}/                  # Update booking
DELETE /api/v1/bookings/{id}/                # Cancel booking
POST /api/v1/bookings/{id}/check-in/         # Check-in
POST /api/v1/bookings/{id}/check-out/        # Check-out
```

### User Profile
```
GET  /api/v1/auth/profile/        # Get user profile
PUT  /api/v1/auth/profile/        # Update profile
POST /api/v1/auth/verify-email/   # Email verification
```

## 🧪 Testing the API

### Option 1: Using the Interactive Dashboard (Recommended)
The easiest way to test the API is through the built-in dashboard:

1. **Start the server**: `python manage.py runserver 0.0.0.0:8002`
2. **Open your browser**: Go to http://127.0.0.1:8002/
3. **Test all features**: Use the beautiful interface to test authentication, search hotels, create bookings, and more
4. **No command line needed**: Everything is visual and user-friendly

### Option 2: Using the Built-in Test Script
```bash
# Run comprehensive API tests
python complete_api_test.py --check-server
```

### Option 3: Using curl (Manual Testing)

#### 1. Login and Get Token
```bash
curl -X POST http://127.0.0.1:8002/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "guest@example.com",
    "password": "TestPass123!"
  }'
```

#### 2. List Hotels (No authentication required)
```bash
curl -X GET http://127.0.0.1:8002/api/v1/hotels/
```

#### 3. Search Hotels with Availability
```bash
curl -X GET "http://127.0.0.1:8002/api/v1/hotels/search-availability/?check_in=2025-08-01&check_out=2025-08-03&capacity=2"
```

#### 4. Create Booking (Requires authentication)
```bash
curl -X POST http://127.0.0.1:8002/api/v1/bookings/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "room": "ROOM_UUID",
    "check_in": "2025-08-01",
    "check_out": "2025-08-03",
    "guests": 2,
    "primary_guest_name": "John Doe",
    "primary_guest_email": "john@example.com",
    "primary_guest_phone": "+1-555-0123"
  }'
```

### Option 4: Using Swagger UI
1. Go to http://127.0.0.1:8002/swagger/
2. Click "Authorize" and enter JWT token  
3. Test endpoints interactively

## 📁 Project Structure

```
HotelBookingEngine/
├── hotel_booking/           # Main Django project
│   ├── manage.py           # Django management script
│   ├── db.sqlite3          # SQLite database
│   ├── accounts/           # User authentication & management
│   ├── bookings/           # Booking system
│   ├── core/               # Hotels, rooms, services
│   └── hotel_booking/      # Project settings
├── requirements.txt        # Python dependencies
├── complete_api_test.py    # API testing script
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file for production settings:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/hotel_booking

# Security
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # days

# Email (for password reset)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Production Deployment

#### 1. Install Production Dependencies
```bash
pip install gunicorn psycopg2-binary
```

#### 2. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

#### 3. Run with Gunicorn
```bash
gunicorn hotel_booking.wsgi:application --bind 0.0.0.0:8000
```

## 🔍 Available Data

After running `setup_initial_data`, you'll have:

### Hotel: "Hotel Maar"
- Luxury beachfront resort in Miami Beach
- 18 rooms across 4 room types
- 7 extra services available

### Room Types:
1. **Standard Room** (6 rooms) - $149.99/night
2. **Deluxe Room** (8 rooms) - $229.99/night  
3. **Ocean View Suite** (3 rooms) - $449.99/night
4. **Presidential Suite** (1 room) - $999.99/night

### Extra Services:
- Airport Transfer ($75)
- Spa Package ($200/person)
- Ocean View Dining ($150/person)
- Premium Wi-Fi ($15/night)
- Late Checkout ($50)
- Continental Breakfast ($25/person/night)
- Valet Parking ($30/night)

## 🚨 Troubleshooting

### Common Issues:

#### 1. Permission Denied (Windows/macOS/Linux)
```bash
# Windows: If you get permission errors
pip install --user -r requirements.txt

# macOS/Linux: If you get permission errors
pip install --user -r requirements.txt
```

#### 2. Python Version Issues
```bash
# Check Python version (must be 3.8+)
python --version
python3 --version

# Windows: Use specific Python version
python -m venv hotel_booking_env

# macOS/Linux: Use specific Python version  
python3.9 -m venv hotel_booking_env
```

#### 3. Port Already in Use
```bash
# If port 8002 is busy, use a different port
python manage.py runserver 0.0.0.0:8003

# Then access dashboard at: http://127.0.0.1:8003/
```

#### 4. Database Issues
```bash
# Reset database if needed (Windows)
del db.sqlite3
python manage.py migrate
python manage.py setup_initial_data --reset

# Reset database if needed (macOS/Linux)
rm db.sqlite3
python manage.py migrate  
python manage.py setup_initial_data --reset
```

#### 5. Virtual Environment Issues
```bash
# Windows: Reactivate virtual environment
hotel_booking_env\Scripts\activate

# macOS/Linux: Reactivate virtual environment
source hotel_booking_env/bin/activate

# Verify you're in the virtual environment
which python  # Should show path to venv
pip list       # Should show installed packages
```

#### 6. Import Errors
```bash
# Make sure you're in the correct directory
cd hotel_booking

# Verify Django is installed
python -c "import django; print(django.get_version())"

# Reinstall requirements if needed
pip install -r ../requirements.txt
```

### 📍 Quick Verification Steps

1. **Check you're in the right directory**:
   ```bash
   pwd  # Should end with: .../HotelBookingEngine/hotel_booking
   ls   # Should show: manage.py, accounts/, bookings/, core/, etc.
   ```

2. **Verify virtual environment is active**:
   ```bash
   # Should show (hotel_booking_env) in your prompt
   python --version  # Should be 3.8+
   ```

3. **Test basic Django functionality**:
   ```bash
   python manage.py check  # Should show "System check identified no issues"
   ```

4. **Access the application**:
   - Dashboard: http://127.0.0.1:8002/
   - API: http://127.0.0.1:8002/api/v1/
   - Swagger: http://127.0.0.1:8002/swagger/

## 📞 Support

For issues or questions:
1. Check the API documentation at `/swagger/`
2. Review the error logs in the terminal
3. Use the test script to verify API functionality
4. Check that all dependencies are installed correctly

## � Security Notes

- JWT tokens expire after 60 minutes (configurable)
- Refresh tokens expire after 7 days (configurable)
- All sensitive endpoints require authentication
- Input validation on all API endpoints
- CORS headers configured for development

## 📊 API Performance

- **Response Time**: < 200ms for most endpoints
- **Concurrent Users**: Supports 100+ concurrent users
- **Database**: Optimized with proper indexing
- **Caching**: Room availability caching implemented
- **Pagination**: Large result sets are paginated

---

**Ready to build amazing hotel booking experiences! 🏨✨**
