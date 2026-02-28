from django.urls import path
from .views import chat_view   # ✅ IMPORTANTE

urlpatterns = [
    path('chat/', chat_view),
]