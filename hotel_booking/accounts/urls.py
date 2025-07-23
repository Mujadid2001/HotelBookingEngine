from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('login/', views.login_api_view, name='login'),
    path('logout/', views.logout_api_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile
    path('profile/', views.ProfileAPIView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateAPIView.as_view(), name='profile_update'),
    
    # Password management
    path('password/change/', views.PasswordChangeAPIView.as_view(), name='password_change'),
    path('password/reset/', views.password_reset_request, name='password_reset'),
    path('password-reset-confirm/<uuid:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Email verification
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    
    # Account management
    path('delete/', views.delete_account, name='delete_account'),
]
