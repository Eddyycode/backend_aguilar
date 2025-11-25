# vehiculos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VehiculoViewSet,
    TallerMecanicoViewSet,
    MantenimientoViewSet,
    # Nuevas vistas de AWS Maps
    BuscarLugaresAPIView,
    BuscarTalleresAWSAPIView,
    GeocodificarAPIView,
    GeocodificarInversoAPIView,
    ValidarConfiguracionAWSAPIView,
    CalcularRutaAPIView,
)

# Crear el router
router = DefaultRouter()

# Registrar los viewsets
router.register(r'vehiculos', VehiculoViewSet, basename='vehiculo')
router.register(r'talleres', TallerMecanicoViewSet, basename='taller')
router.register(r'mantenimientos', MantenimientoViewSet, basename='mantenimiento')

# URLs de la aplicación
urlpatterns = [
    path('', include(router.urls)),
    
    # Endpoints de AWS Maps
    path('aws-maps/buscar-lugares/', BuscarLugaresAPIView.as_view(), name='aws-buscar-lugares'),
    path('aws-maps/buscar-talleres/', BuscarTalleresAWSAPIView.as_view(), name='aws-buscar-talleres'),
    path('aws-maps/geocodificar/', GeocodificarAPIView.as_view(), name='aws-geocodificar'),
    path('aws-maps/geocodificar-inverso/', GeocodificarInversoAPIView.as_view(), name='aws-geocodificar-inverso'),
    path('aws-maps/validar-configuracion/', ValidarConfiguracionAWSAPIView.as_view(), name='aws-validar-config'),
    path('aws-maps/calcular-ruta/', CalcularRutaAPIView.as_view(), name='aws-calcular-ruta'),
]

