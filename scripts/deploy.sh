#!/bin/bash
##############################################################################
# HOTEL BOOKING ENGINE - PRODUCTION DEPLOYMENT SCRIPT
# This script automates the deployment process with environment configuration
# Usage: ./scripts/deploy.sh
##############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Check if .env exists
if [ ! -f .env ]; then
    log_error ".env file not found! Copy .env.example to .env and configure it."
fi

log_info "Starting Hotel Booking Engine Deployment..."
log_info "Project Root: $PROJECT_ROOT"

# Load environment
source .env

log_info "Configuration Loaded:"
log_info "  Environment: $ENVIRONMENT"
log_info "  Domain: $DOMAIN_NAME"
log_info "  Database: $DB_HOST:$DB_PORT/$DB_NAME"

# Verify critical variables are set
if [ -z "$DOMAIN_NAME" ]; then
    log_error "DOMAIN_NAME not set in .env"
fi

if [ -z "$SECRET_KEY" ] || [ ${#SECRET_KEY} -lt 50 ]; then
    log_error "SECRET_KEY not set or too short (minimum 50 characters)"
fi

# SSL certificate check for production
if [ "$ENVIRONMENT" = "production" ]; then
    if [ "$USE_HTTPS" = "True" ] || [ "$USE_HTTPS" = "true" ]; then
        if [ ! -f "$NGINX_SSL_CERT_PATH" ] || [ ! -f "$NGINX_SSL_KEY_PATH" ]; then
            log_error "SSL certificates not found at configured paths:"
            echo "  Certificate: $NGINX_SSL_CERT_PATH"
            echo "  Key: $NGINX_SSL_KEY_PATH"
        fi
        log_success "SSL certificates verified"
    fi
fi

# Step 1: Stop existing containers
log_info "Step 1/8: Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Step 2: Create directories if missing
log_info "Step 2/8: Creating required directories..."
mkdir -p certs logs logs/nginx logs/postgres logs/redis media staticfiles
chmod 755 logs logs/nginx logs/postgres logs/redis

# Step 3: Build Docker images
log_info "Step 3/8: Building Docker images..."
docker-compose build --no-cache

# Step 4: Start services
log_info "Step 4/8: Starting services..."
if [ "$ENVIRONMENT" = "production" ]; then
    log_info "Using production overrides..."
    docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d
else
    docker-compose up -d
fi

# Step 5: Wait for services to be ready
log_info "Step 5/8: Waiting for services to be ready (30 seconds)..."
sleep 10

# Health check loop
for i in {1..20}; do
    if docker-compose exec -T web curl -f http://localhost:$APP_PORT/api/v1/health/ &> /dev/null; then
        log_success "Services are healthy"
        break
    fi
    if [ $i -eq 20 ]; then
        log_warning "Services slower than expected. Continuing..."
    fi
    sleep 1.5
done

# Step 6: Run migrations
log_info "Step 6/8: Running database migrations..."
docker-compose exec -T web python manage.py migrate

# Step 7: Collect static files
log_info "Step 7/8: Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Step 8: Health check
log_info "Step 8/8: Running final health checks..."
sleep 2

if curl -f http://localhost:8000/api/v1/health/ &> /dev/null; then
    log_success "API health check passed"
else
    log_warning "API health check may have failed, but deployment completed"
fi

# Final summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         DEPLOYMENT COMPLETED SUCCESSFULLY                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Deployment Summary:${NC}"
echo "  Environment: $ENVIRONMENT"
echo "  Domain: $DOMAIN_NAME"
echo "  Database: $DB_HOST:$DB_PORT/$DB_NAME"
echo ""

# Show API URLs
PROTOCOL="http"
if [ "$USE_HTTPS" = "True" ] || [ "$USE_HTTPS" = "true" ]; then
    PROTOCOL="https"
fi

echo -e "${BLUE}Access Points:${NC}"
echo "  API: $PROTOCOL://$API_DOMAIN/api/v1/"
echo "  Health: $PROTOCOL://$API_DOMAIN/api/v1/health/"
echo "  Admin: $PROTOCOL://$API_DOMAIN/admin/"
echo ""

echo -e "${BLUE}Container Status:${NC}"
docker-compose ps
echo ""

echo -e "${BLUE}Useful Commands:${NC}"
echo "  Stop services:       docker-compose down"
echo "  View logs:           docker-compose logs -f"
echo "  Web logs only:       docker-compose logs -f web"
echo "  Django shell:        docker-compose exec web python manage.py shell"
echo "  Create superuser:    docker-compose exec web python manage.py createsuperuser"
echo ""

log_success "Your API is ready at $DOMAIN_NAME!"


# Config
ENVIRONMENT=${1:-production}
ACTION=${2:-deploy}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$PROJECT_ROOT/backups"

# ==============================================================================
# Helper Functions
# ==============================================================================

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

check_requirements() {
    local required_cmds=("docker" "docker-compose" "curl")
    
    for cmd in "${required_cmds[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "$cmd is not installed"
            return 1
        fi
    done
    
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log_error ".env file not found at $PROJECT_ROOT/.env"
        log_info "Create one from .env.example: cp .env.example .env"
        return 1
    fi
}

backup_database() {
    print_header "BACKING UP DATABASE"
    
    mkdir -p "$BACKUP_DIR"
    
    local backup_file="$BACKUP_DIR/db_backup_${ENVIRONMENT}_${TIMESTAMP}.sql"
    
    log_info "Backing up database to: $backup_file"
    
    docker-compose exec -T db pg_dump -U hotelapi_user hotelMaarDB > "$backup_file" 2>/dev/null
    
    if [ -f "$backup_file" ]; then
        log_success "Database backed up successfully"
        gzip "$backup_file"
        log_info "Backup compressed: ${backup_file}.gz"
    else
        log_error "Failed to backup database"
        return 1
    fi
}

backup_volumes() {
    print_header "BACKING UP VOLUME DATA"
    
    mkdir -p "$BACKUP_DIR"
    
    log_info "Backing up media files..."
    if [ -d "$PROJECT_ROOT/media" ]; then
        tar -czf "$BACKUP_DIR/media_backup_${ENVIRONMENT}_${TIMESTAMP}.tar.gz" \
            -C "$PROJECT_ROOT" media 2>/dev/null
        log_success "Media files backed up"
    else
        log_warn "No media directory found"
    fi
    
    log_info "Backing up logs..."
    if [ -d "$PROJECT_ROOT/logs" ]; then
        tar -czf "$BACKUP_DIR/logs_backup_${ENVIRONMENT}_${TIMESTAMP}.tar.gz" \
            -C "$PROJECT_ROOT" logs 2>/dev/null
        log_success "Logs backed up"
    else
        log_warn "No logs directory found"
    fi
}

pull_latest_code() {
    print_header "PULLING LATEST CODE"
    
    cd "$PROJECT_ROOT"
    
    log_info "Fetching from repository..."
    if git fetch origin main 2>/dev/null; then
        log_success "Fetched latest changes"
    else
        log_warn "Unable to fetch from git (might not be a git repo)"
    fi
    
    log_info "Current HEAD:"
    git log -1 --oneline 2>/dev/null || log_info "Git log unavailable"
    
    cd - > /dev/null
}

stop_containers() {
    print_header "STOPPING CONTAINERS"
    
    log_info "Stopping all services..."
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" stop
    log_success "Containers stopped"
}

start_containers() {
    print_header "STARTING CONTAINERS"
    
    log_info "Starting all services..."
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" up -d
    
    log_info "Waiting for services to be ready..."
    sleep 10
    
    # Check if containers are running
    local running=$(docker-compose -f "$PROJECT_ROOT/docker-compose.yml" ps -q | wc -l)
    if [ "$running" -gt 0 ]; then
        log_success "Containers started successfully"
    else
        log_error "Failed to start containers"
        return 1
    fi
}

run_migrations() {
    print_header "RUNNING DATABASE MIGRATIONS"
    
    log_info "Applying migrations..."
    
    if docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec -T web \
        python manage.py migrate --noinput; then
        log_success "Migrations completed successfully"
    else
        log_error "Migration failed"
        return 1
    fi
}

collect_static() {
    print_header "COLLECTING STATIC FILES"
    
    log_info "Collecting static files..."
    
    if docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec -T web \
        python manage.py collectstatic --noinput; then
        log_success "Static files collected"
    else
        log_warn "Failed to collect static files (may not be critical)"
    fi
}

create_superuser() {
    print_header "CHECKING SUPERUSER"
    
    log_info "Checking if superuser exists..."
    
    if docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec -T web \
        python manage.py shell <<< "
from django.contrib.auth import get_user_model
User = get_user_model()
print('Superuser exists' if User.objects.filter(username='admin').exists() else 'No superuser')
" | grep -q "Superuser exists"; then
        log_success "Superuser already exists"
    else
        log_warn "No superuser found - one should be created via env vars on first run"
    fi
}

verify_health() {
    print_header "VERIFYING DEPLOYMENT HEALTH"
    
    log_info "Checking container status..."
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" ps
    
    log_info "Testing health endpoint..."
    
    local max_attempts=5
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/v1/health/ | grep -q "200"; then
            log_success "Health endpoint responding"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "Health endpoint not responding after $max_attempts attempts"
            log_info "Check logs: docker-compose logs web"
            return 1
        fi
        
        log_info "Attempt $attempt/$max_attempts... waiting 5 seconds"
        sleep 5
        ((attempt++))
    done
    
    log_info "Testing database connectivity..."
    if docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec -T db \
        pg_isready -U hotelapi_user -d hotelMaarDB > /dev/null 2>&1; then
        log_success "Database is accessible"
    else
        log_error "Database is not responding"
        return 1
    fi
}

clean_docker() {
    print_header "CLEANING DOCKER"
    
    log_warn "This will remove unused images and containers"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker system prune -f
        log_success "Docker cleanup completed"
    else
        log_info "Cleanup skipped"
    fi
}

rebuild_containers() {
    print_header "REBUILDING CONTAINERS"
    
    log_info "Building Docker images..."
    
    if docker-compose -f "$PROJECT_ROOT/docker-compose.yml" build --no-cache; then
        log_success "Docker images built successfully"
    else
        log_error "Failed to build Docker images"
        return 1
    fi
}

view_logs() {
    print_header "APPLICATION LOGS"
    
    local service=${3:-web}
    local tail=${4:-50}
    
    log_info "Showing last $tail lines of $service logs:"
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" logs --tail=$tail $service
}

# ==============================================================================
# Composite Actions
# ==============================================================================

action_deploy() {
    print_header "DEPLOYING HOTEL BOOKING ENGINE - $ENVIRONMENT"
    
    check_requirements || return 1
    backup_database || return 1
    backup_volumes || return 1
    
    if [ -d "$PROJECT_ROOT/.git" ]; then
        pull_latest_code
    fi
    
    stop_containers || return 1
    rebuild_containers || return 1
    start_containers || return 1
    
    run_migrations || return 1
    collect_static || return 1
    create_superuser
    verify_health || return 1
    
    log_success "DEPLOYMENT COMPLETED SUCCESSFULLY"
    log_info "Your application is now running on: http://127.0.0.1:8000"
    
    print_header "NEXT STEPS"
    echo "1. Configure Apache reverse proxy: cp config/apache-hotel-booking.conf /etc/httpd/conf.d/"
    echo "2. Set up SSL certificate: certbot --apache -d marhotels.com.sa"
    echo "3. Verify deployment: ./scripts/health-check.sh"
    echo "4. Monitor logs: docker-compose logs -f web"
}

action_migrate() {
    print_header "RUNNING DATABASE MIGRATION - $ENVIRONMENT"
    
    check_requirements || return 1
    backup_database || return 1
    
    run_migrations || return 1
    
    log_success "MIGRATION COMPLETED"
}

action_restart() {
    print_header "RESTARTING APPLICATION - $ENVIRONMENT"
    
    check_requirements || return 1
    
    stop_containers || return 1
    sleep 3
    start_containers || return 1
    
    verify_health || return 1
    
    log_success "APPLICATION RESTARTED"
}

action_stop() {
    print_header "STOPPING APPLICATION - $ENVIRONMENT"
    
    check_requirements || return 1
    stop_containers || return 1
    
    log_success "APPLICATION STOPPED"
}

action_start() {
    print_header "STARTING APPLICATION - $ENVIRONMENT"
    
    check_requirements || return 1
    start_containers || return 1
    
    verify_health || return 1
    
    log_success "APPLICATION STARTED"
}

action_health() {
    print_header "HEALTH CHECK - $ENVIRONMENT"
    
    check_requirements || return 1
    verify_health || return 1
    
    log_success "HEALTH CHECK PASSED"
}

action_backup() {
    print_header "BACKING UP SYSTEM - $ENVIRONMENT"
    
    check_requirements || return 1
    backup_database || return 1
    backup_volumes || return 1
    
    log_success "BACKUP COMPLETED"
    log_info "Backups stored in: $BACKUP_DIR"
}

action_logs() {
    view_logs
}

action_clean() {
    clean_docker
}

# ==============================================================================
# Main Menu
# ==============================================================================

show_usage() {
    cat << EOF

${BLUE}HOTEL BOOKING ENGINE - DEPLOYMENT SCRIPT${NC}

Usage: ./scripts/deploy.sh [ENVIRONMENT] [ACTION]

${BLUE}Environments:${NC}
  - development  (local development)
  - staging      (testing environment)
  - production   (live environment)

${BLUE}Actions:${NC}
  - deploy       Full deployment with backups (stops services, pulls code, migrates, restarts)
  - migrate      Run database migrations only
  - restart      Restart all containers
  - start        Start all containers
  - stop         Stop all containers
  - health       Run health checks
  - backup       Backup database and volumes
  - logs         View application logs
  - clean        Clean Docker system
  - rebuild      Rebuild Docker images

${BLUE}Examples:${NC}
  ./scripts/deploy.sh production deploy
  ./scripts/deploy.sh staging migrate
  ./scripts/deploy.sh production health
  ./scripts/deploy.sh production logs

${BLUE}For server migration:${NC}
  1. Backup current server:   ./scripts/deploy.sh production backup
  2. Set up new server with Docker
  3. Clone project on new server
  4. Create .env from .env.example
  5. Deploy on new server:    ./scripts/deploy.sh production deploy
  6. Configure reverse proxy:  cp config/apache-hotel-booking.conf /etc/httpd/conf.d/
  7. Update DNS records to point to new server
  
EOF
}

# ==============================================================================
# Main Execution
# ==============================================================================

if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_usage
    exit 0
fi

cd "$PROJECT_ROOT"

case "$ACTION" in
    deploy)
        action_deploy
        ;;
    migrate)
        action_migrate
        ;;
    restart)
        action_restart
        ;;
    start)
        action_start
        ;;
    stop)
        action_stop
        ;;
    health)
        action_health
        ;;
    backup)
        action_backup
        ;;
    logs)
        action_logs "$@"
        ;;
    clean)
        action_clean
        ;;
    rebuild)
        rebuild_containers
        ;;
    *)
        log_error "Unknown action: $ACTION"
        show_usage
        exit 1
        ;;
esac

exit $?
