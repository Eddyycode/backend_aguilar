# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework import permissions
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

# Simple views for health check and root
def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'API de Mantenimiento Vehicular funcionando correctamente'
    })

def root_view(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'Bienvenido a la API de Mantenimiento Vehicular',
        'endpoints': {
            'api': '/api/',
            'admin': '/admin/',
            'health': '/health',
            'docs': '/api/docs/',
        }
    })

urlpatterns = [
    # Root and health endpoints
    path('', root_view, name='root'),
    path('health', health_check, name='health'),

    path('admin/', admin.site.urls),
    path('api/', include('vehiculos.urls')),

    # Documentación de la API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]