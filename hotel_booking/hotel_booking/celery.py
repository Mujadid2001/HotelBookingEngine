"""
Celery configuration for Hotel Booking Engine.
Handles asynchronous task processing for emails, notifications, and housekeeping.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_booking.settings')

app = Celery('hotel_booking')

# Load configuration from Django settings with CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover all task.py modules in installed apps
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'check-booking-expiry': {
        'task': 'bookings.tasks.check_pending_booking_expiry',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'send-reminder-emails': {
        'task': 'bookings.tasks.send_check_in_reminders',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
    'cleanup-cancelled-bookings': {
        'task': 'bookings.tasks.cleanup_cancelled_bookings',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    """Debug task for Celery testing."""
    print(f'Request: {self.request!r}')
