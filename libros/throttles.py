from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class BurstRateThrottle(UserRateThrottle):
    """Límite para ráfagas cortas"""
    scope = 'burst'


class SustainedRateThrottle(UserRateThrottle):
    """Límite sostenido"""
    scope = 'sustained'


class AnonBurstRateThrottle(AnonRateThrottle):
    """Límite para usuarios anónimos"""
    scope = 'anon_burst'


class PremiumUserThrottle(UserRateThrottle):
    """Límite más alto para usuarios premium"""
    scope = 'premium'
    
    def allow_request(self, request, view):
        # Usuarios premium tienen límite más alto
        if request.user.is_authenticated and hasattr(request.user, 'is_premium'):
            if request.user.is_premium:
                return True
        
        return super().allow_request(request, view)