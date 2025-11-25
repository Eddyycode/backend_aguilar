from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from vehiculos.models import Vehiculo, TallerMecanico, Mantenimiento


class Command(BaseCommand):
    help = 'Agrega 10 vehículos y genera 50 mantenimientos distribuidos en el último mes'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando generación de datos...\n')

        # Datos para vehículos
        marcas = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'Nissan', 'Mazda', 'Volkswagen', 'Hyundai']
        modelos = {
            'Toyota': ['Corolla', 'Camry', 'RAV4', 'Hilux'],
            'Honda': ['Civic', 'Accord', 'CR-V', 'Pilot'],
            'Ford': ['F-150', 'Escape', 'Explorer', 'Mustang'],
            'Chevrolet': ['Silverado', 'Equinox', 'Malibu', 'Tahoe'],
            'Nissan': ['Sentra', 'Altima', 'Rogue', 'Frontier'],
            'Mazda': ['Mazda3', 'Mazda6', 'CX-5', 'CX-9'],
            'Volkswagen': ['Jetta', 'Tiguan', 'Passat', 'Golf'],
            'Hyundai': ['Elantra', 'Sonata', 'Tucson', 'Santa Fe']
        }
        colores = ['Blanco', 'Negro', 'Gris', 'Plata', 'Azul', 'Rojo', 'Verde']
        tipos = ['AUTO', 'CAMIONETA', 'VAN', 'MOTO']
        nombres = [
            'Juan Pérez', 'María González', 'Carlos López', 'Ana Martínez',
            'Luis Hernández', 'Laura Rodríguez', 'Miguel Sánchez', 'Patricia Torres',
            'Roberto Díaz', 'Carmen Ramírez'
        ]

        # Crear 10 vehículos
        self.stdout.write('Creando 10 vehículos nuevos...')
        vehiculos_nuevos = []

        for i in range(10):
            marca = random.choice(marcas)
            modelo = random.choice(modelos[marca])
            año = random.randint(2015, 2024)

            # Generar placa única
            placa = f"ABC-{random.randint(1000, 9999)}"
            while Vehiculo.objects.filter(placa=placa).exists():
                placa = f"ABC-{random.randint(1000, 9999)}"

            vehiculo = Vehiculo.objects.create(
                placa=placa,
                marca=marca,
                modelo=modelo,
                año=año,
                tipo=random.choice(tipos),
                kilometraje=random.randint(5000, 150000),
                color=random.choice(colores),
                propietario_nombre=nombres[i],
                propietario_telefono=f"999-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                propietario_email=f"{nombres[i].split()[0].lower()}@email.com",
                activo=True,
                notas=f"Vehículo agregado para pruebas - {timezone.now().strftime('%Y-%m-%d')}"
            )
            vehiculos_nuevos.append(vehiculo)
            self.stdout.write(f'  ✓ Creado: {vehiculo}')

        self.stdout.write(self.style.SUCCESS(f'\n✓ {len(vehiculos_nuevos)} vehículos creados\n'))

        # Obtener todos los vehículos y talleres disponibles
        todos_vehiculos = list(Vehiculo.objects.all())
        talleres = list(TallerMecanico.objects.filter(activo=True))

        if not talleres:
            self.stdout.write(self.style.ERROR('No hay talleres disponibles. Creando uno...'))
            taller = TallerMecanico.objects.create(
                nombre='Taller de Pruebas',
                direccion='Calle Principal #123',
                telefono='999-000-0000',
                latitud=Decimal('17.9892'),
                longitud=Decimal('-92.9475'),
                calificacion=Decimal('4.5'),
                activo=True,
                verificado=True
            )
            talleres.append(taller)

        # Datos para mantenimientos
        tipos_mantenimiento = ['PREVENTIVO', 'CORRECTIVO', 'REVISION', 'REPARACION']
        titulos = [
            'Cambio de aceite',
            'Cambio de filtros',
            'Revisión de frenos',
            'Alineación y balanceo',
            'Cambio de llantas',
            'Revisión de suspensión',
            'Cambio de batería',
            'Mantenimiento de transmisión',
            'Cambio de bujías',
            'Revisión general',
            'Reparación de motor',
            'Cambio de líquidos',
            'Revisión eléctrica',
            'Cambio de pastillas de freno',
            'Servicio de aire acondicionado'
        ]

        piezas = [
            'Aceite sintético, filtro de aceite',
            'Filtro de aire, filtro de combustible',
            'Pastillas de freno delanteras',
            'Neumáticos nuevos',
            'Amortiguadores traseros',
            'Batería 12V',
            'Kit de embrague',
            'Bujías de iridio',
            'Líquido de frenos, refrigerante',
            'Alternador',
            'Bomba de agua',
            'Correa de distribución'
        ]

        # Calcular fechas
        ahora = timezone.now()
        hace_24_horas = ahora - timedelta(hours=24)
        hace_1_semana = ahora - timedelta(days=7)
        hace_1_mes = ahora - timedelta(days=30)

        self.stdout.write('\nGenerando 50 mantenimientos...')
        mantenimientos_creados = []

        # Función auxiliar para crear mantenimiento
        def crear_mantenimiento(fecha_base, vehiculo):
            # Añadir variación aleatoria a la fecha
            variacion_horas = random.randint(0, 23)
            variacion_minutos = random.randint(0, 59)
            fecha = fecha_base + timedelta(hours=variacion_horas, minutes=variacion_minutos)

            tipo = random.choice(tipos_mantenimiento)
            titulo = random.choice(titulos)

            mantenimiento = Mantenimiento.objects.create(
                vehiculo=vehiculo,
                taller=random.choice(talleres),
                tipo=tipo,
                titulo=titulo,
                descripcion=f"Mantenimiento de tipo {tipo.lower()} realizado en {fecha.strftime('%Y-%m-%d')}",
                estado='COMPLETADO',
                fecha_programada=fecha.date(),
                fecha_realizado=fecha.date(),
                kilometraje_realizado=vehiculo.kilometraje + random.randint(-5000, 0),
                proximo_kilometraje=vehiculo.kilometraje + random.randint(5000, 15000),
                costo=Decimal(str(random.randint(500, 5000))),
                piezas_reemplazadas=random.choice(piezas),
                notas_adicionales=f"Generado automáticamente - {fecha.strftime('%Y-%m-%d %H:%M')}"
            )
            return mantenimiento

        # 1. Generar 15 mantenimientos en las últimas 24 horas
        self.stdout.write('\n  Generando 15 mantenimientos en las últimas 24 horas...')
        for i in range(15):
            # Distribuir uniformemente en las últimas 24 horas
            horas_atras = random.uniform(0, 24)
            fecha_base = ahora - timedelta(hours=horas_atras)
            vehiculo = random.choice(todos_vehiculos)

            mantenimiento = crear_mantenimiento(fecha_base, vehiculo)
            mantenimientos_creados.append(mantenimiento)
            self.stdout.write(f'    ✓ {mantenimiento.titulo} - {vehiculo.placa} ({mantenimiento.fecha_realizado})')

        # 2. Generar 20 mantenimientos en la última semana (excluyendo últimas 24 horas)
        self.stdout.write('\n  Generando 20 mantenimientos en la última semana...')
        for i in range(20):
            # Entre hace 1 semana y hace 24 horas
            dias_atras = random.uniform(1, 7)
            fecha_base = ahora - timedelta(days=dias_atras)
            vehiculo = random.choice(todos_vehiculos)

            mantenimiento = crear_mantenimiento(fecha_base, vehiculo)
            mantenimientos_creados.append(mantenimiento)
            self.stdout.write(f'    ✓ {mantenimiento.titulo} - {vehiculo.placa} ({mantenimiento.fecha_realizado})')

        # 3. Generar 15 mantenimientos en el resto del mes
        self.stdout.write('\n  Generando 15 mantenimientos en el resto del mes...')
        for i in range(15):
            # Entre hace 1 mes y hace 1 semana
            dias_atras = random.uniform(7, 30)
            fecha_base = ahora - timedelta(days=dias_atras)
            vehiculo = random.choice(todos_vehiculos)

            mantenimiento = crear_mantenimiento(fecha_base, vehiculo)
            mantenimientos_creados.append(mantenimiento)
            self.stdout.write(f'    ✓ {mantenimiento.titulo} - {vehiculo.placa} ({mantenimiento.fecha_realizado})')

        self.stdout.write(self.style.SUCCESS(f'\n✓ {len(mantenimientos_creados)} mantenimientos creados\n'))

        # Resumen
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('RESUMEN:'))
        self.stdout.write(self.style.SUCCESS(f'  • Vehículos agregados: {len(vehiculos_nuevos)}'))
        self.stdout.write(self.style.SUCCESS(f'  • Total de vehículos: {Vehiculo.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  • Mantenimientos generados: {len(mantenimientos_creados)}'))
        self.stdout.write(self.style.SUCCESS(f'    - Últimas 24 horas: 15'))
        self.stdout.write(self.style.SUCCESS(f'    - Última semana: 20'))
        self.stdout.write(self.style.SUCCESS(f'    - Resto del mes: 15'))
        self.stdout.write(self.style.SUCCESS(f'  • Total de mantenimientos: {Mantenimiento.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
