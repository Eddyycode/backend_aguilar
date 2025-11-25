# vehiculos/management/commands/crear_datos_prueba.py
from django.core.management.base import BaseCommand
from vehiculos.models import Vehiculo, TallerMecanico, Mantenimiento
from decimal import Decimal
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Crea datos de prueba para el sistema'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--vehiculos',
            type=int,
            default=5,
            help='Número de vehículos a crear'
        )
        parser.add_argument(
            '--talleres',
            type=int,
            default=3,
            help='Número de talleres a crear'
        )
    
    def handle(self, *args, **options):
        num_vehiculos = options['vehiculos']
        num_talleres = options['talleres']
        
        self.stdout.write('Creando datos de prueba...')
        
        # Crear vehículos
        vehiculos = self.crear_vehiculos(num_vehiculos)
        self.stdout.write(self.style.SUCCESS(f'✓ {len(vehiculos)} vehículos creados'))
        
        # Crear talleres
        talleres = self.crear_talleres(num_talleres)
        self.stdout.write(self.style.SUCCESS(f'✓ {len(talleres)} talleres creados'))
        
        # Crear mantenimientos
        mantenimientos = self.crear_mantenimientos(vehiculos, talleres)
        self.stdout.write(self.style.SUCCESS(f'✓ {len(mantenimientos)} mantenimientos creados'))
        
        self.stdout.write(self.style.SUCCESS('\n¡Datos de prueba creados exitosamente!'))
    
    def crear_vehiculos(self, cantidad):
        marcas = ['Toyota', 'Honda', 'Nissan', 'Ford', 'Chevrolet', 'Mazda']
        modelos = {
            'Toyota': ['Corolla', 'Camry', 'RAV4'],
            'Honda': ['Civic', 'Accord', 'CR-V'],
            'Nissan': ['Sentra', 'Altima', 'X-Trail'],
            'Ford': ['Focus', 'Fusion', 'Escape'],
            'Chevrolet': ['Cruze', 'Malibu', 'Equinox'],
            'Mazda': ['3', '6', 'CX-5']
        }
        tipos = ['AUTO', 'CAMIONETA', 'VAN']
        
        vehiculos = []
        for i in range(cantidad):
            marca = random.choice(marcas)
            modelo = random.choice(modelos[marca])
            
            vehiculo = Vehiculo.objects.create(
                placa=f'ABC{1000 + i}',
                marca=marca,
                modelo=modelo,
                año=random.randint(2015, 2023),
                tipo=random.choice(tipos),
                kilometraje=random.randint(5000, 100000),
                propietario_nombre=f'Usuario {i+1}',
                propietario_telefono=f'993{random.randint(1000000, 9999999)}',
                color=random.choice(['Blanco', 'Negro', 'Gris', 'Rojo', 'Azul'])
            )
            vehiculos.append(vehiculo)
        
        return vehiculos
    
    def crear_talleres(self, cantidad):
        # Coordenadas alrededor de Villahermosa
        lat_base = 17.9892
        lon_base = -92.9475
        
        talleres = []
        for i in range(cantidad):
            # Variar coordenadas ligeramente
            lat = Decimal(str(lat_base + random.uniform(-0.05, 0.05)))
            lon = Decimal(str(lon_base + random.uniform(-0.05, 0.05)))
            
            taller = TallerMecanico.objects.create(
                nombre=f'Taller {["Central", "Norte", "Sur", "Este", "Oeste"][i % 5]} {i+1}',
                direccion=f'Av. Principal {random.randint(100, 999)}',
                telefono=f'993{random.randint(1000000, 9999999)}',
                latitud=lat,
                longitud=lon,
                calificacion=Decimal(str(round(random.uniform(3.5, 5.0), 2))),
                horario='Lun-Vie 8:00-18:00, Sáb 8:00-14:00',
                verificado=random.choice([True, False])
            )
            talleres.append(taller)
        
        return talleres
    
    def crear_mantenimientos(self, vehiculos, talleres):
        tipos = ['PREVENTIVO', 'CORRECTIVO', 'REVISION', 'REPARACION']
        estados = ['COMPLETADO', 'PENDIENTE', 'EN_PROCESO']
        
        titulos = [
            'Cambio de aceite y filtro',
            'Revisión de frenos',
            'Alineación y balanceo',
            'Cambio de llantas',
            'Revisión general',
            'Reparación de motor',
            'Cambio de batería'
        ]
        
        mantenimientos = []
        for vehiculo in vehiculos:
            # Crear 2-4 mantenimientos por vehículo
            num_mantenimientos = random.randint(2, 4)
            
            for i in range(num_mantenimientos):
                estado = random.choice(estados)
                fecha_base = datetime.now().date() - timedelta(days=random.randint(1, 365))
                
                mantenimiento = Mantenimiento.objects.create(
                    vehiculo=vehiculo,
                    taller=random.choice(talleres),
                    tipo=random.choice(tipos),
                    titulo=random.choice(titulos),
                    descripcion=f'Mantenimiento {random.choice(tipos).lower()} realizado según especificaciones',
                    estado=estado,
                    fecha_programada=fecha_base if estado == 'PENDIENTE' else None,
                    fecha_realizado=fecha_base if estado == 'COMPLETADO' else None,
                    kilometraje_realizado=vehiculo.kilometraje - random.randint(0, 10000),
                    costo=Decimal(str(random.randint(200, 5000)))
                )
                mantenimientos.append(mantenimiento)
        
        return mantenimientos