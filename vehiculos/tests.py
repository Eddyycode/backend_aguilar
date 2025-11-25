# vehiculos/tests.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from .models import Vehiculo, TallerMecanico, Mantenimiento


class VehiculoModelTest(TestCase):
    """
    Tests para el modelo Vehiculo
    """
    
    def setUp(self):
        self.vehiculo = Vehiculo.objects.create(
            placa='ABC123',
            marca='Toyota',
            modelo='Corolla',
            año=2020,
            tipo='AUTO',
            kilometraje=15000,
            propietario_nombre='Juan Pérez'
        )
    
    def test_vehiculo_creation(self):
        """Prueba la creación de un vehículo"""
        self.assertEqual(self.vehiculo.placa, 'ABC123')
        self.assertEqual(self.vehiculo.marca, 'Toyota')
        self.assertTrue(self.vehiculo.activo)
    
    def test_vehiculo_str(self):
        """Prueba el método __str__"""
        expected = "Toyota Corolla (ABC123)"
        self.assertEqual(str(self.vehiculo), expected)
    
    def test_vehiculo_nombre_completo(self):
        """Prueba el método get_nombre_completo"""
        expected = "Toyota Corolla 2020"
        self.assertEqual(self.vehiculo.get_nombre_completo(), expected)


class TallerMecanicoModelTest(TestCase):
    """
    Tests para el modelo TallerMecanico
    """
    
    def setUp(self):
        self.taller = TallerMecanico.objects.create(
            nombre='Taller Central',
            direccion='Av. Principal 123',
            telefono='9931234567',
            latitud=Decimal('17.9892'),
            longitud=Decimal('-92.9475'),
            calificacion=Decimal('4.5')
        )
    
    def test_taller_creation(self):
        """Prueba la creación de un taller"""
        self.assertEqual(self.taller.nombre, 'Taller Central')
        self.assertEqual(self.taller.calificacion, Decimal('4.5'))
    
    def test_taller_coordenadas(self):
        """Prueba el método get_coordenadas"""
        coords = self.taller.get_coordenadas()
        self.assertEqual(coords, (17.9892, -92.9475))


class VehiculoAPITest(APITestCase):
    """
    Tests para los endpoints de Vehiculo
    """
    
    def setUp(self):
        self.vehiculo_data = {
            'placa': 'XYZ789',
            'marca': 'Honda',
            'modelo': 'Civic',
            'año': 2021,
            'tipo': 'AUTO',
            'kilometraje': 10000,
            'propietario_nombre': 'María González'
        }
    
    def test_create_vehiculo(self):
        """Prueba la creación de un vehículo vía API"""
        url = reverse('vehiculo-list')
        response = self.client.post(url, self.vehiculo_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vehiculo.objects.count(), 1)
        self.assertEqual(Vehiculo.objects.get().placa, 'XYZ789')
    
    def test_list_vehiculos(self):
        """Prueba el listado de vehículos"""
        Vehiculo.objects.create(**self.vehiculo_data)
        
        url = reverse('vehiculo-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_vehiculo_detail(self):
        """Prueba obtener detalle de un vehículo"""
        vehiculo = Vehiculo.objects.create(**self.vehiculo_data)
        
        url = reverse('vehiculo-detail', args=[vehiculo.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['placa'], 'XYZ789')
    
    def test_update_vehiculo(self):
        """Prueba actualizar un vehículo"""
        vehiculo = Vehiculo.objects.create(**self.vehiculo_data)
        
        url = reverse('vehiculo-detail', args=[vehiculo.id])
        updated_data = self.vehiculo_data.copy()
        updated_data['kilometraje'] = 20000
        
        response = self.client.put(url, updated_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        vehiculo.refresh_from_db()
        self.assertEqual(vehiculo.kilometraje, 20000)
    
    def test_delete_vehiculo(self):
        """Prueba eliminar un vehículo"""
        vehiculo = Vehiculo.objects.create(**self.vehiculo_data)
        
        url = reverse('vehiculo-detail', args=[vehiculo.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Vehiculo.objects.count(), 0)
    
    def test_vehiculo_invalid_data(self):
        """Prueba crear vehículo con datos inválidos"""
        invalid_data = {
            'placa': '',  # Placa vacía
            'marca': 'Honda',
            'modelo': 'Civic',
            'año': 2021
        }
        
        url = reverse('vehiculo-list')
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MantenimientoAPITest(APITestCase):
    """
    Tests para los endpoints de Mantenimiento
    """
    
    def setUp(self):
        self.vehiculo = Vehiculo.objects.create(
            placa='TEST123',
            marca='Toyota',
            modelo='Corolla',
            año=2020,
            kilometraje=15000,
            propietario_nombre='Test User'
        )
        
        self.taller = TallerMecanico.objects.create(
            nombre='Taller Test',
            direccion='Calle Test 123',
            latitud=Decimal('17.9892'),
            longitud=Decimal('-92.9475')
        )
        
        self.mantenimiento_data = {
            'vehiculo': self.vehiculo.id,
            'taller': self.taller.id,
            'tipo': 'PREVENTIVO',
            'titulo': 'Cambio de aceite',
            'descripcion': 'Cambio de aceite y filtro',
            'estado': 'PENDIENTE',
            'kilometraje_realizado': 15000,
            'costo': '500.00'
        }
    
    def test_create_mantenimiento(self):
        """Prueba crear un mantenimiento"""
        url = reverse('mantenimiento-list')
        response = self.client.post(url, self.mantenimiento_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Mantenimiento.objects.count(), 1)
    
    def test_list_mantenimientos(self):
        """Prueba listar mantenimientos"""
        Mantenimiento.objects.create(
            vehiculo=self.vehiculo,
            taller=self.taller,
            tipo='PREVENTIVO',
            titulo='Test',
            descripcion='Test',
            kilometraje_realizado=15000
        )
        
        url = reverse('mantenimiento-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_completar_mantenimiento(self):
        """Prueba completar un mantenimiento"""
        mantenimiento = Mantenimiento.objects.create(
            vehiculo=self.vehiculo,
            taller=self.taller,
            tipo='PREVENTIVO',
            titulo='Test',
            descripcion='Test',
            estado='PENDIENTE',
            kilometraje_realizado=15000
        )
        
        url = reverse('mantenimiento-completar', args=[mantenimiento.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mantenimiento.refresh_from_db()
        self.assertEqual(mantenimiento.estado, 'COMPLETADO')
        self.assertIsNotNone(mantenimiento.fecha_realizado)