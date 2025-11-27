# vehiculos/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from decimal import Decimal
import math

from .models import Vehiculo, TallerMecanico, Mantenimiento
from .serializers import (
    VehiculoSerializer, 
    VehiculoListSerializer,
    TallerMecanicoSerializer,
    TallerMecanicoListSerializer,
    MantenimientoSerializer,
    MantenimientoListSerializer,
    MantenimientoCreateSerializer,
)


class VehiculoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar operaciones CRUD de Vehículos
    
    Endpoints:
    - GET /vehiculos/ - Listar todos los vehículos
    - POST /vehiculos/ - Crear un vehículo
    - GET /vehiculos/{id}/ - Obtener detalle de un vehículo
    - PUT /vehiculos/{id}/ - Actualizar un vehículo
    - PATCH /vehiculos/{id}/ - Actualizar parcialmente un vehículo
    - DELETE /vehiculos/{id}/ - Eliminar un vehículo
    """
    
    queryset = Vehiculo.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'marca', 'activo']
    search_fields = ['placa', 'marca', 'modelo', 'propietario_nombre']
    ordering_fields = ['fecha_registro', 'kilometraje', 'año']
    ordering = ['-fecha_registro']
    
    def get_serializer_class(self):
        """
        Usar serializer diferente según la acción
        """
        if self.action == 'list':
            return VehiculoListSerializer
        return VehiculoSerializer
    
    def get_queryset(self):
        """
        Personalizar el queryset con filtros adicionales
        """
        queryset = super().get_queryset()
        
        # Filtro por año mínimo
        año_min = self.request.query_params.get('año_min', None)
        if año_min:
            queryset = queryset.filter(año__gte=año_min)
        
        # Filtro por año máximo
        año_max = self.request.query_params.get('año_max', None)
        if año_max:
            queryset = queryset.filter(año__lte=año_max)
        
        # Filtro por kilometraje máximo
        km_max = self.request.query_params.get('kilometraje_max', None)
        if km_max:
            queryset = queryset.filter(kilometraje__lte=km_max)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def mantenimientos(self, request, pk=None):
        """
        Endpoint personalizado: GET /vehiculos/{id}/mantenimientos/
        Retorna todos los mantenimientos de un vehículo específico
        Parámetros opcionales:
        - fecha_desde: Filtrar mantenimientos desde esta fecha (formato: YYYY-MM-DD)
        - fecha_hasta: Filtrar mantenimientos hasta esta fecha (formato: YYYY-MM-DD)
        """
        vehiculo = self.get_object()
        mantenimientos = vehiculo.mantenimientos.all()

        # Aplicar filtros de fecha si se proporcionan
        fecha_desde = request.query_params.get('fecha_desde', None)
        fecha_hasta = request.query_params.get('fecha_hasta', None)

        if fecha_desde:
            mantenimientos = mantenimientos.filter(fecha_realizado__gte=fecha_desde)
        if fecha_hasta:
            mantenimientos = mantenimientos.filter(fecha_realizado__lte=fecha_hasta)

        serializer = MantenimientoListSerializer(mantenimientos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def actualizar_kilometraje(self, request, pk=None):
        """
        Endpoint personalizado: POST /vehiculos/{id}/actualizar_kilometraje/
        Body: {"kilometraje": 50000}
        """
        vehiculo = self.get_object()
        nuevo_km = request.data.get('kilometraje')
        
        if not nuevo_km:
            return Response(
                {'error': 'El campo kilometraje es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            nuevo_km = int(nuevo_km)
            if nuevo_km < vehiculo.kilometraje:
                return Response(
                    {'error': 'El nuevo kilometraje no puede ser menor al actual'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            vehiculo.kilometraje = nuevo_km
            vehiculo.save()
            
            serializer = self.get_serializer(vehiculo)
            return Response(serializer.data)
        
        except ValueError:
            return Response(
                {'error': 'El kilometraje debe ser un número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Endpoint personalizado: GET /vehiculos/estadisticas/
        Retorna estadísticas generales de los vehículos
        Parámetros opcionales:
        - fecha_desde: Filtrar vehículos registrados desde esta fecha (formato: YYYY-MM-DD)
        - fecha_hasta: Filtrar vehículos registrados hasta esta fecha (formato: YYYY-MM-DD)
        """
        # Obtener parámetros de fecha
        fecha_desde = request.query_params.get('fecha_desde', None)
        fecha_hasta = request.query_params.get('fecha_hasta', None)

        # Aplicar filtros de fecha al queryset base
        queryset = Vehiculo.objects.all()
        if fecha_desde:
            queryset = queryset.filter(fecha_registro__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_registro__lte=fecha_hasta)

        total = queryset.count()
        activos = queryset.filter(activo=True).count()

        # Estadísticas por tipo
        por_tipo = queryset.values('tipo').annotate(
            total=Count('id')
        )

        # Estadísticas por marca (top 10)
        por_marca = queryset.values('marca').annotate(
            total=Count('id')
        ).order_by('-total')[:10]

        # Promedio de kilometraje
        from django.db.models import Avg
        km_promedio = queryset.aggregate(
            promedio=Avg('kilometraje')
        )['promedio'] or 0

        # Top vehículos por cantidad de mantenimientos
        from django.db.models import Count as CountAgg, Q
        from vehiculos.models import Mantenimiento

        # Obtener vehículos con la cuenta de mantenimientos
        vehiculos_con_mantenimientos = queryset.annotate(
            count=CountAgg('mantenimientos')
        ).filter(count__gt=0).order_by('-count')[:10]

        top_mantenimientos = [{
            'vehiculo_nombre': f"{v.marca} {v.modelo}",
            'placa': v.placa,
            'count': v.count,
            'total': v.count,  # Agregar también como 'total' para compatibilidad
        } for v in vehiculos_con_mantenimientos]

        return Response({
            'total_vehiculos': total,
            'vehiculos_activos': activos,
            'vehiculos_inactivos': total - activos,
            'por_tipo': list(por_tipo),
            'por_marca': list(por_marca),
            'kilometraje_promedio': round(km_promedio, 2),
            'top_mantenimientos': top_mantenimientos,
        })


class TallerMecanicoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar operaciones CRUD de Talleres Mecánicos
    
    Incluye funcionalidad de búsqueda por ubicación
    """
    
    queryset = TallerMecanico.objects.filter(activo=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['verificado', 'activo']
    search_fields = ['nombre', 'direccion', 'servicios']
    ordering_fields = ['calificacion', 'nombre', 'fecha_registro']
    ordering = ['-calificacion', 'nombre']
    
    def get_serializer_class(self):
        """
        Usar serializer diferente según la acción
        """
        if self.action == 'list':
            return TallerMecanicoListSerializer
        return TallerMecanicoSerializer
    
    def get_queryset(self):
        """
        Personalizar queryset con búsqueda por ubicación
        """
        queryset = super().get_queryset()
        
        # Filtro por calificación mínima
        calificacion_min = self.request.query_params.get('calificacion_min', None)
        if calificacion_min:
            queryset = queryset.filter(calificacion__gte=calificacion_min)
        
        # Búsqueda por proximidad (simple)
        lat = self.request.query_params.get('latitud', None)
        lon = self.request.query_params.get('longitud', None)
        radio = self.request.query_params.get('radio', 10)  # Radio en km
        
        if lat and lon:
            try:
                lat = Decimal(lat)
                lon = Decimal(lon)
                radio = float(radio)
                
                # Calcular distancia y filtrar (método simplificado)
                talleres_con_distancia = []
                for taller in queryset:
                    distancia = self._calcular_distancia(
                        float(lat), float(lon),
                        float(taller.latitud), float(taller.longitud)
                    )
                    if distancia <= radio:
                        taller.distancia = Decimal(str(round(distancia, 2)))
                        talleres_con_distancia.append(taller)
                
                # Ordenar por distancia
                talleres_con_distancia.sort(key=lambda x: x.distancia)
                
                # Retornar IDs para el queryset
                ids = [t.id for t in talleres_con_distancia]
                queryset = TallerMecanico.objects.filter(id__in=ids)
                
                # Preservar el orden
                preserved = {id: idx for idx, id in enumerate(ids)}
                queryset = sorted(queryset, key=lambda x: preserved[x.id])
                
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    def _calcular_distancia(self, lat1, lon1, lat2, lon2):
        """
        Calcula la distancia entre dos puntos geográficos usando la fórmula de Haversine
        Retorna la distancia en kilómetros
        """
        R = 6371  # Radio de la Tierra en kilómetros
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distancia = R * c
        return distancia
    
    @action(detail=False, methods=['get'])
    def cercanos(self, request):
        """
        Endpoint personalizado: GET /talleres/cercanos/?latitud=X&longitud=Y&radio=10
        Retorna talleres cercanos a una ubicación
        """
        lat = request.query_params.get('latitud')
        lon = request.query_params.get('longitud')
        radio = request.query_params.get('radio', 10)
        
        if not lat or not lon:
            return Response(
                {'error': 'Se requieren los parámetros latitud y longitud'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Usar el queryset ya filtrado
        talleres = self.get_queryset()
        serializer = self.get_serializer(talleres, many=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def mantenimientos(self, request, pk=None):
        """
        Endpoint personalizado: GET /talleres/{id}/mantenimientos/
        Retorna todos los mantenimientos realizados en este taller
        Parámetros opcionales:
        - fecha_desde: Filtrar mantenimientos desde esta fecha (formato: YYYY-MM-DD)
        - fecha_hasta: Filtrar mantenimientos hasta esta fecha (formato: YYYY-MM-DD)
        """
        taller = self.get_object()
        mantenimientos = taller.mantenimientos.all()

        # Aplicar filtros de fecha si se proporcionan
        fecha_desde = request.query_params.get('fecha_desde', None)
        fecha_hasta = request.query_params.get('fecha_hasta', None)

        if fecha_desde:
            mantenimientos = mantenimientos.filter(fecha_realizado__gte=fecha_desde)
        if fecha_hasta:
            mantenimientos = mantenimientos.filter(fecha_realizado__lte=fecha_hasta)

        serializer = MantenimientoListSerializer(mantenimientos, many=True)
        return Response(serializer.data)


class MantenimientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar operaciones CRUD de Mantenimientos
    """
    
    queryset = Mantenimiento.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'estado', 'vehiculo', 'taller']
    search_fields = ['titulo', 'descripcion']
    ordering_fields = ['fecha_realizado', 'fecha_programada', 'costo']
    ordering = ['-fecha_realizado', '-fecha_programada']
    
    def get_serializer_class(self):
        """
        Usar serializer diferente según la acción
        """
        if self.action == 'list':
            return MantenimientoListSerializer
        elif self.action == 'create':
            return MantenimientoCreateSerializer
        return MantenimientoSerializer
    
    def get_queryset(self):
        """
        Personalizar queryset con filtros adicionales
        """
        queryset = super().get_queryset()
        
        # Filtro por rango de fechas
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        
        if fecha_desde:
            queryset = queryset.filter(fecha_realizado__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_realizado__lte=fecha_hasta)
        
        # Filtro por rango de costos
        costo_min = self.request.query_params.get('costo_min', None)
        costo_max = self.request.query_params.get('costo_max', None)
        
        if costo_min:
            queryset = queryset.filter(costo__gte=costo_min)
        if costo_max:
            queryset = queryset.filter(costo__lte=costo_max)
        
        # Filtro: Solo mantenimientos vencidos
        solo_vencidos = self.request.query_params.get('solo_vencidos', None)
        if solo_vencidos == 'true':
            from django.utils import timezone
            queryset = queryset.filter(
                estado='PENDIENTE',
                fecha_programada__lt=timezone.now().date()
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """
        Endpoint personalizado: GET /mantenimientos/pendientes/
        Retorna mantenimientos pendientes
        """
        mantenimientos = self.queryset.filter(estado='PENDIENTE')
        serializer = MantenimientoListSerializer(mantenimientos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def proximos(self, request):
        """
        Endpoint personalizado: GET /mantenimientos/proximos/
        Retorna próximos mantenimientos programados (siguiente semana)
        """
        from django.utils import timezone
        from datetime import timedelta
        
        hoy = timezone.now().date()
        proxima_semana = hoy + timedelta(days=7)
        
        mantenimientos = self.queryset.filter(
            estado='PENDIENTE',
            fecha_programada__range=[hoy, proxima_semana]
        )
        
        serializer = MantenimientoListSerializer(mantenimientos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """
        Endpoint personalizado: POST /mantenimientos/{id}/completar/
        Marca un mantenimiento como completado
        """
        mantenimiento = self.get_object()
        
        if mantenimiento.estado == 'COMPLETADO':
            return Response(
                {'error': 'Este mantenimiento ya está completado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.utils import timezone
        mantenimiento.estado = 'COMPLETADO'
        mantenimiento.fecha_realizado = timezone.now().date()
        mantenimiento.save()
        
        serializer = self.get_serializer(mantenimiento)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Endpoint personalizado: GET /mantenimientos/estadisticas/
        Retorna estadísticas de mantenimientos
        Parámetros opcionales:
        - fecha_desde: Filtrar desde esta fecha (formato: YYYY-MM-DD)
        - fecha_hasta: Filtrar hasta esta fecha (formato: YYYY-MM-DD)
        """
        from django.db.models import Avg, Sum
        from collections import defaultdict
        from datetime import datetime

        # Obtener parámetros de fecha
        fecha_desde = request.query_params.get('fecha_desde', None)
        fecha_hasta = request.query_params.get('fecha_hasta', None)

        # Aplicar filtros de fecha al queryset base
        queryset = Mantenimiento.objects.all()
        if fecha_desde:
            queryset = queryset.filter(fecha_realizado__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_realizado__lte=fecha_hasta)

        total = queryset.count()
        por_estado = queryset.values('estado').annotate(
            total=Count('id')
        )
        por_tipo = queryset.values('tipo').annotate(
            total=Count('id')
        )

        # Mantenimientos por mes (manual aggregation for SQLite compatibility)
        mantenimientos = queryset.filter(
            fecha_realizado__isnull=False
        ).values('fecha_realizado')

        por_mes_dict = defaultdict(int)
        por_fecha_dict = defaultdict(int)

        for m in mantenimientos:
            fecha = m['fecha_realizado']
            # Group by month
            mes_key = fecha.strftime('%Y-%m-01')
            por_mes_dict[mes_key] += 1
            # Group by date
            fecha_key = fecha.strftime('%Y-%m-%d')
            por_fecha_dict[fecha_key] += 1

        # Convert to list format
        por_mes = [{'mes': mes, 'total': total} for mes, total in sorted(por_mes_dict.items(), reverse=True)[:12]]
        por_fecha = [{'fecha': fecha, 'total': total} for fecha, total in sorted(por_fecha_dict.items(), key=lambda x: x[1], reverse=True)[:10]]

        # Costo promedio y total (usando el queryset filtrado)
        costo_promedio = queryset.aggregate(
            promedio=Avg('costo')
        )['promedio'] or 0

        costo_total = queryset.aggregate(
            total=Sum('costo')
        )['total'] or 0

        return Response({
            'total_mantenimientos': total,
            'por_estado': list(por_estado),
            'por_tipo': list(por_tipo),
            'por_mes': por_mes,
            'por_fecha': por_fecha,
            'costo_promedio': round(float(costo_promedio), 2),
            'costo_total': round(float(costo_total), 2),
        })
    
# vehiculos/views.py
# ... (código anterior existente) ...

# Agregar estos imports al inicio del archivo
from rest_framework.views import APIView
from .aws_location_service import aws_location_service

# Agregar estas vistas al final del archivo

class BuscarLugaresAPIView(APIView):
    """
    API View para buscar lugares usando AWS Location Service
    
    GET /api/aws-maps/buscar-lugares/?texto=taller&latitud=17.9892&longitud=-92.9475
    """
    
    def get(self, request):
        texto = request.query_params.get('texto')
        latitud = request.query_params.get('latitud')
        longitud = request.query_params.get('longitud')
        max_resultados = request.query_params.get('max_resultados', 10)
        
        if not texto:
            return Response(
                {'error': 'El parámetro "texto" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Convertir coordenadas si se proporcionan
            lat = float(latitud) if latitud else None
            lon = float(longitud) if longitud else None
            max_res = int(max_resultados)
            
            # Buscar lugares
            lugares = aws_location_service.buscar_lugares(
                texto=texto,
                latitud=lat,
                longitud=lon,
                max_resultados=max_res
            )
            
            return Response({
                'total': len(lugares),
                'lugares': lugares
            })
        
        except ValueError as e:
            return Response(
                {'error': 'Coordenadas inválidas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error al buscar lugares: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BuscarTalleresAWSAPIView(APIView):
    """
    API View para buscar talleres mecánicos usando AWS Location Service
    
    GET /api/aws-maps/buscar-talleres/?latitud=17.9892&longitud=-92.9475&radio=10
    """
    
    def get(self, request):
        latitud = request.query_params.get('latitud')
        longitud = request.query_params.get('longitud')
        radio = request.query_params.get('radio', 10)
        max_resultados = request.query_params.get('max_resultados', 20)
        
        if not latitud or not longitud:
            return Response(
                {'error': 'Los parámetros "latitud" y "longitud" son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            lat = float(latitud)
            lon = float(longitud)
            rad = float(radio)
            max_res = int(max_resultados)
            
            # Buscar talleres
            talleres = aws_location_service.buscar_talleres_cercanos(
                latitud=lat,
                longitud=lon,
                radio_km=rad,
                max_resultados=max_res
            )
            
            return Response({
                'ubicacion_busqueda': {
                    'latitud': lat,
                    'longitud': lon,
                    'radio_km': rad
                },
                'total': len(talleres),
                'talleres': talleres
            })
        
        except ValueError:
            return Response(
                {'error': 'Parámetros numéricos inválidos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error al buscar talleres: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GeocodificarAPIView(APIView):
    """
    API View para geocodificar direcciones (dirección → coordenadas)
    
    GET /api/aws-maps/geocodificar/?direccion=Av Universidad 2000, Villahermosa
    """
    
    def get(self, request):
        direccion = request.query_params.get('direccion')
        
        if not direccion:
            return Response(
                {'error': 'El parámetro "direccion" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            resultado = aws_location_service.geocodificar_direccion(direccion)
            
            if resultado:
                return Response(resultado)
            else:
                return Response(
                    {'error': 'No se encontraron resultados para la dirección proporcionada'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        except Exception as e:
            return Response(
                {'error': f'Error al geocodificar: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GeocodificarInversoAPIView(APIView):
    """
    API View para geocodificación inversa (coordenadas → dirección)
    
    GET /api/aws-maps/geocodificar-inverso/?latitud=17.9892&longitud=-92.9475
    """
    
    def get(self, request):
        latitud = request.query_params.get('latitud')
        longitud = request.query_params.get('longitud')
        
        if not latitud or not longitud:
            return Response(
                {'error': 'Los parámetros "latitud" y "longitud" son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            lat = float(latitud)
            lon = float(longitud)
            
            resultado = aws_location_service.geocodificar_inverso(lat, lon)
            
            if resultado:
                return Response(resultado)
            else:
                return Response(
                    {'error': 'No se encontró dirección para las coordenadas proporcionadas'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        except ValueError:
            return Response(
                {'error': 'Coordenadas inválidas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error en geocodificación inversa: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ValidarConfiguracionAWSAPIView(APIView):
    """
    API View para validar la configuración de AWS Location Service

    GET /api/aws-maps/validar-configuracion/
    """

    def get(self, request):
        try:
            estado = aws_location_service.validar_configuracion()

            return Response({
                'configuracion': estado,
                'mensaje': 'Configuración validada' if all(estado.values()) else 'Hay problemas con la configuración'
            })

        except Exception as e:
            return Response(
                {'error': f'Error al validar configuración: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CalcularRutaAPIView(APIView):
    """
    API View para calcular rutas entre dos puntos

    POST /api/aws-maps/calcular-ruta/
    Body: {
        "origen_lat": 18.0,
        "origen_lon": -92.9,
        "destino_lat": 19.4,
        "destino_lon": -99.1,
        "modo_viaje": "Car",  # Opcional: Car, Truck, Walking
        "optimizar_para": "FastestRoute"  # Opcional: FastestRoute, ShortestRoute
    }
    """

    def post(self, request):
        try:
            # Validar parámetros requeridos
            origen_lat = request.data.get('origen_lat')
            origen_lon = request.data.get('origen_lon')
            destino_lat = request.data.get('destino_lat')
            destino_lon = request.data.get('destino_lon')

            if not all([origen_lat, origen_lon, destino_lat, destino_lon]):
                return Response(
                    {'error': 'Se requieren origen_lat, origen_lon, destino_lat, destino_lon'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Parámetros opcionales
            modo_viaje = request.data.get('modo_viaje', 'Car')
            optimizar_para = request.data.get('optimizar_para', 'FastestRoute')

            # Calcular ruta
            ruta = aws_location_service.calcular_ruta(
                float(origen_lat),
                float(origen_lon),
                float(destino_lat),
                float(destino_lon),
                modo_viaje,
                optimizar_para
            )

            if ruta:
                return Response(ruta)
            else:
                return Response(
                    {'error': 'No se pudo calcular la ruta'},
                    status=status.HTTP_404_NOT_FOUND
                )

        except Exception as e:
            return Response(
                {'error': f'Error al calcular ruta: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BuscarRefaccionariasAPIView(APIView):
    """
    API View para buscar refaccionarias usando AWS Location Service

    GET /api/aws-maps/buscar-refaccionarias/?latitud=17.9892&longitud=-92.9475&radio=10
    """

    def get(self, request):
        latitud = request.query_params.get('latitud')
        longitud = request.query_params.get('longitud')
        radio = request.query_params.get('radio', 10)
        max_resultados = request.query_params.get('max_resultados', 20)

        if not latitud or not longitud:
            return Response(
                {'error': 'Los parámetros "latitud" y "longitud" son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lat = float(latitud)
            lon = float(longitud)
            rad = float(radio)
            max_res = int(max_resultados)

            # Buscar refaccionarias
            refaccionarias = aws_location_service.buscar_refaccionarias(
                latitud=lat,
                longitud=lon,
                radio_km=rad,
                max_resultados=max_res
            )

            return Response({
                'ubicacion_busqueda': {
                    'latitud': lat,
                    'longitud': lon,
                    'radio_km': rad
                },
                'total': len(refaccionarias),
                'refaccionarias': refaccionarias
            })

        except ValueError:
            return Response(
                {'error': 'Coordenadas o radio inválidos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error al buscar refaccionarias: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MapaEstaticoAPIView(APIView):
    """
    API View para generar URL de mapa estático

    GET /api/aws-maps/mapa-estatico/?latitud=17.9892&longitud=-92.9475&zoom=14&ancho=600&alto=400
    """

    def get(self, request):
        latitud = request.query_params.get('latitud')
        longitud = request.query_params.get('longitud')
        zoom = request.query_params.get('zoom', 14)
        ancho = request.query_params.get('ancho', 600)
        alto = request.query_params.get('alto', 400)

        if not latitud or not longitud:
            return Response(
                {'error': 'Los parámetros "latitud" y "longitud" son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lat = float(latitud)
            lon = float(longitud)
            z = int(zoom)
            w = int(ancho)
            h = int(alto)

            # Generar URL del mapa estático
            url_mapa = aws_location_service.obtener_url_mapa_estatico(
                latitud=lat,
                longitud=lon,
                zoom=z,
                ancho=w,
                alto=h
            )

            return Response({
                'url': url_mapa,
                'parametros': {
                    'latitud': lat,
                    'longitud': lon,
                    'zoom': z,
                    'dimensiones': f'{w}x{h}'
                }
            })

        except ValueError:
            return Response(
                {'error': 'Parámetros inválidos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error al generar URL del mapa: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

