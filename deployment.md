
# Hotel Booking Engine API - AlmaLinux RHEL Deployment Guide

A comprehensive Django REST API for hotel booking management with search, booking flow, user authentication, room management, and email notifications.

## 🏨 API Overview

This Hotel Booking Engine provides:

### **Core Features**
- **User Authentication**: JWT-based authentication with registration, login, and profile management
- **Hotel Management**: Complete hotel information, room types, amenities, and policies
- **Advanced Search**: Location-based search, availability checking, capacity filtering
- **Booking Management**: Full booking lifecycle from search to checkout
- **Real-time Availability**: Dynamic room availability checking with conflict detection
- **Payment Processing**: Integrated payment flow with booking confirmation
- **Email Notifications**: Automated booking confirmations and notifications
- **Dynamic Pricing**: Real-time price calculation with taxes and extras

### **API Endpoints**
- **Authentication**: `/api/v1/auth/` - User registration, login, profile management
- **Hotels**: `/api/v1/hotels/` - Hotel search, details, rooms, amenities
- **Bookings**: `/api/v1/bookings/` - Booking management, search, create, update, cancel
- **Health Check**: `/api/v1/health/` - API health monitoring
- **Documentation**: `/api/v1/docs/` - Interactive Swagger UI documentation

### **Technology Stack**
- **Backend**: Django 5.2.4 + Django REST Framework
- **Database**: PostgreSQL 15 with Redis for caching
- **Authentication**: JWT with SimpleJWT
- **Documentation**: drf-spectacular (OpenAPI/Swagger)
- **Security**: Rate limiting, CORS, comprehensive middleware
- **Email**: SMTP integration for notifications
- **Deployment**: Containerized with Podman/Docker

This guide provides step-by-step instructions for deploying this Hotel Booking Engine API on AlmaLinux/RHEL VPS using Podman Compose.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Install Required Software](#install-required-software)
4. [Project Setup](#project-setup)
5. [Environment Configuration](#environment-configuration)
6. [Podman Compose Configuration](#podman-compose-configuration)
7. [Build and Deploy Application](#build-and-deploy-application)
8. [Nginx Configuration](#nginx-configuration)
9. [SSL Certificate Setup](#ssl-certificate-setup)
10. [Firewall Configuration](#firewall-configuration)
11. [System Services](#system-services)
12. [Testing and Verification](#testing-and-verification)
13. [Monitoring and Maintenance](#monitoring-and-maintenance)
14. [Troubleshooting](#troubleshooting)

## Prerequisites

- AlmaLinux 8/9 or RHEL 8/9 VPS with root or sudo access
- Minimum 4GB RAM, 2 CPU cores, 30GB storage (recommended for production)
- Domain name `api.marhotels.com.sa` pointed to your VPS IP address
- SSH access to the server
- Basic knowledge of Linux command line

### Hardware Requirements
- **Development**: 2GB RAM, 1 CPU, 20GB storage
- **Production**: 4GB+ RAM, 2+ CPU cores, 30GB+ storage
- **High Traffic**: 8GB+ RAM, 4+ CPU cores, 50GB+ storage

## Server Setup

### 1. Update System
```bash
sudo dnf update -y
sudo dnf install -y epel-release
sudo dnf update -y
```

### 2. Create Application User
```bash
sudo useradd -m -s /bin/bash hotelapi
sudo usermod -aG wheel hotelapi
sudo passwd hotelapi
```

### 3. Configure SSH (Optional but Recommended)
```bash
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

## Install Required Software

### 1. Install Podman and Podman Compose
```bash
# Install Podman and required tools
sudo dnf install -y podman podman-docker buildah skopeo

# Install podman-compose using pip
sudo dnf install -y python3-pip python3-devel
sudo pip3 install podman-compose

# Alternative: Install from package if available
# sudo dnf install -y podman-compose

# Verify installation
podman --version
podman-compose --version

# Enable podman socket for systemd integration
systemctl --user enable --now podman.socket
loginctl enable-linger $(whoami)
```

### 2. Install Nginx
```bash
sudo dnf install -y nginx
sudo systemctl enable nginx
```

### 3. Install Git
```bash
sudo dnf install -y git
```

### 4. Install Additional Tools
```bash
sudo dnf install -y curl wget nano vim htop iotop net-tools firewalld
```

## Project Setup

### 1. Switch to Application User
```bash
su - hotelapi
```

### 2. Clone or Upload Your Project
```bash
# Option A: Clone from Git (if using version control)
git clone https://github.com/Mujadid2001/HotelBookingEngine.git
cd HotelBookingEngine

# Option B: Create directory and upload files
mkdir -p ~/HotelBookingEngine
cd ~/HotelBookingEngine
# Upload your project files here using scp, rsync, or SFTP
```

### 3. Set Proper Permissions
```bash
chmod +x hotel_booking/manage.py
find . -type f -name "*.py" -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;
```

## Environment Configuration

### 1. Create Production Environment File
```bash
cd ~/HotelBookingEngine
nano .env
```

### 2. Configure .env File
```bash
# Django Configuration
DJANGO_SETTINGS_MODULE=hotel_booking.deployment
SECRET_KEY="your-super-secret-key-here-make-it-long-and-random-at-least-50-characters"
DEBUG=False
ALLOWED_HOSTS=api.marhotels.com.sa,www.api.marhotels.com.sa,localhost,127.0.0.1

# Database Configuration
DB_NAME=hotelMaarDB
DB_USER=hotelapi_user
DB_PASSWORD="your-secure-database-password-with-special-characters"
DB_HOST=db
DB_PORT=5432

# Redis Configuration
REDIS_PASSWORD="your-secure-redis-password-123"

# Email Configuration (Gmail example)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD="your-app-password"
DEFAULT_FROM_EMAIL="Mar Hotels API <noreply@marhotels.com.sa>"
SERVER_EMAIL="Mar Hotels API <admin@marhotels.com.sa>"

# CORS Configuration
CORS_ALLOWED_ORIGINS="https://api.marhotels.com.sa,https://www.marhotels.com.sa"

# Security Settings (Production)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

### 3. Generate Secret Key
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Podman Compose Configuration

### 1. Create Production Podman Compose File
```bash
cd ~/HotelBookingEngine
nano podman-compose.yml
```

### 2. Configure podman-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    command: >
      sh -c "cd /app/hotel_booking &&
             python manage.py migrate --noinput &&
             python manage.py collectstatic --noinput &&
             gunicorn hotel_booking.wsgi:application --bind 0.0.0.0:8000 --timeout 120 --workers 3 --max-requests 1000 --max-requests-jitter 100"
    working_dir: /app
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
      - logs_volume:/app/logs
    env_file:
      - .env
    environment:
      - DJANGO_SETTINGS_MODULE=hotel_booking.deployment
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "127.0.0.1:8000:8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network
    # Security: No external port exposure

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    restart: unless-stopped
    networks:
      - app-network
    # Security: No external port exposure

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
  logs_volume:

networks:
  app-network:
    driver: bridge
```

### 3. Create Podman Secrets (Optional for Enhanced Security)
```bash
# Create secure password files
echo "your-secure-database-password" | podman secret create db_password -
echo "your-secure-redis-password" | podman secret create redis_password -

# Update podman-compose.yml to use secrets if desired
```

## Build and Deploy Application

### 1. Build the Application with Podman
```bash
cd ~/HotelBookingEngine

# Pull base images first
podman pull python:3.12-slim
podman pull postgres:15-alpine
podman pull redis:7-alpine

# Build the application
podman-compose build --no-cache web
```

### 2. Start the Services
```bash
# Start all services
podman-compose up -d

# Verify all containers are running
podman-compose ps
```

### 3. Check Container Status and Logs
```bash
# Check status
podman-compose ps

# View logs for all services
podman-compose logs

# View specific service logs
podman-compose logs web
podman-compose logs db
podman-compose logs redis

# Follow logs in real-time
podman-compose logs -f web
```

### 4. Initialize Database and Create Superuser
```bash
# Wait for database to be ready (check logs first)
podman-compose logs db | grep "database system is ready"

# Run initial migrations (should already be done by startup command)
podman-compose exec web python manage.py migrate

# Create Django superuser for admin access
podman-compose exec web python manage.py createsuperuser

# Collect static files (should already be done by startup command)
podman-compose exec web python manage.py collectstatic --noinput
```

### 5. Test Application Connectivity
```bash
# Test API health endpoint
curl http://localhost:8000/api/v1/health/

# Test API root endpoint
curl http://localhost:8000/api/v1/

# Test database connectivity
podman-compose exec db pg_isready -U hotelapi_user -d hotelMaarDB

# Test through nginx (if configured)
curl http://localhost:80/api/v1/health/
```

### 6. Verify Container Resources
```bash
# Check container resource usage
podman stats

# Check volume usage
podman volume ls
podman system df
```

## 🔧 Deployment Issues and Solutions

During deployment testing, several issues were identified and resolved. Here are the common problems and their solutions:

### Issue 1: Security Middleware Error
**Problem**: The security middleware in `core/security_middleware.py` had an error accessing `request.content_length`.

**Error Message**:
```
AttributeError: 'WSGIRequest' object has no attribute 'content_length'
```

**Solution**: The middleware was accessing a non-existent attribute. Fixed by using `request.META.get('CONTENT_LENGTH')` instead:

```python
# In hotel_booking/core/security_middleware.py
def process_request(self, request):
    max_size = getattr(settings, 'DATA_UPLOAD_MAX_MEMORY_SIZE', 10 * 1024 * 1024)
    
    # Get content length from META headers
    content_length = request.META.get('CONTENT_LENGTH')
    if content_length:
        try:
            content_length = int(content_length)
            if content_length > max_size:
                logger.warning(f'Request size {content_length} exceeds limit from {request.META.get("REMOTE_ADDR")}')
                return HttpResponseForbidden('Request too large')
        except (ValueError, TypeError):
            # Invalid content length, let it pass
            pass
    
    return None
```

**Prevention**: Always test middleware thoroughly before deployment.

### Issue 2: Environment Configuration
**Problem**: The `.env` file referenced Redis services that weren't configured in the deployment.

**Solution**: Remove Redis configuration from `.env` file for basic deployment or add Redis service to `podman-compose.yml`:

```bash
# Remove these lines from .env for basic deployment:
# REDIS_URL=redis://:redis_password_123@redis:6379/0
# REDIS_PASSWORD=redis_password_123
# CACHE_BACKEND=django_redis.cache.RedisCache
# CACHE_LOCATION=redis://:redis_password_123@redis:6379/1
# SESSION_ENGINE=django.contrib.sessions.backends.cache
```

### Issue 3: Container Build Optimization
**Problem**: Initial builds were slow due to dependencies installation.

**Solution**: Optimized Dockerfile and podman-compose configuration:

```dockerfile
# Optimized layer caching in Dockerfile
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . /app/
```

### Issue 4: Static Files Configuration
**Problem**: Static files paths mismatch between nginx and Django containers.

**Solution**: Ensured consistent volume mapping in `podman-compose.yml`:

```yaml
volumes:
  - static_volume:/app/static
  - media_volume:/app/media
```

And updated nginx.conf to use container paths:

```nginx
location /static/ {
    alias /app/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

## 🚨 Critical Deployment Steps

### Step 1: Pre-Deployment Verification
```bash
# Verify all configuration files exist
ls -la podman-compose.yml .env nginx.conf Dockerfile

# Check .env file has all required variables
grep -E "SECRET_KEY|DB_PASSWORD|ALLOWED_HOSTS" .env

# Validate YAML syntax
podman-compose config
```

### Step 2: Safe Container Restart Procedure
```bash
# Stop containers gracefully
podman-compose down

# Rebuild if code changes were made
podman-compose build web

# Start with logs monitoring
podman-compose up -d && podman-compose logs -f web
```

### Step 3: Health Check Verification
```bash
# Wait for containers to start (30-45 seconds)
sleep 45

# Test endpoints in order
curl -f http://localhost:80/api/v1/health/
curl -f http://localhost:80/api/v1/
curl -f http://localhost:80/api/v1/docs/

# Check container health
podman-compose ps | grep healthy
```

### Step 4: Database Migration Safety
```bash
# Always backup before migrations in production
podman-compose exec db pg_dump -U hotelapi_user hotelMaarDB > backup_$(date +%Y%m%d_%H%M%S).sql

# Run migrations with verbose output
podman-compose exec web python manage.py migrate --verbosity=2

# Verify migration status
podman-compose exec web python manage.py showmigrations
```

## ✅ Deployment Verification Results

### Successful Local Testing Results

The following endpoints were successfully tested during local deployment:

#### 1. Health Check Endpoint
```bash
curl http://localhost:80/api/v1/health/
# Response: HTTP 200 OK
# Content: {"status": "healthy", "timestamp": 1756050449.4315, "database": "connected", "cache": "connected", "response_time_ms": 2.79}
```

#### 2. API Root Endpoint
```bash
curl http://localhost:80/api/v1/
# Response: HTTP 200 OK
# Content: {"message": "Hotel Booking API", "version": "v1.0", "status": "operational", "endpoints": {...}}
```

#### 3. API Documentation
```bash
curl http://localhost:80/api/v1/docs/
# Response: HTTP 200 OK
# Content: Full Swagger UI documentation page
```

#### 4. Hotels Listing Endpoint
```bash
curl http://localhost:80/api/v1/hotels/
# Response: HTTP 200 OK
# Content: {"count":0,"next":null,"previous":null,"results":[]}
```

### Container Status Verification
```bash
podman-compose ps
# All containers showing as healthy:
# - hotelbookingengine-db-1: Up (healthy)
# - hotelbookingengine-web-1: Up (healthy) 
# - hotelbookingengine-nginx-1: Up
```

### Database Migration Success
```bash
# All migrations applied successfully:
# - contenttypes, auth, accounts, admin, core, bookings, sessions, token_blacklist
# Static files collected: 163 static files copied
# Gunicorn started with 2 workers on port 8000
```

## 📋 Pre-Production Checklist

Before deploying to production, ensure the following:

### Configuration Files
- [ ] `.env` file contains production values (not test values)
- [ ] `SECRET_KEY` is properly generated and secure (50+ characters)
- [ ] `DEBUG=False` in production environment
- [ ] Database credentials are secure and different from defaults
- [ ] Email configuration is properly set up
- [ ] `ALLOWED_HOSTS` includes your production domain

### Security Configuration
- [ ] SSL certificates are configured
- [ ] Firewall rules are properly configured
- [ ] Nginx security headers are enabled
- [ ] Rate limiting is configured appropriately
- [ ] File upload restrictions are in place

### Performance Optimization
- [ ] Database connection pooling is configured
- [ ] Static files are properly served through nginx
- [ ] Caching is configured (Redis if needed)
- [ ] Gunicorn worker count is optimized for server resources

### Monitoring and Backup
- [ ] Log rotation is configured
- [ ] Backup scripts are set up and tested
- [ ] Monitoring scripts are in place
- [ ] Health check endpoints are accessible

## 🎯 Production Deployment Commands

### Quick Start Commands for AlmaLinux/RHEL
```bash
# 1. Clone and setup
git clone https://github.com/Mujadid2001/HotelBookingEngine.git
cd HotelBookingEngine
cp .env.example .env  # Configure your environment variables

# 2. Build and deploy
podman-compose build
podman-compose up -d

# 3. Initialize database
podman-compose exec web python manage.py migrate
podman-compose exec web python manage.py createsuperuser

# 4. Test deployment
curl http://localhost:80/api/v1/health/
```

### Production Startup Sequence
```bash
# 1. Verify prerequisites
systemctl --user is-active podman.socket
sudo systemctl is-active nginx

# 2. Start application
sudo systemctl start hotel-api

# 3. Verify all services
podman-compose ps
curl -f https://yourdomain.com/api/v1/health/

# 4. Monitor startup
journalctl -u hotel-api -f
```

## 🔍 Troubleshooting Quick Reference

### Container Won't Start
```bash
# Check container logs
podman-compose logs service_name

# Check available resources
df -h
free -h

# Verify network connectivity
podman network ls
podman network inspect hotelbookingengine_app-network
```

### Application Errors
```bash
# Django check
podman-compose exec web python manage.py check

# Database connectivity
podman-compose exec web python manage.py dbshell

# Static files check
podman-compose exec web python manage.py collectstatic --dry-run
```

### Performance Issues
```bash
# Monitor resource usage
podman stats --no-stream

# Check database performance
podman-compose exec db psql -U hotelapi_user -d hotelMaarDB -c "SELECT version();"

# Verify nginx configuration
podman-compose exec nginx nginx -t
```

## Nginx Configuration

### 1. Create Nginx Configuration
```bash
sudo nano /etc/nginx/conf.d/hotel_booking.conf
```

### 2. Add Nginx Configuration
```nginx
# Upstream configuration for load balancing
upstream hotel_api {
    least_conn;
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
}

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api_general:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=api_auth:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=api_booking:10m rate=20r/m;

# Cache configuration
proxy_cache_path /var/cache/nginx/api levels=1:2 keys_zone=api_cache:10m max_size=100m inactive=60m;

server {
    listen 80;
    server_name api.marhotels.com.sa www.api.marhotels.com.sa;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self';" always;
    
    # Hide server information
    server_tokens off;
    
    # Client configuration
    client_max_body_size 20M;
    client_body_buffer_size 128k;
    
    # Authentication endpoints (stricter rate limiting)
    location /api/v1/auth/ {
        limit_req zone=api_auth burst=10 nodelay;
        limit_req_status 429;
        
        proxy_pass http://hotel_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # No caching for auth endpoints
        proxy_no_cache 1;
        proxy_cache_bypass 1;
    }
    
    # Booking endpoints (moderate rate limiting)
    location /api/v1/bookings/ {
        limit_req zone=api_booking burst=30 nodelay;
        limit_req_status 429;
        
        proxy_pass http://hotel_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # General API endpoints
    location /api/ {
        limit_req zone=api_general burst=20 nodelay;
        limit_req_status 429;
        
        proxy_pass http://hotel_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Cache static responses
        proxy_cache api_cache;
        proxy_cache_valid 200 5m;
        proxy_cache_key "$scheme$request_method$host$request_uri";
        add_header X-Cache-Status $upstream_cache_status;
    }

    # Root redirect to API documentation
    location = / {
        return 301 /api/v1/docs/;
    }
    
    # Health check endpoint (no rate limiting)
    location /api/v1/health/ {
        proxy_pass http://hotel_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Cache health checks briefly
        proxy_cache api_cache;
        proxy_cache_valid 200 30s;
    }

    # Static files
    location /static/ {
        alias /home/hotelapi/HotelBookingEngine/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        
        # Gzip compression
        gzip on;
        gzip_types text/css application/javascript text/javascript application/json;
    }

    # Media files
    location /media/ {
        alias /home/hotelapi/HotelBookingEngine/media/;
        expires 7d;
        add_header Cache-Control "public";
        
        # Security for uploaded files
        location ~* \.(php|php\d+|phtml|pl|asp|aspx|shtml|sh|cgi)$ {
            deny all;
        }
    }

    # Security: Deny access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ /\.env {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ /(docker-compose|Dockerfile|requirements\.txt|manage\.py) {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Robots.txt
    location = /robots.txt {
        return 200 "User-agent: *\nDisallow: /api/v1/admin/\nDisallow: /static/admin/\n";
        add_header Content-Type text/plain;
    }
}
```

### 3. Create Required Directories and Set Permissions
```bash
# Create nginx cache directory
sudo mkdir -p /var/cache/nginx/api
sudo chown nginx:nginx /var/cache/nginx/api

# Create static and media directories
mkdir -p ~/HotelBookingEngine/staticfiles
mkdir -p ~/HotelBookingEngine/media
sudo chown -R hotelapi:hotelapi ~/HotelBookingEngine/

# Set proper permissions for nginx to access static files
sudo setfacl -R -m u:nginx:rx /home/hotelapi/HotelBookingEngine/staticfiles/
sudo setfacl -R -m u:nginx:rx /home/hotelapi/HotelBookingEngine/media/
```

### 4. Test and Enable Nginx
```bash
# Test nginx configuration
sudo nginx -t

# If test passes, start and enable nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Check nginx status
sudo systemctl status nginx
```

## SSL Certificate Setup

### 1. Install Certbot
```bash
sudo dnf install -y certbot python3-certbot-nginx
```

### 2. Obtain SSL Certificate
```bash
sudo certbot --nginx -d api.marhotels.com.sa
```

### 3. Set Up Auto-Renewal
```bash
sudo crontab -e
```

Add this line:
```bash
0 3 * * * /usr/bin/certbot renew --quiet
```

### 4. Test Auto-Renewal
```bash
sudo certbot renew --dry-run
```

## Firewall Configuration

### 1. Configure Firewall
```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

### 2. Check Firewall Status
```bash
sudo firewall-cmd --list-all
```

## System Services

### 1. Create Systemd Service for Podman Compose
```bash
sudo nano /etc/systemd/system/hotel-api.service
```

```ini
[Unit]
Description=Hotel Booking API - Podman Compose Service
Documentation=https://github.com/Mujadid2001/HotelBookingEngine
Requires=network-online.target
After=network-online.target
RequiresMountsFor=%h

[Service]
Type=oneshot
RemainAfterExit=yes
User=hotelapi
Group=hotelapi
WorkingDirectory=/home/hotelapi/HotelBookingEngine
Environment=PATH=/usr/local/bin:/usr/bin:/bin
Environment=XDG_RUNTIME_DIR=/run/user/1001

# Start services
ExecStart=/usr/local/bin/podman-compose up -d
# Stop services
ExecStop=/usr/local/bin/podman-compose down
# Reload services
ExecReload=/usr/local/bin/podman-compose restart

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=/home/hotelapi/HotelBookingEngine

# Restart settings
Restart=on-failure
RestartSec=30s
TimeoutStartSec=300
TimeoutStopSec=120

[Install]
WantedBy=multi-user.target
```

### 2. Create Podman Auto-Update Service
```bash
sudo nano /etc/systemd/system/podman-auto-update.service
```

```ini
[Unit]
Description=Podman Auto Update
Documentation=man:podman-auto-update(1)

[Service]
Type=oneshot
ExecStart=/usr/bin/podman auto-update
User=hotelapi
Group=hotelapi
```

### 3. Create Auto-Update Timer
```bash
sudo nano /etc/systemd/system/podman-auto-update.timer
```

```ini
[Unit]
Description=Podman Auto Update Timer
Documentation=man:podman-auto-update(1)

[Timer]
OnCalendar=daily
RandomizedDelaySec=15m
Persistent=true

[Install]
WantedBy=timers.target
```

### 4. Enable and Start Services
```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable and start the hotel API service
sudo systemctl enable hotel-api.service
sudo systemctl start hotel-api.service

# Enable auto-update timer
sudo systemctl enable podman-auto-update.timer
sudo systemctl start podman-auto-update.timer

# Check service status
sudo systemctl status hotel-api.service
sudo systemctl status podman-auto-update.timer

# View service logs
journalctl -u hotel-api.service -f
```

### 5. Configure Log Management
```bash
# Create log rotation for container logs
sudo nano /etc/logrotate.d/podman-containers
```

```bash
/home/hotelapi/.local/share/containers/storage/overlay-containers/*/userdata/ctr.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
    su hotelapi hotelapi
}
```

## Testing and Verification

### 1. Test API Endpoints
```bash
# Test health endpoint
curl -s https://api.marhotels.com.sa/api/v1/health/ | jq

# Test API root
curl -s https://api.marhotels.com.sa/api/v1/ | jq

# Test authentication endpoint (should return 405 for GET)
curl -I https://api.marhotels.com.sa/api/v1/auth/login/

# Test hotel search
curl -s "https://api.marhotels.com.sa/api/v1/hotels/" | jq

# Test API documentation
curl -I https://api.marhotels.com.sa/api/v1/docs/

# Test hotel search with parameters
curl -s "https://api.marhotels.com.sa/api/v1/hotels/search-availability/?check_in=2025-12-25&check_out=2025-12-27&guests=2" | jq
```

### 2. Test User Registration and Authentication
```bash
# Register a test user
curl -X POST https://api.marhotels.com.sa/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "first_name": "Test",
    "last_name": "User",
    "phone_number": "+1234567890"
  }' | jq

# Login with test user
curl -X POST https://api.marhotels.com.sa/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpassword123"
  }' | jq
```

### 2. Check SSL Certificate
```bash
curl -I https://api.marhotels.com.sa
openssl s_client -connect api.marhotels.com.sa:443 -servername api.marhotels.com.sa
```

### 3. Performance and Load Testing
```bash
# Install apache bench for testing
sudo dnf install -y httpd-tools

# Test API health endpoint performance
ab -n 100 -c 10 https://api.marhotels.com.sa/api/v1/health/

# Test hotel search performance
ab -n 50 -c 5 "https://api.marhotels.com.sa/api/v1/hotels/"

# Test rate limiting (should return 429 after threshold)
for i in {1..20}; do
  curl -w "%{http_code}\n" -o /dev/null -s https://api.marhotels.com.sa/api/v1/hotels/
  sleep 0.1
done
```

### 4. Database and Redis Connectivity Tests
```bash
# Test database connectivity
podman-compose exec db pg_isready -U hotelapi_user -d hotelMaarDB

# Test database connection from Django
podman-compose exec web python manage.py dbshell --command="SELECT version();"

# Test Redis connectivity
podman-compose exec redis redis-cli ping

# Check Redis authentication
podman-compose exec redis redis-cli auth "${REDIS_PASSWORD}" ping
```

## Monitoring and Maintenance

### 1. Set Up Log Rotation
```bash
sudo nano /etc/logrotate.d/hotel-api
```

```bash
/home/hotelapi/HotelBookingEngine/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    su hotelapi hotelapi
}
```

### 2. Create Comprehensive Backup Script
```bash
nano ~/backup.sh
```

```bash
#!/bin/bash

# Hotel Booking API Backup Script
# Run this script daily via cron

BACKUP_DIR="/home/hotelapi/backups"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/home/hotelapi/HotelBookingEngine"
RETENTION_DAYS=7

# Create backup directory
mkdir -p $BACKUP_DIR

echo "Starting backup at $(date)"

# Backup database
echo "Backing up PostgreSQL database..."
podman-compose exec -T db pg_dump -U hotelapi_user hotelMaarDB | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup Redis data
echo "Backing up Redis data..."
podman-compose exec redis redis-cli --rdb /data/dump.rdb save
tar -czf $BACKUP_DIR/redis_backup_$DATE.tar.gz -C $APP_DIR/redis_data dump.rdb

# Backup media files
echo "Backing up media files..."
if [ -d "$APP_DIR/media" ] && [ "$(ls -A $APP_DIR/media)" ]; then
    tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz -C $APP_DIR media/
else
    echo "No media files to backup"
fi

# Backup configuration files
echo "Backing up configuration files..."
tar -czf $BACKUP_DIR/config_backup_$DATE.tar.gz -C $APP_DIR .env podman-compose.yml nginx.conf

# Backup application logs
echo "Backing up application logs..."
if [ -d "$APP_DIR/logs" ] && [ "$(ls -A $APP_DIR/logs)" ]; then
    tar -czf $BACKUP_DIR/logs_backup_$DATE.tar.gz -C $APP_DIR logs/
fi

# Clean up old backups
echo "Cleaning up backups older than $RETENTION_DAYS days..."
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Create backup summary
echo "Backup completed at $(date)" > $BACKUP_DIR/backup_summary_$DATE.txt
ls -lh $BACKUP_DIR/*_$DATE.* >> $BACKUP_DIR/backup_summary_$DATE.txt

echo "Backup completed successfully!"
```

```bash
chmod +x ~/backup.sh
```

### 3. Set Up Automated Backups
```bash
# Add backup to crontab
crontab -e
```

Add this line for daily backups at 2 AM:
```bash
0 2 * * * /home/hotelapi/backup.sh >> /home/hotelapi/backup.log 2>&1
```

### 4. Create Monitoring Script
```bash
nano ~/monitor.sh
```

```bash
#!/bin/bash

# Hotel Booking API Monitoring Script

echo "=== Hotel Booking API Status Report ==="
echo "Generated at: $(date)"
echo

# Check systemd service status
echo "=== Service Status ==="
systemctl --user is-active hotel-api.service
echo

# Check container status
echo "=== Container Status ==="
cd /home/hotelapi/HotelBookingEngine
podman-compose ps
echo

# Check API health
echo "=== API Health Check ==="
health_response=$(curl -s -w "%{http_code}" http://localhost:8000/api/v1/health/)
if [[ "${health_response: -3}" == "200" ]]; then
    echo "✅ API Health: OK"
else
    echo "❌ API Health: FAILED (HTTP ${health_response: -3})"
fi
echo

# Check database connectivity
echo "=== Database Status ==="
if podman-compose exec -T db pg_isready -U hotelapi_user -d hotelMaarDB >/dev/null 2>&1; then
    echo "✅ Database: Connected"
else
    echo "❌ Database: Connection Failed"
fi

# Check Redis connectivity
echo "=== Redis Status ==="
if podman-compose exec -T redis redis-cli ping >/dev/null 2>&1; then
    echo "✅ Redis: Connected"
else
    echo "❌ Redis: Connection Failed"
fi

# Check disk usage
echo
echo "=== Disk Usage ==="
df -h /home/hotelapi/
echo

# Check memory usage
echo "=== Memory Usage ==="
free -h
echo

# Check recent errors in logs
echo "=== Recent Errors (last 10) ==="
podman-compose logs --tail=50 web 2>/dev/null | grep -i error | tail -10
echo

echo "=== End of Report ==="
```

```bash
chmod +x ~/monitor.sh
```

### 5. Set Up Application Monitoring Commands
```bash
# Add useful aliases to .bashrc
echo '
# Hotel API Monitoring Aliases
alias check-api="cd /home/hotelapi/HotelBookingEngine && podman-compose ps && echo && curl -s http://localhost:8000/api/v1/health/ | jq"
alias api-logs="cd /home/hotelapi/HotelBookingEngine && podman-compose logs --tail=50 web"
alias api-logs-live="cd /home/hotelapi/HotelBookingEngine && podman-compose logs -f web"
alias db-logs="cd /home/hotelapi/HotelBookingEngine && podman-compose logs --tail=50 db"
alias redis-logs="cd /home/hotelapi/HotelBookingEngine && podman-compose logs --tail=50 redis"
alias nginx-logs="sudo tail -f /var/log/nginx/error.log"
alias nginx-access="sudo tail -f /var/log/nginx/access.log"
alias restart-api="cd /home/hotelapi/HotelBookingEngine && podman-compose restart web"
alias restart-all="cd /home/hotelapi/HotelBookingEngine && podman-compose restart"
alias api-status="~/monitor.sh"
alias api-backup="~/backup.sh"
' >> ~/.bashrc

# Reload bashrc
source ~/.bashrc
```

### 6. Create Log Analysis Tools
```bash
nano ~/log_analyzer.sh
```

```bash
#!/bin/bash

# Hotel API Log Analyzer

APP_DIR="/home/hotelapi/HotelBookingEngine"

echo "=== Hotel API Log Analysis ==="
echo "Date: $(date)"
echo

# Analyze nginx access logs
echo "=== Top 10 API Endpoints (Last 1000 requests) ==="
sudo tail -1000 /var/log/nginx/access.log | awk '{print $7}' | sort | uniq -c | sort -nr | head -10
echo

echo "=== Top 10 IP Addresses (Last 1000 requests) ==="
sudo tail -1000 /var/log/nginx/access.log | awk '{print $1}' | sort | uniq -c | sort -nr | head -10
echo

echo "=== HTTP Status Code Distribution ==="
sudo tail -1000 /var/log/nginx/access.log | awk '{print $9}' | sort | uniq -c | sort -nr
echo

echo "=== Recent API Errors (Last 50 log entries) ==="
cd $APP_DIR && podman-compose logs --tail=50 web | grep -i "error\|exception\|failed" | tail -10
echo

echo "=== Database Connection Errors ==="
cd $APP_DIR && podman-compose logs --tail=100 db | grep -i "error\|failed" | tail -5
echo

echo "=== Redis Connection Issues ==="
cd $APP_DIR && podman-compose logs --tail=100 redis | grep -i "error\|warning" | tail -5
```

```bash
chmod +x ~/log_analyzer.sh
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Container Issues
```bash
# Check all container status
cd /home/hotelapi/HotelBookingEngine
podman-compose ps -a

# Check container logs for specific service
podman-compose logs web
podman-compose logs db
podman-compose logs redis

# Check container resource usage
podman stats

# Restart specific container
podman-compose restart web

# Rebuild container if needed
podman-compose down
podman-compose build --no-cache web
podman-compose up -d
```

#### 2. Database Connection Issues
```bash
# Check database container status
podman-compose ps db

# Test database connection manually
podman-compose exec db psql -U hotelapi_user -d hotelMaarDB -c '\l'

# Check database logs for errors
podman-compose logs db | grep -i error

# Reset database if corrupted (CAUTION: Data loss!)
podman-compose down
podman volume rm hotelbookingengine_postgres_data
podman-compose up -d db
# Wait for database to initialize, then restore from backup
```

#### 3. Redis Connection Issues
```bash
# Check Redis container status
podman-compose ps redis

# Test Redis connection
podman-compose exec redis redis-cli ping

# Check Redis authentication
podman-compose exec redis redis-cli auth "${REDIS_PASSWORD}" ping

# Check Redis logs
podman-compose logs redis

# Clear Redis cache if needed
podman-compose exec redis redis-cli FLUSHALL
```

#### 4. Application Startup Issues
```bash
# Check Django configuration
podman-compose exec web python manage.py check

# Run migrations manually
podman-compose exec web python manage.py migrate

# Check Django logs for specific errors
podman-compose logs web | grep -A 10 -B 10 "ERROR\|CRITICAL"

# Check environment variables
podman-compose exec web env | grep -E "DJANGO_|DB_|EMAIL_"

# Test application in debug mode (temporarily)
# Edit .env: DEBUG=True, then restart
```

#### 5. Nginx and SSL Issues
```bash
# Test nginx configuration
sudo nginx -t

# Check nginx status and logs
sudo systemctl status nginx
sudo journalctl -u nginx -f

# Check SSL certificate status
sudo certbot certificates

# Test SSL connection
openssl s_client -connect api.marhotels.com.sa:443 -servername api.marhotels.com.sa

# Renew SSL certificate manually
sudo certbot renew --force-renewal

# Check nginx access patterns
sudo tail -f /var/log/nginx/access.log | grep -E "(POST|PUT|DELETE)"
```

#### 6. Performance and Resource Issues
```bash
# Monitor system resources in real-time
htop
iotop
nethogs

# Check disk space and usage
df -h
du -sh /home/hotelapi/HotelBookingEngine/*

# Check memory usage by containers
podman stats --no-stream

# Check for memory leaks in Django
podman-compose exec web python manage.py shell -c "
import gc
print(f'Objects in memory: {len(gc.get_objects())}')
"

# Scale containers for high load
podman-compose up -d --scale web=2

# Check database performance
podman-compose exec db psql -U hotelapi_user -d hotelMaarDB -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;"
```

#### 7. Network and Connectivity Issues
```bash
# Check port bindings
netstat -tulpn | grep -E ":80|:443|:8000"

# Test internal container networking
podman network ls
podman network inspect hotelbookingengine_app-network

# Check firewall rules
sudo firewall-cmd --list-all

# Test API connectivity from different sources
curl -I http://localhost:8000/api/v1/health/
curl -I http://127.0.0.1:8000/api/v1/health/
curl -I https://api.marhotels.com.sa/api/v1/health/
```

#### 8. Email Service Issues
```bash
# Test email configuration
podman-compose exec web python manage.py shell -c "
from django.core.mail import send_mail
from django.conf import settings
print('Email backend:', settings.EMAIL_BACKEND)
print('Email host:', settings.EMAIL_HOST)
send_mail('Test', 'Test message', settings.DEFAULT_FROM_EMAIL, ['test@example.com'])
"

# Check email service logs
podman-compose logs web | grep -i "email\|smtp"
```

### Essential Management Commands

```bash
# === Podman Compose Operations ===
cd /home/hotelapi/HotelBookingEngine

# Start all services
podman-compose up -d

# Stop all services
podman-compose down

# Restart specific service
podman-compose restart web
podman-compose restart db
podman-compose restart redis

# View logs
podman-compose logs -f web          # Follow web logs
podman-compose logs --tail=100 web  # Last 100 lines
podman-compose logs --since=1h web  # Last hour

# Execute commands in containers
podman-compose exec web bash                    # Enter web container
podman-compose exec web python manage.py shell # Django shell
podman-compose exec db psql -U hotelapi_user -d hotelMaarDB  # Database shell
podman-compose exec redis redis-cli             # Redis CLI

# === System Service Management ===
sudo systemctl start hotel-api        # Start API service
sudo systemctl stop hotel-api         # Stop API service
sudo systemctl restart hotel-api      # Restart API service
sudo systemctl status hotel-api       # Check service status
journalctl -u hotel-api -f           # Follow service logs

# === Nginx Management ===
sudo systemctl start nginx           # Start nginx
sudo systemctl stop nginx            # Stop nginx
sudo systemctl restart nginx         # Restart nginx
sudo systemctl reload nginx          # Reload config
sudo nginx -t                       # Test configuration

# === SSL Certificate Management ===
sudo certbot certificates           # List certificates
sudo certbot renew                 # Renew certificates
sudo certbot renew --dry-run       # Test renewal

# === Database Operations ===
# Backup database
podman-compose exec db pg_dump -U hotelapi_user hotelMaarDB > backup.sql

# Restore database
podman-compose exec -T db psql -U hotelapi_user -d hotelMaarDB < backup.sql

# === Application Management ===
# Run Django management commands
podman-compose exec web python manage.py migrate
podman-compose exec web python manage.py collectstatic --noinput
podman-compose exec web python manage.py createsuperuser
podman-compose exec web python manage.py check

# === Monitoring Commands ===
podman stats                        # Container resource usage
podman system df                    # Disk usage
free -h                            # Memory usage
df -h                              # Disk space
htop                               # System monitoring
```

### Quick Troubleshooting Commands

```bash
# Check if API is responding
curl -s http://localhost:8000/api/v1/health/ | jq

# Check all container status
podman-compose ps

# View recent errors
podman-compose logs --tail=50 web | grep -i error

# Check database connectivity
podman-compose exec db pg_isready -U hotelapi_user -d hotelMaarDB

# Check Redis connectivity
podman-compose exec redis redis-cli ping

# Check nginx configuration
sudo nginx -t

# Check firewall status
sudo firewall-cmd --list-all

# Check SSL certificate expiry
sudo certbot certificates | grep -A 3 -B 3 "api.marhotels.com.sa"

# Check disk space
df -h /home/hotelapi/

# Check recent nginx errors
sudo tail -20 /var/log/nginx/error.log

# Full system restart sequence
sudo systemctl stop hotel-api
podman-compose down
sudo systemctl start hotel-api
sleep 30
curl -s http://localhost:8000/api/v1/health/
```

## Final Deployment Checklist

### Pre-Deployment
- [ ] AlmaLinux/RHEL server provisioned and accessible
- [ ] Domain name configured and pointing to server IP
- [ ] SSH access configured with key-based authentication
- [ ] Server firewall configured properly

### System Setup
- [ ] System packages updated (`sudo dnf update -y`)
- [ ] Application user `hotelapi` created
- [ ] Podman and podman-compose installed and working
- [ ] Nginx installed and configured
- [ ] Git installed for code deployment

### Application Deployment
- [ ] Hotel Booking Engine code deployed to `/home/hotelapi/HotelBookingEngine`
- [ ] Environment file `.env` created with production settings
- [ ] Secret key generated and configured (50+ characters)
- [ ] Database credentials configured securely
- [ ] Email service credentials configured
- [ ] CORS origins configured for production domains

### Container Configuration
- [ ] podman-compose.yml configured for production
- [ ] PostgreSQL container configured with health checks
- [ ] Redis container configured with authentication
- [ ] Web container configured with proper resource limits
- [ ] All containers started and healthy (`podman-compose ps`)

### Database Setup
- [ ] PostgreSQL database initialized and migrations applied
- [ ] Django superuser created for admin access
- [ ] Database connectivity verified
- [ ] Redis connectivity verified

### Web Server Configuration
- [ ] Nginx configuration created with security headers
- [ ] Rate limiting configured for API endpoints
- [ ] Static and media file serving configured
- [ ] Reverse proxy to Django application working
- [ ] Nginx configuration tested (`sudo nginx -t`)

### SSL/TLS Security
- [ ] SSL certificate obtained with Let's Encrypt
- [ ] HTTPS redirection configured
- [ ] SSL certificate auto-renewal configured
- [ ] Security headers properly set (HSTS, etc.)

### System Services
- [ ] Systemd service for hotel-api created and enabled
- [ ] Auto-start on boot configured
- [ ] Log rotation configured
- [ ] Service status monitoring setup

### Security Configuration
- [ ] Firewall configured (ports 80, 443, 22 only)
- [ ] SSH hardened (no root login, key-based auth)
- [ ] Container security practices applied
- [ ] Sensitive files protected (`.env`, etc.)

### Monitoring and Backup
- [ ] Health check endpoints working
- [ ] Application monitoring script created
- [ ] Automated backup script configured
- [ ] Log analysis tools setup
- [ ] Monitoring aliases configured

### Testing and Validation
- [ ] API health endpoint responding (`/api/v1/health/`)
- [ ] API documentation accessible (`/api/v1/docs/`)
- [ ] User registration and authentication working
- [ ] Hotel search functionality working
- [ ] Booking flow accessible (requires frontend)
- [ ] Email notifications working
- [ ] Performance testing completed

### Production Readiness
- [ ] Debug mode disabled (`DEBUG=False`)
- [ ] Production database (PostgreSQL) configured
- [ ] Environment-specific settings applied
- [ ] Security middleware enabled
- [ ] CORS properly configured for production
- [ ] Rate limiting working as expected

### Documentation and Maintenance
- [ ] Deployment documentation updated
- [ ] Admin credentials securely stored
- [ ] Backup and recovery procedures documented
- [ ] Monitoring and alerting setup
- [ ] Update and maintenance procedures documented

---

## 🎉 Deployment Complete!

**Your Django Hotel Booking Engine API is now fully deployed and production-ready on AlmaLinux/RHEL with Podman!**

### 🔗 Key URLs
- **API Base**: `https://api.marhotels.com.sa/api/v1/`
- **API Documentation**: `https://api.marhotels.com.sa/api/v1/docs/`
- **Health Check**: `https://api.marhotels.com.sa/api/v1/health/`
- **Admin Panel**: `https://api.marhotels.com.sa/admin/`

### 📊 API Features Available
- ✅ **User Authentication** - Registration, login, JWT tokens
- ✅ **Hotel Management** - Search, details, rooms, amenities
- ✅ **Booking System** - Complete booking flow and management
- ✅ **Real-time Availability** - Dynamic room availability checking
- ✅ **Email Notifications** - Automated booking confirmations
- ✅ **API Documentation** - Interactive Swagger UI
- ✅ **Health Monitoring** - System health checks
- ✅ **Security** - Rate limiting, CORS, SSL/TLS

### 🛠️ For Support
- Check logs: `api-logs` or `podman-compose logs web`
- Monitor status: `api-status` or `~/monitor.sh`
- View documentation: Visit `/api/v1/docs/` for complete API reference
- Troubleshooting: Follow the troubleshooting section above

**Happy coding! 🚀**
