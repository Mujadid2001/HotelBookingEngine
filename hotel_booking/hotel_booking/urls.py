"""
URL configuration for hotel_booking project.
Backend API for Hotel Booking Engine
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/bookings/', include('bookings.urls')),
    path('api/core/', include('core.urls')),
]
