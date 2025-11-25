# vehiculos/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Vehiculo(models.Model):
    """
    Modelo para representar un vehículo del usuario
    """
    
    TIPO_VEHICULO_CHOICES = [
        ('AUTO', 'Automóvil'),
        ('MOTO', 'Motocicleta'),
        ('CAMIONETA', 'Camioneta'),
        ('CAMION', 'Camión'),
        ('VAN', 'Van'),
    ]
    
    # Identificación del vehículo
    placa = models.CharField(
        max_length=20, 
        unique=True,
        help_text="Placa o matrícula del vehículo"
    )
    marca = models.CharField(
        max_length=50,
        help_text="Marca del vehículo (ej: Toyota, Ford, Honda)"
    )
    modelo = models.CharField(
        max_length=50,
        help_text="Modelo del vehículo (ej: Corolla, F-150)"
    )
    año = models.IntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(2030)
        ],
        help_text="Año de fabricación"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_VEHICULO_CHOICES,
        default='AUTO'
    )
    
    # Información técnica
    kilometraje = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Kilometraje actual del vehículo"
    )
    numero_serie = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Número de serie o VIN"
    )
    color = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )
    
    # Información del propietario (simplificado)
    propietario_nombre = models.CharField(
        max_length=100,
        help_text="Nombre del propietario"
    )
    propietario_telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )
    propietario_email = models.EmailField(
        blank=True,
        null=True
    )
    
    # Metadatos
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de registro en el sistema"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si el vehículo está activo en el sistema"
    )
    notas = models.TextField(
        blank=True,
        null=True,
        help_text="Notas adicionales sobre el vehículo"
    )
    
    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['placa']),
            models.Index(fields=['marca', 'modelo']),
        ]
    
    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.placa})"
    
    def get_nombre_completo(self):
        """Retorna el nombre completo del vehículo"""
        return f"{self.marca} {self.modelo} {self.año}"


class TallerMecanico(models.Model):
    """
    Modelo para representar talleres mecánicos con geolocalización
    """
    
    # Información básica
    nombre = models.CharField(
        max_length=150,
        help_text="Nombre del taller mecánico"
    )
    direccion = models.CharField(
        max_length=255,
        help_text="Dirección completa del taller"
    )
    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )
    email = models.EmailField(
        blank=True,
        null=True
    )
    
    # Geolocalización (CRÍTICO para AWS Maps)
    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Latitud geográfica del taller"
    )
    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Longitud geográfica del taller"
    )
    
    # Información operativa
    horario = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Horario de atención (ej: Lun-Vie 8:00-18:00)"
    )
    sitio_web = models.URLField(
        blank=True,
        null=True
    )
    calificacion = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('5.00'))
        ],
        help_text="Calificación del taller (0.00 a 5.00)"
    )
    
    # Servicios ofrecidos
    servicios = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción de servicios ofrecidos (separados por comas)"
    )
    
    # Metadatos
    verificado = models.BooleanField(
        default=False,
        help_text="Indica si el taller ha sido verificado por el sistema"
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si el taller está activo"
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = "Taller Mecánico"
        verbose_name_plural = "Talleres Mecánicos"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['latitud', 'longitud']),
            models.Index(fields=['nombre']),
        ]
    
    def __str__(self):
        return f"{self.nombre} - {self.direccion}"
    
    def get_coordenadas(self):
        """Retorna las coordenadas como tupla (lat, lon)"""
        return (float(self.latitud), float(self.longitud))


class Mantenimiento(models.Model):
    """
    Modelo para registrar mantenimientos realizados a vehículos
    """
    
    TIPO_MANTENIMIENTO_CHOICES = [
        ('PREVENTIVO', 'Mantenimiento Preventivo'),
        ('CORRECTIVO', 'Mantenimiento Correctivo'),
        ('REVISION', 'Revisión General'),
        ('REPARACION', 'Reparación'),
    ]
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En Proceso'),
        ('COMPLETADO', 'Completado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    # Relaciones
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name='mantenimientos',
        help_text="Vehículo al que se le realizó el mantenimiento"
    )
    taller = models.ForeignKey(
        TallerMecanico,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mantenimientos',
        help_text="Taller donde se realizó el mantenimiento"
    )
    
    # Información del mantenimiento
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_MANTENIMIENTO_CHOICES,
        default='PREVENTIVO'
    )
    titulo = models.CharField(
        max_length=200,
        help_text="Título o resumen del mantenimiento"
    )
    descripcion = models.TextField(
        help_text="Descripción detallada del mantenimiento realizado"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )
    
    # Fechas
    fecha_programada = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha programada para el mantenimiento"
    )
    fecha_realizado = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha en que se realizó el mantenimiento"
    )
    
    # Información técnica
    kilometraje_realizado = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Kilometraje del vehículo al momento del mantenimiento"
    )
    proximo_kilometraje = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Kilometraje sugerido para próximo mantenimiento"
    )
    
    # Costos
    costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Costo total del mantenimiento"
    )
    
    # Piezas/Refacciones
    piezas_reemplazadas = models.TextField(
        blank=True,
        null=True,
        help_text="Lista de piezas que fueron reemplazadas"
    )
    
    # Metadatos
    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True
    )
    notas_adicionales = models.TextField(
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"
        ordering = ['-fecha_realizado', '-fecha_programada']
        indexes = [
            models.Index(fields=['vehiculo', 'fecha_realizado']),
            models.Index(fields=['estado']),
            models.Index(fields=['tipo']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.vehiculo.placa} ({self.fecha_realizado or 'Pendiente'})"
    
    def save(self, *args, **kwargs):
        """
        Sobrescribir save para validaciones personalizadas
        """
        # Si el mantenimiento está completado, asegurar que tenga fecha_realizado
        if self.estado == 'COMPLETADO' and not self.fecha_realizado:
            from django.utils import timezone
            self.fecha_realizado = timezone.now().date()
        
        super().save(*args, **kwargs)
    
    def esta_vencido(self):
        """
        Verifica si un mantenimiento programado está vencido
        """
        from django.utils import timezone
        if self.estado == 'PENDIENTE' and self.fecha_programada:
            return self.fecha_programada < timezone.now().date()
        return False