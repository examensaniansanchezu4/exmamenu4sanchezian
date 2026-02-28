from django.shortcuts import render, redirect
from django.conf import settings


def home(request):
    """Página de inicio"""
    return render(request, 'home.html')


def oauth_login(request):
    """Página de login con OAuth que maneja el callback de Google"""
    # Si hay un código en la URL, renderizar la página
    # que procesará el código
    return render(request, 'oauth_login.html')


def jwt_login_page(request):
    """Página de login con JWT (tradicional)"""
    return render(request, 'jwt_login.html')