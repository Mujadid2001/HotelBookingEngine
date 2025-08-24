
# Hotel Booking Engine API - AlmaLinux RHEL Deployment Guide

This guide provides step-by-step instructions for deploying the Django Hotel Booking Engine API on AlmaLinux/RHEL VPS using Podman Compose.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Install Required Software](#install-required-software)
4. [Project Setup](#project-setup)
5. [Environment Configuration](#environment-configuration)
6. [Database Setup](#database-setup)
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
- Minimum 2GB RAM, 2 CPU cores, 20GB storage
- Domain name pointed to your VPS IP address
- SSH access to the server

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
# Install Podman
sudo dnf install -y podman podman-docker

# Install podman-compose
sudo dnf install -y python3-pip
sudo pip3 install podman-compose

# Verify installation
podman --version
podman-compose --version
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
sudo dnf install -y curl wget nano vim htop
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
SECRET_KEY="your-super-secret-key-here-make-it-long-and-random"
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost,127.0.0.1

# Database Configuration
DB_NAME=hotelMaarDB
DB_USER=hotelapi_user
DB_PASSWORD="your-secure-database-password"
DB_HOST=db
DB_PORT=5432

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD="your-app-password"
DEFAULT_FROM_EMAIL="Hotel Booking <noreply@yourdomain.com>"
SERVER_EMAIL="Hotel Booking <admin@yourdomain.com>"

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 3. Generate Secret Key
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Database Setup

### 1. Update Docker Compose for Production
```bash
nano docker-compose.yml
```

Ensure your docker-compose.yml looks like this:
```yaml
services:
  web:
    build: .
    command: >
      sh -c "cd /app/hotel_booking &&
             python manage.py migrate --noinput &&
             python manage.py collectstatic --noinput &&
             gunicorn hotel_booking.wsgi:application --bind 0.0.0.0:8000 --timeout 120 --workers 3"
    working_dir: /app
    env_file:
      - .env
    environment:
      - DJANGO_SETTINGS_MODULE=hotel_booking.deployment
    depends_on:
      db:
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
    volumes:
      - static_volume:/app/hotel_booking/staticfiles
      - media_volume:/app/hotel_booking/media
      
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=hotelMaarDB
      - POSTGRES_USER=hotelapi_user
      - POSTGRES_PASSWORD=your-secure-database-password
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hotelapi_user -d hotelMaarDB"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

## Build and Deploy Application

### 1. Build the Application
```bash
cd ~/HotelBookingEngine
podman-compose build --no-cache
```

### 2. Start the Services
```bash
podman-compose up -d
```

### 3. Check Container Status
```bash
podman-compose ps
podman-compose logs web
```

### 4. Create Django Superuser
```bash
podman-compose exec web python manage.py createsuperuser
```

### 5. Test Application
```bash
curl http://localhost:8000/api/v1/health/
```

## Nginx Configuration

### 1. Create Nginx Configuration
```bash
sudo nano /etc/nginx/conf.d/hotel_booking.conf
```

### 2. Add Nginx Configuration
```nginx
upstream hotel_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Client max body size
    client_max_body_size 20M;

    # API endpoints
    location / {
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

    # Static files
    location /static/ {
        alias /home/hotelapi/HotelBookingEngine/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/hotelapi/HotelBookingEngine/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Deny access to sensitive files
    location ~ /\. {
        deny all;
    }
    
    location ~ /\.env {
        deny all;
    }
}
```

### 3. Test and Enable Nginx
```bash
sudo nginx -t
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 4. Create Static Files Directory
```bash
mkdir -p ~/HotelBookingEngine/staticfiles
mkdir -p ~/HotelBookingEngine/media
sudo chown -R hotelapi:hotelapi ~/HotelBookingEngine/
```

## SSL Certificate Setup

### 1. Install Certbot
```bash
sudo dnf install -y certbot python3-certbot-nginx
```

### 2. Obtain SSL Certificate
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
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
Description=Hotel Booking API
Requires=network.target
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
User=hotelapi
WorkingDirectory=/home/hotelapi/HotelBookingEngine
ExecStart=/usr/local/bin/podman-compose up -d
ExecStop=/usr/local/bin/podman-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

### 2. Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable hotel-api.service
sudo systemctl start hotel-api.service
```

## Testing and Verification

### 1. Test API Endpoints
```bash
# Test health endpoint
curl https://yourdomain.com/api/v1/health/

# Test main API
curl https://yourdomain.com/api/v1/

# Test documentation
curl https://yourdomain.com/api/v1/docs/
```

### 2. Check SSL Certificate
```bash
curl -I https://yourdomain.com
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

### 3. Performance Test
```bash
# Install apache bench for testing
sudo dnf install -y httpd-tools

# Test API performance
ab -n 100 -c 10 https://yourdomain.com/api/v1/health/
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

### 2. Create Backup Script
```bash
nano ~/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/hotelapi/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
podman-compose exec -T db pg_dump -U hotelapi_user hotelMaarDB > $BACKUP_DIR/db_backup_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz media/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
chmod +x ~/backup.sh
```

### 3. Set Up Monitoring Commands
```bash
# Check application status
alias check-api='podman-compose ps && curl -s https://yourdomain.com/api/v1/health/'

# View logs
alias api-logs='podman-compose logs --tail=50 web'
alias nginx-logs='sudo tail -f /var/log/nginx/error.log'

# Restart services
alias restart-api='podman-compose restart web'
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Container Not Starting
```bash
# Check logs
podman-compose logs web
podman-compose logs db

# Check system resources
htop
df -h
```

#### 2. Database Connection Issues
```bash
# Test database connection
podman-compose exec db psql -U hotelapi_user -d hotelMaarDB -c '\l'

# Reset database container
podman-compose down
podman volume rm hotelbookingengine_postgres_data
podman-compose up -d
```

#### 3. Nginx Issues
```bash
# Test nginx configuration
sudo nginx -t

# Check nginx status
sudo systemctl status nginx

# View nginx logs
sudo journalctl -u nginx -f
```

#### 4. SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate manually
sudo certbot renew --force-renewal
```

#### 5. Performance Issues
```bash
# Monitor system resources
htop
iotop
netstat -tulpn

# Scale containers
podman-compose up -d --scale web=2
```

### Useful Commands

```bash
# Application management
podman-compose up -d              # Start services
podman-compose down               # Stop services
podman-compose restart web        # Restart web container
podman-compose logs -f web        # Follow web logs
podman-compose exec web bash      # Enter web container

# System monitoring
sudo systemctl status nginx       # Check nginx status
sudo systemctl status hotel-api   # Check API service
sudo firewall-cmd --list-all      # Check firewall rules
free -h                          # Check memory usage
df -h                           # Check disk usage

# Maintenance
sudo dnf update -y              # Update system
podman system prune -a          # Clean unused containers/images
sudo certbot renew             # Renew SSL certificates
```

---

## Final Checklist

- [ ] System updated and secured
- [ ] Podman and podman-compose installed
- [ ] Application deployed and running
- [ ] Database connected and migrated
- [ ] Nginx configured and running
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Systemd services enabled
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] API endpoints tested
- [ ] Documentation accessible

**Your Django Hotel Booking Engine API is now fully deployed and production-ready on AlmaLinux/RHEL!**

For support or questions, refer to the troubleshooting section or check the application logs.
