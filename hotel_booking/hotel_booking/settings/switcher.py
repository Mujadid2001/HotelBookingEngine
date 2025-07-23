"""
Settings switcher for different environments
"""
import os

def get_settings():
    """
    Get the appropriate settings module based on environment
    """
    environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')
    
    if environment == 'production':
        return 'hotel_booking.settings.production'
    elif environment == 'local':
        return 'hotel_booking.settings.local'
    else:
        return 'hotel_booking.settings.development'

# You can also set a default here
DJANGO_SETTINGS_MODULE = get_settings()
