# Dockerfile for Django API (HotelBookingEngine)
# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Create necessary directories and set proper ownership
RUN mkdir -p /app/logs /app/static /app/media && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser


# Collect static files (optional, can also be done in entrypoint)
# RUN python manage.py collectstatic --noinput

# Expose port 8000 for Gunicorn
EXPOSE 8000

# Start Gunicorn server
CMD ["sh", "-c", "cd /app/hotel_booking && gunicorn hotel_booking.wsgi:application --bind 0.0.0.0:8000"]
