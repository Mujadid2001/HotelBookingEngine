# HOTEL BOOKING ENGINE - DEPLOYMENT GUIDE

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Server Information](#server-information)
3. [Deployment Steps](#deployment-steps)
4. [Server Migration Checklist](#server-migration-checklist)
5. [Environment Variable Guide](#environment-variable-guide)
6. [Troubleshooting](#troubleshooting)
7. [Post-Deployment Verification](#post-deployment-verification)

---

## 🚀 Quick Start

### For Current Server (209.74.88.53 - marhotels.com.sa)

**Assumption:** Docker and Docker Compose are already installed.

```bash
# 1. SSH into the server
ssh root@209.74.88.53

# 2. Clone or update the project
cd /path/to/HotelBookingEngine
git pull origin main

# 3. Create environment file from template
cp .env.example .env

# 4. Edit the .env file with production values
nano .env
# Update these critical values:
# - SECRET_KEY
# - ALLOWED_HOSTS
# - DB_PASSWORD
# - DJANGO_SUPERUSER_PASSWORD
# - EMAIL_* variables
# - SECURE_SSL_REDIRECT=True
# - SESSION_COOKIE_SECURE=True
# - CSRF_COOKIE_SECURE=True

# 5. Start Docker containers
docker-compose up -d

# 6. Verify deployment
./scripts/health-check.sh

# 7. Stop application (for server migration preparation)
docker-compose stop
```

---

## 📊 Server Information

### Current Server (Expiring Tomorrow)
- **Hostname:** server1.marhotels.com.sa
- **IP Address:** 209.74.88.53
- **OS:** AlmaLinux 9.7 (RHEL-based)
- **Hardware:** 4 CPU, 5.8GB RAM, 118GB storage
- **Web Server:** Apache/2.4.62 (HTTP/HTTPS on ports 80/443)
- **Container Runtime:** Docker 29.4.0, Docker Compose v2.24.0
- **Databases:** PostgreSQL (internal), Redis (internal)
- **Application Port:** 8000 (internal container)

### Network Configuration
```
┌─────────────────────────────────────────────────────┐
│         Internal Network (Docker)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Web App      │  │ PostgreSQL   │  │ Redis      │ │
│  │ Port: 8000   │  │ Port: 5432   │  │ Port: 6379 │ │
│  └──────────────┘  └──────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────┘
         ↑ (port 8000 exposed)
┌─────────────────────────────────────────────────────┐
│         Host (AlmaLinux Server)                      │
│  ┌──────────────────────────────────────────────────┐│
│  │ Apache (Reverse Proxy)                           ││
│  │ HTTP: 80    HTTPS: 443                           ││
│  └──────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Deployment Steps

### Step 1: Prepare the .env File

```bash
# Copy template
cp .env.example .env

# Edit with production values
nano .env
```

**Essential Production Values:**

| Variable | Value | Notes |
|----------|-------|-------|
| `DEBUG` | `False` | Never True in production |
| `SECRET_KEY` | Generate new | Use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `ALLOWED_HOSTS` | `marhotels.com.sa,www.marhotels.com.sa,209.74.88.53` | All expected domains |
| `DB_PASSWORD` | Secure password | Use: `openssl rand -base64 32` |
| `SECURE_SSL_REDIRECT` | `True` | Enable HTTPS redirect |
| `SESSION_COOKIE_SECURE` | `True` | Only send cookies over HTTPS |
| `CSRF_COOKIE_SECURE` | `True` | Only send CSRF over HTTPS |

### Step 2: Verify Docker & Docker Compose

```bash
# Check Docker
docker version

# Check Docker Compose
docker-compose version

# Expected output: Docker 29+, Compose v2.20+
```

### Step 3: Pull Latest Code

```bash
cd /path/to/HotelBookingEngine

# If using git
git fetch origin
git checkout main
git pull origin main

# Verify latest changes
git log -1 --oneline
```

### Step 4: Start Services

```bash
# Build and start all containers
docker-compose up -d

# Check container status
docker-compose ps

# Expected: All containers should show "Up"
```

### Step 5: Verify Database & Migrations

```bash
# Check logs
docker-compose logs web

# Expected: No critical errors, migrations applied

# Verify superuser created
docker-compose exec web python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.filter(username='admin').exists()
# Should return: True
>>> exit()
```

### Step 6: Configure Apache Reverse Proxy

```bash
# Copy Apache configuration (see below for full config)
cp config/apache-hotel-booking.conf /etc/httpd/sites-available/

# Enable the site
a2ensite apache-hotel-booking

# Test configuration
apache2ctl configtest
# or
apachectl configtest

# Restart Apache
systemctl restart httpd
# or
apachectl restart
```

### Step 7: Verify SSL Certificate

```bash
# For Let's Encrypt (if using)
certbot --apache -d marhotels.com.sa -d www.marhotels.com.sa

# Verify certificate
openssl s_client -connect marhotels.com.sa:443 -brief
```

### Step 8: Run Health Checks

```bash
# Execute health check script
./scripts/health-check.sh

# Or manually
curl -I https://marhotels.com.sa/api/v1/health/
# Expected: HTTP 200 OK
```

---

## 🔄 Server Migration Checklist

### 1. **Backup Current Server** ✓
```bash
# Backup database
docker-compose exec db pg_dump -U hotelapi_user hotelMaarDB > backup_db.sql

# Backup media files
cp -r media/ media_backup/

# Backup Redis data (if needed)
docker-compose exec redis redis-cli BGSAVE
```

### 2. **Prepare New Server** 
```bash
# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Verify installation
docker --version
docker-compose --version
```

### 3. **Transfer Project to New Server**
```bash
# Option A: Using git (recommended)
git clone https://github.com/your-repo/HotelBookingEngine.git
cd HotelBookingEngine

# Option B: Using SCP
scp -r HotelBookingEngine root@new-server-ip:/path/to/

# Option C: Using rsync
rsync -avz --exclude='.env' --exclude='node_modules' --exclude='__pycache__' \
  HotelBookingEngine/ root@new-server-ip:/path/to/HotelBookingEngine/
```

### 4. **Restore Data on New Server**
```bash
# Start database service only
docker-compose up -d db redis

# Wait for database to be ready (30 seconds)
sleep 30

# Run migrations
docker-compose exec web python manage.py migrate

# Restore database backup (if migrating existing site)
docker-compose exec -T db psql -U hotelapi_user hotelMaarDB < backup_db.sql

# Or import media files
scp -r media/ root@new-server-ip:/path/to/HotelBookingEngine/
```

### 5. **Start Application Stack**
```bash
docker-compose up -d

# Verify all services
docker-compose ps

# Check application logs
docker-compose logs -f web
```

### 6. **Update DNS Records**
```
# In your DNS provider (update these):
marhotels.com.sa    A    new-server-ip
www.marhotels.com.sa A    new-server-ip
```

### 7. **Test on New Server**
```bash
# Before DNS switch, test with hosts file modification
echo "new-server-ip marhotels.com.sa" >> /etc/hosts

# Test API
curl -I https://marhotels.com.sa/api/v1/health/

# Remove from hosts file
sed -i '/marhotels.com.sa/d' /etc/hosts
```

### 8. **Switch DNS & Verify**
- Update DNS to point to new server
- Wait for DNS propagation (5-30 minutes)
- Test from multiple locations

### 9. **Monitor & Cleanup**
```bash
# Monitor logs on new server
docker-compose logs -f

# After verification, stop old server
# (On old server)
docker-compose stop

# Backup old server data before decommission
```

---

## 📝 Environment Variable Guide

### By Environment

#### **Development** (.env.example)
```env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

#### **Staging** (.env.staging)
```env
DEBUG=False
ALLOWED_HOSTS=staging.marhotels.com.sa
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

#### **Production** (.env.production)
```env
DEBUG=False
ALLOWED_HOSTS=marhotels.com.sa,www.marhotels.com.sa
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
# Additional vars...
```

### Generating Secure Values

```bash
# Generate Django SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate secure database password
openssl rand -base64 32

# Generate secure JWT secret
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## 🔍 Troubleshooting

### Issue: Database Connection Error
```
Error: could not connect to server: Connection refused

Solution:
1. Check if PostgreSQL container is running
   docker-compose ps db

2. Check database logs
   docker-compose logs db

3. Verify DB_HOST in .env (should be 'db' for Docker)

4. Wait longer for database to start
   docker-compose up -d && sleep 30
```

### Issue: Port Already in Use
```
Error: bind: address already in use

Solution:
1. Find process using port 8000
   lsof -i :8000   # or: ss -tulpn | grep 8000

2. Either:
   - Stop the process: kill <PID>
   - Change port in docker-compose.yml: "9000:8000"
```

### Issue: Static Files Not Loading
```
Error: 404 on CSS/JS assets

Solution:
1. Collect static files
   docker-compose exec web python manage.py collectstatic --noinput

2. Check volumes are mounted
   docker-compose logs web | grep staticfiles

3. Verify Apache serves static content (see reverse proxy config)
```

### Issue: Migrations Not Running
```
Error: django.core.exceptions.ImproperlyConfigured: No installed app

Solution:
1. Check migrations ran in entrypoint
   docker-compose logs web | grep -i migrat

2. Manually run migrations
   docker-compose exec web python manage.py migrate

3. Verify database is accessible
   docker-compose exec web python manage.py dbshell
```

### Issue: Celery Tasks Not Running
```
Error: Task failed

Solution:
1. Check Celery worker status
   docker-compose logs celery_worker

2. Verify Redis is running and accessible
   docker-compose exec redis redis-cli ping
   # Expected: PONG

3. Check Celery broker URL in .env
   CELERY_BROKER_URL=redis://redis:6379/1
```

---

## ✅ Post-Deployment Verification

### Immediate Checks

```bash
# 1. Health endpoint
curl -I https://marhotels.com.sa/api/v1/health/
# Expected: 200 OK

# 2. API docs
curl -I https://marhotels.com.sa/api/v1/docs/
# Expected: 200 OK

# 3. Django admin
curl -I https://marhotels.com.sa/admin/
# Expected: 302 (redirect to login) or 200

# 4. Database connection
docker-compose exec web python manage.py dbshell
# Should connect without errors

# 5. Redis connection
docker-compose exec redis redis-cli ping
# Expected: PONG

# 6. Celery status
docker-compose exec celery_worker celery -A hotel_booking inspect active
# Should show worker status
```

### Monitoring & Logging

```bash
# Real-time logs
docker-compose logs -f web

# Filtered logs (errors only)
docker-compose logs web | grep ERROR

# Check application health
docker-compose exec web curl -s http://localhost:8000/api/v1/health/ | python -m json.tool

# Monitor resource usage
docker-compose stats

# Check disk space
df -h /

# Check available memory
free -h
```

### Performance Verification

```bash
# Response time test
time curl https://marhotels.com.sa/api/v1/health/

# Load testing (install: pip install locust)
locust -f locustfile.py --host=https://marhotels.com.sa

# Check database slow queries
docker-compose exec db psql -U hotelapi_user -d hotelMaarDB \
  -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

### Security Checks

```bash
# SSL/TLS verification
openssl s_client -connect marhotels.com.sa:443 -brief

# Security headers
curl -I https://marhotels.com.sa/ | grep -i 'strict\|csp\|x-'

# CORS configuration
curl -H "Origin: https://marhotels.com.sa" -I https://marhotels.com.sa/api/v1/

# Test CSRF protection
curl -I -X POST https://marhotels.com.sa/api/v1/auth/login/
```

---

## 📞 Support & Additional Resources

### Configuration Files
- Docker Compose config: `docker-compose.yml`
- Environment template: `.env.example`
- Apache reverse proxy: `config/apache-hotel-booking.conf`
- Health check script: `scripts/health-check.sh`
- Deployment script: `scripts/deploy.sh`

### Common Tasks

**Restart Application**
```bash
docker-compose restart web
```

**View Logs**
```bash
docker-compose logs -f [service-name]
# Services: web, db, redis, celery_worker, celery_beat
```

**Execute Management Command**
```bash
docker-compose exec web python manage.py [command]
```

**Backup Database**
```bash
docker-compose exec db pg_dump -U hotelapi_user hotelMaarDB > backup_$(date +%Y%m%d).sql
```

**Restore Database**
```bash
docker-compose exec -T db psql -U hotelapi_user hotelMaarDB < backup_20260415.sql
```

---

**Last Updated:** April 15, 2026  
**Version:** 1.0.0
