# vehiculos/management/commands/generar_mantenimientos.py
import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from vehiculos.models import Vehiculo, TallerMecanico, Mantenimiento


class Command(BaseCommand):
    help = 'Genera 500 registros de mantenimiento coherentes con los vehículos existentes'

    # Tipos de mantenimiento según el tipo
    MANTENIMIENTOS_PREVENTIVOS = [
        ('Cambio de aceite y filtro', 800, 1500),
        ('Rotación de neumáticos', 300, 600),
        ('Revisión de frenos', 500, 1200),
        ('Cambio de filtro de aire', 250, 500),
        ('Revisión de suspensión', 600, 1000),
        ('Cambio de bujías', 800, 1500),
        ('Revisión general de motor', 1500, 3000),
        ('Cambio de líquido de frenos', 600, 1200),
        ('Cambio de anticongelante', 700, 1300),
        ('Alineación y balanceo', 500, 900),
        ('Cambio de filtro de combustible', 400, 800),
        ('Revisión de sistema eléctrico', 800, 1500),
        ('Cambio de correa de distribución', 3000, 6000),
        ('Servicio de transmisión', 2000, 4000),
        ('Inspección pre-ITV', 500, 1000),
    ]

    MANTENIMIENTOS_CORRECTIVOS = [
        ('Reparación de frenos delanteros', 2000, 4500),
        ('Reparación de frenos traseros', 1800, 4000),
        ('Cambio de batería', 1500, 3500),
        ('Reparación de alternador', 2500, 5000),
        ('Reparación de motor de arranque', 2000, 4000),
        ('Ajuste de válvulas', 1500, 3000),
        ('Reparación de escape', 1000, 2500),
        ('Cambio de embrague', 4000, 8000),
        ('Reparación de aire acondicionado', 2500, 5500),
        ('Cambio de sensor de oxígeno', 1200, 2500),
        ('Reparación de dirección hidráulica', 2000, 4500),
        ('Cambio de amortiguadores', 3000, 6000),
        ('Reparación de sistema de enfriamiento', 1500, 3500),
    ]

    MANTENIMIENTOS_REPARACION = [
        ('Reparación de transmisión automática', 8000, 15000),
        ('Reparación de motor', 10000, 25000),
        ('Reparación de sistema de suspensión', 5000, 10000),
        ('Reparación de caja de cambios', 6000, 12000),
        ('Reparación de sistema eléctrico completo', 4000, 9000),
        ('Reparación de chasis', 7000, 15000),
        ('Reparación de carrocería por colisión', 8000, 20000),
        ('Cambio de motor completo', 15000, 35000),
        ('Reparación de diferencial', 5000, 10000),
        ('Reparación de sistema de inyección', 4000, 8000),
        ('Rectificación de motor', 12000, 22000),
        ('Reparación de turbo', 6000, 12000),
    ]

    ESTADOS = ['COMPLETADO', 'COMPLETADO', 'COMPLETADO', 'COMPLETADO', 'PENDIENTE', 'CANCELADO']

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=500,
            help='Cantidad de mantenimientos a generar (default: 500)'
        )

    def handle(self, *args, **options):
        cantidad = options['cantidad']

        # Obtener vehículos y talleres
        vehiculos = list(Vehiculo.objects.all())
        talleres = list(TallerMecanico.objects.all())

        if not vehiculos:
            self.stdout.write(self.style.ERROR('No hay vehículos en la base de datos'))
            return

        if not talleres:
            self.stdout.write(self.style.ERROR('No hay talleres en la base de datos'))
            return

        self.stdout.write(f'Generando {cantidad} mantenimientos...')
        self.stdout.write(f'Vehículos disponibles: {len(vehiculos)}')
        self.stdout.write(f'Talleres disponibles: {len(talleres)}')

        mantenimientos_creados = 0
        fecha_actual = timezone.now().date()

        for i in range(cantidad):
            # Seleccionar vehículo aleatorio
            vehiculo = random.choice(vehiculos)
            taller = random.choice(talleres)

            # Seleccionar tipo de mantenimiento
            tipo = random.choice(['PREVENTIVO', 'CORRECTIVO', 'REPARACION'])

            if tipo == 'PREVENTIVO':
                titulo, costo_min, costo_max = random.choice(self.MANTENIMIENTOS_PREVENTIVOS)
            elif tipo == 'CORRECTIVO':
                titulo, costo_min, costo_max = random.choice(self.MANTENIMIENTOS_CORRECTIVOS)
            else:
                titulo, costo_min, costo_max = random.choice(self.MANTENIMIENTOS_REPARACION)

            # Generar costo aleatorio
            costo = Decimal(str(random.randint(costo_min, costo_max)))

            # Generar fechas coherentes basadas en el año del vehículo
            # Los mantenimientos deben ser posteriores a la compra del vehículo
            año_vehiculo = vehiculo.año
            fecha_inicio_posible = datetime(año_vehiculo, 1, 1).date()

            # Generar fecha programada entre el año del vehículo y ahora
            dias_desde_compra = (fecha_actual - fecha_inicio_posible).days
            if dias_desde_compra > 0:
                dias_random = random.randint(0, dias_desde_compra)
                fecha_programada = fecha_inicio_posible + timedelta(days=dias_random)
            else:
                fecha_programada = fecha_actual

            # Determinar estado
            estado = random.choice(self.ESTADOS)

            # Si está completado, la fecha realizada es cercana a la programada
            fecha_realizado = None
            if estado == 'COMPLETADO':
                # Completado entre 0 y 7 días después de la fecha programada
                dias_retraso = random.randint(0, 7)
                fecha_realizado = fecha_programada + timedelta(days=dias_retraso)

                # No puede ser en el futuro
                if fecha_realizado > fecha_actual:
                    fecha_realizado = fecha_actual
            elif estado == 'CANCELADO':
                costo = Decimal('0.00')

            # Generar descripción
            descripciones = [
                f'Mantenimiento {tipo.lower()} realizado en {taller.nombre}',
                f'Servicio programado de {titulo.lower()}',
                f'Intervención {tipo.lower()} en el vehículo {vehiculo.marca} {vehiculo.modelo}',
                f'{titulo} - Kilometraje: {vehiculo.kilometraje} km',
            ]
            descripcion = random.choice(descripciones)

            # Crear el mantenimiento
            try:
                # Calcular kilometraje realizado basado en la fecha del mantenimiento
                if estado == 'COMPLETADO':
                    # Simular un kilometraje histórico basado en la fecha
                    dias_transcurridos = (fecha_actual - fecha_realizado).days
                    km_aproximado = max(0, vehiculo.kilometraje - (dias_transcurridos * random.randint(5, 30)))
                    kilometraje_realizado = km_aproximado
                else:
                    kilometraje_realizado = vehiculo.kilometraje

                mantenimiento = Mantenimiento.objects.create(
                    vehiculo=vehiculo,
                    taller=taller,
                    tipo=tipo,
                    titulo=titulo,
                    descripcion=descripcion,
                    fecha_programada=fecha_programada,
                    fecha_realizado=fecha_realizado,
                    kilometraje_realizado=kilometraje_realizado,
                    costo=costo,
                    estado=estado,
                    notas_adicionales=f'Generado automáticamente - {tipo}'
                )
                mantenimientos_creados += 1

                if (i + 1) % 50 == 0:
                    self.stdout.write(f'Progreso: {i + 1}/{cantidad} mantenimientos creados...')

            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error al crear mantenimiento {i + 1}: {str(e)}'))

        self.stdout.write(
            self.style.SUCCESS(f'¡Proceso completado! Se crearon {mantenimientos_creados} mantenimientos.')
        )

        # Mostrar estadísticas
        total_mantenimientos = Mantenimiento.objects.count()
        self.stdout.write(f'\nEstadísticas finales:')
        self.stdout.write(f'Total de mantenimientos en BD: {total_mantenimientos}')
        self.stdout.write(f'Completados: {Mantenimiento.objects.filter(estado="COMPLETADO").count()}')
        self.stdout.write(f'Pendientes: {Mantenimiento.objects.filter(estado="PENDIENTE").count()}')
        self.stdout.write(f'Cancelados: {Mantenimiento.objects.filter(estado="CANCELADO").count()}')
