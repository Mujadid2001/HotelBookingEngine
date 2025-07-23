"""
JWT Token Blacklist Middleware

This middleware checks if JWT tokens are blacklisted and rejects requests
with blacklisted tokens automatically.
"""
# Standard library imports
import json

# Django imports
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.db import connection

# Third-party imports
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class TokenBlacklistMiddleware(MiddlewareMixin):
    """Middleware to check if JWT tokens are blacklisted"""
    
    SKIP_PATHS = ['/api/accounts/register/', '/api/accounts/login/', 
                  '/api/accounts/password/reset/', '/api/accounts/token/refresh/', '/admin/']
    
    def process_request(self, request):
        # Skip blacklist check for certain endpoints
        if any(request.path.startswith(path) for path in self.SKIP_PATHS):
            return None
        
        # Check Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        try:
            # Parse token to get JTI and check if blacklisted
            token = UntypedToken(auth_header.split(' ')[1])
            jti = str(token['jti'])
            
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1 FROM simple_token_blacklist WHERE jti = ?', [jti])
                if cursor.fetchone():
                    return JsonResponse({'error': 'Token has been blacklisted', 'code': 'token_blacklisted'}, 
                                      status=401)
                    
        except (InvalidToken, TokenError, Exception):
            # Invalid token, let DRF handle it
            pass
        
        return None
