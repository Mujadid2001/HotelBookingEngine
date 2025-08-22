#!/bin/bash
# Production deployment script for Hotel Booking API

set -e

echo "🚀 Starting Hotel Booking API deployment..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.template to .env and configure it with your production values."
    exit 1
fi

# Validate required environment variables
echo "🔍 Validating environment variables..."
required_vars=("SECRET_KEY" "DB_PASSWORD" "EMAIL_HOST_PASSWORD")
for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env || grep -q "^${var}=$" .env; then
        echo "❌ Error: ${var} is not set in .env file"
        exit 1
    fi
done

# Pull latest code (if in git repository)
if [ -d ".git" ]; then
    echo "📦 Pulling latest code..."
    git pull origin main
fi

# Create logs directory
mkdir -p logs

# Build and start containers
echo "🐳 Building and starting containers..."
docker-compose -f docker-compose.prod.yml down --volumes
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if database is ready
echo "🔧 Checking database connection..."
if ! docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U hotel_booking_user; then
    echo "❌ Database is not ready. Check database logs:"
    docker-compose -f docker-compose.prod.yml logs db
    exit 1
fi

# Run migrations
echo "🔧 Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T api python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
docker-compose -f docker-compose.prod.yml exec -T api python manage.py collectstatic --noinput

# Check if we need to create a superuser
echo "👤 Checking for existing superusers..."
has_superuser=$(docker-compose -f docker-compose.prod.yml exec -T api python manage.py shell -c "from accounts.models import CustomUser; print(CustomUser.objects.filter(is_superuser=True).exists())")

if [ "$has_superuser" = "False" ]; then
    read -p "No superuser found. Do you want to create one? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f docker-compose.prod.yml exec api python manage.py createsuperuser
    fi
fi

# Run deployment checks
echo "🔍 Running Django deployment checks..."
if ! docker-compose -f docker-compose.prod.yml exec -T api python manage.py check --deploy; then
    echo "⚠️ Deployment checks failed. Please review the warnings above."
fi

# Test API health
echo "🔍 Testing API health..."
sleep 5
if curl -f -s http://localhost/api/v1/health/ > /dev/null; then
    echo "✅ API is responding to health checks!"
    
    # Show service status
    echo "📊 Service Status:"
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo ""
    echo "📋 Service Information:"
    echo "   🌐 API Base URL: http://localhost/api/v1/"
    echo "   � API Documentation: http://localhost/api/v1/docs/"
    echo "   � Admin Panel: http://localhost/admin/"
    echo "   ❤️  Health Check: http://localhost/api/v1/health/"
    echo ""
    echo "📝 Next Steps:"
    echo "   1. Configure your domain and SSL certificates"
    echo "   2. Update CORS_ALLOWED_ORIGINS in .env"
    echo "   3. Set up monitoring and backups"
    echo "   4. Test all API endpoints"
    
else
    echo "❌ API health check failed! Checking logs..."
    echo ""
    echo "🔍 API Logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=20 api
    echo ""
    echo "🔍 Database Logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=10 db
    echo ""
    echo "🔍 Nginx Logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=10 nginx
    exit 1
fi
