@echo off
REM Development environment setup
echo Setting up development environment...
set DJANGO_ENVIRONMENT=development
set DJANGO_SETTINGS_MODULE=hotel_booking.settings.development

echo Environment set to: %DJANGO_ENVIRONMENT%
echo Settings module: %DJANGO_SETTINGS_MODULE%

REM Run Django development server
python manage.py runserver
