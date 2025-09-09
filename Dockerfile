# Dockerfile for Django API (HotelBookingEngine)
# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=hotel_booking.deployment

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc libpq-dev curl postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn psycopg2-binary

# Copy project files
COPY . /app/

# Create directories
RUN mkdir -p /app/logs /app/hotel_booking/staticfiles /app/hotel_booking/media

EXPOSE 8000

# Simple command without shell scripts
CMD ["sh", "-c", "cd /app/hotel_booking && python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn hotel_booking.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120"]