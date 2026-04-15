#!/bin/bash

# ==============================================================================
# HOTEL BOOKING ENGINE - HEALTH CHECK SCRIPT
# ==============================================================================
# Purpose: Verify all services are running and healthy
# Usage: ./scripts/health-check.sh
# ==============================================================================

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# ==============================================================================
# Helper Functions
# ==============================================================================

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_check() {
    echo -n "$1 ... "
}

print_pass() {
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
}

print_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((FAILED++))
}

print_warning() {
    echo -e "${YELLOW}⚠ WARNING${NC}: $1"
    ((WARNINGS++))
}

# ==============================================================================
# System Checks
# ==============================================================================

check_system() {
    print_header "SYSTEM & ENVIRONMENT CHECKS"
    
    # Check Docker
    print_check "Docker installed"
    if command -v docker &> /dev/null; then
        print_pass
        docker_version=$(docker --version | awk '{print $3}' | cut -d',' -f1)
    else
        print_fail "Docker not found. Please install Docker."
        return 1
    fi
    
    # Check Docker Compose
    print_check "Docker Compose installed"
    if command -v docker-compose &> /dev/null; then
        print_pass
        compose_version=$(docker-compose --version | awk '{print $3}' | cut -d',' -f1)
    else
        print_fail "Docker Compose not found. Please install Docker Compose."
        return 1
    fi
    
    # Check .env file
    print_check "Environment file (.env) exists"
    if [ -f .env ]; then
        print_pass
    else
        print_fail ".env file not found. Copy from .env.example"
        return 1
    fi
    
    # Check required vars in .env
    print_check "Required environment variables"
    required_vars=("SECRET_KEY" "DEBUG" "ALLOWED_HOSTS" "DB_PASSWORD")
    missing_vars=()
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -eq 0 ]; then
        print_pass
    else
        print_fail "Missing vars: ${missing_vars[*]}"
        return 1
    fi
}

# ==============================================================================
# Container Checks
# ==============================================================================

check_containers() {
    print_header "CONTAINER STATUS CHECKS"
    
    # Check if any containers are running
    print_check "Docker containers running"
    container_count=$(docker-compose ps -q | wc -l)
    if [ "$container_count" -gt 0 ]; then
        print_pass
    else
        print_fail "No containers running. Run: docker-compose up -d"
        return 1
    fi
    
    # Check specific services
    services=("web" "db" "redis" "celery_worker")
    
    for service in "${services[@]}"; do
        print_check "$service container status"
        if docker-compose ps "$service" | grep -q "Up"; then
            print_pass
        else
            print_fail "$service is not running"
        fi
    done
    
    # Check container health
    print_check "Web container health"
    health=$(docker-compose ps web | awk '{print $11}' | tail -1)
    if [[ "$health" == "Up" ]] || [[ "$health" == "(healthy)" ]] || [[ "$health" == "Up"* ]]; then
        print_pass
    else
        print_warning "Web container status: $health"
    fi
}

# ==============================================================================
# Application Checks
# ==============================================================================

check_application() {
    print_header "APPLICATION HEALTH CHECKS"
    
    # Wait a bit for services to stabilize
    sleep 2
    
    # Check Django app health endpoint
    print_check "Django health endpoint"
    if response=$(curl -s -w "\n%{http_code}" http://127.0.0.1:8000/api/v1/health/ 2>/dev/null); then
        http_code=$(echo "$response" | tail -1)
        if [ "$http_code" = "200" ]; then
            print_pass
        else
            print_fail "Health endpoint returned HTTP $http_code"
        fi
    else
        print_fail "Could not reach health endpoint (http://127.0.0.1:8000/api/v1/health/)"
    fi
    
    # Check Django API docs
    print_check "API documentation (Swagger)"
    if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/v1/docs/ | grep -q "200"; then
        print_pass
    else
        print_warning "API docs not accessible"
    fi
    
    # Check admin interface
    print_check "Django admin interface"
    if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/admin/ | grep -q "302\|200"; then
        print_pass
    else
        print_warning "Admin interface not accessible"
    fi
}

# ==============================================================================
# Database Checks
# ==============================================================================

check_database() {
    print_header "DATABASE CHECKS"
    
    # Check PostgreSQL connection
    print_check "PostgreSQL connectivity"
    if docker-compose exec -T db pg_isready -U hotelapi_user -d hotelMaarDB &>/dev/null; then
        print_pass
    else
        print_fail "Could not connect to PostgreSQL"
    fi
    
    # Check database tables
    print_check "Database tables exist"
    table_count=$(docker-compose exec -T db psql -U hotelapi_user -d hotelMaarDB \
        -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null | tail -1)
    
    if [ -n "$table_count" ] && [ "$table_count" -gt 0 ]; then
        print_pass
        echo "  (Found $table_count tables)"
    else
        print_fail "No tables found in database"
    fi
    
    # Check admin user
    print_check "Superuser exists"
    superuser_count=$(docker-compose exec -T db psql -U hotelapi_user -d hotelMaarDB \
        -c "SELECT COUNT(*) FROM auth_user WHERE is_superuser=true;" 2>/dev/null | tail -1)
    
    if [ "$superuser_count" -gt 0 ]; then
        print_pass
        echo "  (Found $superuser_count superuser(s))"
    else
        print_warning "No superusers found. Create one with: docker-compose exec web python manage.py createsuperuser"
    fi
}

# ==============================================================================
# Cache & Queue Checks
# ==============================================================================

check_cache_queue() {
    print_header "CACHE & MESSAGE QUEUE CHECKS"
    
    # Check Redis connectivity
    print_check "Redis connectivity"
    if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
        print_pass
    else
        print_fail "Could not connect to Redis"
    fi
    
    # Check Redis memory
    print_check "Redis memory usage"
    memory=$(docker-compose exec -T redis redis-cli info memory | grep used_memory_human | cut -d: -f2 | tr -d ' ')
    if [ -n "$memory" ]; then
        print_pass
        echo "  (Used: $memory)"
    else
        print_warning "Could not determine Redis memory usage"
    fi
    
    # Check Celery worker
    print_check "Celery worker status"
    if docker-compose exec -T celery_worker celery -A hotel_booking inspect active &>/dev/null; then
        print_pass
    else
        print_warning "Celery worker not responding"
    fi
}

# ==============================================================================
# Performance & Resource Checks
# ==============================================================================

check_performance() {
    print_header "PERFORMANCE & RESOURCE CHECKS"
    
    # Container resource usage
    print_check "Container resource limits"
    total_cpu=$(docker-compose stats --no-stream 2>/dev/null | tail -1 | awk '{print $3}')
    total_mem=$(docker-compose stats --no-stream 2>/dev/null | tail -1 | awk '{print $5}')
    
    if [ -n "$total_cpu" ] && [ -n "$total_mem" ]; then
        print_pass
        echo "  (CPU: $total_cpu, Memory: $total_mem)"
    else
        print_warning "Could not determine container resource usage"
    fi
    
    # Check disk space
    print_check "Disk space available"
    disk_usage=$(df -h / | tail -1 | awk '{print $5}')
    disk_available=$(df -h / | tail -1 | awk '{print $4}')
    disk_percent=$(echo $disk_usage | sed 's/%//')
    
    if [ "$disk_percent" -lt 80 ]; then
        print_pass
        echo "  (Usage: $disk_usage, Available: $disk_available)"
    else
        print_warning "Disk usage is $disk_usage"
    fi
    
    # Check memory
    print_check "System memory available"
    mem_available=$(free -h | grep Mem | awk '{print $7}')
    if [ -n "$mem_available" ]; then
        print_pass
        echo "  (Available: $mem_available)"
    else
        print_warning "Could not determine available memory"
    fi
}

# ==============================================================================
# Log Checks
# ==============================================================================

check_logs() {
    print_header "LOG ANALYSIS"
    
    # Check for recent errors in logs
    print_check "Django application errors (last 10)"
    error_count=$(docker-compose logs web 2>/dev/null | grep -i "error" | wc -l)
    if [ "$error_count" -eq 0 ]; then
        print_pass
    else
        print_warning "Found $error_count error(s) in application logs"
        echo "  Recent errors:"
        docker-compose logs web 2>/dev/null | grep -i "error" | tail -3 | sed 's/^/    /'
    fi
    
    # Check database logs
    print_check "Database errors (last 10)"
    db_error_count=$(docker-compose logs db 2>/dev/null | grep -i "error\|fatal" | wc -l)
    if [ "$db_error_count" -eq 0 ]; then
        print_pass
    else
        print_warning "Found $db_error_count error(s) in database logs"
    fi
}

# ==============================================================================
# Summary
# ==============================================================================

print_summary() {
    print_header "HEALTH CHECK SUMMARY"
    
    total=$((PASSED + FAILED + WARNINGS))
    
    echo -e "Total Checks: $total"
    echo -e "${GREEN}Passed: $PASSED${NC}"
    
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
    fi
    
    if [ $FAILED -gt 0 ]; then
        echo -e "${RED}Failed: $FAILED${NC}"
        echo
        echo -e "${RED}Status: UNHEALTHY ✗${NC}"
        return 1
    else
        echo
        echo -e "${GREEN}Status: HEALTHY ✓${NC}"
        return 0
    fi
}

# ==============================================================================
# Main Execution
# ==============================================================================

check_system
check_containers
check_application
check_database
check_cache_queue
check_performance
check_logs
print_summary

exit_code=$?
exit $exit_code
