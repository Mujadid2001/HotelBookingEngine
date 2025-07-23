# Development environment setup
Write-Host "Setting up development environment..." -ForegroundColor Green
$env:DJANGO_ENVIRONMENT = "development"
$env:DJANGO_SETTINGS_MODULE = "hotel_booking.settings.development"

Write-Host "Environment set to: $($env:DJANGO_ENVIRONMENT)" -ForegroundColor Yellow
Write-Host "Settings module: $($env:DJANGO_SETTINGS_MODULE)" -ForegroundColor Yellow

# Run Django development server
python manage.py runserver
