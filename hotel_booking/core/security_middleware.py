"""
Additional security middleware for production
"""
import logging
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger('django.security')


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add additional security headers"""
    
    def process_response(self, request, response):
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        # Additional security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response


class RequestSizeMiddleware(MiddlewareMixin):
    """Limit request size for security"""
    
    def process_request(self, request):
        max_size = getattr(settings, 'DATA_UPLOAD_MAX_MEMORY_SIZE', 10 * 1024 * 1024)
        
        if request.content_length and request.content_length > max_size:
            logger.warning(f'Request size {request.content_length} exceeds limit from {request.META.get("REMOTE_ADDR")}')
            return HttpResponseForbidden('Request too large')
        
        return None


class SuspiciousRequestMiddleware(MiddlewareMixin):
    """Log suspicious requests"""
    
    SUSPICIOUS_PATTERNS = [
        '../', '..\\', '/etc/', '/proc/', '/var/',
        '<script', 'javascript:', 'eval(', 'document.cookie',
        'union select', 'drop table', 'insert into',
    ]
    
    def process_request(self, request):
        # Check for suspicious patterns in URL and parameters
        full_path = request.get_full_path().lower()
        
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern in full_path:
                logger.warning(
                    f'Suspicious request pattern "{pattern}" detected from {request.META.get("REMOTE_ADDR")}: {full_path}'
                )
                break
        
        # Check POST data for suspicious patterns
        if request.method == 'POST' and hasattr(request, 'POST'):
            post_data = str(request.POST).lower()
            for pattern in self.SUSPICIOUS_PATTERNS:
                if pattern in post_data:
                    logger.warning(
                        f'Suspicious POST data pattern "{pattern}" detected from {request.META.get("REMOTE_ADDR")}'
                    )
                    break
        
        return None
