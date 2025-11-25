# vehiculos/admin.py
from django.contrib import admin
from .models import Vehiculo, TallerMecanico, Mantenimiento

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ['placa', 'marca', 'modelo', 'año', 'kilometraje', 'activo']
    list_filter = ['tipo', 'activo', 'marca']
    search_fields = ['placa', 'marca', 'modelo', 'propietario_nombre']
    ordering = ['-fecha_registro']
    
    fieldsets = (
        ('Información del Vehículo', {
            'fields': ('placa', 'marca', 'modelo', 'año', 'tipo', 'color', 'numero_serie')
        }),
        ('Información Técnica', {
            'fields': ('kilometraje', 'activo')
        }),
        ('Propietario', {
            'fields': ('propietario_nombre', 'propietario_telefono', 'propietario_email')
        }),
        ('Notas', {
            'fields': ('notas',),
            'classes': ('collapse',)
        }),
    )


@admin.register(TallerMecanico)
class TallerMecanicoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'direccion', 'telefono', 'calificacion', 'verificado', 'activo']
    list_filter = ['verificado', 'activo', 'calificacion']
    search_fields = ['nombre', 'direccion']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'direccion', 'telefono', 'email', 'sitio_web')
        }),
        ('Geolocalización', {
            'fields': ('latitud', 'longitud'),
            'description': 'Coordenadas geográficas del taller'
        }),
        ('Operación', {
            'fields': ('horario', 'servicios', 'calificacion', 'verificado', 'activo')
        }),
    )


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'vehiculo', 'taller', 'tipo', 'estado', 'fecha_realizado', 'costo']
    list_filter = ['tipo', 'estado', 'fecha_realizado']
    search_fields = ['titulo', 'descripcion', 'vehiculo__placa']
    ordering = ['-fecha_realizado', '-fecha_programada']
    date_hierarchy = 'fecha_realizado'
    
    fieldsets = (
        ('Relaciones', {
            'fields': ('vehiculo', 'taller')
        }),
        ('Información del Mantenimiento', {
            'fields': ('tipo', 'titulo', 'descripcion', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_programada', 'fecha_realizado')
        }),
        ('Información Técnica', {
            'fields': ('kilometraje_realizado', 'proximo_kilometraje', 'piezas_reemplazadas')
        }),
        ('Costos', {
            'fields': ('costo',)
        }),
        ('Notas Adicionales', {
            'fields': ('notas_adicionales',),
            'classes': ('collapse',)
        }),
    )