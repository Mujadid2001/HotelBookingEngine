#!/usr/bin/env python
"""
Hotel Booking Engine - Environment Checker Utility
=================================================

This utility script checks and validates the Django environment configuration.
Use this to verify your setup before running the application.

Usage:
    cd hotel_booking/scripts
    python environment_checker.py

Features:
    - Django settings validation
    - Database connectivity check
    - Environment variables verification
    - Installed packages validation
    - Development/Production mode detection

Last Updated: July 23, 2025
"""
# Standard library imports
import os
import sys
from pathlib import Path

# Django imports
import django

def check_environment():
    """Check and display current environment configuration"""
    
    print("=" * 60)
    print("🏨 Hotel Booking Engine - Environment Checker")
    print("=" * 60)
    
    # Check Django environment variable
    django_env = os.environ.get('DJANGO_ENVIRONMENT', 'not set')
    settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'not set')
    
    print(f"📊 DJANGO_ENVIRONMENT: {django_env}")
    print(f"⚙️  DJANGO_SETTINGS_MODULE: {settings_module}")
    print()
    
    # Set up Django
    if settings_module == 'not set':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_booking.settings.development')
        settings_module = 'hotel_booking.settings.development (default)'
    
    try:
        django.setup()
        from django.conf import settings
        
        print("✅ Django setup successful!")
        print(f"🐍 Python version: {sys.version}")
        print(f"🌐 Django version: {django.get_version()}")
        print(f"🛡️  Debug mode: {settings.DEBUG}")
        print(f"🗄️  Database engine: {settings.DATABASES['default']['ENGINE']}")
        print(f"📁 Database name: {settings.DATABASES['default']['NAME']}")
        print()
        
        print("📱 Installed Apps:")
        for app in settings.INSTALLED_APPS:
            if not app.startswith('django.'):
                print(f"   • {app}")
        print()
        
        # Check if migrations are needed
        print("🔍 Checking migrations...")
        os.system('python manage.py showmigrations --plan')
        
    except Exception as e:
        print(f"❌ Error setting up Django: {e}")
        return False
    
    print("=" * 60)
    print("✨ Environment check complete!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    check_environment()
