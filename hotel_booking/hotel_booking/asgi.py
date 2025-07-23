"""
ASGI config for hotel_booking project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Use deployment.py for production, settings.py for development
if os.environ.get('DJANGO_ENV') == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_booking.deployment')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_booking.settings')

application = get_asgi_application()
