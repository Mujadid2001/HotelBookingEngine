from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

try:
    from rest_framework import permissions
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    HAS_SWAGGER = True
except ImportError:
    HAS_SWAGGER = False

def api_root(request):
    return JsonResponse({
        'message': 'Hotel Booking Engine API',
        'version': 'v1.0',
        'endpoints': {
            'auth': f'{request.build_absolute_uri()}auth/',
            'hotels': f'{request.build_absolute_uri()}hotels/',
            'bookings': f'{request.build_absolute_uri()}bookings/',
        }
    })

urlpatterns = [
    path('', include('core.dashboard_urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', api_root, name='api_root'),
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/hotels/', include('core.urls')),
    path('api/v1/bookings/', include('bookings.urls')),
]

if HAS_SWAGGER:
    schema_view = get_schema_view(
        openapi.Info(
            title="Hotel Booking Engine API",
            default_version='v1',
            description="Hotel booking and management API",
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )
    
    urlpatterns += [
        path('api/v1/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    ]
