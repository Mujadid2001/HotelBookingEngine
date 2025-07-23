@echo off
REM Production environment setup
echo Setting up production environment...
set DJANGO_ENVIRONMENT=production
set DJANGO_SETTINGS_MODULE=hotel_booking.settings.production

echo Environment set to: %DJANGO_ENVIRONMENT%
echo Settings module: %DJANGO_SETTINGS_MODULE%

REM Collect static files and run with gunicorn (adjust as needed)
python manage.py collectstatic --noinput
echo Starting production server with gunicorn...
REM gunicorn hotel_booking.wsgi:application --bind 0.0.0.0:8000
