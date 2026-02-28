# ===================================
# URLS DE LA API - libros/api_urls.py
# ===================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.urls import path


# Importar vistas JWT de SimpleJWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,      # Vista para login (obtener tokens)
    TokenRefreshView,          # Vista para refrescar access token
    TokenVerifyView,           # Vista para verificar token
)

# Importar ViewSets
from . import api_views
from . import oauth_views 

# ===== ROUTER PARA VIEWSETS =====
# El router genera automáticamente las URLs para CRUD
router = DefaultRouter()
router.register(r'libros', api_views.LibroViewSet, basename='libro')
router.register(r'autores', api_views.AutorViewSet, basename='autor')
router.register(r'categorias', api_views.CategoriaViewSet, basename='categoria')
router.register(r'prestamos', api_views.PrestamoViewSet, basename='prestamo')

# ===== URL PATTERNS =====
urlpatterns = [
    # ─────────────────────────────────
    # 🔐 AUTENTICACIÓN JWT
    # ─────────────────────────────────
    
    # Login con JWT (POST: username + password → access y refresh tokens)
    path('auth/jwt/login/', TokenObtainPairView.as_view(), name='jwt_login'),
    
    # Refrescar token (POST: refresh_token → nuevo access_token)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Verificar token (POST: token → válido o inválido)
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
     
    # ─────────────────────────────────
    # 🔑 AUTENTICACIÓN OAUTH 2.0 (GOOGLE)
    # ─────────────────────────────────
    path('auth/google/redirect/', oauth_views.google_oauth_redirect, name='google_redirect'),
    path('auth/google/callback/', oauth_views.google_oauth_callback, name='google_callback'),
    # ─────────────────────────────────
    # 📚 ENDPOINTS DE LA API (CRUD)
    # ─────────────────────────────────
    
    # Incluir todas las rutas del router
    # Esto genera automáticamente:
    # GET    /api/libros/          - Listar todos los libros
    # POST   /api/libros/          - Crear nuevo libro
    # GET    /api/libros/{id}/     - Ver detalle de libro
    # PUT    /api/libros/{id}/     - Actualizar libro
    # DELETE /api/libros/{id}/     - Eliminar libro
    # Y lo mismo para autores, categorias, prestamos
    path('', include(router.urls)),
    

    
]