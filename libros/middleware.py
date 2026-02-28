from django.core.cache import cache
from django.http import JsonResponse, HttpResponsePermanentRedirect
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """Middleware de seguridad personalizado"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verificar headers de seguridad
        if not request.is_secure() and not request.META.get('HTTP_X_FORWARDED_PROTO') == 'https':
            if hasattr(settings, 'SECURE_SSL_REDIRECT') and settings.SECURE_SSL_REDIRECT:
                return HttpResponsePermanentRedirect(
                    request.build_absolute_uri().replace('http://', 'https://')
                )
        
        response = self.get_response(request)
        
        # Agregar headers de seguridad
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        return response


class RateLimitMiddleware:
    """Limitar requests por IP"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.limit = 100  # requests
        self.period = 3600  # 1 hora en segundos
    
    def __call__(self, request):
        ip = self.get_client_ip(request)
        
        # Solo para rutas /api/
        if request.path.startswith('/api/'):
            cache_key = f'rate_limit_{ip}'
            requests_count = cache.get(cache_key, 0)
            
            if requests_count >= self.limit:
                logger.warning(f'Rate limit exceeded for IP: {ip}')
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'detail': f'Máximo {self.limit} requests por hora'
                }, status=429)
            
            # Incrementar contador
            cache.set(cache_key, requests_count + 1, self.period)
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Obtener IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip