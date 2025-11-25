# vehiculos/serializers.py
from rest_framework import serializers
from .models import Vehiculo, TallerMecanico, Mantenimiento
from decimal import Decimal

class VehiculoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Vehiculo
    Convierte instancias de Vehiculo a JSON y viceversa
    """
    
    # Campos calculados (read-only)
    nombre_completo = serializers.CharField(
        source='get_nombre_completo', 
        read_only=True
    )
    total_mantenimientos = serializers.SerializerMethodField()
    ultimo_mantenimiento = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehiculo
        fields = [
            'id',
            'placa',
            'marca',
            'modelo',
            'año',
            'tipo',
            'color',
            'kilometraje',
            'numero_serie',
            'propietario_nombre',
            'propietario_telefono',
            'propietario_email',
            'activo',
            'notas',
            'fecha_registro',
            # Campos calculados
            'nombre_completo',
            'total_mantenimientos',
            'ultimo_mantenimiento',
        ]
        read_only_fields = ['id', 'fecha_registro']
    
    def get_total_mantenimientos(self, obj):
        """Retorna el total de mantenimientos del vehículo"""
        return obj.mantenimientos.count()
    
    def get_ultimo_mantenimiento(self, obj):
        """Retorna información del último mantenimiento"""
        ultimo = obj.mantenimientos.filter(
            estado='COMPLETADO'
        ).order_by('-fecha_realizado').first()
        
        if ultimo:
            return {
                'id': ultimo.id,
                'titulo': ultimo.titulo,
                'fecha': ultimo.fecha_realizado,
                'kilometraje': ultimo.kilometraje_realizado,
            }
        return None
    
    def validate_placa(self, value):
        """Validación personalizada para la placa"""
        # Convertir a mayúsculas
        value = value.upper().strip()
        
        # Verificar que no esté vacía
        if not value:
            raise serializers.ValidationError("La placa no puede estar vacía")
        
        # Verificar longitud mínima
        if len(value) < 3:
            raise serializers.ValidationError(
                "La placa debe tener al menos 3 caracteres"
            )
        
        return value
    
    def validate_kilometraje(self, value):
        """Validación del kilometraje"""
        if value < 0:
            raise serializers.ValidationError(
                "El kilometraje no puede ser negativo"
            )
        if value > 1000000:
            raise serializers.ValidationError(
                "El kilometraje parece ser demasiado alto. Verifica el valor."
            )
        return value
    
    def validate(self, data):
        """Validación a nivel de objeto completo"""
        # Validar que el año no sea mayor al actual + 1
        from datetime import datetime
        año_actual = datetime.now().year
        
        if 'año' in data and data['año'] > año_actual + 1:
            raise serializers.ValidationError({
                'año': f'El año no puede ser mayor a {año_actual + 1}'
            })
        
        return data


class VehiculoListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar vehículos (más ligero)
    """
    nombre_completo = serializers.CharField(source='get_nombre_completo', read_only=True)
    
    class Meta:
        model = Vehiculo
        fields = [
            'id',
            'placa',
            'marca',
            'modelo',
            'año',
            'tipo',
            'kilometraje',
            'nombre_completo',
            'activo',
        ]


class TallerMecanicoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo TallerMecanico
    Incluye información de geolocalización
    """
    
    # Campo calculado para coordenadas
    coordenadas = serializers.SerializerMethodField()
    distancia = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True,
        required=False,
        help_text="Distancia en kilómetros (calculada dinámicamente)"
    )
    total_mantenimientos = serializers.SerializerMethodField()
    
    class Meta:
        model = TallerMecanico
        fields = [
            'id',
            'nombre',
            'direccion',
            'telefono',
            'email',
            'latitud',
            'longitud',
            'coordenadas',
            'horario',
            'sitio_web',
            'calificacion',
            'servicios',
            'verificado',
            'activo',
            'fecha_registro',
            'distancia',
            'total_mantenimientos',
        ]
        read_only_fields = ['id', 'fecha_registro']
    
    def get_coordenadas(self, obj):
        """Retorna las coordenadas como objeto"""
        return {
            'latitud': float(obj.latitud),
            'longitud': float(obj.longitud)
        }
    
    def get_total_mantenimientos(self, obj):
        """Retorna el total de mantenimientos realizados en este taller"""
        return obj.mantenimientos.filter(estado='COMPLETADO').count()
    
    def validate_latitud(self, value):
        """Validación de latitud"""
        if value < -90 or value > 90:
            raise serializers.ValidationError(
                "La latitud debe estar entre -90 y 90 grados"
            )
        return value
    
    def validate_longitud(self, value):
        """Validación de longitud"""
        if value < -180 or value > 180:
            raise serializers.ValidationError(
                "La longitud debe estar entre -180 y 180 grados"
            )
        return value
    
    def validate_calificacion(self, value):
        """Validación de calificación"""
        if value < Decimal('0.00') or value > Decimal('5.00'):
            raise serializers.ValidationError(
                "La calificación debe estar entre 0.00 y 5.00"
            )
        return value


class TallerMecanicoListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar talleres (más ligero)
    """
    coordenadas = serializers.SerializerMethodField()
    distancia = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True,
        required=False
    )
    
    class Meta:
        model = TallerMecanico
        fields = [
            'id',
            'nombre',
            'direccion',
            'telefono',
            'calificacion',
            'coordenadas',
            'verificado',
            'distancia',
        ]
    
    def get_coordenadas(self, obj):
        return {
            'latitud': float(obj.latitud),
            'longitud': float(obj.longitud)
        }


class MantenimientoSerializer(serializers.ModelSerializer):
    """
    Serializer completo para el modelo Mantenimiento
    """
    
    # Nested serializers para mostrar información relacionada
    vehiculo_info = VehiculoListSerializer(source='vehiculo', read_only=True)
    taller_info = TallerMecanicoListSerializer(source='taller', read_only=True)
    
    # Para escritura, solo se necesitan los IDs
    vehiculo = serializers.PrimaryKeyRelatedField(
        queryset=Vehiculo.objects.all(),
        write_only=True
    )
    taller = serializers.PrimaryKeyRelatedField(
        queryset=TallerMecanico.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )
    
    # Campos calculados
    dias_desde_mantenimiento = serializers.SerializerMethodField()
    esta_vencido = serializers.BooleanField(
        source='esta_vencido',
        read_only=True
    )
    
    class Meta:
        model = Mantenimiento
        fields = [
            'id',
            'vehiculo',
            'vehiculo_info',
            'taller',
            'taller_info',
            'tipo',
            'titulo',
            'descripcion',
            'estado',
            'fecha_programada',
            'fecha_realizado',
            'kilometraje_realizado',
            'proximo_kilometraje',
            'costo',
            'piezas_reemplazadas',
            'notas_adicionales',
            'fecha_registro',
            'fecha_actualizacion',
            'dias_desde_mantenimiento',
            'esta_vencido',
        ]
        read_only_fields = ['id', 'fecha_registro', 'fecha_actualizacion']
    
    def get_dias_desde_mantenimiento(self, obj):
        """Calcula los días desde que se realizó el mantenimiento"""
        if obj.fecha_realizado:
            from django.utils import timezone
            delta = timezone.now().date() - obj.fecha_realizado
            return delta.days
        return None
    
    def validate_costo(self, value):
        """Validación del costo"""
        if value < Decimal('0.00'):
            raise serializers.ValidationError(
                "El costo no puede ser negativo"
            )
        if value > Decimal('999999.99'):
            raise serializers.ValidationError(
                "El costo parece ser demasiado alto"
            )
        return value
    
    def validate(self, data):
        """Validaciones a nivel de objeto"""
        # Si hay próximo kilometraje, debe ser mayor al actual
        if 'proximo_kilometraje' in data and data.get('proximo_kilometraje'):
            kilometraje_actual = data.get('kilometraje_realizado')
            if data['proximo_kilometraje'] <= kilometraje_actual:
                raise serializers.ValidationError({
                    'proximo_kilometraje': 'El próximo kilometraje debe ser mayor al actual'
                })
        
        # Si está completado, debe tener fecha_realizado
        if data.get('estado') == 'COMPLETADO' and not data.get('fecha_realizado'):
            from django.utils import timezone
            data['fecha_realizado'] = timezone.now().date()
        
        # Validar que fecha_realizado no sea futura
        if data.get('fecha_realizado'):
            from django.utils import timezone
            if data['fecha_realizado'] > timezone.now().date():
                raise serializers.ValidationError({
                    'fecha_realizado': 'La fecha realizada no puede ser futura'
                })
        
        return data


class MantenimientoListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar mantenimientos (más ligero)
    """
    vehiculo_placa = serializers.CharField(source='vehiculo.placa', read_only=True)
    taller_nombre = serializers.CharField(source='taller.nombre', read_only=True)
    
    class Meta:
        model = Mantenimiento
        fields = [
            'id',
            'vehiculo_placa',
            'taller_nombre',
            'tipo',
            'titulo',
            'estado',
            'fecha_programada',
            'fecha_realizado',
            'costo',
        ]


class MantenimientoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer optimizado para crear mantenimientos
    """
    class Meta:
        model = Mantenimiento
        fields = [
            'vehiculo',
            'taller',
            'tipo',
            'titulo',
            'descripcion',
            'estado',
            'fecha_programada',
            'fecha_realizado',
            'kilometraje_realizado',
            'proximo_kilometraje',
            'costo',
            'piezas_reemplazadas',
            'notas_adicionales',
        ]
    
    def validate(self, data):
        """Validaciones para creación"""
        # Validar que el vehículo esté activo
        if not data['vehiculo'].activo:
            raise serializers.ValidationError({
                'vehiculo': 'No se puede crear un mantenimiento para un vehículo inactivo'
            })
        
        # Si hay taller, validar que esté activo
        if data.get('taller') and not data['taller'].activo:
            raise serializers.ValidationError({
                'taller': 'No se puede asignar un taller inactivo'
            })
        
        return data