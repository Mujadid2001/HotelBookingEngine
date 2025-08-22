# 🚀 Production Deployment Guide
# Hotel Booking API (Backend Only)

## 📋 Production Readiness Status

### ✅ **READY FOR DEPLOYMENT**
- ✅ Clean API-only backend structure
- ✅ JWT Authentication for frontend integration
- ✅ Comprehensive API documentation (Swagger/ReDoc)
- ✅ Production-optimized Docker configuration
- ✅ Security headers and HTTPS support
- ✅ Database migrations and health checks
- ✅ Logging and monitoring setup

### ⚠️ **CONFIGURATION REQUIRED**
- ⚠️ Generate production SECRET_KEY
- ⚠️ Configure database credentials
- ⚠️ Set up email SMTP settings
- ⚠️ Configure CORS for your frontend domain
- ⚠️ Add SSL certificates (recommended)

## 🔧 **QUICK PRODUCTION SETUP**

### 1. **Environment Configuration**
```bash
# Copy environment template
cp .env.template .env

# Edit .env with your production values:
# - Generate a 50+ character SECRET_KEY
# - Set your database credentials
# - Configure email settings
# - Set ALLOWED_HOSTS to your domain
# - Configure CORS_ALLOWED_ORIGINS for your frontend
```

### 2. **Deploy with Docker (Recommended)**
```bash
# Start all services
./deploy.sh

# Or manually:
docker-compose -f docker-compose.prod.yml up -d
```

### 3. **Verify Deployment**
- ✅ Health Check: `http://your-domain/api/v1/health/`
- ✅ API Docs: `http://your-domain/api/v1/docs/`
- ✅ Admin Panel: `http://your-domain/admin/`

## 🌐 **API Endpoints for Frontend Integration**

### Authentication
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - User login (returns JWT tokens)
- `POST /api/v1/auth/logout/` - User logout
- `POST /api/v1/auth/refresh/` - Refresh JWT token
- `GET /api/v1/auth/profile/` - Get user profile

### Hotel Search & Booking
- `GET /api/v1/hotels/` - List all hotels
- `GET /api/v1/hotels/{id}/` - Hotel details
- `POST /api/v1/bookings/search-rooms/` - Search available rooms
- `POST /api/v1/bookings/complete-booking/` - Complete booking flow
- `GET /api/v1/bookings/` - User's bookings
- `GET /api/v1/bookings/{reference}/` - Booking details

### Health & Status
- `GET /api/v1/health/` - System health check
- `GET /api/v1/` - API information

## 🔒 **Security Features Implemented**

- ✅ **JWT Authentication** - Secure token-based auth
- ✅ **CORS Protection** - Configurable for your frontend
- ✅ **Rate Limiting** - API and auth endpoint protection
- ✅ **Security Headers** - XSS, CSRF, clickjacking protection
- ✅ **Input Validation** - All API inputs validated
- ✅ **SQL Injection Protection** - Django ORM protection
- ✅ **Environment Variables** - No secrets in code

## 📊 **Monitoring & Maintenance**

### Health Monitoring
```bash
# Check API health
curl http://your-domain/api/v1/health/

# View logs
docker-compose -f docker-compose.prod.yml logs api
docker-compose -f docker-compose.prod.yml logs db
docker-compose -f docker-compose.prod.yml logs nginx
```

### Database Backup
```bash
# Backup database
docker-compose -f docker-compose.prod.yml exec db pg_dump -U hotel_booking_user hotel_booking_prod > backup.sql

# Restore database
docker-compose -f docker-compose.prod.yml exec -T db psql -U hotel_booking_user hotel_booking_prod < backup.sql
```

## � **Hosting Recommendations**

### Small to Medium Scale (up to 1000 users/day)
- **DigitalOcean Droplet** - $20-40/month
- **AWS EC2 t3.small** - $15-25/month  
- **Google Cloud VM** - $20-35/month

### Enterprise Scale (1000+ users/day)
- **AWS ECS/EKS with RDS** - $100-500/month
- **Google Kubernetes Engine** - $100-400/month
- **Azure Container Instances** - $100-450/month

## � **Frontend Integration Guide**

### Authentication Flow
```javascript
// 1. User login
const loginResponse = await fetch('/api/v1/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
});
const { tokens } = await loginResponse.json();

// 2. Store tokens
localStorage.setItem('access_token', tokens.access);
localStorage.setItem('refresh_token', tokens.refresh);

// 3. Use token for API calls
const apiCall = await fetch('/api/v1/bookings/', {
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json'
    }
});
```

### Hotel Search
```javascript
const searchRooms = async (searchCriteria) => {
    const response = await fetch('/api/v1/bookings/search-rooms/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            check_in: '2025-08-25',
            check_out: '2025-08-27',
            guests: 2,
            location: 'New York'
        })
    });
    return await response.json();
};
```

### Complete Booking
```javascript
const createBooking = async (bookingData) => {
    const response = await fetch('/api/v1/bookings/complete-booking/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(bookingData)
    });
    return await response.json();
};
```

## 🚀 **DEPLOYMENT CHECKLIST**

### Pre-Deployment
- [ ] Generate secure SECRET_KEY (50+ characters)
- [ ] Configure production database
- [ ] Set up email SMTP settings
- [ ] Configure CORS for your frontend domain
- [ ] Set ALLOWED_HOSTS to your domain
- [ ] Review all environment variables

### Deployment
- [ ] Run `./deploy.sh` or docker-compose
- [ ] Verify health check endpoint
- [ ] Test authentication endpoints
- [ ] Test booking flow
- [ ] Create admin superuser

### Post-Deployment
- [ ] Set up SSL certificates
- [ ] Configure domain DNS
- [ ] Set up monitoring/alerting
- [ ] Configure automated backups
- [ ] Document API for frontend team

## 📞 **Support & Documentation**

- **API Documentation:** `https://your-domain/api/v1/docs/`
- **Admin Panel:** `https://your-domain/admin/`
- **Health Check:** `https://your-domain/api/v1/health/`
- **OpenAPI Schema:** `https://your-domain/api/v1/schema/`

---

## ⚡ **READY FOR PRODUCTION**

Your Hotel Booking API is now **production-ready** with:
- 🔒 Enterprise-grade security
- 🚀 Optimized Docker deployment
- 📖 Complete API documentation
- 🔍 Health monitoring
- 🌐 Frontend-ready endpoints

**Estimated deployment time:** 15-30 minutes with proper configuration.
